from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone 

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
    
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='user', verbose_name='Должность')
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Зарплата', default=0)
    hire_date = models.DateField(verbose_name='Дата приема', default=timezone.now) 
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True, null=True)
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_position_display()}"
    
    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

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