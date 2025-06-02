from django.shortcuts import render
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from core.models import CoreUser
from companies.models import Company, EmployeeProfile
import uuid
import json

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def register_company(request):
    """Register a new company with admin user"""
    try:
        data = request.data

        # Validate required fields
        required_fields = ['company_name', 'company_phone', 'company_location',
                          'first_name', 'last_name', 'username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return Response({'message': f'{field} is required'},
                              status=status.HTTP_400_BAD_REQUEST)

        # Check if username already exists
        if CoreUser.objects.filter(username=data['username']).exists():
            return Response({'message': 'Username already exists'},
                          status=status.HTTP_400_BAD_REQUEST)

        # Check if email already exists
        if CoreUser.objects.filter(email=data['email']).exists():
            return Response({'message': 'Email already exists'},
                          status=status.HTTP_400_BAD_REQUEST)

        # Check if company name already exists
        if Company.objects.filter(name=data['company_name']).exists():
            return Response({'message': 'Company name already exists'},
                          status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Create admin user
            admin_user = CoreUser.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                role=CoreUser.Role.COMPANY_ADMIN
            )

            # Create company
            company = Company.objects.create(
                name=data['company_name'],
                phone_number=data['company_phone'],
                location=data['company_location'],
                company_code=str(uuid.uuid4())[:8].upper(),
                admin_user=admin_user
            )

            return Response({
                'message': 'Company registered successfully',
                'company_code': company.company_code,
                'company_name': company.name
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'message': f'Registration failed: {str(e)}'},
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_company_code(request):
    """Verify company code and return company details"""
    company_code = request.GET.get('code')
    if not company_code:
        return Response({'message': 'Company code is required'},
                       status=status.HTTP_400_BAD_REQUEST)

    try:
        company = Company.objects.get(company_code=company_code.upper())
        return Response({
            'id': company.id,
            'name': company.name,
            'location': company.location,
            'phone_number': company.phone_number
        })
    except Company.DoesNotExist:
        return Response({'message': 'Invalid company code'},
                       status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_employee(request):
    """Register a new employee with company code"""
    try:
        data = request.data

        # Validate required fields
        required_fields = ['company_code', 'first_name', 'last_name',
                          'username', 'email', 'phone_number', 'password']
        for field in required_fields:
            if not data.get(field):
                return Response({'message': f'{field} is required'},
                              status=status.HTTP_400_BAD_REQUEST)

        # Check if username already exists
        if CoreUser.objects.filter(username=data['username']).exists():
            return Response({'message': 'Username already exists'},
                          status=status.HTTP_400_BAD_REQUEST)

        # Check if email already exists
        if CoreUser.objects.filter(email=data['email']).exists():
            return Response({'message': 'Email already exists'},
                          status=status.HTTP_400_BAD_REQUEST)

        # Verify company code
        try:
            company = Company.objects.get(company_code=data['company_code'].upper())
        except Company.DoesNotExist:
            return Response({'message': 'Invalid company code'},
                          status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Create employee user
            employee_user = CoreUser.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                role=CoreUser.Role.EMPLOYEE
            )

            # Create employee profile
            EmployeeProfile.objects.create(
                user=employee_user,
                company=company,
                phone_number=data['phone_number']
            )

            return Response({
                'message': 'Employee registered successfully',
                'company_name': company.name
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'message': f'Registration failed: {str(e)}'},
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user and create session"""
    try:
        data = request.data
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return Response({'message': 'Username and password are required'},
                          status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login user (creates session)
            login(request, user)

            # Get user's company info if they're an employee
            company_info = None
            if user.role == CoreUser.Role.EMPLOYEE:
                try:
                    employee_profile = EmployeeProfile.objects.get(user=user)
                    company_info = {
                        'id': employee_profile.company.id,
                        'name': employee_profile.company.name,
                        'code': employee_profile.company.company_code
                    }
                except EmployeeProfile.DoesNotExist:
                    pass
            elif user.role == CoreUser.Role.COMPANY_ADMIN:
                try:
                    company = Company.objects.get(admin_user=user)
                    company_info = {
                        'id': company.id,
                        'name': company.name,
                        'code': company.company_code
                    }
                except Company.DoesNotExist:
                    pass

            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                },
                'company': company_info
            }, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid username or password'},
                          status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return Response({'message': f'Login failed: {str(e)}'},
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])  # Temporarily allow any for debugging
def debug_user_info(request):
    """Debug endpoint to check user's company association"""
    from core.permissions import get_user_company

    user = request.user
    user_company = get_user_company(user)

    # Get employee profile if exists
    employee_profile = None
    if user.role == CoreUser.Role.EMPLOYEE:
        try:
            employee_profile = EmployeeProfile.objects.get(user=user)
        except EmployeeProfile.DoesNotExist:
            pass

    # Get admin company if exists
    admin_company = None
    if user.role == CoreUser.Role.COMPANY_ADMIN:
        try:
            admin_company = Company.objects.get(admin_user=user)
        except Company.DoesNotExist:
            pass

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'is_authenticated': user.is_authenticated
        },
        'user_company': {
            'id': user_company.id if user_company else None,
            'name': user_company.name if user_company else None,
            'code': user_company.company_code if user_company else None
        } if user_company else None,
        'employee_profile': {
            'id': employee_profile.id if employee_profile else None,
            'company_id': employee_profile.company.id if employee_profile else None,
            'company_name': employee_profile.company.name if employee_profile else None
        } if employee_profile else None,
        'admin_company': {
            'id': admin_company.id if admin_company else None,
            'name': admin_company.name if admin_company else None
        } if admin_company else None
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_user(request):
    """Logout user and clear session"""
    try:
        if request.user.is_authenticated:
            logout(request)
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'User not authenticated'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'message': f'Logout failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
