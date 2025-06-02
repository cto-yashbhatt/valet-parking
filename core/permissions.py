# core/permissions.py
from rest_framework import permissions
from companies.models import Company, EmployeeProfile


def get_user_company(user):
    """Get the company associated with a user"""
    if not user.is_authenticated:
        print(f"DEBUG: User {user} not authenticated")
        return None

    print(f"DEBUG: Getting company for user {user.username} (role: {user.role})")

    if user.role == user.Role.COMPANY_ADMIN:
        try:
            company = Company.objects.get(admin_user=user)
            print(f"DEBUG: Found admin company: {company.name}")
            return company
        except Company.DoesNotExist:
            print(f"DEBUG: No admin company found for {user.username}")
            return None
    elif user.role == user.Role.EMPLOYEE:
        try:
            employee_profile = EmployeeProfile.objects.get(user=user)
            print(f"DEBUG: Found employee profile: {employee_profile.company.name}")
            return employee_profile.company
        except EmployeeProfile.DoesNotExist:
            print(f"DEBUG: No employee profile found for {user.username}")
            # Try to create one if there's a company available
            companies = Company.objects.all()
            if companies.exists():
                first_company = companies.first()
                print(f"DEBUG: Creating employee profile for {user.username} in {first_company.name}")
                EmployeeProfile.objects.create(
                    user=user,
                    company=first_company,
                    phone_number='+0000000000'
                )
                return first_company
            return None

    return None


class IsCompanyMember(permissions.BasePermission):
    """
    Permission that allows access only to users who belong to the same company
    as the object being accessed.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view"""
        return request.user.is_authenticated and get_user_company(request.user) is not None
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access the specific object"""
        user_company = get_user_company(request.user)
        if not user_company:
            return False
        
        # Check if the object has a company field
        if hasattr(obj, 'company'):
            return obj.company == user_company
        
        # For Company objects, check if user is admin or employee of this company
        if hasattr(obj, 'admin_user'):  # This is a Company object
            return obj == user_company
        
        return False


class IsCompanyAdmin(permissions.BasePermission):
    """
    Permission that allows access only to company admins for their own company.
    """
    
    def has_permission(self, request, view):
        """Check if user is a company admin"""
        return (
            request.user.is_authenticated 
            and request.user.role == request.user.Role.COMPANY_ADMIN
            and get_user_company(request.user) is not None
        )
    
    def has_object_permission(self, request, view, obj):
        """Check if user is admin of the object's company"""
        user_company = get_user_company(request.user)
        if not user_company:
            return False
        
        # Check if the object has a company field
        if hasattr(obj, 'company'):
            return obj.company == user_company
        
        # For Company objects, check if user is the admin
        if hasattr(obj, 'admin_user'):  # This is a Company object
            return obj.admin_user == request.user
        
        return False


class IsCompanyAdminOrEmployee(permissions.BasePermission):
    """
    Permission that allows access to company admins and employees for their own company.
    """
    
    def has_permission(self, request, view):
        """Check if user belongs to a company"""
        is_authenticated = request.user.is_authenticated
        has_valid_role = request.user.role in [request.user.Role.COMPANY_ADMIN, request.user.Role.EMPLOYEE] if is_authenticated else False
        user_company = get_user_company(request.user) if is_authenticated else None

        result = is_authenticated and has_valid_role and user_company is not None

        # Only log failed permissions for debugging
        if not result:
            print(f"DEBUG: Permission DENIED for {request.method} {request.path}")
            print(f"DEBUG: User: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
            print(f"DEBUG: Reason - authenticated: {is_authenticated}, valid_role: {has_valid_role}, has_company: {user_company is not None}")

        return result
    
    def has_object_permission(self, request, view, obj):
        """Check if user belongs to the object's company"""
        user_company = get_user_company(request.user)
        if not user_company:
            return False
        
        # Check if the object has a company field
        if hasattr(obj, 'company'):
            return obj.company == user_company
        
        # For Company objects, check if user belongs to this company
        if hasattr(obj, 'admin_user'):  # This is a Company object
            return obj == user_company
        
        return False
