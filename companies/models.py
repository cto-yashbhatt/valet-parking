from django.db import models

# companies/models.py
import uuid
from django.db import models
from django.conf import settings

class Company(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    company_code = models.CharField(max_length=50, unique=True)
    admin_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_admin_profile'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.company_code})"

class EmployeeProfile(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='employees'
    )
    phone_number = models.CharField(max_length=20)
    other_info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} @ {self.company.company_code}"

