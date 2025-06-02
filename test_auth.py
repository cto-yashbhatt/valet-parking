#!/usr/bin/env python
"""
Quick test script to debug authentication issues
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valet_project.settings')
django.setup()

from core.models import CoreUser
from companies.models import Company, EmployeeProfile
from django.contrib.auth import authenticate

def test_authentication():
    print("=== Authentication Test ===")
    
    # List all users
    print("\nAll users in database:")
    users = CoreUser.objects.all()
    for user in users:
        print(f"  - Username: {user.username}, Role: {user.role}, Active: {user.is_active}")
    
    if not users:
        print("  No users found!")
        return
    
    # Test authentication with the first user
    test_user = users.first()
    print(f"\nTesting authentication with user: {test_user.username}")
    
    # Try to authenticate (this will fail because we don't know the password)
    # But let's check if the user is properly set up
    print(f"User is active: {test_user.is_active}")
    print(f"User has usable password: {test_user.has_usable_password()}")
    
    # Check companies
    print("\nAll companies:")
    companies = Company.objects.all()
    for company in companies:
        print(f"  - Company: {company.name}, Code: {company.company_code}")
    
    # Check employee profiles
    print("\nAll employee profiles:")
    profiles = EmployeeProfile.objects.all()
    for profile in profiles:
        print(f"  - User: {profile.user.username}, Company: {profile.company.name}")

if __name__ == "__main__":
    test_authentication()
