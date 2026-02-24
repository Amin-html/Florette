from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
import json

from .models import Flower, Category, Order, OrderItem, Review
from .forms import RegisterForm, ReviewForm, FlowerForm, CheckoutForm


def is_admin(user):
    return user.is_staff or user.is_superuser


def index(request):
    featured = Flower.objects.filter(is_featured=True, in_stock=True)[:4]
    categories = Category.objects.all()
    new_arrivals = Flower.objects.filter(in_stock=True)[:8]
    return render(request, 'shop/index.html', {
        'featured': featured,
        'categories': categories,
        'new_arrivals': new_arrivals,
    })


def catalog(request):
    flowers = Flower.objects.filter(in_stock=True)
    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    search = request.GET.get('q', '')
    sort = request.GET.get('sort', '')

    if category_slug:
        flowers = flowers.filter(category__slug=category_slug)
    if search:
        flowers = flowers.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if sort == 'price_asc':
        flowers = flowers.order_by('price')
    elif sort == 'price_desc':
        flowers = flowers.order_by('-price')

    return render(request, 'shop/catalog.html', {
        'flowers': flowers,
        'categories': categories,
        'current_category': category_slug,
        'search': search,
        'sort': sort,
    })


def flower_detail(request, pk):
    flower = get_object_or_404(Flower, pk=pk)
    reviews = flower.reviews.all()
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        if user_review:
            messages.error(request, 'Вы уже оставили отзыв на этот товар.')
        else:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.flower = flower
                review.user = request.user
                review.save()
                messages.success(request, '💐 Спасибо за ваш отзыв!')
                return redirect('flower_detail', pk=pk)

    return render(request, 'shop/flower_detail.html', {
        'flower': flower,
        'reviews': reviews,
        'form': form,
        'user_review': user_review,
    })


@require_POST
def add_to_cart(request, pk):
    flower = get_object_or_404(Flower, pk=pk)
    cart = request.session.get('cart', {})
    key = str(pk)
    cart[key] = cart.get(key, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({'success': True, 'count': sum(cart.values())})


@require_POST
def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    key = str(pk)
    if key in cart:
        del cart[key]
        request.session['cart'] = cart
        request.session.modified = True
    return JsonResponse({'success': True, 'count': sum(cart.values())})


@require_POST
def update_cart(request, pk):
    data = json.loads(request.body)
    qty = int(data.get('quantity', 1))
    cart = request.session.get('cart', {})
    key = str(pk)
    if qty > 0:
        cart[key] = qty
    else:
        cart.pop(key, None)
    request.session['cart'] = cart
    request.session.modified = True
    total = sum(Flower.objects.get(pk=k).price * v for k, v in cart.items() if Flower.objects.filter(pk=k).exists())
    return JsonResponse({'success': True, 'count': sum(cart.values()), 'total': str(total)})


def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for pk, qty in cart.items():
        try:
            flower = Flower.objects.get(pk=pk)
            subtotal = flower.price * qty
            total += subtotal
            items.append({'flower': flower, 'qty': qty, 'subtotal': subtotal})
        except Flower.DoesNotExist:
            pass
    return render(request, 'shop/cart.html', {'items': items, 'total': total})


@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, 'Корзина пуста!')
        return redirect('cart')

    items = []
    total = 0
    for pk, qty in cart.items():
        try:
            flower = Flower.objects.get(pk=pk)
            subtotal = flower.price * qty
            total += subtotal
            items.append({'flower': flower, 'qty': qty, 'subtotal': subtotal, 'pk': pk})
        except Flower.DoesNotExist:
            pass

    form = CheckoutForm()
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                total=total,
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    flower=item['flower'],
                    quantity=item['qty'],
                    price=item['flower'].price,
                )
            request.session['cart'] = {}
            messages.success(request, f'🌸 Заказ #{order.id} успешно оформлен! Мы свяжемся с вами.')
            return redirect('order_success', pk=order.id)

    return render(request, 'shop/checkout.html', {'items': items, 'total': total, 'form': form})


@login_required
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'shop/order_success.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'shop/my_orders.html', {'orders': orders})


# --- Auth ---

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '🌺 Добро пожаловать в Florette!')
            return redirect('index')
    return render(request, 'shop/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'index'))
        else:
            messages.error(request, 'Неверный логин или пароль')
    return render(request, 'shop/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


# --- Admin panel ---

@login_required
@user_passes_test(is_admin)
def admin_panel(request):
    flowers = Flower.objects.all()
    orders = Order.objects.all()[:10]
    return render(request, 'shop/admin_panel.html', {'flowers': flowers, 'orders': orders})


@login_required
@user_passes_test(is_admin)
def flower_add(request):
    form = FlowerForm()
    if request.method == 'POST':
        form = FlowerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '🌸 Цветок добавлен!')
            return redirect('admin_panel')
    return render(request, 'shop/flower_form.html', {'form': form, 'action': 'Добавить'})


@login_required
@user_passes_test(is_admin)
def flower_edit(request, pk):
    flower = get_object_or_404(Flower, pk=pk)
    form = FlowerForm(instance=flower)
    if request.method == 'POST':
        form = FlowerForm(request.POST, request.FILES, instance=flower)
        if form.is_valid():
            form.save()
            messages.success(request, '✏️ Цветок обновлён!')
            return redirect('admin_panel')
    return render(request, 'shop/flower_form.html', {'form': form, 'action': 'Редактировать', 'flower': flower})


@login_required
@user_passes_test(is_admin)
def flower_delete(request, pk):
    flower = get_object_or_404(Flower, pk=pk)
    if request.method == 'POST':
        flower.delete()
        messages.success(request, '🗑️ Цветок удалён.')
        return redirect('admin_panel')
    return render(request, 'shop/flower_confirm_delete.html', {'flower': flower})
