from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone 
from decimal import Decimal

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('cashier', 'Кассир'),
        ('admin', 'Администратор'),
    )
    POSITION_CHOICES = (
        ('user', 'Пользователь'),
        ('cashier', 'Кассир'),
        ('admin', 'Администратор'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name='Роль')
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='user', verbose_name='Должность')
    
    employee_profile = models.OneToOneField(
        'Employee', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name='Профиль сотрудника'
    )

class Employee(models.Model):
    POSITION_CHOICES = (
        ('user', 'Пользователь'),
        ('cashier', 'Кассир'),
        ('admin', 'Администратор'),
    )
    
    DEFAULT_HOURLY_RATES = {
        'user': Decimal('200'),
        'cashier': Decimal('250'),
        'admin': Decimal('400'),
    }
    
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='user', verbose_name='Должность')
    
    # === ОПЛАТА ===
    hourly_rate = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0,
        verbose_name='Ставка ₽/час'
    )
    
    # === ГРАФИК РАБОТЫ ===
    work_start = models.TimeField(
        default='09:00',
        verbose_name='Начало рабочего дня'
    )
    work_end = models.TimeField(
        default='18:00',
        verbose_name='Конец рабочего дня'
    )
    break_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name='Перерыв (мин)'
    )
    work_days = models.CharField(
        max_length=20,
        default='1,2,3,4,5',
        verbose_name='Рабочие дни',
        help_text='1=Пн, 2=Вт, 3=Ср, 4=Чт, 5=Пт, 6=Сб, 7=Вс'
    )
    
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Зарплата', default=0)
    hire_date = models.DateField(verbose_name='Дата приема', default=timezone.now) 
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True, null=True)
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.hourly_rate == 0:
            self.hourly_rate = self.DEFAULT_HOURLY_RATES.get(self.position, Decimal('200'))
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def hours_per_day(self):
        """Рабочих часов в день"""
        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), self.work_start)
        end = datetime.combine(datetime.today(), self.work_end)
        if end < start:
            end += timedelta(days=1)
        total_minutes = (end - start).seconds // 60 - self.break_minutes
        return Decimal(total_minutes) / 60
    
    @property
    def work_days_list(self):
        """Список рабочих дней как числа"""
        if not self.work_days:
            return [1, 2, 3, 4, 5]
        return [int(d.strip()) for d in self.work_days.split(',') if d.strip().isdigit()]
    
    @property
    def work_days_display(self):
        """Красивое отображение рабочих дней"""
        days_names = {1: 'Пн', 2: 'Вт', 3: 'Ср', 4: 'Чт', 5: 'Пт', 6: 'Сб', 7: 'Вс'}
        return ', '.join(days_names.get(d, '') for d in self.work_days_list)
    
    @property
    def schedule_display(self):
        """Красивое отображение графика"""
        return f"{self.work_start.strftime('%H:%M')} - {self.work_end.strftime('%H:%M')}"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_position_display()}"
    
    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

class Payroll(models.Model):
    """Расчётный лист зарплаты"""
    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('confirmed', 'Подтверждён'),
        ('paid', 'Выплачено'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник', related_name='payrolls')
    
    period_start = models.DateField(verbose_name='Начало периода')
    period_end = models.DateField(verbose_name='Конец периода')
    
    # Отработанное время
    work_days = models.PositiveIntegerField(default=0, verbose_name='Рабочих дней')  # НОВОЕ
    total_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name='Всего часов')
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name='Переработка')
    
    # Начисления
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Оклад/Базовая')
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='За переработку')
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Премия')
    
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Начислено')
    
    ndfl_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='НДФЛ (13%)')
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Прочие удержания')
    
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='К выплате')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата выплаты')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name='Создал')
    
    def __str__(self):
        return f"{self.employee.full_name} | {self.period_start} - {self.period_end} | {self.net_salary} ₽"
    
    class Meta:
        verbose_name = 'Расчётный лист'
        verbose_name_plural = 'Расчётные листы'
        ordering = ['-period_end', 'employee']
    """Расчётный лист зарплаты"""
    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('confirmed', 'Подтверждён'),
        ('paid', 'Выплачено'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник', related_name='payrolls')
    
    # Период
    period_start = models.DateField(verbose_name='Начало периода')
    period_end = models.DateField(verbose_name='Конец периода')
    
    # Отработанное время (для почасовых)
    total_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name='Всего часов')
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name='Переработка')
    
    # Начисления
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Оклад/Базовая')
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='За переработку')
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Премия')
    
    # Итого начислено
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Начислено')
    
    # Удержания
    ndfl_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='НДФЛ (13%)')
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Прочие удержания')
    
    # На руки
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='К выплате')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата выплаты')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name='Создал')
    
    def __str__(self):
        return f"{self.employee.full_name} | {self.period_start} - {self.period_end} | {self.net_salary} ₽"
    
    class Meta:
        verbose_name = 'Расчётный лист'
        verbose_name_plural = 'Расчётные листы'
        ordering = ['-period_end', 'employee']

class Visitor(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = 'Посетитель'
        verbose_name_plural = 'Посетители'

class Ticket(models.Model):
    TICKET_TYPES = (
        ('adult', 'Взрослый'),
        ('child', 'Детский'),
        ('family', 'Семейный'),
        ('vip', 'VIP всё включено'),
        ('water', 'Водная зона'),       
        ('extreme', 'Экстрим-пакет'), 
    )
    
    TICKET_PRICES = {
        'adult': 1500,
        'child': 800, 
        'family': 3500,
        'vip': 5000,
        'water': 1200,
        'extreme': 2000,
    }
    
    
    
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, verbose_name='Посетитель')
    ticket_type = models.CharField(max_length=10, choices=TICKET_TYPES, verbose_name='Тип билета')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена')
    purchase_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата покупки')
    valid_date = models.DateField(verbose_name='Действителен до')
    cashier = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Кассир')
    
    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.TICKET_PRICES.get(self.ticket_type, 0)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.visitor} - {self.get_ticket_type_display()}"
    
    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'


class Attraction(models.Model):
    """Аттракционы и зоны парка Немо"""
    ZONE_CHOICES = (
        ('water', 'Водная зона'),
        ('extreme', 'Экстремальные аттракционы'),
        ('kids', 'Детская зона'),
        ('relax', 'Зона отдыха'),
        ('food', 'Фудкорт'),
    )
    
    name = models.CharField(max_length=200, verbose_name='Название')
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES, verbose_name='Зона')
    description = models.TextField(verbose_name='Описание', blank=True)
    min_age = models.PositiveIntegerField(default=0, verbose_name='Мин. возраст')
    min_height = models.PositiveIntegerField(default=0, verbose_name='Мин. рост (см)')
    is_active = models.BooleanField(default=True, verbose_name='Работает')
    
    def __str__(self):
        return f"{self.name} ({self.get_zone_display()})"
    
    class Meta:
        verbose_name = 'Аттракцион'
        verbose_name_plural = 'Аттракционы'
    
class Product(models.Model):
    """Товары (еда и напитки)"""
    CATEGORY_CHOICES = (
        ('pizza', 'Пицца'),
        ('burger', 'Бургеры'),
        ('snack', 'Закуски'),
        ('drink', 'Напитки'),
        ('dessert', 'Десерты'),
        ('combo', 'Комбо-наборы'),
    )
    
    name = models.CharField(max_length=200, verbose_name='Название')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Категория')
    description = models.TextField(verbose_name='Описание', blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена')
    image_emoji = models.CharField(max_length=10, default='🍽️', verbose_name='Иконка')
    is_available = models.BooleanField(default=True, verbose_name='В наличии')
    is_popular = models.BooleanField(default=False, verbose_name='Популярное')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Добавлено')
    
    def __str__(self):
        return f"{self.image_emoji} {self.name} - {self.price} ₽"
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['category', 'name']


class Order(models.Model):
    """Заказы еды"""
    STATUS_CHOICES = (
        ('pending', 'В обработке'),
        ('preparing', 'Готовится'),
        ('ready', 'Готов'),
        ('delivered', 'Выдан'),
        ('cancelled', 'Отменён'),
    )
    
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, verbose_name='Посетитель', null=True, blank=True)
    products = models.ManyToManyField(Product, through='OrderItem', verbose_name='Товары')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Итого')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    cashier = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Кассир')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    notes = models.TextField(blank=True, verbose_name='Примечания')
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.total_price} ₽"
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Позиции в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена')
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    def get_total(self):
        return self.price * self.quantity
    
    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'