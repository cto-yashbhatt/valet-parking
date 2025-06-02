#!/usr/bin/env python
"""
Test script to verify company-scoped access control
"""
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valet_project.settings')
django.setup()

from core.models import CoreUser
from companies.models import Company, EmployeeProfile
from parking.models import ParkingSlot

def test_company_access():
    print("=== Company-Scoped Access Control Test ===")
    
    # Create test data
    print("\n1. Creating test companies and users...")
    
    # Company A
    admin_a, created = CoreUser.objects.get_or_create(
        username='admin_a',
        defaults={
            'email': 'admin_a@test.com',
            'first_name': 'Admin',
            'last_name': 'A',
            'role': CoreUser.Role.COMPANY_ADMIN
        }
    )
    if created:
        admin_a.set_password('password123')
        admin_a.save()
    
    company_a, created = Company.objects.get_or_create(
        name='Company A',
        defaults={
            'phone_number': '+1111111111',
            'location': 'Location A',
            'company_code': 'COMPA',
            'admin_user': admin_a
        }
    )
    
    employee_a, created = CoreUser.objects.get_or_create(
        username='employee_a',
        defaults={
            'email': 'employee_a@test.com',
            'first_name': 'Employee',
            'last_name': 'A',
            'role': CoreUser.Role.EMPLOYEE
        }
    )
    if created:
        employee_a.set_password('password123')
        employee_a.save()
    
    emp_profile_a, created = EmployeeProfile.objects.get_or_create(
        user=employee_a,
        defaults={
            'company': company_a,
            'phone_number': '+1111111112'
        }
    )
    
    # Company B
    admin_b, created = CoreUser.objects.get_or_create(
        username='admin_b',
        defaults={
            'email': 'admin_b@test.com',
            'first_name': 'Admin',
            'last_name': 'B',
            'role': CoreUser.Role.COMPANY_ADMIN
        }
    )
    if created:
        admin_b.set_password('password123')
        admin_b.save()
    
    company_b, created = Company.objects.get_or_create(
        name='Company B',
        defaults={
            'phone_number': '+2222222222',
            'location': 'Location B',
            'company_code': 'COMPB',
            'admin_user': admin_b
        }
    )
    
    # Create parking slots for each company
    slot_a, created = ParkingSlot.objects.get_or_create(
        name='Slot A1',
        defaults={
            'company': company_a,
            'division': 'Division A'
        }
    )
    
    slot_b, created = ParkingSlot.objects.get_or_create(
        name='Slot B1',
        defaults={
            'company': company_b,
            'division': 'Division B'
        }
    )
    
    print(f"Created Company A: {company_a.name} (Code: {company_a.company_code})")
    print(f"Created Company B: {company_b.name} (Code: {company_b.company_code})")
    print(f"Created Slot A1 for Company A")
    print(f"Created Slot B1 for Company B")
    
    # Test API access
    print("\n2. Testing API access control...")
    
    base_url = 'http://localhost:8000'
    
    # Login as Employee A
    print("\n2.1. Testing Employee A access...")
    login_response = requests.post(f'{base_url}/api/auth/login/', 
                                 json={'username': 'employee_a', 'password': 'password123'})
    
    if login_response.status_code == 200:
        print("✓ Employee A login successful")
        
        # Get session cookies
        session_cookies = login_response.cookies
        
        # Test parking slots access
        slots_response = requests.get(f'{base_url}/api/parking/slots/', cookies=session_cookies)
        if slots_response.status_code == 200:
            slots_data = slots_response.json()
            print(f"✓ Employee A can access {len(slots_data)} parking slots")
            
            # Check if only Company A slots are returned
            company_a_slots = [slot for slot in slots_data if slot.get('company') == company_a.id]
            company_b_slots = [slot for slot in slots_data if slot.get('company') == company_b.id]
            
            if len(company_a_slots) > 0 and len(company_b_slots) == 0:
                print("✓ Employee A can only see Company A slots (correct)")
            else:
                print("✗ Employee A can see other company slots (SECURITY ISSUE)")
        else:
            print(f"✗ Employee A cannot access parking slots: {slots_response.status_code}")
        
        # Test companies access
        companies_response = requests.get(f'{base_url}/api/companies/', cookies=session_cookies)
        if companies_response.status_code == 200:
            companies_data = companies_response.json()
            print(f"✓ Employee A can access {len(companies_data)} companies")
            
            # Check if only Company A is returned
            if len(companies_data) == 1 and companies_data[0].get('name') == 'Company A':
                print("✓ Employee A can only see Company A (correct)")
            else:
                print("✗ Employee A can see other companies (SECURITY ISSUE)")
        else:
            print(f"✗ Employee A cannot access companies: {companies_response.status_code}")
    else:
        print(f"✗ Employee A login failed: {login_response.status_code}")
    
    # Test creating slot for wrong company
    print("\n2.2. Testing slot creation access control...")
    if 'session_cookies' in locals():
        # Try to create a slot (should be assigned to Company A automatically)
        slot_data = {
            'name': 'Test Slot',
            'division': 'Test Division'
        }
        create_response = requests.post(f'{base_url}/api/parking/slots/', 
                                      json=slot_data, cookies=session_cookies)
        
        if create_response.status_code == 201:
            created_slot = create_response.json()
            if created_slot.get('company') == company_a.id:
                print("✓ New slot automatically assigned to Employee A's company (correct)")
            else:
                print("✗ New slot assigned to wrong company (SECURITY ISSUE)")
        else:
            print(f"✗ Employee A cannot create slots: {create_response.status_code}")
    
    print("\n=== Test Complete ===")
    print("\nTest Results Summary:")
    print("- Company-scoped access should prevent users from seeing other companies' data")
    print("- New resources should be automatically assigned to user's company")
    print("- Check the output above for any SECURITY ISSUES")

if __name__ == "__main__":
    test_company_access()
