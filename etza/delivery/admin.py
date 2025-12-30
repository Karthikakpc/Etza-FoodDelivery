from django.contrib import admin
from .models import Item, Restaurant, User, Cart

# Register your models here.
admin.site.register(User)
admin.site.register(Restaurant)
admin.site.register(Item)
admin.site.register(Cart)