from django.shortcuts import render

# Create your views here.
# companies/views.py
from rest_framework import generics, permissions
from .models import Company, EmployeeProfile
from .serializers import CompanySerializer, EmployeeProfileSerializer

class IsCompanyAdmin(permissions.BasePermission):
    """
    Custom permission: user must have role=company_admin and be the admin of that company.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user.role == request.user.Role.COMPANY_ADMIN
            and obj.admin_user == request.user
        )

class CompanyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Set the authenticated user as the admin_user
        serializer.save(admin_user=self.request.user)

class CompanyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated & IsCompanyAdmin]

class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EmployeeProfileSerializer
    permission_classes = [permissions.IsAuthenticated & IsCompanyAdmin]

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return EmployeeProfile.objects.filter(company__id=company_id)

    def perform_create(self, serializer):
        company = Company.objects.get(id=self.kwargs['company_id'])
        serializer.save(company=company)

class EmployeeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeProfileSerializer
    permission_classes = [permissions.IsAuthenticated & IsCompanyAdmin]

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return EmployeeProfile.objects.filter(company__id=company_id)
