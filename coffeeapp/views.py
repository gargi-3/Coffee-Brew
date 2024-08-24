from django.http import HttpResponse
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from . models import Coffee, Food, Cart, CartItem, OrderItems
from . forms import SearchForm, OrderCreateForm
from django.contrib.auth.decorators import login_required
from . forms import UserRegistrationForm
# from . forms import UserRegistrationForm, CustomPasswordChangeForm #PWC
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Create your views here.
def home(request):
    return render(request, 'base.html')

def coffee_list(request):
    form = SearchForm(request.GET or None)
    coffees = Coffee.objects.all()

    if form.is_valid():
        query = form.cleaned_data['query']
        coffees = coffees.filter(name__icontains=query)

    return render(request, 'coffeeapp/coffee_list.html', {'coffees':coffees, 'form': form})

def coffee_detail(request, pk):
    coffee = get_object_or_404(Coffee, pk=pk)
    return render(request, 'coffeeapp/coffee_detail.html', {'coffee':coffee})

def food_list(request):
    form = SearchForm(request.GET or None)
    foods = Food.objects.all()

    if form.is_valid():
        query = form.cleaned_data['query']
        foods = foods.filter(name__icontains=query)

    return render(request, 'coffeeapp/food_list.html', {'foods':foods, 'form': form})

def food_detail(request, pk):
    food = get_object_or_404(Food, pk=pk)
    return render(request, 'coffeeapp/food_detail.html', {'food':food})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'coffeeapp/register.html', {'form':form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('coffee_list')
            else : 
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    return render(request, 'coffeeapp/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

# PWC
# @login_required
# def password_change_view(request):
#     if request.method == 'POST':
#         form = CustomPasswordChangeForm(user=request.user, data=request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login')
#     else:
#         form = CustomPasswordChangeForm(user=request.user)
#     return render(request, 'coffeeapp/password_change.html', {'form': form})

@login_required
def add_to_cart(request, item_type, item_id):
    user_cart, created = Cart.objects.get_or_create(user_id=request.user.id)
    if item_type == 'coffee':
        item = get_object_or_404(Coffee, id=item_id)
        cart_item, created = CartItem.objects.get_or_create(cart=user_cart, coffee=item)
    else:
        item = get_object_or_404(Food, id=item_id)
        cart_item, created = CartItem.objects.get_or_create(cart=user_cart, food=item)

    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user_id=request.user.id)
    cart_items = CartItem.objects.filter(cart=cart) 
    total = sum(item.total for item in cart_items)
    print("total : ", total )
    return render(request, 'coffeeapp/cart_detail.html', {'cart_items': cart_items, 'total': total})

@login_required
def increase_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')

@login_required
def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_detail')

@login_required
def order_create(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()

            for item in cart.items.all():
                OrderItems.objects.create(
                    order=order,
                    food=item.food,
                    coffee=item.coffee,
                    price=item.food.price if item.food else item.coffee.price,
                    quantity=item.quantity
                )
            cart.items.all().delete()

            # Send email with order details
            subject = f'Order Confirmation - {order.id}'
            html_message = render_to_string('coffeeapp/order_confirmation_email.html', {'order': order})
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            to = form.cleaned_data['email']
            send_mail(subject, plain_message, from_email, [to], html_message=html_message, fail_silently=False)

            total_amount = order.total_cost

            client = razorpay.Client(auth=(settings.RAZORPAY_TEST_KEY_ID, settings.RAZORPAY_TEST_KEY_SECRET))
            payment_data = {
                'amount': int(total_amount * 100),  
                'currency': 'INR',
                'receipt': f'order_{order.id}',
            }
            payment = client.order.create(data=payment_data)

            return render(request, 'coffeeapp/order_created.html', {'order': order, 'payment': payment, 'razorpay_key_id': settings.RAZORPAY_TEST_KEY_ID})
    else: 
        form = OrderCreateForm()
    return render(request, 'coffeeapp/order_create.html', {'cart': cart, 'form': form})

@login_required
@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        return HttpResponse("Payment Successful!")
    return HttpResponse(status=400)

def search(request):
    query = request.GET.get('query')
    coffee_results = Coffee.objects.filter(name__icontains=query) if query else []
    food_results = Food.objects.filter(name__icontains=query) if query else []
    context = {
        'query': query,
        'coffee_results': coffee_results,
        'food_results': food_results,
    }
    return render(request, 'search_results.html', context)