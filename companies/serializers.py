# companies/serializers.py
import uuid
from rest_framework import serializers
from .models import Company, EmployeeProfile
from core.models import CoreUser

class CoreUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')

class CompanySerializer(serializers.ModelSerializer):
    admin_user = CoreUserSerializer(read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'phone_number', 'location', 'company_code', 'admin_user', 'created_at')
        read_only_fields = ('company_code', 'created_at')

    def create(self, validated_data):
        # company_code can be auto-generated (e.g. UUID4 or custom logic)
        company = Company.objects.create(**validated_data, company_code=str(uuid.uuid4())[:8])
        return company

class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = CoreUserSerializer()

    class Meta:
        model = EmployeeProfile
        fields = ('id', 'user', 'company', 'phone_number', 'other_info')

    def create(self, validated_data):
        # Expect nested user creation
        user_data = validated_data.pop('user')
        user = CoreUser.objects.create_user(**user_data, role=CoreUser.Role.EMPLOYEE)
        employee = EmployeeProfile.objects.create(user=user, **validated_data)
        return employee
