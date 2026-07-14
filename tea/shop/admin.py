from django.contrib import admin
from .models import Customer, Drink, Snacks, Order_data

@admin.register(Drink)
class DrinkAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price")

@admin.register(Snacks)
class SnacksAdmin(admin.ModelAdmin):
    list_display = ("name", "price")

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email")

@admin.register(Order_data)
class Order_dataAdmin(admin.ModelAdmin):
    list_display =("item_name","price","quantity","mobile")