from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

# Create your views here.

def home(request):
    """Landing page - redirects to dashboard if authenticated"""
    if request.user.is_authenticated:
        return render(request, 'frontend/dashboard.html')
    return render(request, 'frontend/landing.html')

def login_view(request):
    """Custom login page"""
    return render(request, 'frontend/login.html')

def register_view(request):
    """Registration page"""
    return render(request, 'frontend/register.html')

@login_required
def dashboard(request):
    """Main dashboard - different views based on user role"""
    return render(request, 'frontend/dashboard.html')

@login_required
def companies_view(request):
    """Companies management page"""
    return render(request, 'frontend/companies.html')

@login_required
def parking_view(request):
    """Parking management page"""
    return render(request, 'frontend/parking.html')

@login_required
def transactions_view(request):
    """Parking transactions monitoring page"""
    return render(request, 'frontend/transactions.html')
