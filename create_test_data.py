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
    
    # ==================== ПОЛЬЗОВАТЕЛИ ====================
    admin_user = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@nemopark.ru',
        password='admin123',
        role='admin',
        position='admin'
    )
    
    # ==================== СОТРУДНИКИ ====================
    employee1 = Employee.objects.create(
        first_name='Иван',
        last_name='Петров',
        position='cashier',
        salary=35000,
        phone='+7 (999) 123-45-67',
        email='ivan@nemopark.ru'
    )
    
    employee2 = Employee.objects.create(
        first_name='Мария',
        last_name='Сидорова', 
        position='admin',
        salary=50000,
        phone='+7 (999) 765-43-21',
        email='maria@nemopark.ru'
    )
    
    cashier_user = CustomUser.objects.create_user(
        username='cashier',
        password='cashier123',
        role='cashier',
        position='cashier',
        employee_profile=employee1
    )
    
    admin2_user = CustomUser.objects.create_user(
        username='manager',
        password='manager123', 
        role='admin',
        position='admin',
        employee_profile=employee2
    )
    
    print("👥 Сотрудники созданы")
    
    # ==================== ПОСЕТИТЕЛИ ====================
    visitor1 = Visitor.objects.create(
        first_name='Алексей',
        last_name='Козлов',
        email='alex@mail.ru',
        phone='+7 (999) 111-22-33'
    )
    
    visitor2 = Visitor.objects.create(
        first_name='Ольга',
        last_name='Новикова',
        email='olga@mail.ru', 
        phone='+7 (999) 444-55-66'
    )
    
    visitor3 = Visitor.objects.create(
        first_name='Дмитрий',
        last_name='Волков',
        email='dmitry@mail.ru', 
        phone='+7 (999) 777-88-99'
    )
    
    print("👤 Посетители созданы")
    
    # ==================== БИЛЕТЫ ====================
    ticket1 = Ticket.objects.create(
        visitor=visitor1,
        ticket_type='adult',
        valid_date=timezone.now().date(),
        cashier=cashier_user
    )
    
    ticket2 = Ticket.objects.create(
        visitor=visitor2,
        ticket_type='family', 
        valid_date=timezone.now().date(),
        cashier=admin_user
    )
    
    ticket3 = Ticket.objects.create(
        visitor=visitor3,
        ticket_type='vip', 
        valid_date=timezone.now().date(),
        cashier=cashier_user
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
    print("\n" + "="*50)
    print("✅ Тестовые данные успешно созданы!")
    print("="*50)
    print("\n👤 Тестовые пользователи:")
    print("   🔑 Админ:   login=admin,   password=admin123")
    print("   🔑 Кассир:  login=cashier, password=cashier123") 
    print("   🔑 Менеджер: login=manager, password=manager123")
    print("\n📊 Статистика:")
    print(f"   👥 Сотрудников: {Employee.objects.count()}")
    print(f"   👤 Посетителей: {Visitor.objects.count()}")
    print(f"   🎫 Билетов: {Ticket.objects.count()}")
    print(f"   🍕 Товаров: {Product.objects.count()}")
    print("="*50)

if __name__ == '__main__':
    create_test_data()