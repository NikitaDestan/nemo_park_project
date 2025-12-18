from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Employee, Visitor, Ticket, Product, Order, OrderItem


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'position', 'employee_profile', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Роль и профиль', {'fields': ('role', 'position', 'employee_profile')}),
    )
    list_filter = ('role', 'position')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'position', 'salary', 'phone', 'get_user')
    list_filter = ('position',)
    
    def get_user(self, obj):
        if hasattr(obj, 'customuser'):
            return obj.customuser.username
        return "Нет профиля"
    get_user.short_description = 'Логин пользователя'


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'registration_date')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'ticket_type', 'price', 'purchase_date', 'valid_date', 'cashier')
    list_filter = ('ticket_type', 'purchase_date')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_emoji', 'name', 'category', 'price', 'is_available', 'is_popular']
    list_filter = ['category', 'is_available', 'is_popular']
    search_fields = ['name', 'description']
    list_editable = ['is_available', 'is_popular', 'price']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'visitor', 'total_price', 'status', 'cashier', 'created_at']
    list_filter = ['status', 'created_at']
    inlines = [OrderItemInline]