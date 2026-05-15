from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Car, Order

# ============================================================
# ТЕСТЫ МОДЕЛЕЙ (Django ORM) — без изменений
# ============================================================

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
        self.assertEqual(car.base_price, 500000)


class OrderModelTest(TestCase):

    def setUp(self):
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


# ============================================================
# ТЕСТЫ ENTITIES (без Django)
# ============================================================

from .entities.car import CarEntity
from .entities.order import OrderEntity


class CarEntityTest(TestCase):

    def test_create_car_entity(self):
        car = CarEntity(vin_id='ENT123', base_price=700000, description='Тест')
        self.assertEqual(car.vin_id, 'ENT123')
        self.assertEqual(car.base_price, 700000)
        self.assertEqual(car.description, 'Тест')

    def test_car_entity_default_description(self):
        car = CarEntity(vin_id='ENT456', base_price=500000)
        self.assertEqual(car.description, '')


class OrderEntityTest(TestCase):

    def test_create_order_entity(self):
        order = OrderEntity(
            order_id=1,
            user_id=10,
            vin_id='ENT789',
            base_price=600000,
            tuning_options=['Турбонаддув'],
            total_price=650000,
            username='testuser'
        )
        self.assertEqual(order.order_id, 1)
        self.assertEqual(order.user_id, 10)
        self.assertEqual(order.vin_id, 'ENT789')
        self.assertEqual(order.tuning_options, ['Турбонаддув'])
        self.assertEqual(order.total_price, 650000)
        self.assertEqual(order.username, 'testuser')


# ============================================================
# ТЕСТЫ USE CASES (с Fake-репозиториями, без БД)
# ============================================================

from .use_cases.calculate_price import CalculatePriceUseCase
from .use_cases.create_order import CreateOrderUseCase
from .use_cases.get_user_orders import GetUserOrdersUseCase
from .use_cases.get_all_orders import GetAllOrdersUseCase
from .interfaces.order_repository import OrderRepository
from .interfaces.car_repository import CarRepository


class FakeCarRepository(CarRepository):
    """Фейковый репозиторий автомобилей (хранит в памяти)"""

    def __init__(self):
        self.cars = {}

    def get_or_create(self, vin_id: str, base_price: int) -> CarEntity:
        if vin_id not in self.cars:
            self.cars[vin_id] = CarEntity(vin_id=vin_id, base_price=base_price)
        return self.cars[vin_id]

    def get_by_vin(self, vin_id: str):
        return self.cars.get(vin_id)

    def get_by_id(self, car_id):
        for car in self.cars.values():
            if car.vin_id == car_id:
                return car
        return None


class FakeOrderRepository(OrderRepository):
    """Фейковый репозиторий заказов (хранит в памяти)"""

    def __init__(self):
        self.orders = []
        self.next_id = 1

    def create(self, user_id, vin_id, base_price, tuning_options, total_price):
        order = OrderEntity(
            order_id=self.next_id,
            user_id=user_id,
            vin_id=vin_id,
            base_price=base_price,
            tuning_options=tuning_options,
            total_price=total_price,
            username=f'user_{user_id}'
        )
        self.orders.append(order)
        self.next_id += 1
        return order

    def get_by_user(self, user_id):
        return [o for o in self.orders if o.user_id == user_id]

    def get_all(self):
        return self.orders


class CalculatePriceUseCaseTest(TestCase):
    """Тесты расчёта цены (без БД!)"""

    def setUp(self):
        self.use_case = CalculatePriceUseCase()

    def test_no_options(self):
        price = self.use_case.execute(base_price=500000, selected_options=[])
        self.assertEqual(price, 500000)

    def test_engine_only(self):
        price = self.use_case.execute(base_price=500000, selected_options=['engine'])
        self.assertEqual(price, 750000)  # 500k + 50% = 750k

    def test_nitrous_only(self):
        price = self.use_case.execute(base_price=500000, selected_options=['nitrous'])
        self.assertEqual(price, 600000)  # 500k + 100k

    def test_turbine_only(self):
        price = self.use_case.execute(base_price=500000, selected_options=['turbine'])
        self.assertEqual(price, 550000)  # 500k + 50k

    def test_sound_only(self):
        price = self.use_case.execute(base_price=500000, selected_options=['sound'])
        self.assertEqual(price, 600000)  # 500k + 20% = 600k

    def test_all_options(self):
        price = self.use_case.execute(
            base_price=500000,
            selected_options=['engine', 'nitrous', 'turbine', 'sound']
        )
        # 500k + 250k + 100k + 50k + 100k = 1 000 000
        self.assertEqual(price, 1000000)

    def test_unknown_option_ignored(self):
        price = self.use_case.execute(base_price=500000, selected_options=['rocket'])
        self.assertEqual(price, 500000)  # нет такого — не добавляем

    def test_round_multiplier(self):
        price = self.use_case.execute(base_price=333333, selected_options=['engine'])
        expected = 333333 + 166666  # round(166666.5) = 166666 в Python
        self.assertEqual(price, expected)


class CreateOrderUseCaseTest(TestCase):
    """Тесты создания заказа (с Fake-репозиториями)"""

    def setUp(self):
        self.order_repo = FakeOrderRepository()
        self.car_repo = FakeCarRepository()
        self.use_case = CreateOrderUseCase(
            order_repository=self.order_repo,
            car_repository=self.car_repo
        )

    def test_create_order_new_car(self):
        order = self.use_case.execute(
            user_id=1,
            vin_id='NEWVIN001',
            car_id=None,
            base_price=600000,
            options=['engine']
        )
        self.assertEqual(order.vin_id, 'NEWVIN001')
        self.assertEqual(order.base_price, 600000)
        self.assertEqual(order.total_price, 900000)  # 600k + 50%
        self.assertEqual(order.tuning_options, ['engine'])
        self.assertEqual(len(self.order_repo.orders), 1)

    def test_create_order_existing_car(self):
        # Сначала создаём авто через репозиторий
        self.car_repo.get_or_create('EXIST001', 800000)

        order = self.use_case.execute(
            user_id=2,
            vin_id='EXIST001',
            car_id=None,
            base_price=0,  # подтянется из существующего
            options=['turbine']
        )
        self.assertEqual(order.base_price, 800000)
        self.assertEqual(order.total_price, 850000)  # 800k + 50k

    def test_create_order_by_car_id(self):
        # Админ выбирает авто из списка
        car = self.car_repo.get_or_create('BYID001', 700000)

        order = self.use_case.execute(
            user_id=3,
            vin_id='',
            car_id='BYID001',
            base_price=700000,
            options=['sound']
        )
        self.assertEqual(order.vin_id, 'BYID001')
        self.assertEqual(order.total_price, 840000)  # 700k + 20%

    def test_create_order_missing_vin_raises_error(self):
        with self.assertRaises(ValueError):
            self.use_case.execute(
                user_id=4,
                vin_id='',
                car_id=None,
                base_price=500000,
                options=[]
            )


class GetUserOrdersUseCaseTest(TestCase):
    """Тесты получения заказов пользователя"""

    def setUp(self):
        self.repo = FakeOrderRepository()
        self.use_case = GetUserOrdersUseCase(order_repository=self.repo)

    def test_returns_only_user_orders(self):
        self.repo.create(user_id=1, vin_id='A', base_price=100, tuning_options=[], total_price=100)
        self.repo.create(user_id=2, vin_id='B', base_price=200, tuning_options=[], total_price=200)
        self.repo.create(user_id=1, vin_id='C', base_price=300, tuning_options=[], total_price=300)

        orders = self.use_case.execute(user_id=1)
        self.assertEqual(len(orders), 2)
        for order in orders:
            self.assertEqual(order.user_id, 1)

    def test_returns_empty_list_for_new_user(self):
        orders = self.use_case.execute(user_id=999)
        self.assertEqual(orders, [])


class GetAllOrdersUseCaseTest(TestCase):
    """Тесты получения всех заказов"""

    def setUp(self):
        self.repo = FakeOrderRepository()
        self.use_case = GetAllOrdersUseCase(order_repository=self.repo)

    def test_returns_all_orders(self):
        self.repo.create(user_id=1, vin_id='A', base_price=100, tuning_options=[], total_price=100)
        self.repo.create(user_id=2, vin_id='B', base_price=200, tuning_options=[], total_price=200)

        orders = self.use_case.execute()
        self.assertEqual(len(orders), 2)


# ============================================================
# ТЕСТЫ VIEWS (Django TestCase) — без изменений
# ============================================================

class ViewsTest(TestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='admin123'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            password='user123'
        )
        self.car = Car.objects.create(
            vin_id='VIEWTEST12345',
            base_price=800000
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Центр тюнинга автомобилей')

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

    def test_admin_panel_as_superuser(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('admin_panel'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Панель администратора')

    def test_admin_panel_as_regular_user(self):
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('admin_panel'))
        self.assertEqual(response.status_code, 302)

    def test_user_page_as_regular_user(self):
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('user_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Личный кабинет')

    def test_user_page_as_superuser(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('user_page'))
        self.assertEqual(response.status_code, 302)

    def test_user_page_shows_only_own_orders(self):
        Order.objects.create(
            user=self.regular_user,
            car=self.car,
            base_price=800000,
            tuning_options=['Турбонаддув'],
            total_price=850000
        )
        Order.objects.create(
            user=self.superuser,
            car=self.car,
            base_price=800000,
            tuning_options=[],
            total_price=800000
        )
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('user_page'))
        self.assertContains(response, 'Турбонаддув')
        self.assertNotContains(response, 'admin')

    def test_create_order_page_requires_login(self):
        response = self.client.get(reverse('create_order'))
        self.assertEqual(response.status_code, 302)

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
            'base_price': 600000,  # не пустая строка
            'tuning_options': '["Улучшение двигателя", "Турбонаддув"]',
            'total_price': 950000,
        })
        self.assertRedirects(response, reverse('user_page'))
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
            'vin_id': 'VIEWTEST12345',
            'base_price': 800000,  # явно, не пустая
            'tuning_options': '["Закись азота"]',
            'total_price': 900000,
        })
        self.assertRedirects(response, reverse('user_page'))
        order = Order.objects.first()
        self.assertEqual(order.base_price, 800000)

    def test_logout(self):
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))


# ============================================================
# ТЕСТЫ API
# ============================================================

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
        response = self.client.get('/api/cars/APITEST123456/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['vin_id'], 'APITEST123456')
        self.assertEqual(data['base_price'], 750000)

    def test_car_search(self):
        response = self.client.get('/api/cars/?search=APITEST')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_car_search_not_found(self):
        response = self.client.get('/api/cars/?search=ZZZZZZ')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)


# ============================================================
# ТЕСТЫ ФОРМ
# ============================================================

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

    def test_form_invalid_negative_base_price(self):
        from .forms import OrderForm
        form = OrderForm(data={
            'user': self.user.id,
            'vin_id': 'NEGTEST001',
            'base_price': -100,
            'tuning_options': '[]',
            'total_price': 0,
        })
        self.assertFalse(form.is_valid())
        self.assertTrue('base_price' in form.errors)

