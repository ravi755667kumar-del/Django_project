from django.shortcuts import render,redirect
from .models import Customer,Drink,Snacks
from .models import Order_data
import json


def menu(request):
    drinks = Drink.objects.all()
    snacks = Snacks.objects.all()


    return render(request, "menu.html",{
        "hot_drinks": drinks.filter(category="Hot"),
        "cold_drinks":drinks.filter(category="Cold"),
        "snacks": snacks
    })


def login(request):
    if request.method == "POST":

        action = request.POST.get("action")

        # ------------------ SIGNUP ------------------

        if action == "signup":

            name = request.POST.get("name")
            email = request.POST.get("email")
            password = request.POST.get("password")

            # Check if email already exists
            if Customer.objects.filter(email=email).exists():
                return render (request, "login.html", {
                    "error_message" : " Invalid Email or Password"  
                })

         
            # Save new customer
            customer = Customer(
                name=name,
                email=email,
                password=password
            )

            customer.save()

            print("Customer Saved Successfully")

            # Open Tea World after registration
            return redirect("menu")
            

        # ------------------ LOGIN ------------------

        elif action == "login":

            email = request.POST.get("email")
            password = request.POST.get("password")

            try:

                customer = Customer.objects.get(
                    email=email,
                    password=password
                )

                print("Login Successful")

                # Open Tea World
                return redirect("menu")

            except Customer.DoesNotExist:

                print("Invalid Email or Password")

                return render(request, "login.html", {
                    "error_message": "Invalid Email or Password"
                })

    return render(request, "login.html",)


def cart(request):
    return render(request, "cart.html")



def order(request):

    if request.method == "POST":

        mobile = request.POST.get("customer_mobile")

        cart_data = request.POST.get("cart_data")

        cart = json.loads(cart_data)

        for item in cart:

            Order_data.objects.create(

                item_name=item["name"],

                quantity=item["quantity"],

                price=item["price"] * item["quantity"],

                mobile=mobile

            )

        return redirect("payment")

    return render(request, "order.html")
def payment(request):
    return render(request, "payment.html")
def success(request):
    return render(request,"success.html")




