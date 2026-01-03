from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .models import User, Restaurant, Item, Cart

import razorpay
from django.conf import settings

# Create your views here.
def index(request):
    return render(request, 'index.html')

def auth(request):
    mode = request.GET.get("mode", "signin")
    return render(request, 'auth.html', {
        "mode": mode
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
            return render(request, 'fail.html')

    return redirect('/auth')


        
    
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exists")

        User.objects.create(
            username=username,
            password=request.POST.get('password'),
            email=request.POST.get('email'),
            mobile=request.POST.get('mobile'),
            address=request.POST.get('address')
        )

        return redirect('/auth?mode=signin')

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

def checkout(request, username):
    # Fetch customer and their cart
    customer = get_object_or_404(User, username=username)
    cart = Cart.objects.filter(customer=customer).first()
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    if total_price == 0:
        return render(request, 'checkout.html', {
            'error': 'Your cart is empty!',
        })
    
    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Razorpay order
    order_data = {
        'amount': int(total_price * 100),  # Amount in paisa
        'currency': 'INR',
        'payment_capture': '1',  # Automatically capture payment
    }
    order = client.order.create(data=order_data)

    # Pass the order details to the frontend
    return render(request, 'checkout.html', {
        'username': username,
        'cart_items': cart_items,
        'total_price': total_price,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],  # Razorpay order ID
        'amount': total_price,
    })

def orders(request, username):
    customer = get_object_or_404(User, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    # Fetch cart items and total price before clearing the cart
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    # Clear the cart after fetching its details
    if cart:
        cart.items.clear()

    return render(request, 'orders.html', {
        'username': username,
        'customer': customer,
        'cart_items': cart_items,
        'total_price': total_price,
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
