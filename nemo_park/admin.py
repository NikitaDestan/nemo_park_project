from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Employee, Visitor, Ticket

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

admin.site.register(Visitor)
admin.site.register(Ticket)