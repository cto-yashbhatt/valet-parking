from django.shortcuts import render
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from core.models import CoreUser
from companies.models import Company, EmployeeProfile
import uuid

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
