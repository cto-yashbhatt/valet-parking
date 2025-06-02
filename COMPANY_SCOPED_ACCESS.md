# Company-Scoped Access Control - Valet Parking System

## 🎯 **Problem Solved**

Previously, employees from Company A could see and access data from Company B, which is a major security issue. Now, **all data access is strictly scoped to the user's company**.

## 🔒 **Security Implementation**

### **1. Permission Classes Created**

#### `IsCompanyMember`
- Allows access only to users who belong to the same company as the object
- Used for general company-scoped access

#### `IsCompanyAdmin` 
- Allows access only to company admins for their own company
- Used for admin-only operations

#### `IsCompanyAdminOrEmployee`
- Allows access to both admins and employees for their own company
- Used for general operations within a company

### **2. Helper Function**
```python
def get_user_company(user):
    """Get the company associated with a user"""
    # Returns the user's company or None
```

## 🛡️ **Access Control by Endpoint**

### **Parking Slots (`/api/parking/slots/`)**
- **GET**: Returns only slots belonging to user's company
- **POST**: Automatically assigns new slots to user's company
- **PUT/PATCH/DELETE**: Only allows modification of user's company slots

### **Parking Transactions (`/api/parking/transactions/`)**
- **GET**: Returns only transactions for slots belonging to user's company
- **POST**: Updates only transactions for user's company slots

### **Companies (`/api/companies/`)**
- **GET**: Returns only the user's own company
- **POST**: Creates company (handled by registration system)

### **Employees (`/api/companies/{id}/employees/`)**
- **GET**: Returns only employees from user's company
- **POST**: Creates employees only for user's company (admin only)

## 🎭 **User Role Behavior**

### **Company Admin**
- Can see/manage all data within their company
- Can create/manage employees
- Can create/manage parking slots
- Can view/manage all transactions for their company

### **Employee**
- Can see/manage data within their company only
- Cannot manage other employees
- Can create parking slots for their company
- Can manage transactions for their company slots

## 🔧 **Frontend Changes**

### **Dashboard**
- Shows company name at the top
- Statistics are company-specific
- Recent transactions are company-scoped

### **Parking Management**
- Company field is auto-filled and readonly
- Only shows slots from user's company
- New slots automatically assigned to user's company

### **Companies Management**
- Only shows user's own company
- Employees list is company-scoped

### **Transactions**
- Only shows transactions for user's company slots
- Status updates only work on user's company transactions

## 🧪 **Testing Company Isolation**

### **Test Scenario 1: Employee Access**
```bash
# Login as Employee from Company A
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "employee_a", "password": "password123"}'

# Get parking slots (should only return Company A slots)
curl -X GET http://localhost:8000/api/parking/slots/ \
  -H "Cookie: sessionid=<session_id>"

# Result: Only Company A slots returned ✓
```

### **Test Scenario 2: Slot Creation**
```bash
# Create new slot as Employee A
curl -X POST http://localhost:8000/api/parking/slots/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=<session_id>" \
  -d '{"name": "New Slot", "division": "Test"}'

# Result: Slot automatically assigned to Company A ✓
```

### **Test Scenario 3: Cross-Company Access**
```bash
# Try to access Company B's slot as Employee A
curl -X GET http://localhost:8000/api/parking/slots/<company_b_slot_id>/ \
  -H "Cookie: sessionid=<session_id>"

# Result: 404 Not Found (slot not in queryset) ✓
```

## 🔍 **Security Verification**

### **Database Level**
- All queries are filtered by company
- No raw SQL that bypasses filters
- Foreign key relationships respect company boundaries

### **API Level**
- Permission classes on all endpoints
- Automatic company assignment for new objects
- Object-level permissions for updates/deletes

### **Frontend Level**
- Company information stored in localStorage
- Forms auto-populate company fields
- UI only shows company-relevant data

## 📊 **Data Flow Example**

### **Employee Login Process**
1. Employee logs in with username/password
2. System identifies employee's company
3. Frontend stores user + company info in localStorage
4. All subsequent API calls are company-scoped

### **Slot Creation Process**
1. Employee fills out slot form (company field readonly)
2. Frontend sends slot data (without company field)
3. Backend automatically assigns user's company
4. Slot is created and linked to correct company

### **Data Retrieval Process**
1. Frontend requests parking slots
2. Backend filters by user's company automatically
3. Only company-specific slots returned
4. Frontend displays company-scoped data

## 🚨 **Security Guarantees**

### **What's Protected**
✅ Parking slots are company-isolated
✅ Transactions are company-isolated  
✅ Employee lists are company-isolated
✅ Company information is company-isolated
✅ New resources auto-assigned to correct company

### **What's Prevented**
❌ Cross-company data access
❌ Unauthorized slot creation for other companies
❌ Viewing other companies' transactions
❌ Managing other companies' employees
❌ Data leakage between companies

## 🔧 **Implementation Details**

### **Permission Inheritance**
```python
# All parking views inherit from:
permission_classes = [IsCompanyAdminOrEmployee]

# All company admin views inherit from:
permission_classes = [IsCompanyAdmin]
```

### **Automatic Company Assignment**
```python
def perform_create(self, serializer):
    user_company = get_user_company(self.request.user)
    if user_company:
        serializer.save(company=user_company)
```

### **Company-Scoped Querysets**
```python
def get_queryset(self):
    user_company = get_user_company(self.request.user)
    if user_company:
        return Model.objects.filter(company=user_company)
    return Model.objects.none()
```

## 🎯 **Result**

**Before**: Employee from Company A could see Company B's data ❌
**After**: Employee from Company A can only see Company A's data ✅

**Before**: New slots could be assigned to any company ❌  
**After**: New slots automatically assigned to user's company ✅

**Before**: No data isolation between companies ❌
**After**: Complete data isolation between companies ✅

## 🧪 **How to Test**

1. **Create two companies** using the registration system
2. **Create employees** for each company
3. **Login as Employee A** and create some parking slots
4. **Login as Employee B** and verify you can't see Employee A's slots
5. **Create slots as Employee B** and verify they're assigned to Company B
6. **Switch back to Employee A** and verify you still only see Company A's data

The system now provides **complete company-level data isolation** ensuring that each company's data remains private and secure! 🔒
