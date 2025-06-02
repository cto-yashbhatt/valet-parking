# authentication/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register-company/', views.register_company, name='register-company'),
    path('register-employee/', views.register_employee, name='register-employee'),
    path('verify-company-code/', views.verify_company_code, name='verify-company-code'),
    path('debug/', views.debug_user_info, name='debug-user-info'),
]
