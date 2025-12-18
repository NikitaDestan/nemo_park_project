from decimal import Decimal
from datetime import date, timedelta

from ..models import Employee, Payroll


class PayrollCalculator:
    """Калькулятор зарплаты для Nemo Park"""
    
    NDFL_RATE = Decimal('0.13')
    OVERTIME_MULTIPLIER = Decimal('1.5')
    STANDARD_HOURS_PER_DAY = 8
    
    def __init__(self, employee: Employee, period_start: date, period_end: date):
        self.employee = employee
        self.period_start = period_start
        self.period_end = period_end
    
    def count_work_days(self) -> int:
        """Подсчёт рабочих дней в периоде"""
        work_days = self.employee.work_days_list
        count = 0
        current = self.period_start
        
        while current <= self.period_end:
            if current.isoweekday() in work_days:
                count += 1
            current += timedelta(days=1)
        
        return count
    
    def calculate(self) -> dict:
        """Полный расчёт зарплаты"""
        
        work_days_count = self.count_work_days()
        hours_per_day = self.employee.hours_per_day
        total_hours = work_days_count * hours_per_day
        
        overtime_per_day = max(Decimal('0'), hours_per_day - self.STANDARD_HOURS_PER_DAY)
        overtime_hours = work_days_count * overtime_per_day
        regular_hours = total_hours - overtime_hours
        
        hourly_rate = self.employee.hourly_rate
        
        base_salary = regular_hours * hourly_rate
        overtime_pay = overtime_hours * hourly_rate * self.OVERTIME_MULTIPLIER
        bonus = Decimal('0')
        
        gross_salary = base_salary + overtime_pay + bonus
        ndfl_tax = (gross_salary * self.NDFL_RATE).quantize(Decimal('0.01'))
        other_deductions = Decimal('0')
        net_salary = gross_salary - ndfl_tax - other_deductions
        
        return {
            'work_days': work_days_count,
            'hours_per_day': hours_per_day,
            'total_hours': total_hours.quantize(Decimal('0.01')),
            'overtime_hours': overtime_hours.quantize(Decimal('0.01')),
            'base_salary': base_salary.quantize(Decimal('0.01')),
            'overtime_pay': overtime_pay.quantize(Decimal('0.01')),
            'bonus': bonus,
            'gross_salary': gross_salary.quantize(Decimal('0.01')),
            'ndfl_tax': ndfl_tax,
            'other_deductions': other_deductions,
            'net_salary': net_salary.quantize(Decimal('0.01')),
        }
    
    def create_payroll(self, created_by=None) -> Payroll:
        """Создать расчётный лист"""
        data = self.calculate()
        
        return Payroll.objects.create(
            employee=self.employee,
            period_start=self.period_start,
            period_end=self.period_end,
            created_by=created_by,
            total_hours=data['total_hours'],
            overtime_hours=data['overtime_hours'],
            base_salary=data['base_salary'],
            overtime_pay=data['overtime_pay'],
            bonus=data['bonus'],
            gross_salary=data['gross_salary'],
            ndfl_tax=data['ndfl_tax'],
            other_deductions=data['other_deductions'],
            net_salary=data['net_salary'],
        )
    
    def get_preview(self) -> dict:
        """Предпросмотр расчёта"""
        data = self.calculate()
        data['employee'] = self.employee
        data['period_start'] = self.period_start
        data['period_end'] = self.period_end
        data['hourly_rate'] = self.employee.hourly_rate
        return data