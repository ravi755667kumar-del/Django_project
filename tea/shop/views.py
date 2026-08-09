from django.shortcuts import render, redirect
from django.db import IntegrityError
from .models import Customer, Drink, Snacks
from .models import Order_data
from django.db.models import Q
from django.http import JsonResponse
from .chat import ask_bot
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from django.contrib.auth import login as django_admin_login
import random
import time
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
import threading
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from shop.tokens import token_generator
from shop.email_utlis import send_reset_email, send_otp_email
from shop.recommendations.dataset import update_dataset
from shop.recommendations.predict import get_ml_recommendations


# ── helper ──────────────────────────────────────────────────────────────────
def is_logged_in(request):
    return request.session.get("customer_id") is not None


# ── AUTH ─────────────────────────────────────────────────────────────────────
def login(request):
    # Already logged-in → go straight to menu
    if is_logged_in(request):
        return redirect("menu")

    if request.method == "POST":
        action = request.POST.get("action")

        # ------------------ SIGNUP (Generate OTP) ------------------
        if action == "signup":
            name     = request.POST.get("name", "").strip()
            email    = request.POST.get("email", "").strip()
            password = request.POST.get("password", "")

            # Check if this email belongs to a Django superuser
            # We look up by email only, then verify password — bypasses OTP for admins
            admin_user = User.objects.filter(email=email, is_superuser=True).first()
            if admin_user and admin_user.check_password(password):
                django_admin_login(request, admin_user)
                return redirect("/admin/")

            if Customer.objects.filter(email=email).exists():
                return render(request, "login.html", {
                    "error_message": "This email is already registered. Please log in instead.",
                    "form_name": name, "form_email": email,
                })

            # Generate OTP
            otp = str(random.randint(100000, 999999))
            
            # Save temporary registration data to session
            request.session['temp_user'] = {
                'name': name,
                'email': email,
                'password': password,
                'otp': otp,
                'otp_time': time.time()
            }

            # Send OTP Email via Brevo in background thread — page returns instantly
            def _send_otp_email():
                try:
                    send_otp_email(name, email, otp)
                except Exception as e:
                    print(f"\n[!] OTP EMAIL FAILED: {e}\n")

            threading.Thread(target=_send_otp_email, daemon=True).start()

            # Render login page with OTP section open immediately
            return render(request, "login.html", {"show_otp": True, "email": email})

        # ------------------ VERIFY OTP ------------------
        elif action == "verify_otp":
            entered_otp = request.POST.get("otp", "").strip()
            temp_user = request.session.get('temp_user')

            if not temp_user:
                return render(request, "login.html", {
                    "error_message": "Session expired. Please register again."
                })

            email = temp_user.get('email', '')

            # Check if OTP is expired (60 seconds)
            if time.time() - temp_user['otp_time'] > 60:
                del request.session['temp_user']
                return render(request, "login.html", {
                    "error_message": "OTP expired. Please fill the form again."
                })

            if entered_otp == temp_user['otp']:
                try:
                    # Valid OTP! Create the customer account with hashed password.
                    customer = Customer(
                        name=temp_user['name'],
                        email=temp_user['email'],
                        password=make_password(temp_user['password'])
                    )
                    customer.save()
                except IntegrityError:
                    # If they double-clicked verify or email exists, gracefully fail
                    del request.session['temp_user']
                    return render(request, "login.html", {
                        "error_message": "This email is already registered. Please log in instead."
                    })

                # Clean session and log in
                del request.session['temp_user']
                request.session.flush()
                request.session["customer_id"]   = customer.id
                request.session["customer_name"] = customer.name

                return redirect("menu")
            else:
                return render(request, "login.html", {
                    "show_otp": True,
                    "email": email,
                    "error_message": "Wrong OTP. Please try again."
                })

        # ------------------ LOGIN ------------------
        elif action == "login":
            email    = request.POST.get("email")
            password = request.POST.get("password")

            # Check if this matches a Django Admin Superuser
            admin_user = User.objects.filter(email=email, is_superuser=True).first()
            if admin_user and admin_user.check_password(password):
                django_admin_login(request, admin_user)
                return redirect("/admin/")

            try:
                customer = Customer.objects.get(email=email)

                # Verify password with hash
                if check_password(password, customer.password):
                    # Save session
                    request.session.flush()
                    request.session["customer_id"]   = customer.id
                    request.session["customer_name"] = customer.name
                    return redirect("menu")
                
                # Fallback to upgrade existing plain-text passwords
                elif customer.password == password:
                    customer.password = make_password(password)
                    customer.save()
                    
                    request.session.flush()
                    request.session["customer_id"]   = customer.id
                    request.session["customer_name"] = customer.name
                    return redirect("menu")
                
                else:
                    return render(request, "login.html", {
                        "error_message": "Invalid Email or Password"
                    })

            except Customer.DoesNotExist:
                return render(request, "login.html", {
                    "error_message": "Invalid Email or Password"
                })

    return render(request, "login.html")


def logout_view(request):
    request.session.flush()
    return redirect("login")

def delete_account(request):
    customer_id = request.session.get("customer_id")
    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
            customer.delete()
        except Customer.DoesNotExist:
            pass
    request.session.flush()
    return redirect("login")

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            customer = Customer.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(customer.pk))
            token = token_generator.make_token(customer)
            
            # Build the reset link
            reset_url = request.build_absolute_uri(reverse('reset_password', kwargs={'uidb64': uid, 'token': token}))
            
            # Send reset email in background thread so page returns instantly
            def _send_reset():
                try:
                    send_reset_email(customer.email, reset_url)
                except Exception as e:
                    print(f"\n[!] RESET EMAIL ERROR: {e}\n")

            threading.Thread(target=_send_reset, daemon=True).start()

            messages.success(request, "A password reset link has been sent to your email.", extra_tags='forgot')
        except Customer.DoesNotExist:
            messages.error(request, "If that email exists in our system, a reset link was sent.", extra_tags='forgot')
            
        return render(request, "login.html", {"forgot_error": True})
    return redirect("login")

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        customer = Customer.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Customer.DoesNotExist):
        customer = None

    if customer is not None and token_generator.check_token(customer, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            re_password = request.POST.get("re_password")
            
            if new_password != re_password:
                return render(request, "reset_password.html", {"error": "Passwords do not match.", "uidb64": uidb64, "token": token})
                
            customer.password = make_password(new_password)
            customer.save()
            messages.success(request, "Password reset successfully! Please log in.", extra_tags='login_success')
            return redirect("login")

        return render(request, "reset_password.html", {"uidb64": uidb64, "token": token})
    else:
        return render(request, "reset_password.html", {"error": "Invalid or expired password reset link."})



# ── MENU ──────────────────────────────────────────────────────────────────────
def menu(request):
    search       = request.GET.get("search", "")
    price_filter = request.GET.get("price_filter", "")

    drinks = Drink.objects.all()
    snacks = Snacks.objects.all()

    if search:
        drinks = drinks.filter(
            Q(name__icontains=search) | Q(category__icontains=search)
        )
        snacks = snacks.filter(Q(name__icontains=search))

    if price_filter == "low_high":
        drinks = drinks.order_by("price")
        snacks = snacks.order_by("price")
    elif price_filter == "high_low":
        drinks = drinks.order_by("-price")
        snacks = snacks.order_by("-price")

    # Ask the Machine Learning model for recommendations!
    rec_items = get_ml_recommendations(top_n=5)

    return render(request, "menu.html", {
        "hot_drinks":    drinks.filter(category="Hot"),
        "cold_drinks":   drinks.filter(category="Cold"),
        "snacks":        snacks,
        "customer_name": request.session.get("customer_name", "Guest"),
        "rec_items":     rec_items,
    })


def search_menu(request):
    search       = request.GET.get("search", "")
    price_filter = request.GET.get("price_filter", "")

    drinks = Drink.objects.all()
    snacks = Snacks.objects.all()

    if search:
        drinks = drinks.filter(
            Q(name__icontains=search) | Q(category__icontains=search)
        )
        snacks = snacks.filter(Q(name__icontains=search))

    if price_filter == "low_high":
        drinks = drinks.order_by("price")
        snacks = snacks.order_by("price")
    elif price_filter == "high_low":
        drinks = drinks.order_by("-price")
        snacks = snacks.order_by("-price")

    return render(request, "menu_item.html", {
        "hot_drinks":  drinks.filter(category="Hot"),
        "cold_drinks": drinks.filter(category="Cold"),
        "snacks":      snacks,
    })


# ── PROTECTED VIEWS ───────────────────────────────────────────────────────────
def cart(request):
    return render(request, "cart.html", {
        "is_logged_in": is_logged_in(request)
    })


def order(request):
    if not is_logged_in(request):
        return redirect("login")

    if request.method == "POST":
        mobile    = request.POST.get("customer_mobile")
        cart_data = request.POST.get("cart_data")
        cart      = json.loads(cart_data)

        # Get the logged-in customer object from session
        customer_id = request.session.get("customer_id")
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return redirect("login")

        order_ids = request.session.get("user_orders", [])

        for item in cart:
            order_item = Order_data.objects.create(
                item_name=item["name"],
                quantity=item["quantity"],
                price=item["price"] * item["quantity"],
                mobile=mobile,
                customer=customer
            )
            order_ids.append(order_item.id)

        request.session["user_orders"] = order_ids

        # ── Step 1: Update dataset.csv with new order + weather ──────────────
        # Run in ONE background thread so the user is NOT kept waiting
        def update_only():
            try:
                update_dataset()           # rebuilds dataset.csv
                print("[AI] Dataset updated successfully. (Offline training mode active)")
            except Exception as e:
                print(f"[AI] Error during dataset update: {e}")

        thread = threading.Thread(target=update_only, daemon=True)
        thread.start()

        return redirect("payment")

    return render(request, "order.html")
@csrf_exempt
def chatbot(request):

    if request.method == "POST":

        data = json.loads(request.body)

        question = data.get("message")


        # Get or create session key to use as user_id for memory
        if not request.session.session_key:
            request.session.create()
        user_id = request.session.session_key
        customer_name = request.session.get("customer_name", "Guest")

        answer = ask_bot(question, user_id, customer_name)

        return JsonResponse({
            "reply": answer
        })

    return JsonResponse({
        "reply": "Invalid request"
    })
def order_history(request):
    if not is_logged_in(request):
        return redirect("login")

    # Fetch the logged-in customer from the DB
    customer_id = request.session.get("customer_id")
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return redirect("login")

    # Get ALL orders for this customer from the database
    # This works even after logout & re-login because it's stored in DB, not session
    orders = Order_data.objects.filter(customer=customer).order_by("-Order_data_date")

    return render(request, "order_history.html", {"orders": orders})

def payment(request):
    if not is_logged_in(request):
        return redirect("login")
    return render(request, "payment.html")


def success(request):
    return render(request, "success.html")
