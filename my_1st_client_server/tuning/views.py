from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Car, Order
from .decorators import superuser_required, user_required
from django.contrib.auth.decorators import login_required
from .forms import OrderForm
from django.contrib import messages
from django import forms

class CarListView(ListView):
    model = Car
    paginate_by = 10

class CarCreateView(CreateView):
    model = Car
    fields = ['vin_id','base_price', 'description']

class CarUpdateView(UpdateView):
    model = Car
    fields = ['base_price', 'description']
    template_name_suffix = '_update_form'

class CarDeleteView(DeleteView):
    model = Car
    success_url = '/cars/'
    template_name_suffix = '_confirm_delete'

from rest_framework import viewsets, filters
from .serializers import CarSerializer

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['vin_id']

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

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
                return redirect('admin_panel')  # Важно указать правильное имя URL
            else:
                return redirect('user_page')  # Или куда нужно для обычного пользователя
        else:
            messages.error(request, 'Неверные логин или пароль')
            return redirect('login')

    return render(request, 'login.html')


@superuser_required
def admin_panel(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_panel.html', {
        'orders': orders,
        'user': request.user,
        'has_orders': orders.exists()
    })


@user_required
def user_page(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Считаем общую сумму
    total_sum = sum(order.total_price for order in user_orders)

    return render(request, 'user_page.html', {
        'orders': user_orders,
        'user': request.user,
        'total_sum': total_sum
    })


@login_required
def create_order(request):
    if request.method == 'POST':
        # Копируем POST данные и добавляем user
        post_data = request.POST.copy()
        if not request.user.is_superuser:
            post_data['user'] = request.user.id

        form = OrderForm(post_data)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            if request.user.is_superuser:
                return redirect('admin_panel')
            else:
                return redirect('user_page')
        else:
            print("FORM ERRORS:", form.errors)
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