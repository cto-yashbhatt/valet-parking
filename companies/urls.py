# companies/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.CompanyListCreateAPIView.as_view(), name='company-list-create'),
    path('<int:pk>/', views.CompanyRetrieveUpdateDestroyAPIView.as_view(), name='company-detail'),
    path('<int:company_id>/employees/', views.EmployeeListCreateAPIView.as_view(), name='employee-list-create'),
    path('<int:company_id>/employees/<int:pk>/', views.EmployeeRetrieveUpdateDestroyAPIView.as_view(), name='employee-detail'),
]
