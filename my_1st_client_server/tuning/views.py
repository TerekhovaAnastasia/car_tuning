from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms

from .decorators import superuser_required, user_required
from .forms import OrderForm
from .adapters.django_order_repository import DjangoOrderRepository
from .adapters.django_car_repository import DjangoCarRepository
from .use_cases.create_order import CreateOrderUseCase
from .use_cases.get_user_orders import GetUserOrdersUseCase
from .use_cases.get_all_orders import GetAllOrdersUseCase


def home(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_panel')
            else:
                return redirect('user_page')
        else:
            messages.error(request, 'Неверные логин или пароль')
            return redirect('login')

    return render(request, 'login.html')


@superuser_required
def admin_panel(request):
    use_case = GetAllOrdersUseCase(order_repository=DjangoOrderRepository())
    orders = use_case.execute()

    return render(request, 'admin_panel.html', {
        'orders': orders,
        'user': request.user,
        'has_orders': len(orders) > 0
    })


@user_required
def user_page(request):
    use_case = GetUserOrdersUseCase(order_repository=DjangoOrderRepository())
    orders = use_case.execute(user_id=request.user.id)

    total_sum = sum(order.total_price for order in orders)

    return render(request, 'user_page.html', {
        'orders': orders,
        'user': request.user,
        'total_sum': total_sum
    })


@login_required
def create_order(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        if not request.user.is_superuser:
            post_data['user'] = request.user.id

        form = OrderForm(post_data)
        if form.is_valid():
            # Сохраняем заказ напрямую через форму (как в лабе №2)
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            if request.user.is_superuser:
                return redirect('admin_panel')
            else:
                return redirect('user_page')
    else:
        form = OrderForm()
        if not request.user.is_superuser:
            form.fields['user'].widget = forms.HiddenInput()
            form.fields['user'].initial = request.user
            form.fields['car'].widget = forms.HiddenInput()

    return render(request, 'create_order.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


# REST API
from rest_framework import viewsets, filters
from .serializers import CarSerializer
from .models import Car

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['vin_id']