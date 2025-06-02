# frontend/urls.py
from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('register/company/', views.register_company_view, name='register_company'),
    path('register/employee/', views.register_employee_view, name='register_employee'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('companies/', views.companies_view, name='companies'),
    path('parking/', views.parking_view, name='parking'),
    path('transactions/', views.transactions_view, name='transactions'),
]
