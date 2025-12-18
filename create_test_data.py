import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nemo_park_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from nemo_park.models import Employee, Visitor, Ticket, Product
from django.utils import timezone

CustomUser = get_user_model()

def create_test_data():
    # Очищаем старые данные
    CustomUser.objects.all().delete()
    Employee.objects.all().delete()
    Visitor.objects.all().delete()
    Ticket.objects.all().delete()
    Product.objects.all().delete()
    
    print("🗑️ Старые данные удалены")
    
    # ==================== СОТРУДНИКИ И ПОЛЬЗОВАТЕЛИ ====================
    
    # 5 КАССИРОВ с разными графиками
    employees_cashiers = [
        {'first_name': 'Иван', 'last_name': 'Петров', 'username': 'ivan', 'password': '1111',
         'work_start': '09:00', 'work_end': '18:00', 'break_minutes': 60, 'work_days': '1,2,3,4,5', 'hourly_rate': 250},
        {'first_name': 'Мария', 'last_name': 'Сидорова', 'username': 'maria', 'password': '2222',
         'work_start': '10:00', 'work_end': '19:00', 'break_minutes': 60, 'work_days': '1,2,3,4,5', 'hourly_rate': 250},
        {'first_name': 'Алексей', 'last_name': 'Козлов', 'username': 'alex', 'password': '3333',
         'work_start': '12:00', 'work_end': '22:00', 'break_minutes': 60, 'work_days': '2,3,4,5,6', 'hourly_rate': 280},
        {'first_name': 'Ольга', 'last_name': 'Новикова', 'username': 'olga', 'password': '4444',
         'work_start': '08:00', 'work_end': '16:00', 'break_minutes': 45, 'work_days': '1,2,3,4,5', 'hourly_rate': 250},
        {'first_name': 'Дмитрий', 'last_name': 'Волков', 'username': 'dmitry', 'password': '5555',
         'work_start': '14:00', 'work_end': '23:00', 'break_minutes': 60, 'work_days': '3,4,5,6,7', 'hourly_rate': 300},
    ]
    
    for i, data in enumerate(employees_cashiers):
        employee = Employee.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            position='cashier',
            hourly_rate=data['hourly_rate'],
            work_start=data['work_start'],
            work_end=data['work_end'],
            break_minutes=data['break_minutes'],
            work_days=data['work_days'],
            phone=f'+7 (999) 100-{i:02d}-00',
            email=f"{data['username']}@nemopark.ru"
        )
        
        CustomUser.objects.create_user(
            username=data['username'],
            password=data['password'],
            role='cashier',
            position='cashier',
            employee_profile=employee
        )
    
    # 5 АДМИНОВ с разными графиками
    employees_admins = [
        {'first_name': 'Анна', 'last_name': 'Смирнова', 'username': 'anna', 'password': '6666',
         'work_start': '09:00', 'work_end': '18:00', 'break_minutes': 60, 'work_days': '1,2,3,4,5', 'hourly_rate': 400},
        {'first_name': 'Сергей', 'last_name': 'Кузнецов', 'username': 'sergey', 'password': '7777',
         'work_start': '10:00', 'work_end': '20:00', 'break_minutes': 60, 'work_days': '1,2,3,4,5', 'hourly_rate': 450},
        {'first_name': 'Елена', 'last_name': 'Попова', 'username': 'elena', 'password': '8888',
         'work_start': '08:00', 'work_end': '17:00', 'break_minutes': 60, 'work_days': '1,2,3,4,5', 'hourly_rate': 400},
        {'first_name': 'Михаил', 'last_name': 'Лебедев', 'username': 'mikhail', 'password': '9999',
         'work_start': '11:00', 'work_end': '21:00', 'break_minutes': 60, 'work_days': '2,3,4,5,6', 'hourly_rate': 420},
        {'first_name': 'Татьяна', 'last_name': 'Морозова', 'username': 'tatyana', 'password': '0000',
         'work_start': '09:00', 'work_end': '18:00', 'break_minutes': 45, 'work_days': '1,2,3,4,5', 'hourly_rate': 400},
    ]
    
    for i, data in enumerate(employees_admins):
        employee = Employee.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            position='admin',
            hourly_rate=data['hourly_rate'],
            work_start=data['work_start'],
            work_end=data['work_end'],
            break_minutes=data['break_minutes'],
            work_days=data['work_days'],
            phone=f'+7 (999) 200-{i:02d}-00',
            email=f"{data['username']}@nemopark.ru"
        )
        
        CustomUser.objects.create_user(
            username=data['username'],
            password=data['password'],
            role='admin',
            position='admin',
            employee_profile=employee
        )
    
    # СУПЕР АДМИН
    admin_employee = Employee.objects.create(
        first_name='Администратор',
        last_name='Главный',
        position='admin',
        hourly_rate=500,
        work_start='09:00',
        work_end='18:00',
        break_minutes=60,
        work_days='1,2,3,4,5',
        phone='+7 (999) 999-99-99',
        email='admin@nemopark.ru'
    )
    
    CustomUser.objects.create_superuser(
        username='admin',
        email='admin@nemopark.ru',
        password='admin',
        role='admin',
        position='admin',
        employee_profile=admin_employee
    )
    
    print("👥 Сотрудники созданы")
    
    # ==================== ПОСЕТИТЕЛИ ====================
    visitors_data = [
        {'first_name': 'Артём', 'last_name': 'Соколов', 'email': 'artem@mail.ru', 'phone': '+7 (999) 111-22-33'},
        {'first_name': 'Виктория', 'last_name': 'Павлова', 'email': 'vika@mail.ru', 'phone': '+7 (999) 222-33-44'},
        {'first_name': 'Никита', 'last_name': 'Егоров', 'email': 'nikita@mail.ru', 'phone': '+7 (999) 333-44-55'},
        {'first_name': 'Екатерина', 'last_name': 'Фёдорова', 'email': 'kate@mail.ru', 'phone': '+7 (999) 444-55-66'},
        {'first_name': 'Максим', 'last_name': 'Орлов', 'email': 'maxim@mail.ru', 'phone': '+7 (999) 555-66-77'},
    ]
    
    visitors = []
    for data in visitors_data:
        visitor = Visitor.objects.create(**data)
        visitors.append(visitor)
    
    print("👤 Посетители созданы")
    
    # ==================== БИЛЕТЫ ====================
    ticket_types = ['adult', 'child', 'family', 'vip']
    cashier_users = CustomUser.objects.filter(role='cashier')
    
    for i, visitor in enumerate(visitors):
        Ticket.objects.create(
            visitor=visitor,
            ticket_type=ticket_types[i % len(ticket_types)],
            valid_date=timezone.now().date(),
            cashier=cashier_users[i % cashier_users.count()]
        )
    
    print("🎫 Билеты созданы")
    
        # ==================== ТОВАРЫ (ЕДА) ====================
    products_data = [
        # Пицца
        {'name': 'Пицца Маргарита', 'category': 'pizza', 'price': 450, 'emoji': '🍕', 'popular': True,
         'description': 'Классическая итальянская пицца с томатами и моцареллой'},
        {'name': 'Пицца Пепперони', 'category': 'pizza', 'price': 520, 'emoji': '🍕', 'popular': True,
         'description': 'Острая пицца с пепперони и сыром'},
        {'name': 'Пицца 4 сыра', 'category': 'pizza', 'price': 580, 'emoji': '🧀',
         'description': 'Моцарелла, пармезан, горгонзола, чеддер'},
        {'name': 'Пицца Гавайская', 'category': 'pizza', 'price': 490, 'emoji': '🍍',
         'description': 'Курица, ананасы, сыр моцарелла'},
        
        # Бургеры
        {'name': 'Классический бургер', 'category': 'burger', 'price': 320, 'emoji': '🍔', 'popular': True,
         'description': 'Говяжья котлета, салат, томаты, соус'},
        {'name': 'Чизбургер', 'category': 'burger', 'price': 350, 'emoji': '🍔',
         'description': 'Двойной сыр, говяжья котлета'},
        {'name': 'Чикенбургер', 'category': 'burger', 'price': 290, 'emoji': '🍗',
         'description': 'Куриная котлета, салат, майонез'},
        {'name': 'Двойной бургер', 'category': 'burger', 'price': 450, 'emoji': '🍔',
         'description': 'Две котлеты, двойной сыр, бекон'},
        
        # Закуски
        {'name': 'Картофель фри', 'category': 'snack', 'price': 150, 'emoji': '🍟', 'popular': True,
         'description': 'Хрустящий картофель с солью'},
        {'name': 'Куриные наггетсы', 'category': 'snack', 'price': 220, 'emoji': '🍗',
         'description': '6 штук с соусом на выбор'},
        {'name': 'Луковые кольца', 'category': 'snack', 'price': 180, 'emoji': '🧅',
         'description': 'Хрустящие луковые кольца'},
        {'name': 'Сырные палочки', 'category': 'snack', 'price': 250, 'emoji': '🧀',
         'description': '8 штук с томатным соусом'},
        
        # Напитки
        {'name': 'Кола', 'category': 'drink', 'price': 120, 'emoji': '🥤', 'popular': True,
         'description': 'Coca-Cola 0.5л'},
        {'name': 'Фанта', 'category': 'drink', 'price': 120, 'emoji': '🥤',
         'description': 'Fanta Orange 0.5л'},
        {'name': 'Сок апельсиновый', 'category': 'drink', 'price': 150, 'emoji': '🧃',
         'description': 'Свежевыжатый апельсиновый сок'},
        {'name': 'Молочный коктейль', 'category': 'drink', 'price': 200, 'emoji': '🥛',
         'description': 'Ванильный, шоколадный или клубничный'},
        
        # Десерты
        {'name': 'Мороженое', 'category': 'dessert', 'price': 150, 'emoji': '🍦', 'popular': True,
         'description': '3 шарика на выбор'},
        {'name': 'Чизкейк', 'category': 'dessert', 'price': 220, 'emoji': '🍰',
         'description': 'Классический чизкейк Нью-Йорк'},
        {'name': 'Пончики', 'category': 'dessert', 'price': 180, 'emoji': '🍩',
         'description': '3 пончика с глазурью'},
        
        # Комбо-наборы
        {'name': 'Комбо Немо', 'category': 'combo', 'price': 550, 'emoji': '🐠', 'popular': True,
         'description': 'Бургер + картофель фри + напиток'},
        {'name': 'Семейный набор', 'category': 'combo', 'price': 1200, 'emoji': '👨‍👩‍👧',
         'description': '2 пиццы + 4 напитка + картофель'},
    ]
    
    for p in products_data:
        Product.objects.create(
            name=p['name'],
            category=p['category'],
            price=p['price'],
            image_emoji=p['emoji'],
            description=p.get('description', ''),
            is_popular=p.get('popular', False),
            is_available=True
        )
    
    print(f"🍕 Создано {len(products_data)} товаров")
    
    # ==================== ИТОГ ====================
    print("\n" + "="*60)
    print("✅ Тестовые данные успешно созданы!")
    print("="*60)
    print("\n👤 ПОЛЬЗОВАТЕЛИ:")
    print("\n🔴 СУПЕР АДМИН:")
    print("   login=admin       password=admin")
    print("\n🟢 КАССИРЫ (250-300 ₽/час):")
    for data in employees_cashiers:
        days = data['work_days'].replace('1','Пн').replace('2','Вт').replace('3','Ср').replace('4','Чт').replace('5','Пт').replace('6','Сб').replace('7','Вс')
        print(f"   {data['username']:<10} {data['password']}  |  {data['work_start']}-{data['work_end']}  |  {days}")
    print("\n🟡 АДМИНЫ (400-450 ₽/час):")
    for data in employees_admins:
        days = data['work_days'].replace('1','Пн').replace('2','Вт').replace('3','Ср').replace('4','Чт').replace('5','Пт').replace('6','Сб').replace('7','Вс')
        print(f"   {data['username']:<10} {data['password']}  |  {data['work_start']}-{data['work_end']}  |  {days}")
    print("="*60)

if __name__ == '__main__':
    create_test_data()