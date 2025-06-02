#!/usr/bin/env python
"""
Debug script to check user company association
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valet_project.settings')
django.setup()

from core.models import CoreUser
from companies.models import Company, EmployeeProfile
from core.permissions import get_user_company

def debug_user_company():
    print("=== User Company Debug ===")
    
    # Check all users
    users = CoreUser.objects.all()
    print(f"\nTotal users: {users.count()}")
    
    for user in users:
        print(f"\nUser: {user.username} (Role: {user.role})")
        
        # Check employee profile
        if user.role == CoreUser.Role.EMPLOYEE:
            try:
                profile = EmployeeProfile.objects.get(user=user)
                print(f"  Employee Profile: Company = {profile.company.name}")
            except EmployeeProfile.DoesNotExist:
                print(f"  ERROR: No employee profile found!")
        
        # Check admin company
        if user.role == CoreUser.Role.COMPANY_ADMIN:
            try:
                company = Company.objects.get(admin_user=user)
                print(f"  Admin Company: {company.name}")
            except Company.DoesNotExist:
                print(f"  ERROR: No admin company found!")
        
        # Test get_user_company function
        user_company = get_user_company(user)
        if user_company:
            print(f"  get_user_company(): {user_company.name}")
        else:
            print(f"  get_user_company(): None (ERROR!)")
    
    # Check all companies
    companies = Company.objects.all()
    print(f"\nTotal companies: {companies.count()}")
    for company in companies:
        print(f"  Company: {company.name} (Admin: {company.admin_user.username})")
    
    # Check all employee profiles
    profiles = EmployeeProfile.objects.all()
    print(f"\nTotal employee profiles: {profiles.count()}")
    for profile in profiles:
        print(f"  Profile: {profile.user.username} -> {profile.company.name}")

if __name__ == "__main__":
    debug_user_company()
