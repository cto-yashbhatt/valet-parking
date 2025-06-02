"""
Django command to create test data for the valet parking system
"""
from django.core.management.base import BaseCommand
from core.models import CoreUser
from companies.models import Company, EmployeeProfile


class Command(BaseCommand):
    """Django command to create test data"""

    def handle(self, *args, **options):
        """Create test data"""
        self.stdout.write('Creating test data...')

        # First, let's check what already exists
        existing_users = CoreUser.objects.all()
        existing_companies = Company.objects.all()
        existing_profiles = EmployeeProfile.objects.all()

        self.stdout.write(f'Existing users: {existing_users.count()}')
        self.stdout.write(f'Existing companies: {existing_companies.count()}')
        self.stdout.write(f'Existing profiles: {existing_profiles.count()}')
        
        # Create test company admin
        admin_user, created = CoreUser.objects.get_or_create(
            username='testadmin',
            defaults={
                'email': 'admin@test.com',
                'first_name': 'Test',
                'last_name': 'Admin',
                'role': CoreUser.Role.COMPANY_ADMIN
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'Created admin user: testadmin / admin123')
        else:
            self.stdout.write(f'Admin user already exists: testadmin')
        
        # Create test company
        company, created = Company.objects.get_or_create(
            name='Test Valet Company',
            defaults={
                'phone_number': '+1234567890',
                'location': '123 Test Street, Test City',
                'company_code': 'TEST123',
                'admin_user': admin_user
            }
        )
        if created:
            self.stdout.write(f'Created company: {company.name} (Code: {company.company_code})')
        else:
            self.stdout.write(f'Company already exists: {company.name}')
        
        # Create test employee
        employee_user, created = CoreUser.objects.get_or_create(
            username='testemployee',
            defaults={
                'email': 'employee@test.com',
                'first_name': 'Test',
                'last_name': 'Employee',
                'role': CoreUser.Role.EMPLOYEE
            }
        )
        if created:
            employee_user.set_password('employee123')
            employee_user.save()
            self.stdout.write(f'Created employee user: testemployee / employee123')
        else:
            self.stdout.write(f'Employee user already exists: testemployee')
        
        # Create employee profile
        employee_profile, created = EmployeeProfile.objects.get_or_create(
            user=employee_user,
            defaults={
                'company': company,
                'phone_number': '+1234567891'
            }
        )
        if created:
            self.stdout.write(f'Created employee profile for: {employee_user.username}')
        else:
            self.stdout.write(f'Employee profile already exists for: {employee_user.username}')
        
        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))
        self.stdout.write('')
        self.stdout.write('Test credentials:')
        self.stdout.write(f'  Company Admin: testadmin / admin123')
        self.stdout.write(f'  Employee: testemployee / employee123')
        self.stdout.write(f'  Company Code: {company.company_code}')
