from django.db import models
from django.core.validators import RegexValidator



class Drink(models.Model):
    CATEGORY = (
        ('Hot', 'Hot'),
        ('Cold', 'Cold'),
        ('Snacks', 'Snacks'),
    )

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY)
    price = models.IntegerField()
    description = models.TextField()


    def __str__(self):
        return self.name

class Snacks(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return self.name

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)



    def __str__(self):
        return self.name
    

mobile_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='Enter a valid 10-digit mobile number.'
)

class Order_data(models.Model):
    item_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    mobile = models.CharField(
        max_length=10,
        validators=[mobile_validator]
    )
    Order_data_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_name

