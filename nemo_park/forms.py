from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
import re
from .models import CustomUser, Employee, Visitor, Ticket, Product
from datetime import date, timedelta

# ==================== ВАЛИДАТОРЫ ====================

# Валидатор для телефона (только российские номера)
phone_validator = RegexValidator(
    regex=r'^\+7\s?\(?\d{3}\)?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}$',
    message='Введите номер в формате: +7 (999) 123-45-67'
)

# Валидатор для имени/фамилии (только буквы)
name_validator = RegexValidator(
    regex=r'^[а-яА-ЯёЁa-zA-Z\s\-]+$',
    message='Только буквы, пробелы и дефис'
)


# ==================== ФУНКЦИИ ОЧИСТКИ ====================

def clean_name(value, field_name='Поле'):
    """Очистка и валидация имени/фамилии"""
    if not value:
        return value
    
    value = value.strip()
    
    # Проверка на цифры
    if any(char.isdigit() for char in value):
        raise ValidationError(f'{field_name} не должно содержать цифры')
    
    # Проверка на спецсимволы (кроме дефиса и пробела)
    if not re.match(r'^[а-яА-ЯёЁa-zA-Z\s\-]+$', value):
        raise ValidationError(f'{field_name} может содержать только буквы, пробелы и дефис')
    
    # Минимальная длина
    if len(value) < 2:
        raise ValidationError(f'{field_name} должно содержать минимум 2 буквы')
    
    # Приводим к нормальному виду (первая буква заглавная)
    return ' '.join(word.capitalize() for word in value.split())


def clean_phone(value):
    """Очистка и валидация телефона"""
    if not value:
        return value
    
    # Убираем все кроме цифр
    digits = re.sub(r'\D', '', value)
    
    # Проверяем длину
    if len(digits) == 11 and digits.startswith('8'):
        digits = '7' + digits[1:]
    elif len(digits) == 10:
        digits = '7' + digits
    elif len(digits) != 11 or not digits.startswith('7'):
        raise ValidationError('Введите корректный российский номер телефона')
    
    # Форматируем
    return f'+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}'


def clean_salary(value):
    """Очистка и валидация зарплаты"""
    if value is None:
        return value
    
    if value < 0:
        raise ValidationError('Зарплата не может быть отрицательной')
    
    if value > 10000000:
        raise ValidationError('Слишком большое значение зарплаты')
    
    return value


# ==================== ФОРМЫ ====================

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите логин',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label='Пароль', 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите пароль',
            'autocomplete': 'current-password'
        })
    )


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        label='Имя',
        min_length=2,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ваше имя',
            'pattern': '[а-яА-ЯёЁa-zA-Z\\s\\-]+',
            'title': 'Только буквы, пробелы и дефис'
        })
    )
    last_name = forms.CharField(
        label='Фамилия', 
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ваша фамилия',
            'pattern': '[а-яА-ЯёЁa-zA-Z\\s\\-]+',
            'title': 'Только буквы, пробелы и дефис'
        })
    )
    phone = forms.CharField(
        label='Телефон',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control phone-mask', 
            'placeholder': '+7 (___) ___-__-__',
            'data-mask': '+7 (999) 999-99-99'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Придумайте логин'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Введите email'
            }),
        }
        labels = {
            'username': 'Логин',
            'email': 'Email',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
    
    def clean_first_name(self):
        return clean_name(self.cleaned_data.get('first_name'), 'Имя')
    
    def clean_last_name(self):
        value = self.cleaned_data.get('last_name')
        if value:
            return clean_name(value, 'Фамилия')
        return value
    
    def clean_phone(self):
        value = self.cleaned_data.get('phone')
        if value:
            return clean_phone(value)
        return value


class EmployeeForm(forms.ModelForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин для входа'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )
    
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'position', 'hourly_rate',
                  'work_start', 'work_end', 'break_minutes', 'work_days',
                  'phone', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '250', 'step': '10'}),
            'work_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}, format='%H:%M'),
            'work_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}, format='%H:%M'),
            'break_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '60'}),
            'work_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1,2,3,4,5'}),
            'phone': forms.TextInput(attrs={'class': 'form-control phone-mask', 'placeholder': '+7 (___) ___-__-__'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
        }


class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Имя',
                'pattern': '[а-яА-ЯёЁa-zA-Z\\s\\-]+',
                'title': 'Только буквы'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Фамилия',
                'pattern': '[а-яА-ЯёЁa-zA-Z\\s\\-]+',
                'title': 'Только буквы'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control phone-mask', 
                'placeholder': '+7 (___) ___-__-__',
                'data-mask': '+7 (999) 999-99-99'
            }),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'phone': 'Телефон',
        }
    
    def clean_first_name(self):
        return clean_name(self.cleaned_data.get('first_name'), 'Имя')
    
    def clean_last_name(self):
        return clean_name(self.cleaned_data.get('last_name'), 'Фамилия')
    
    def clean_phone(self):
        value = self.cleaned_data.get('phone')
        if value:
            return clean_phone(value)
        return value


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['visitor', 'ticket_type', 'valid_date']
        widgets = {
            'visitor': forms.Select(attrs={'class': 'form-control'}),
            'ticket_type': forms.Select(attrs={'class': 'form-control'}),
            'valid_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
        }
        labels = {
            'visitor': 'Посетитель',
            'ticket_type': 'Тип билета',
            'valid_date': 'Действителен до',
        }
    
    def clean_valid_date(self):
        from django.utils import timezone
        valid_date = self.cleaned_data.get('valid_date')
        
        if valid_date and valid_date < timezone.now().date():
            raise ValidationError('Дата не может быть в прошлом')
        
        return valid_date


class EmployeeUserForm(forms.ModelForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Логин для входа'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Пароль'
        })
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Повторите пароль'
        })
    )
    role = forms.ChoiceField(
        label='Роль',
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'position', 'salary', 'hire_date', 'phone', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Имя',
                'pattern': '[а-яА-ЯёЁa-zA-Z\\s\\-]+',
                'title': 'Только буквы'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Фамилия',
                'pattern': '[а-яА-ЯёЁa-zA-Z\\s\\-]+',
                'title': 'Только буквы'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Должность'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Зарплата',
                'min': '0',
                'step': '100'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control phone-mask', 
                'placeholder': '+7 (___) ___-__-__'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Email'
            }),
        }
    
    def clean_first_name(self):
        return clean_name(self.cleaned_data.get('first_name'), 'Имя')
    
    def clean_last_name(self):
        return clean_name(self.cleaned_data.get('last_name'), 'Фамилия')
    
    def clean_phone(self):
        value = self.cleaned_data.get('phone')
        if value:
            return clean_phone(value)
        return value
    
    def clean_salary(self):
        return clean_salary(self.cleaned_data.get('salary'))


class EditEmployeeForm(forms.ModelForm):
    username = forms.CharField(
        label='Логин',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'})
    )
    new_password = forms.CharField(
        label='Новый пароль',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Оставьте пустым, если не меняете'})
    )
    
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'position', 'hourly_rate', 
                  'work_start', 'work_end', 'break_minutes', 'work_days',
                  'phone', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '10'}),
            'work_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'work_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'break_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'work_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1,2,3,4,5'}),
            'phone': forms.TextInput(attrs={'class': 'form-control phone-mask'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean_first_name(self):
        return clean_name(self.cleaned_data.get('first_name'), 'Имя')
    
    def clean_last_name(self):
        return clean_name(self.cleaned_data.get('last_name'), 'Фамилия')
    
    def clean_phone(self):
        value = self.cleaned_data.get('phone')
        if value:
            return clean_phone(value)
        return value
    
    def clean_salary(self):
        return clean_salary(self.cleaned_data.get('salary'))

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'image_emoji', 'is_available', 'is_popular']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название товара'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание товара',
                'rows': 3
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Цена',
                'min': '0',
                'step': '10'
            }),
            'image_emoji': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '🍕'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_popular': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Название',
            'category': 'Категория',
            'description': 'Описание',
            'price': 'Цена (₽)',
            'image_emoji': 'Иконка (эмодзи)',
            'is_available': 'В наличии',
            'is_popular': 'Популярное',
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise ValidationError('Цена не может быть отрицательной')
        return price
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name) < 2:
            raise ValidationError('Название должно содержать минимум 2 символа')
        return name


class PayrollCalculateForm(forms.Form):
    """Форма для расчёта зарплаты"""
    
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Сотрудник'
    )
    period_start = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Начало периода'
    )
    period_end = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Конец периода'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # По умолчанию — текущий месяц
        today = date.today()
        first_day = today.replace(day=1)
        # Последний день месяца
        if today.month == 12:
            last_day = today.replace(day=31)
        else:
            last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        self.fields['period_start'].initial = first_day
        self.fields['period_end'].initial = last_day


class PayrollBulkForm(forms.Form):
    """Массовый расчёт зарплаты для всех сотрудников"""
    
    period_start = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Начало периода'
    )
    period_end = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Конец периода'
    )