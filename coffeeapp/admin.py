from django.contrib import admin
from . models import Coffee, Food, Cart, CartItem

# Register your models here.
admin.site.register(Coffee)
admin.site.register(Food)
admin.site.register(Cart)
admin.site.register(CartItem)
