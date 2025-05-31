from django.contrib import admin

# Register your models here.
# companies/admin.py
from django.contrib import admin
from .models import Company, EmployeeProfile

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_code', 'phone_number')
    search_fields = ('name', 'company_code')

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'phone_number')
    search_fields = ('user__username', 'company__name')
