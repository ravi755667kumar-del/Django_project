from django.shortcuts import render,redirect
from .models import Customer,Drink,Snacks
from .models import Order_data


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
        item_name = request.POST.get("item_name")
        quantity = request.POST.get("quantity")
        price = request.POST.get("price")

        Order_data.objects.create(
            mobile=mobile,
            item_name=item_name,
            quantity=quantity,
            price=price
        )

        return redirect("payment.html")

    return render(request,"order.html")
def payment(request):
    return render(request, "payment.html")
def success(request):
    return render(request,"success.html")




