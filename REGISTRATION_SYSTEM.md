# Registration System - Valet Parking System

## Overview

The valet parking system now has a comprehensive registration system with two distinct user types and proper company management.

## User Roles

### 1. Company Admin
- **Purpose**: Owns and manages a valet parking company
- **Capabilities**:
  - Create and manage parking slots
  - View and manage all company employees
  - Access company management features
  - View all transactions for their company
  - Full administrative control

### 2. Employee
- **Purpose**: Works for a valet parking company
- **Capabilities**:
  - Manage parking transactions (park/retrieve cars)
  - View parking slots and their status
  - Handle customer requests
  - Update transaction statuses
  - Limited access (company-specific)

## Registration Flow

### Company Registration
1. **Access**: Visit `/register/company/` or click "Register Company" from landing page
2. **Process**:
   - Fill company information (name, phone, address)
   - Create admin user account (name, username, email, password)
   - System generates unique company code
   - Admin user is automatically assigned to the company
3. **Result**: 
   - Company is created with unique 8-character code
   - Admin user can login and start managing the company
   - Company code is provided for employee registration

### Employee Registration
1. **Access**: Visit `/register/employee/` or click "Join as Employee" from landing page
2. **Process**:
   - Enter company code (provided by company admin)
   - Verify company exists
   - Fill personal information
   - Create user account
   - System links employee to the company
3. **Result**:
   - Employee account is created
   - Employee is linked to the specified company
   - Employee can login with limited access

## Registration Pages

### 1. Main Registration Page (`/register/`)
- **Purpose**: Choose between company or employee registration
- **Features**:
  - Clear explanation of user roles
  - Visual cards for each registration type
  - Role comparison table

### 2. Company Registration (`/register/company/`)
- **Features**:
  - Company information form
  - Admin user creation
  - Terms and conditions
  - Real-time validation
  - Success message with company code

### 3. Employee Registration (`/register/employee/`)
- **Features**:
  - Company code verification
  - Personal information form
  - Real-time company lookup
  - Terms and conditions
  - Success confirmation

## API Endpoints

### Authentication APIs (`/api/auth/`)

#### 1. Register Company
- **Endpoint**: `POST /api/auth/register-company/`
- **Purpose**: Create new company with admin user
- **Payload**:
```json
{
  "company_name": "ABC Valet Services",
  "company_phone": "+1234567890",
  "company_location": "123 Main St, City, State",
  "first_name": "John",
  "last_name": "Doe",
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword"
}
```
- **Response**:
```json
{
  "message": "Company registered successfully",
  "company_code": "ABC12345",
  "company_name": "ABC Valet Services"
}
```

#### 2. Verify Company Code
- **Endpoint**: `GET /api/auth/verify-company-code/?code=ABC12345`
- **Purpose**: Verify company code exists and return company details
- **Response**:
```json
{
  "id": 1,
  "name": "ABC Valet Services",
  "location": "123 Main St, City, State",
  "phone_number": "+1234567890"
}
```

#### 3. Register Employee
- **Endpoint**: `POST /api/auth/register-employee/`
- **Purpose**: Create employee account linked to company
- **Payload**:
```json
{
  "company_code": "ABC12345",
  "first_name": "Jane",
  "last_name": "Smith",
  "username": "janesmith",
  "email": "jane@example.com",
  "phone_number": "+1234567891",
  "password": "securepassword"
}
```
- **Response**:
```json
{
  "message": "Employee registered successfully",
  "company_name": "ABC Valet Services"
}
```

## Database Changes

### Company Model Updates
- **company_code**: Unique 8-character identifier for employee registration
- **admin_user**: Link to the company admin user

### User Model
- **role**: COMPANY_ADMIN or EMPLOYEE
- Proper role-based access control

### Employee Profile
- **company**: Link to the company
- **phone_number**: Employee contact information

## Security Features

### Validation
- Username uniqueness across all users
- Email uniqueness across all users
- Company name uniqueness
- Company code uniqueness
- Password strength requirements
- Real-time form validation

### Access Control
- Role-based permissions
- Company-specific data access
- Secure password hashing
- CSRF protection

## User Experience

### Landing Page Updates
- **Dropdown Registration**: Choose between company or employee registration
- **Clear Role Explanation**: Visual cards explaining each role
- **Streamlined Flow**: Direct users to appropriate registration

### Form Features
- **Real-time Validation**: Immediate feedback on form errors
- **Company Verification**: Live company code lookup
- **Progress Indicators**: Clear steps and feedback
- **Responsive Design**: Works on all devices

## Testing the System

### 1. Register a Company
```bash
# Visit http://localhost:8000/register/company/
# Fill out the form
# Note the company code provided
```

### 2. Register an Employee
```bash
# Visit http://localhost:8000/register/employee/
# Use the company code from step 1
# Complete employee registration
```

### 3. Login and Test
```bash
# Login as company admin - see full features
# Login as employee - see limited features
```

## Error Handling

### Common Errors
- **Username exists**: Clear message with suggestion
- **Email exists**: Helpful error message
- **Invalid company code**: Immediate feedback
- **Password mismatch**: Real-time validation
- **Missing fields**: Field-specific error messages

### API Error Responses
```json
{
  "message": "Username already exists"
}
```

## Future Enhancements

### Planned Features
- [ ] Email verification for registration
- [ ] Password reset functionality
- [ ] Company admin can invite employees via email
- [ ] Bulk employee import
- [ ] Company settings management
- [ ] Employee role permissions (manager, attendant, etc.)

### Security Improvements
- [ ] Two-factor authentication
- [ ] Password complexity requirements
- [ ] Account lockout after failed attempts
- [ ] Audit logging for registrations

## Troubleshooting

### Common Issues
1. **Registration not working**: Check API endpoints are accessible
2. **Company code not found**: Verify company was created successfully
3. **Form validation errors**: Check required fields and formats
4. **Database errors**: Ensure migrations are applied

### Debug Steps
```bash
# Check server logs
python manage.py runserver

# Verify database
python manage.py shell
>>> from companies.models import Company
>>> Company.objects.all()

# Test API endpoints
curl -X POST http://localhost:8000/api/auth/register-company/ \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Test Company", ...}'
```

The registration system is now complete and provides a professional, secure way for companies and employees to join the valet parking platform!
