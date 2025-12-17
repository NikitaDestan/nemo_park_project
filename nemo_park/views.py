from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Employee, Visitor, Ticket, CustomUser
from .forms import LoginForm, RegisterForm, EmployeeForm, VisitorForm, TicketForm, EditEmployeeForm 

def user_has_role(user):
    return user.is_authenticated and user.role != 'user'

def admin_required(user):
    return user.is_authenticated and user.role == 'admin'

def cashier_required(user):
    return user.is_authenticated and user.role == 'cashier'

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

@login_required
def dashboard(request):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    if request.user.role == 'admin':
        context = {
            'employees_count': Employee.objects.count(),
            'visitors_count': Visitor.objects.count(),
            'tickets_count': Ticket.objects.count(),
            'total_revenue': sum(ticket.price for ticket in Ticket.objects.all()),
        }
    elif request.user.role == 'cashier':
        user_tickets = Ticket.objects.filter(cashier=request.user)
        context = {
            'visitors_count': Visitor.objects.count(),
            'tickets_count': user_tickets.count(),
            'personal_revenue': sum(ticket.price for ticket in user_tickets),
        }
    
    return render(request, 'nemo_park/dashboard.html', context)

@login_required
def employees_list(request):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    if not admin_required(request.user):
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('dashboard')
    
    employees = Employee.objects.all()
    return render(request, 'nemo_park/employees.html', {'employees': employees})

@login_required
def visitors_list(request):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    if not admin_required(request.user):
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('dashboard')
    
    visitors = Visitor.objects.all()
    return render(request, 'nemo_park/visitors.html', {'visitors': visitors})

@login_required
def tickets_list(request):
    if request.user.role == 'user':
        return render(request, 'nemo_park/waiting_approval.html')
    
    if request.user.role == 'admin':
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(cashier=request.user)
    return render(request, 'nemo_park/tickets.html', {'tickets': tickets})

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
    
    return render(request, 'nemo_park/add_employee.html', {'form': form})

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
    
    return render(request, 'nemo_park/add_visitor.html', {'form': form})

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
    
    return render(request, 'nemo_park/add_ticket.html', {'form': form})

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
    
    return render(request, 'nemo_park/edit_employee.html', {
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
    
    return render(request, 'nemo_park/delete_employee.html', {'employee': employee})

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
    
    return render(request, 'nemo_park/edit_visitor.html', {'form': form, 'visitor': visitor})

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
    
    return render(request, 'nemo_park/delete_visitor.html', {'visitor': visitor})

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
    
    return render(request, 'nemo_park/edit_ticket.html', {'form': form, 'ticket': ticket})

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
    
    return render(request, 'nemo_park/delete_ticket.html', {'ticket': ticket})