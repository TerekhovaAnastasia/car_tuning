from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Car, TuningOption
from django.shortcuts import render, redirect
from .decorators import superuser_required, user_required
from django.contrib.auth.decorators import login_required
from .forms import OrderForm
from .models import Order

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

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

from rest_framework import viewsets
from .serializers import CarSerializer

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

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
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            return redirect('admin_panel')
    else:
        form = OrderForm()
    return render(request, 'create_order.html', {'form': form})

@user_required
def user_page(request):
    user_orders = Order.objects.filter(user=request.user)
    return render(request, 'user_page.html', {'orders': user_orders})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


