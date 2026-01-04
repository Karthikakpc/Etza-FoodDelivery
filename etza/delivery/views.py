from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .models import User, Restaurant, Item, Cart

import razorpay
from django.conf import settings

def index(request):
    top_restaurants = Restaurant.objects.order_by('-rating')[:4]
    return render(request, 'index.html', {
        'top_restaurants': top_restaurants
    })


def auth(request):
    mode = request.GET.get("mode", "signin")

    error = None
    success = None

    # Handle errors from redirects
    if request.GET.get("error") == "invalid":
        error = "Invalid username or password"

    if request.GET.get("error") == "duplicate":
        error = "User already exists with this mobile number"

    if request.GET.get("success"):
        success = "Account created successfully. Please sign in."

    return render(request, 'auth.html', {
        "mode": mode,
        "error": error,
        "success": success
    })


from django.shortcuts import render, redirect

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            User.objects.get(username=username, password=password)

            if username == 'admin':
                return render(request, 'admin_home.html')

            restaurantList = Restaurant.objects.all()
            return render(request, 'customer_home.html', {
                "restaurantList": restaurantList,
                "username": username
            })

        except User.DoesNotExist:
            # 🔴 redirect with error flag
            return redirect('/auth?error=invalid')

    return redirect('/auth')

        
    
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        # 🔴 Duplicate mobile check
        if User.objects.filter(mobile=mobile).exists():
            return redirect('/auth?mode=signup&error=duplicate')

        User.objects.create(
            username=username,
            password=password,
            email=email,
            mobile=mobile,
            address=address
        )

        return redirect('/auth?success=1')

    return redirect('/auth?mode=signup')



    
def open_add_restaurant(request):
    return render(request, 'add_restaurant.html')

def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')

        if Restaurant.objects.filter(name=name).exists():
            return HttpResponse("Duplicate restaurant!")

        Restaurant.objects.create(
            name=name,
            picture=picture,
            cuisine=cuisine,
            rating=rating,
        )

        # ✅ Redirect with success flag
        return redirect('/open_add_restaurant?success=1')

    return render(request, 'add_restaurant.html')

def open_show_restaurant(request):
    restaurantList = Restaurant.objects.all()
    return render(request, 'show_restaurants.html', {
        "restaurantList": restaurantList,
        "is_admin": True
    })



def open_update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    return render(request, 'update_restaurant.html', {"restaurant" : restaurant})

def update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)

    if request.method == 'POST':
        restaurant.name = request.POST.get('name')
        restaurant.picture = request.POST.get('picture')
        restaurant.cuisine = request.POST.get('cuisine')
        restaurant.rating = request.POST.get('rating')
        restaurant.save()

    return redirect('open_show_restaurant')


def delete_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    restaurant.delete()

    restaurantList = Restaurant.objects.all()
    return render(request, 'show_restaurants.html',{"restaurantList" : restaurantList})

def open_update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    #itemList = Item.objects.all()
    return render(request, 'update_menu.html',{"itemList" : itemList, "restaurant" : restaurant})

def update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        vegeterian = request.POST.get('vegeterian') == 'on'
        picture = request.POST.get('picture')

        # DUPLICATE CHECK (per restaurant)
        if Item.objects.filter(restaurant=restaurant, name=name).exists():
            return redirect(f'/open_update_menu/{restaurant_id}?duplicate=1')

        Item.objects.create(
            restaurant=restaurant,
            name=name,
            description=description,
            price=price,
            vegeterian=vegeterian,
            picture=picture
        )

        return redirect(f'/open_update_menu/{restaurant_id}?success=1')

    itemList = restaurant.items.all()
    return render(request, 'update_menu.html', {
        'restaurant': restaurant,
        'itemList': itemList
    })


def view_menu(request, restaurant_id, username):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    #return HttpResponse("Items collected")
    #itemList = Item.objects.all()
    return render(request, 'customer_menu.html'
                  ,{"itemList" : itemList,
                     "restaurant" : restaurant, 
                     "username":username})

from django.shortcuts import redirect
def add_to_cart(request, item_id, username):
    item = Item.objects.get(id=item_id)
    customer = User.objects.get(username=username)

    cart, created = Cart.objects.get_or_create(customer=customer)
    cart.items.add(item)

    #add success flag
    return redirect(
        f"/view_menu/{item.restaurant.id}/{username}?added=1"
    )



def show_cart(request, username):
    customer = User.objects.get(username = username)
    cart = Cart.objects.filter(customer=customer).first()
    items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    return render(request, 'cart.html',{"itemList" : items, "total_price" : total_price, "username":username})

from django.shortcuts import render, get_object_or_404
from django.conf import settings
import razorpay

from .models import User, Cart


def checkout(request, username):
    # 1️⃣ Get user
    customer = get_object_or_404(User, username=username)

    # 2️⃣ Get cart
    cart = Cart.objects.filter(customer=customer).first()

    if not cart or cart.items.count() == 0:
        return render(request, 'checkout.html', {
            'username': username,
            'cart_items': [],
            'total_price': 0,
            'error': 'Your cart is empty!'
        })

    cart_items = cart.items.all()
    total_price = cart.total_price()  # MUST return number (int/float)

    # 3️⃣ Razorpay client (TEST MODE)
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    # 4️⃣ Create Razorpay Order
    order = client.order.create({
        "amount": int(total_price * 100),  # amount in paise
        "currency": "INR",
        "payment_capture": 1
    })

    # 5️⃣ Send data to template
    return render(request, 'checkout.html', {
        'username': username,
        'cart_items': cart_items,
        'total_price': total_price,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],
    })


def orders(request, username):
    customer = get_object_or_404(User, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    return render(request, 'orders.html', {
        'username': username,
        'customer': customer,
        'cart_items': cart_items,
        'total_price': total_price
    })


#------------------------
def open_update_item(request, item_id):
    item = Item.objects.get(id=item_id)
    return render(request, 'update_item.html', {'item': item})

def update_item(request, item_id):
    item = Item.objects.get(id=item_id)

    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.price = request.POST.get('price')
        item.vegeterian = request.POST.get('vegeterian') == 'on'
        item.picture = request.POST.get('picture')
        item.save()

    return redirect('open_update_menu', restaurant_id=item.restaurant.id)


def delete_item(request, item_id):
    item = Item.objects.get(id=item_id)
    restaurant_id = item.restaurant.id
    item.delete()
    return redirect('open_update_menu', restaurant_id=restaurant_id)


from django.shortcuts import redirect, get_object_or_404
from .models import Cart, Item, User

def remove_from_cart(request, item_id, username):
    if request.method == "POST":
        customer = get_object_or_404(User, username=username)
        cart = get_object_or_404(Cart, customer=customer)
        item = get_object_or_404(Item, id=item_id)

        cart.items.remove(item)  

    return redirect('show_cart', username=username)

def clear_cart(request, username):
    customer = get_object_or_404(User, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    if cart:
        cart.items.clear()

    return redirect('/')
