# companies/views.py
from rest_framework import generics, permissions
from .models import Company, EmployeeProfile
from .serializers import CompanySerializer, EmployeeProfileSerializer
from core.permissions import IsCompanyAdmin, get_user_company

class CompanyListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: List companies (only user's own company for employees/admins)
    POST: Create company (only for company admins)
    """
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only the user's company"""
        user_company = get_user_company(self.request.user)
        if user_company:
            return Company.objects.filter(id=user_company.id)
        return Company.objects.none()

    def perform_create(self, serializer):
        # Only company admins can create companies (handled by registration)
        # This endpoint is mainly for listing
        serializer.save(admin_user=self.request.user)

class CompanyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated & IsCompanyAdmin]

class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: List employees for user's company only
    POST: Create employee for user's company only (admin only)
    """
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsCompanyAdmin]

    def get_queryset(self):
        """Return employees for the user's company only"""
        user_company = get_user_company(self.request.user)
        if user_company:
            return EmployeeProfile.objects.filter(company=user_company)
        return EmployeeProfile.objects.none()

    def perform_create(self, serializer):
        """Associate the employee with the user's company"""
        user_company = get_user_company(self.request.user)
        if user_company:
            serializer.save(company=user_company)
        else:
            raise permissions.PermissionDenied("User not associated with any company")

class EmployeeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE: Manage employees for user's company only (admin only)
    """
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsCompanyAdmin]

    def get_queryset(self):
        """Return employees for the user's company only"""
        user_company = get_user_company(self.request.user)
        if user_company:
            return EmployeeProfile.objects.filter(company=user_company)
        return EmployeeProfile.objects.none()
