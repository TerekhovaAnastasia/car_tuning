from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Car, Order


class CarModelTest(TestCase):

    def test_create_car(self):
        car = Car.objects.create(
            vin_id='XTA210990Y2766389',
            base_price=500000,
            description='Тестовый автомобиль'
        )
        self.assertEqual(car.vin_id, 'XTA210990Y2766389')
        self.assertEqual(car.base_price, 500000)
        self.assertEqual(str(car), 'Автомобиль XTA210990Y2766389')

    def test_car_default_price(self):
        car = Car.objects.create(
            vin_id='ZFA22300005556789',
            description='Без указания цены'
        )
        self.assertEqual(car.base_price, 500000)  # Значение по умолчанию


class OrderModelTest(TestCase):

    def setUp(self):
        # Создаём пользователя и автомобиль для тестов
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.car = Car.objects.create(
            vin_id='TESTVIN123456',
            base_price=1000000,
            description='Тестовое авто'
        )

    def test_create_order(self):
        order = Order.objects.create(
            user=self.user,
            car=self.car,
            base_price=1000000,
            tuning_options=['Улучшение двигателя'],
            total_price=1500000
        )
        self.assertEqual(order.user.username, 'testuser')
        self.assertEqual(order.car.vin_id, 'TESTVIN123456')
        self.assertEqual(order.tuning_options, ['Улучшение двигателя'])
        self.assertEqual(order.total_price, 1500000)
        self.assertIsNotNone(order.created_at)

    def test_order_str(self):
        order = Order.objects.create(
            user=self.user,
            car=self.car,
            base_price=500000,
            tuning_options=[],
            total_price=500000
        )
        self.assertEqual(str(order), f'Заказ {order.id} от testuser')


class ViewsTest(TestCase):

    def setUp(self):
        # Создание пользователей
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='admin123'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            password='user123'
        )
        # Создание автомобиля
        self.car = Car.objects.create(
            vin_id='VIEWTEST12345',
            base_price=800000
        )

    #Тесты домашней страницы
    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Центр тюнинга автомобилей')

    #Тесты страницы логина
    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Авторизация')

    def test_login_superuser(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertRedirects(response, reverse('admin_panel'))

    def test_login_regular_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'user',
            'password': 'user123'
        })
        self.assertRedirects(response, reverse('user_page'))

    def test_login_wrong_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'wrongpass'
        })
        self.assertRedirects(response, reverse('login'))

    #Тесты админ-панели
    def test_admin_panel_as_superuser(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('admin_panel'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Панель администратора')

    def test_admin_panel_as_regular_user(self):
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('admin_panel'))
        # Обычного пользователя должно редиректить
        self.assertEqual(response.status_code, 302)

    #Тесты страницы пользователя
    def test_user_page_as_regular_user(self):
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('user_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Личный кабинет')

    def test_user_page_as_superuser(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('user_page'))
        # Суперпользователя должно редиректить
        self.assertEqual(response.status_code, 302)

    def test_user_page_shows_only_own_orders(self):
        # Создание заказа для обычного пользователя
        Order.objects.create(
            user=self.regular_user,
            car=self.car,
            base_price=800000,
            tuning_options=['Турбонаддув'],
            total_price=850000
        )
        # Создание заказа для суперпользователя
        Order.objects.create(
            user=self.superuser,
            car=self.car,
            base_price=800000,
            tuning_options=[],
            total_price=800000
        )

        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('user_page'))

        # Проверка, что виден заказ только обычного пользователя
        self.assertContains(response, 'Турбонаддув')
        self.assertNotContains(response, 'admin')

    #Тесты создания заказа
    def test_create_order_page_requires_login(self):
        response = self.client.get(reverse('create_order'))
        self.assertEqual(response.status_code, 302)  # Редирект на логин

    def test_create_order_page_as_user(self):
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('create_order'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Создание нового заказа')

    def test_create_order_post(self):
        self.client.login(username='user', password='user123')
        response = self.client.post(reverse('create_order'), {
            'user': self.regular_user.id,
            'vin_id': 'NEWVIN1234567890',
            'base_price': 600000,
            'tuning_options': '["Улучшение двигателя", "Турбонаддув"]',
            'total_price': 950000,
        })
        self.assertRedirects(response, reverse('user_page'))

        # Проверяем, что заказ создался
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.user, self.regular_user)
        self.assertEqual(order.car.vin_id, 'NEWVIN1234567890')
        self.assertEqual(order.total_price, 950000)
        self.assertIn('Улучшение двигателя', order.tuning_options)
        self.assertIn('Турбонаддув', order.tuning_options)

    def test_create_order_existing_car(self):
        self.client.login(username='user', password='user123')
        response = self.client.post(reverse('create_order'), {
            'user': self.regular_user.id,
            'vin_id': 'VIEWTEST12345',  # Существующий VIN
            'base_price': '',  # Пусто — подтянется из базы
            'tuning_options': '["Закись азота"]',
            'total_price': 900000,
        })
        self.assertRedirects(response, reverse('user_page'))

        order = Order.objects.first()
        self.assertEqual(order.base_price, 800000)

    #Тест выхода
    def test_logout(self):
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))


class APITest(TestCase):

    def setUp(self):
        self.car = Car.objects.create(
            vin_id='APITEST123456',
            base_price=750000,
            description='API тест'
        )

    def test_car_list(self):
        response = self.client.get('/api/cars/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_car_detail(self):
        response = self.client.get(f'/api/cars/APITEST123456/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['vin_id'], 'APITEST123456')
        self.assertEqual(data['base_price'], 750000)

    def test_car_search(self):
        response = self.client.get('/api/cars/?search=APITEST')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_car_search_not_found(self):
        response = self.client.get('/api/cars/?search=NOTEXIST')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)


class FormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='formuser', password='pass123')
        self.car = Car.objects.create(vin_id='FORMTEST12345', base_price=700000)

    def test_form_valid_with_vin(self):
        from .forms import OrderForm
        form = OrderForm(data={
            'user': self.user.id,
            'vin_id': 'NEWVIN9876543210',
            'base_price': 500000,
            'tuning_options': '["Улучшение двигателя"]',
            'total_price': 750000,
        })
        self.assertTrue(form.is_valid())

    def test_form_valid_with_existing_car(self):
        from .forms import OrderForm
        form = OrderForm(data={
            'user': self.user.id,
            'car': self.car.pk,
            'tuning_options': '[]',
            'total_price': 700000,
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid_no_car_no_vin(self):
        from .forms import OrderForm
        form = OrderForm(data={
            'user': self.user.id,
            'tuning_options': '[]',
            'total_price': 0,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('Введите VIN или выберите автомобиль', str(form.errors))
