# Questionnaire Update APIs - cURL Commands

This document provides cURL commands for updating each questionnaire step via PATCH (partial update) or PUT (full update).

**Base URL:** `http://localhost:8000`

**Authentication:** All requests require a JWT access token obtained from `/api/auth/verify-otp/`

**Note:** Use PATCH for partial updates (only send fields you want to change). Use PUT for full updates (must send all required fields).

---

## Table of Contents

1. [Personal Demographic](#1-personal-demographic)
2. [Income Employment](#2-income-employment)
3. [Banking Financial Access](#3-banking-financial-access)
4. [Credit Liabilities](#4-credit-liabilities)
5. [Savings Insurance](#5-savings-insurance)
6. [Expenses Obligations](#6-expenses-obligations)
7. [Behavioral Psychometric](#7-behavioral-psychometric)
8. [Government Scheme Eligibility](#8-government-scheme-eligibility)

**Note:** Step 9 (User Financial Literacy) does not currently have a dedicated API endpoint. The UserFinancialLiteracy model exists but needs to be exposed via an API view.

---

## 1. Personal Demographic

**Endpoint:** `/api/finance/personal-demographic/`

### PATCH - Partial Update
```bash
curl -X PATCH http://localhost:8000/api/finance/personal-demographic/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "age": 35,
    "gender": "Male",
    "state": "Maharashtra",
    "city_district": "Mumbai",
    "occupation_type": "Gig Worker",
    "marital_status": "Married",
    "children": "Yes",
    "dependents": 2,
    "education_level": "Graduate"
  }'
```

### PUT - Full Update (all fields required)
```bash
curl -X PUT http://localhost:8000/api/finance/personal-demographic/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "age": 35,
    "gender": "Male",
    "state": "Maharashtra",
    "city_district": "Mumbai",
    "occupation_type": "Gig Worker",
    "marital_status": "Married",
    "children": "Yes",
    "dependents": 2,
    "education_level": "Graduate"
  }'
```

### POST - Create or Update (Upsert)
```bash
curl -X POST http://localhost:8000/api/finance/personal-demographic/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "age": 35,
    "gender": "Male",
    "state": "Maharashtra",
    "city_district": "Mumbai",
    "occupation_type": "Gig Worker",
    "marital_status": "Married",
    "children": "Yes",
    "dependents": 2,
    "education_level": "Graduate"
  }'
```

**Available Fields:**
- `full_name` (string, optional)
- `age` (integer, optional)
- `gender` (string, optional) - e.g., "Male", "Female", "Other"
- `state` (string, optional)
- `city_district` (string, optional)
- `occupation_type` (string, optional) - e.g., "Gig Worker", "Farmer", "Small Retailer"
- `marital_status` (string, optional) - e.g., "Married", "Single", "Other"
- `children` (string, optional) - e.g., "Yes", "No", "Daughter"
- `dependents` (integer, optional)
- `education_level` (string, optional) - e.g., "None", "School", "College", "Graduate"

---

## 2. Income Employment

**Endpoint:** `/api/finance/income-employment/`

### PATCH - Partial Update
```bash
curl -X PATCH http://localhost:8000/api/finance/income-employment/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_income_source": "Swiggy",
    "monthly_income_range": "20001-30000",
    "working_days_per_month": 25,
    "income_variability": "Fluctuates",
    "mode_of_payment": "UPI"
  }'
```

### PUT - Full Update
```bash
curl -X PUT http://localhost:8000/api/finance/income-employment/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_income_source": "Swiggy",
    "monthly_income_range": "20001-30000",
    "working_days_per_month": 25,
    "income_variability": "Fluctuates",
    "mode_of_payment": "UPI"
  }'
```

### POST - Create or Update (Upsert)
```bash
curl -X POST http://localhost:8000/api/finance/income-employment/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_income_source": "Swiggy",
    "monthly_income_range": "20001-30000",
    "working_days_per_month": 25,
    "income_variability": "Fluctuates",
    "mode_of_payment": "UPI"
  }'
```

**Available Fields:**
- `primary_income_source` (string, optional) - e.g., "Swiggy", "Zomato", "Self-employed", "Farming"
- `monthly_income_range` (string, optional) - e.g., "5000-10000", "10001-20000", "20001-30000", "30001-50000", "50000+"
- `working_days_per_month` (integer, optional)
- `income_variability` (string, optional) - e.g., "Same", "Fluctuates"
- `mode_of_payment` (string, optional) - e.g., "Cash", "Bank", "UPI"

---

## 3. Banking Financial Access

**Endpoint:** `/api/finance/banking-access/`

### PATCH - Partial Update
```bash
curl -X PATCH http://localhost:8000/api/finance/banking-access/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "has_bank_account": true,
    "type_of_account": "Savings",
    "has_upi_wallet": true,
    "avg_monthly_bank_balance": "5000-10000",
    "bank_txn_per_month": 15,
    "has_credit_card_bnpl": false
  }'
```

### PUT - Full Update
```bash
curl -X PUT http://localhost:8000/api/finance/banking-access/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "has_bank_account": true,
    "type_of_account": "Savings",
    "has_upi_wallet": true,
    "avg_monthly_bank_balance": "5000-10000",
    "bank_txn_per_month": 15,
    "has_credit_card_bnpl": false
  }'
```

### POST - Create or Update (Upsert)
```bash
curl -X POST http://localhost:8000/api/finance/banking-access/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "has_bank_account": true,
    "type_of_account": "Savings",
    "has_upi_wallet": true,
    "avg_monthly_bank_balance": "5000-10000",
    "bank_txn_per_month": 15,
    "has_credit_card_bnpl": false
  }'
```

**Available Fields:**
- `has_bank_account` (boolean, optional)
- `type_of_account` (string, optional) - e.g., "Savings", "Current", "None"
- `has_upi_wallet` (boolean, optional)
- `avg_monthly_bank_balance` (string, optional) - e.g., "0-1000", "1000-5000", "5000-10000", "10000+"
- `bank_txn_per_month` (integer, optional)
- `has_credit_card_bnpl` (boolean, optional)

---

## 4. Credit Liabilities

**Endpoint:** `/api/finance/credit-liabilities/`

### PATCH - Partial Update
```bash
curl -X PATCH http://localhost:8000/api/finance/credit-liabilities/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "existing_loans": true,
    "type_of_loan": "Personal",
    "monthly_emi": 5000,
    "missed_payments_6m": false,
    "informal_borrowing": false
  }'
```

### PUT - Full Update
```bash
curl -X PUT http://localhost:8000/api/finance/credit-liabilities/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "existing_loans": true,
    "type_of_loan": "Personal",
    "monthly_emi": 5000,
    "missed_payments_6m": false,
    "informal_borrowing": false
  }'
```

### POST - Create or Update (Upsert)
```bash
curl -X POST http://localhost:8000/api/finance/credit-liabilities/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "existing_loans": true,
    "type_of_loan": "Personal",
    "monthly_emi": 5000,
    "missed_payments_6m": false,
    "informal_borrowing": false
  }'
```

**Available Fields:**
- `existing_loans` (boolean, optional)
- `type_of_loan` (string, optional) - e.g., "Personal", "Vehicle", "Business"
- `monthly_emi` (integer, optional)
- `missed_payments_6m` (boolean, optional)
- `informal_borrowing` (boolean, optional)

---

## 5. Savings Insurance

**Endpoint:** `/api/finance/savings-insurance/`

### PATCH - Partial Update
```bash
curl -X PATCH http://localhost:8000/api/finance/savings-insurance/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "regular_savings_habit": true,
    "savings_amount_per_month": "1000-3000",
    "has_insurance": "Health,Life",
    "type_of_insurance": "Govt",
    "has_pension_pf": false
  }'
```

### PUT - Full Update
```bash
curl -X PUT http://localhost:8000/api/finance/savings-insurance/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "regular_savings_habit": true,
    "savings_amount_per_month": "1000-3000",
    "has_insurance": "Health,Life",
    "type_of_insurance": "Govt",
    "has_pension_pf": false
  }'
```

### POST - Create or Update (Upsert)
```bash
curl -X POST http://localhost:8000/api/finance/savings-insurance/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "regular_savings_habit": true,
    "savings_amount_per_month": "1000-3000",
    "has_insurance": "Health,Life",
    "type_of_insurance": "Govt",
    "has_pension_pf": false
  }'
```

**Available Fields:**
- `regular_savings_habit` (boolean, optional)
- `savings_amount_per_month` (string, optional) - e.g., "<500", "500-1000", "1000-3000", ">3000"
- `has_insurance` (string, optional) - Multi-select: "Health", "Life", "Accident" (comma-separated)
- `type_of_insurance` (string, optional) - e.g., "Govt", "Private"
- `has_pension_pf` (boolean, optional)

---

## 6. Expenses Obligations

**Endpoint:** `/api/finance/expenses-obligations/`

### PATCH - Partial Update
```bash
curl -X PATCH http://localhost:8000/api/finance/expenses-obligations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "rent_per_month": 8000,
    "utilities_expense": 2000,
    "education_medical_expense": 3000,
    "avg_household_spend": 15000,
    "dependents_expense": 5000
  }'
```

### PUT - Full Update
```bash
curl -X PUT http://localhost:8000/api/finance/expenses-obligations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "rent_per_month": 8000,
    "utilities_expense": 2000,
    "education_medical_expense": 3000,
    "avg_household_spend": 15000,
    "dependents_expense": 5000
  }'
```

### POST - Create or Update (Upsert)
```bash
curl -X POST http://localhost:8000/api/finance/expenses-obligations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "rent_per_month": 8000,
    "utilities_expense": 2000,
    "education_medical_expense": 3000,
    "avg_household_spend": 15000,
    "dependents_expense": 5000
  }'
```

**Available Fields:**
- `rent_per_month` (integer, optional)
- `utilities_expense` (integer, optional)
- `education_medical_expense` (integer, optional)
- `avg_household_spend` (integer, optional)
- `dependents_expense` (integer, optional)

---

## 7. Behavioral Psychometric

**Endpoint:** `/api/finance/behavioral-psychometric/`

### PATCH - Partial Update
```bash
curl -X PATCH http://localhost:8000/api/finance/behavioral-psychometric/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "set_monthly_savings_goals": true,
    "track_expenses": true,
    "extra_income_behaviour": "Save",
    "payment_miss_frequency": "Never",
    "digital_comfort_level": 4
  }'
```

### PUT - Full Update
```bash
curl -X PUT http://localhost:8000/api/finance/behavioral-psychometric/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "set_monthly_savings_goals": true,
    "track_expenses": true,
    "extra_income_behaviour": "Save",
    "payment_miss_frequency": "Never",
    "digital_comfort_level": 4
  }'
```

### POST - Create or Update (Upsert)
```bash
curl -X POST http://localhost:8000/api/finance/behavioral-psychometric/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "set_monthly_savings_goals": true,
    "track_expenses": true,
    "extra_income_behaviour": "Save",
    "payment_miss_frequency": "Never",
    "digital_comfort_level": 4
  }'
```

**Available Fields:**
- `set_monthly_savings_goals` (boolean, optional)
- `track_expenses` (boolean, optional)
- `extra_income_behaviour` (string, optional) - e.g., "Save", "Spend", "Both"
- `payment_miss_frequency` (string, optional) - e.g., "Never", "Sometimes", "Often"
- `digital_comfort_level` (integer, optional) - Rating 1-5

---

## 8. Government Scheme Eligibility

**Endpoint:** `/api/finance/government-scheme/`

### PATCH - Partial Update
```bash
curl -X PATCH http://localhost:8000/api/finance/government-scheme/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "has_aadhaar": true,
    "has_pan": true,
    "enrolled_in_scheme": true,
    "scheme_names": "PMJDY,PMJJBY",
    "monthly_govt_benefit": 500
  }'
```

### PUT - Full Update
```bash
curl -X PUT http://localhost:8000/api/finance/government-scheme/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "has_aadhaar": true,
    "has_pan": true,
    "enrolled_in_scheme": true,
    "scheme_names": "PMJDY,PMJJBY",
    "monthly_govt_benefit": 500
  }'
```

### POST - Create or Update (Upsert)
```bash
curl -X POST http://localhost:8000/api/finance/government-scheme/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "has_aadhaar": true,
    "has_pan": true,
    "enrolled_in_scheme": true,
    "scheme_names": "PMJDY,PMJJBY",
    "monthly_govt_benefit": 500
  }'
```

**Available Fields:**
- `has_aadhaar` (boolean, optional)
- `has_pan` (boolean, optional)
- `enrolled_in_scheme` (boolean, optional)
- `scheme_names` (string, optional) - Comma-separated scheme names
- `monthly_govt_benefit` (integer, optional)

---

## Summary

### HTTP Methods:
- **PATCH**: Partial update - only send fields you want to change
- **PUT**: Full update - must send all fields
- **POST**: Create or update (upsert) - creates if doesn't exist, updates if exists

### Response Codes:
- `200 OK`: Update successful
- `201 Created`: Record created (only for POST when creating new)
- `404 Not Found`: Record doesn't exist (for PUT/PATCH only - POST creates if missing)
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing or invalid authentication token

### Important Notes:
1. All endpoints require authentication via JWT Bearer token
2. POST endpoints automatically create a record if it doesn't exist
3. PUT/PATCH endpoints return 404 if the record doesn't exist (use POST first)
4. After updating questionnaire data, call `/api/finance/uhfs-score/` (POST) to recalculate the UHFS score
5. Step 9 (User Financial Literacy) does not currently have an API endpoint - the model exists but needs a view to be created

---

## Example: Complete Questionnaire Flow

```bash
# 1. Verify OTP and get access token
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "otp_code": "123456"
  }'

# Extract ACCESS_TOKEN from response

# 2. Update Personal Demographic
curl -X PATCH http://localhost:8000/api/finance/personal-demographic/ \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "John Doe", "age": 35}'

# 3. Update Income Employment
curl -X PATCH http://localhost:8000/api/finance/income-employment/ \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"monthly_income_range": "20001-30000"}'

# ... continue with other steps ...

# 9. Calculate UHFS Score after completing all steps
curl -X POST http://localhost:8000/api/finance/uhfs-score/ \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```





