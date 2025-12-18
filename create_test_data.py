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
    
    # 5 КАССИРОВ
    employees_cashiers = [
        {'first_name': 'Иван', 'last_name': 'Петров', 'username': 'ivan', 'password': '1111'},
        {'first_name': 'Мария', 'last_name': 'Сидорова', 'username': 'maria', 'password': '2222'},
        {'first_name': 'Алексей', 'last_name': 'Козлов', 'username': 'alex', 'password': '3333'},
        {'first_name': 'Ольга', 'last_name': 'Новикова', 'username': 'olga', 'password': '4444'},
        {'first_name': 'Дмитрий', 'last_name': 'Волков', 'username': 'dmitry', 'password': '5555'},
    ]
    
    for data in employees_cashiers:
        employee = Employee.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            position='cashier',
            salary=35000,
            phone=f'+7 (999) 100-{employees_cashiers.index(data):02d}-00',
            email=f"{data['username']}@nemopark.ru"
        )
        
        CustomUser.objects.create_user(
            username=data['username'],
            password=data['password'],
            role='cashier',
            position='cashier',
            employee_profile=employee
        )
    
    # 5 АДМИНОВ
    employees_admins = [
        {'first_name': 'Анна', 'last_name': 'Смирнова', 'username': 'anna', 'password': '6666'},
        {'first_name': 'Сергей', 'last_name': 'Кузнецов', 'username': 'sergey', 'password': '7777'},
        {'first_name': 'Елена', 'last_name': 'Попова', 'username': 'elena', 'password': '8888'},
        {'first_name': 'Михаил', 'last_name': 'Лебедев', 'username': 'mikhail', 'password': '9999'},
        {'first_name': 'Татьяна', 'last_name': 'Морозова', 'username': 'tatyana', 'password': '0000'},
    ]
    
    for data in employees_admins:
        employee = Employee.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            position='admin',
            salary=50000,
            phone=f'+7 (999) 200-{employees_admins.index(data):02d}-00',
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
        salary=80000,
        phone='+7 (999) 999-99-99',
        email='admin@nemopark.ru'
    )
    
    admin_user = CustomUser.objects.create_superuser(
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
        visitor = Visitor.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone']
        )
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
    
    for product_data in products_data:
        Product.objects.create(
            name=product_data['name'],
            category=product_data['category'],
            price=product_data['price'],
            image_emoji=product_data['emoji'],
            description=product_data.get('description', ''),
            is_popular=product_data.get('popular', False),
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
    print("\n🟢 КАССИРЫ:")
    for data in employees_cashiers:
        print(f"   login={data['username']:<10} password={data['password']}")
    print("\n🟡 АДМИНЫ:")
    for data in employees_admins:
        print(f"   login={data['username']:<10} password={data['password']}")
    print("\n📊 СТАТИСТИКА:")
    print(f"   👥 Сотрудников: {Employee.objects.count()}")
    print(f"   👤 Посетителей: {Visitor.objects.count()}")
    print(f"   🎫 Билетов: {Ticket.objects.count()}")
    print(f"   🍕 Товаров: {Product.objects.count()}")
    print("="*60)

if __name__ == '__main__':
    create_test_data()