from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Coffee(models.Model):
    SMALL = 'S'
    MEDIUM = 'M'
    LARGE = 'L'
    SIZE_CHOICES = [
        (SMALL, 'Small'),
        (MEDIUM, 'Medium'),
        (LARGE, 'Large'),
    ]

    name = models.CharField(max_length=255)
    size = models.CharField(max_length=1, choices=SIZE_CHOICES, default=SMALL)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='coffees/', blank=True, null=True)

    def str(self):
        return f"{self.name} ({self.get_size_display()})"
    
class Food(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='foods/', blank=True, null=True)

    def _str_(self):
        return f"{self.name}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user.username}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    coffee = models.ForeignKey(Coffee, null=True, blank=True, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}"
    
    def get_item_name(self):
        if self.coffee:
            return self.coffee.name
        return self.food.name
    
    @property
    def total(self):
        if self.food:
            return self.food.price * self.quantity
        if self.coffee:
            return self.coffee.price * self.quantity
        return Decimal('0.00')

class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id}"
    
    @property
    def total_cost(self):
        return sum(item.price * item.quantity for item in self.items.all())

class OrderItems(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    food = models.ForeignKey(Food, null=True, blank=True, on_delete=models.CASCADE)
    coffee = models.ForeignKey(Coffee, null=True, blank=True, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.food if self.food else self.coffee}"
