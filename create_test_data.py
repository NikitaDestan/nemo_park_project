import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aquapark_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from aquapark.models import Employee, Visitor, Ticket
from django.utils import timezone

CustomUser = get_user_model()

def create_test_data():
    CustomUser.objects.all().delete()
    Employee.objects.all().delete()
    Visitor.objects.all().delete()
    Ticket.objects.all().delete()
    
    admin_user = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@aquapark.ru',
        password='admin123',
        role='admin',
        position='admin'
    )
    
    employee1 = Employee.objects.create(
        first_name='Иван',
        last_name='Петров',
        position='cashier',
        salary=35000,
        phone='+79991234567',
        email='ivan@aquapark.ru'
    )
    
    employee2 = Employee.objects.create(
        first_name='Мария',
        last_name='Сидорова', 
        position='admin',
        salary=50000,
        phone='+79997654321',
        email='maria@aquapark.ru'
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
    
    visitor1 = Visitor.objects.create(
        first_name='Алексей',
        last_name='Козлов',
        email='alex@mail.ru',
        phone='+79991112233'
    )
    
    visitor2 = Visitor.objects.create(
        first_name='Ольга',
        last_name='Новикова',
        email='olga@mail.ru', 
        phone='+79994445566'
    )
    
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
    
    print("✅ Тестовые данные созданы!")
    print("\n👤 Тестовые пользователи:")
    print("   Админ: login=admin, password=admin123")
    print("   Кассир: login=cashier, password=cashier123") 
    print("   Менеджер: login=manager, password=manager123")

if __name__ == '__main__':
    create_test_data()