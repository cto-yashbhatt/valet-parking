# authentication/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register-company/', views.register_company, name='register-company'),
    path('register-employee/', views.register_employee, name='register-employee'),
    path('verify-company-code/', views.verify_company_code, name='verify-company-code'),
]
