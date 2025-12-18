from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import json

from .models import Employee, Visitor, Ticket, CustomUser, Product, Order, OrderItem, Payroll
from .forms import (LoginForm, RegisterForm, EmployeeForm, VisitorForm, TicketForm, 
                    EditEmployeeForm, ProductForm, PayrollCalculateForm, PayrollBulkForm)
from .services.payroll_service import PayrollCalculator  


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def user_has_role(user):
    return user.is_authenticated and user.role != 'user'

def admin_required(user):
    return user.is_authenticated and user.role == 'admin'

def cashier_required(user):
    return user.is_authenticated and user.role == 'cashier'


# ==================== АВТОРИЗАЦИЯ ====================

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать в Парк Немо, {user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Неверный логин или пароль')
    else:
        form = LoginForm()
    
    return render(request, 'nemo_park/login.html', {'form': form})


def user_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'user'
            user.position = 'user'
            user.save()
            
            employee = Employee.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'] or '',
                position='user',
                salary=0,
                phone=form.cleaned_data['phone'] or '',
                email=form.cleaned_data['email']
            )
            
            user.employee_profile = employee
            user.save()
            
            login(request, user)
            messages.success(request, f'Регистрация успешна! Добро пожаловать в Парк Немо, {user.username}! Ожидайте назначения роли администратором.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    
    return render(request, 'nemo_park/register.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


# ==================== ГЛАВНАЯ ====================

@login_required
def dashboard(request):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    if request.user.role == 'admin':
        # Считаем выручку за билеты
        tickets_revenue = Ticket.objects.aggregate(total=Sum('price'))['total'] or 0
        
        # Считаем выручку за заказы
        orders_revenue = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0
        
        # Общая выручка
        total_revenue = tickets_revenue + orders_revenue
        
        context = {
            'employees_count': Employee.objects.count(),
            'visitors_count': Visitor.objects.count(),
            'tickets_count': Ticket.objects.count(),
            'orders_count': Order.objects.count(),
            'tickets_revenue': tickets_revenue,
            'orders_revenue': orders_revenue,
            'total_revenue': total_revenue,
        }
    elif request.user.role == 'cashier':
        # Билеты этого кассира
        user_tickets = Ticket.objects.filter(cashier=request.user)
        tickets_revenue = user_tickets.aggregate(total=Sum('price'))['total'] or 0
        
        # Заказы этого кассира
        user_orders = Order.objects.filter(cashier=request.user)
        orders_revenue = user_orders.aggregate(total=Sum('total_price'))['total'] or 0
        
        context = {
            'visitors_count': Visitor.objects.count(),
            'tickets_count': user_tickets.count(),
            'orders_count': user_orders.count(),
            'tickets_revenue': tickets_revenue,
            'orders_revenue': orders_revenue,
            'personal_revenue': tickets_revenue + orders_revenue,
        }
    else:
        context = {}
    
    return render(request, 'nemo_park/dashboard.html', context)


# ==================== СОТРУДНИКИ ====================

@login_required
def employees_list(request):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    if not admin_required(request.user):
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('dashboard')
    
    employees = Employee.objects.all()
    return render(request, 'nemo_park/employees/employees.html', {'employees': employees})


@login_required
def add_employee(request):
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав для добавления сотрудников')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            position = form.cleaned_data['position']
            
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                role=position,  
                position=position,
                employee_profile=employee
            )
            
            messages.success(request, f'Сотрудник {employee.first_name} {employee.last_name} успешно добавлен! Создан логин: {username}')
            return redirect('employees')
    else:
        form = EmployeeForm()
    
    return render(request, 'nemo_park/employees/add_employee.html', {'form': form})


@login_required
def edit_employee(request, employee_id):
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав для редактирования сотрудников')
        return redirect('dashboard')
    
    employee = get_object_or_404(Employee, id=employee_id)
    
    current_user = None
    current_username = ""
    if hasattr(employee, 'customuser'):
        current_user = employee.customuser
        current_username = current_user.username
    
    if request.method == 'POST':
        form = EditEmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save()
            
            if hasattr(employee, 'customuser'):
                user = employee.customuser
                user.role = form.cleaned_data['position']
                user.position = form.cleaned_data['position']
                
                new_username = form.cleaned_data['username']
                if new_username:
                    user.username = new_username
                
                new_password = form.cleaned_data['new_password']
                if new_password:
                    user.set_password(new_password)
                
                user.save()
                messages.success(request, f'Данные сотрудника {employee.first_name} {employee.last_name} успешно обновлены!')
            else:
                new_username = form.cleaned_data['username']
                new_password = form.cleaned_data['new_password']
                
                if new_username and new_password:
                    user = CustomUser.objects.create_user(
                        username=new_username,
                        password=new_password,
                        role=form.cleaned_data['position'],
                        position=form.cleaned_data['position'],
                        employee_profile=employee
                    )
                    messages.success(request, f'Данные сотрудника обновлены и создан логин: {new_username}')
                else:
                    messages.success(request, f'Данные сотрудника {employee.first_name} {employee.last_name} успешно обновлены!')
            
            return redirect('employees')
    else:
        form = EditEmployeeForm(instance=employee, initial={
            'username': current_username
        })
    
    return render(request, 'nemo_park/employees/edit_employee.html', {
        'form': form, 
        'employee': employee,
        'current_username': current_username
    })


@login_required
def delete_employee(request, employee_id):
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав для удаления сотрудников')
        return redirect('dashboard')
    
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        if hasattr(employee, 'customuser'):
            employee.customuser.delete()
        
        employee_name = f"{employee.first_name} {employee.last_name}"
        employee.delete()
        messages.success(request, f'Сотрудник {employee_name} успешно удален!')
        return redirect('employees')
    
    return render(request, 'nemo_park/employees/delete_employee.html', {'employee': employee})


# ==================== ПОСЕТИТЕЛИ ====================

@login_required
def visitors_list(request):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    if not admin_required(request.user):
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('dashboard')
    
    visitors = Visitor.objects.all()
    return render(request, 'nemo_park/visitors/visitors.html', {'visitors': visitors})


@login_required
def add_visitor(request):
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав для добавления посетителей')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = VisitorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Посетитель успешно добавлен!')
            return redirect('visitors')
    else:
        form = VisitorForm()
    
    return render(request, 'nemo_park/visitors/add_visitor.html', {'form': form})


@login_required
def edit_visitor(request, visitor_id):
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав для редактирования посетителей')
        return redirect('dashboard')
    
    visitor = get_object_or_404(Visitor, id=visitor_id)
    
    if request.method == 'POST':
        form = VisitorForm(request.POST, instance=visitor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Данные посетителя {visitor.first_name} {visitor.last_name} успешно обновлены!')
            return redirect('visitors')
    else:
        form = VisitorForm(instance=visitor)
    
    return render(request, 'nemo_park/visitors/edit_visitor.html', {'form': form, 'visitor': visitor})


@login_required
def delete_visitor(request, visitor_id):
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав для удаления посетителей')
        return redirect('dashboard')
    
    visitor = get_object_or_404(Visitor, id=visitor_id)
    
    if request.method == 'POST':
        visitor_name = f"{visitor.first_name} {visitor.last_name}"
        visitor.delete()
        messages.success(request, f'Посетитель {visitor_name} успешно удален!')
        return redirect('visitors')
    
    return render(request, 'nemo_park/visitors/delete_visitor.html', {'visitor': visitor})


# ==================== БИЛЕТЫ ====================

@login_required
def tickets_list(request):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    if request.user.role == 'admin':
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(cashier=request.user)
    return render(request, 'nemo_park/tickets/tickets.html', {'tickets': tickets})


@login_required
def add_ticket(request):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.cashier = request.user 
            ticket.save()
            messages.success(request, 'Билет успешно продан!')
            return redirect('tickets')
    else:
        form = TicketForm()
    
    return render(request, 'nemo_park/tickets/add_ticket.html', {'form': form})


@login_required
def edit_ticket(request, ticket_id):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.user.role == 'cashier' and ticket.cashier != request.user:
        messages.error(request, 'Вы можете редактировать только свои билеты')
        return redirect('tickets')
    
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные билета успешно обновлены!')
            return redirect('tickets')
    else:
        form = TicketForm(instance=ticket)
    
    return render(request, 'nemo_park/tickets/edit_ticket.html', {'form': form, 'ticket': ticket})


@login_required
def delete_ticket(request, ticket_id):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.user.role == 'cashier' and ticket.cashier != request.user:
        messages.error(request, 'Вы можете удалять только свои билеты')
        return redirect('tickets')
    
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, 'Билет успешно удален!')
        return redirect('tickets')
    
    return render(request, 'nemo_park/tickets/delete_ticket.html', {'ticket': ticket})


# ==================== ТОВАРЫ ====================

@login_required
def products_list(request):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    products = Product.objects.all().order_by('category', 'name')
    
    categories = {}
    for product in products:
        cat = product.get_category_display()
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(product)
    
    context = {
        'products': products,
        'categories': categories,
        'total_products': products.count(),
        'available_products': products.filter(is_available=True).count(),
    }
    return render(request, 'nemo_park/products/products.html', context)


@login_required
def add_product(request):
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав для добавления товаров')
        return redirect('products')
    
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно добавлен!')
            return redirect('products')
    else:
        form = ProductForm()
    
    return render(request, 'nemo_park/products/add_product.html', {'form': form})


@login_required
def edit_product(request, product_id):
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав для редактирования товаров')
        return redirect('products')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Товар "{product.name}" успешно обновлён!')
            return redirect('products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'nemo_park/products/edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, product_id):
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав для удаления товаров')
        return redirect('products')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Товар "{product_name}" успешно удалён!')
        return redirect('products')
    
    return render(request, 'nemo_park/products/delete_product.html', {'product': product})


# ==================== ЗАКАЗЫ ====================

@login_required
def orders_list(request):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    if request.user.role == 'admin':
        orders = Order.objects.all().order_by('-created_at')
    else:
        orders = Order.objects.filter(cashier=request.user).order_by('-created_at')
    
    total_orders = orders.count()
    total_revenue = sum(order.total_price for order in orders)
    pending_orders = orders.filter(status='pending').count()
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
    }
    return render(request, 'nemo_park/orders/orders.html', context)


@login_required
def create_order(request):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    products = Product.objects.filter(is_available=True).order_by('category', 'name')
    visitors = Visitor.objects.all()
    
    categories = {}
    for product in products:
        cat = product.get_category_display()
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(product)
    
    if request.method == 'POST':
        visitor_id = request.POST.get('visitor')
        notes = request.POST.get('notes', '')
        items_json = request.POST.get('order_items', '[]')
        
        try:
            items = json.loads(items_json)
        except:
            items = []
        
        if not items:
            messages.error(request, 'Добавьте хотя бы один товар в заказ')
            return render(request, 'nemo_park/orders/create_order.html', {
                'products': products,
                'categories': categories,
                'visitors': visitors,
            })
        
        order = Order.objects.create(
            visitor_id=visitor_id if visitor_id else None,
            cashier=request.user,
            notes=notes,
            total_price=0
        )
        
        total = 0
        for item in items:
            product = Product.objects.get(id=item['product_id'])
            quantity = int(item['quantity'])
            price = product.price
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            total += price * quantity
        
        order.total_price = total
        order.save()
        
        messages.success(request, f'Заказ #{order.id} создан! Сумма: {total} ₽')
        return redirect('orders')
    
    return render(request, 'nemo_park/orders/create_order.html', {
        'products': products,
        'categories': categories,
        'visitors': visitors,
    })


@login_required
def order_detail(request, order_id):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.user.role == 'cashier' and order.cashier != request.user:
        messages.error(request, 'Вы можете просматривать только свои заказы')
        return redirect('orders')
    
    items = order.orderitem_set.all()
    
    return render(request, 'nemo_park/orders/order_detail.html', {
        'order': order,
        'items': items,
    })


@login_required
def update_order_status(request, order_id):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Статус заказа #{order.id} обновлён')
    
    return redirect('order_detail', order_id=order_id)


@login_required
def delete_order(request, order_id):
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав для удаления заказов')
        return redirect('orders')
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        order_num = order.id
        order.delete()
        messages.success(request, f'Заказ #{order_num} удалён')
        return redirect('orders')
    
    return render(request, 'nemo_park/orders/delete_order.html', {'order': order})



# ==================== РАСЧЁТ ЗАРПЛАТЫ ====================

@login_required
def payroll_list(request):
    """Список всех расчётных листов"""
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('dashboard')
    
    # Сначала считаем статистику по ВСЕМ записям
    all_payrolls = Payroll.objects.select_related('employee')
    total_paid = all_payrolls.filter(status='paid').aggregate(total=Sum('net_salary'))['total'] or 0
    pending_count = all_payrolls.filter(status='draft').count()
    
    # Потом берём последние 100 для отображения
    payrolls = all_payrolls.order_by('-period_end', '-created_at')[:100]
    
    context = {
        'payrolls': payrolls,
        'total_paid': total_paid,
        'pending_count': pending_count,
    }
    return render(request, 'nemo_park/payroll/payroll_list.html', context)


@login_required 
def payroll_calculate(request):
    """Расчёт зарплаты для одного сотрудника"""
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав для расчёта зарплаты')
        return redirect('dashboard')
    
    preview = None
    
    if request.method == 'POST':
        form = PayrollCalculateForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            period_start = form.cleaned_data['period_start']
            period_end = form.cleaned_data['period_end']
            
            # Проверка: есть ли график у сотрудника
            if not employee.work_days or employee.position == 'user':
                messages.error(request, f'У сотрудника {employee.full_name} не настроен график работы!')
                return render(request, 'nemo_park/payroll/payroll_calculate.html', {'form': form})
            
            calculator = PayrollCalculator(employee, period_start, period_end)
            
            if 'preview' in request.POST:
                preview = calculator.get_preview()
                
                # Проверка: есть ли рабочие дни
                if preview['work_days'] == 0:
                    messages.warning(request, 'В выбранном периоде нет рабочих дней по графику сотрудника')
                    
            elif 'create' in request.POST:
                payroll = calculator.create_payroll(created_by=request.user)
                messages.success(request, f'Расчётный лист создан! К выплате: {payroll.net_salary} ₽')
                return redirect('payroll_detail', pk=payroll.pk)
    else:
        form = PayrollCalculateForm()
    
    return render(request, 'nemo_park/payroll/payroll_calculate.html', {
        'form': form,
        'preview': preview,
    })


@login_required
def payroll_detail(request, pk):
    """Детали расчётного листа"""
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    payroll = get_object_or_404(Payroll, pk=pk)
    
    # Кассир может видеть только свои
    if request.user.role == 'cashier':
        if not hasattr(request.user, 'employee_profile') or request.user.employee_profile != payroll.employee:
            messages.error(request, 'Вы можете просматривать только свои расчётные листы')
            return redirect('my_payroll')
    
    return render(request, 'nemo_park/payroll/payroll_detail.html', {
        'payroll': payroll,
    })


@login_required
def payroll_bulk(request):
    """Массовый расчёт для всех сотрудников"""
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав для массового расчёта')
        return redirect('dashboard')
    
    results = []
    form_data = None
    
    if request.method == 'POST':
        form = PayrollBulkForm(request.POST)
        if form.is_valid():
            period_start = form.cleaned_data['period_start']
            period_end = form.cleaned_data['period_end']
            form_data = {'period_start': period_start, 'period_end': period_end}
            
            employees = Employee.objects.exclude(position='user')
            
            for employee in employees:
                calculator = PayrollCalculator(employee, period_start, period_end)
                preview = calculator.get_preview()
                results.append(preview)
            
            if 'create_all' in request.POST:
                created_count = 0
                total_sum = Decimal('0')
                
                for employee in employees:
                    calculator = PayrollCalculator(employee, period_start, period_end)
                    payroll = calculator.create_payroll(created_by=request.user)
                    created_count += 1
                    total_sum += payroll.net_salary
                
                messages.success(request, f'Создано {created_count} расчётных листов на сумму {total_sum} ₽!')
                return redirect('payroll_list')
    else:
        form = PayrollBulkForm()
    
    total_gross = sum(r['gross_salary'] for r in results)
    total_net = sum(r['net_salary'] for r in results)
    
    return render(request, 'nemo_park/payroll/payroll_bulk.html', {
        'form': form,
        'results': results,
        'form_data': form_data,
        'total_gross': total_gross,
        'total_net': total_net,
    })


@login_required
def my_payroll(request):
    """Мои расчётные листы"""
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    payrolls = []
    employee = None
    total_earned = 0
    
    if hasattr(request.user, 'employee_profile') and request.user.employee_profile:
        employee = request.user.employee_profile
        payrolls = Payroll.objects.filter(employee=employee).order_by('-period_end')
        total_earned = payrolls.filter(status='paid').aggregate(total=Sum('net_salary'))['total'] or 0
    
    return render(request, 'nemo_park/payroll/my_payroll.html', {
        'employee': employee,
        'payrolls': payrolls,
        'total_earned': total_earned,
    })


@login_required
def payroll_mark_paid(request, pk):
    """Отметить как выплачено"""
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав')
        return redirect('dashboard')
    
    payroll = get_object_or_404(Payroll, pk=pk)
    
    if request.method == 'POST':
        payroll.status = 'paid'
        payroll.paid_at = timezone.now()
        payroll.save()
        messages.success(request, f'Выплата {payroll.net_salary} ₽ для {payroll.employee.full_name} отмечена!')
    
    return redirect('payroll_detail', pk=pk)


@login_required
def payroll_delete(request, pk):
    """Удалить расчётный лист"""
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав')
        return redirect('dashboard')
    
    payroll = get_object_or_404(Payroll, pk=pk)
    
    if request.method == 'POST':
        payroll.delete()
        messages.success(request, 'Расчётный лист удалён!')
        return redirect('payroll_list')
    
    return render(request, 'nemo_park/payroll/payroll_delete.html', {'payroll': payroll})
@login_required
def payroll_bulk_delete(request):
    """Массовое удаление расчётных листов"""
    if request.user.role != 'admin':
        messages.error(request, 'У вас нет прав')
        return redirect('dashboard')
    
    if request.method == 'POST':
        delete_type = request.POST.get('delete_type')
        
        if delete_type == 'all':
            count = Payroll.objects.count()
            Payroll.objects.all().delete()
            messages.success(request, f'🗑️ Удалено {count} расчётных листов')
        
        elif delete_type == 'draft':
            count = Payroll.objects.filter(status='draft').count()
            Payroll.objects.filter(status='draft').delete()
            messages.success(request, f'🗑️ Удалено {count} черновиков')
        
        elif delete_type == 'paid':
            count = Payroll.objects.filter(status='paid').count()
            Payroll.objects.filter(status='paid').delete()
            messages.success(request, f'🗑️ Удалено {count} выплаченных')
        
        return redirect('payroll_list')
    
    # Статистика для отображения
    context = {
        'total_count': Payroll.objects.count(),
        'draft_count': Payroll.objects.filter(status='draft').count(),
        'paid_count': Payroll.objects.filter(status='paid').count(),
    }
    
    return render(request, 'nemo_park/payroll/payroll_bulk_delete.html', context)

@login_required
def orders_analytics(request):
    """Аналитика заказов по дням"""
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    from datetime import timedelta
    from django.db.models import Count
    from django.db.models.functions import TruncDate
    
    # Период — последние 30 дней
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Заказы в зависимости от роли
    if request.user.role == 'admin':
        orders_qs = Order.objects.all()
    else:
        orders_qs = Order.objects.filter(cashier=request.user)
    
    # Группируем по дням
    orders_by_day = orders_qs.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(
        count=Count('id'),
        revenue=Sum('total_price')
    ).order_by('day')
    
    # Билеты по дням
    if request.user.role == 'admin':
        tickets_qs = Ticket.objects.all()
    else:
        tickets_qs = Ticket.objects.filter(cashier=request.user)
    
    tickets_by_day = tickets_qs.filter(
        purchase_date__date__gte=start_date,
        purchase_date__date__lte=end_date
    ).annotate(
        day=TruncDate('purchase_date')
    ).values('day').annotate(
        count=Count('id'),
        revenue=Sum('price')
    ).order_by('day')
    
    # Общая статистика
    total_orders = orders_qs.filter(
        created_at__date__gte=start_date
    ).aggregate(
        count=Count('id'),
        revenue=Sum('total_price')
    )
    
    total_tickets = tickets_qs.filter(
        purchase_date__date__gte=start_date
    ).aggregate(
        count=Count('id'),
        revenue=Sum('price')
    )
    
    # Популярные товары
    popular_products = OrderItem.objects.filter(
        order__created_at__date__gte=start_date
    ).values(
        'product__name', 'product__image_emoji'
    ).annotate(
        total_qty=Sum('quantity'),
        total_revenue=Sum('price')
    ).order_by('-total_qty')[:10]
    
    # Лучшие кассиры (только для админа)
    top_cashiers = []
    if request.user.role == 'admin':
        top_cashiers = Order.objects.filter(
            created_at__date__gte=start_date
        ).values(
            'cashier__username', 'cashier__employee_profile__first_name', 
            'cashier__employee_profile__last_name'
        ).annotate(
            orders_count=Count('id'),
            revenue=Sum('total_price')
        ).order_by('-revenue')[:5]
    
    context = {
        'orders_by_day': list(orders_by_day),
        'tickets_by_day': list(tickets_by_day),
        'total_orders': total_orders,
        'total_tickets': total_tickets,
        'popular_products': popular_products,
        'top_cashiers': top_cashiers,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'nemo_park/orders/analytics.html', context)