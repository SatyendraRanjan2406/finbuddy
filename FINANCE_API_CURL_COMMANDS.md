# Finance API - cURL Commands Reference

This document provides cURL commands for all finance-related APIs. All endpoints require authentication using a token obtained from the OTP verification endpoint.

**Base URL:** `http://localhost:8000`

**Authentication:** All requests require a JWT access token in the Authorization header:
```
Authorization: Bearer <your_access_token_here>
```

**Getting JWT Tokens:**
1. Send OTP: `POST /api/auth/send-otp/`
2. Verify OTP: `POST /api/auth/verify-otp/` - Returns `access` and `refresh` tokens
3. Use the `access` token in the `Authorization: Bearer <access_token>` header

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
9. [UHFS Score](#9-uhfs-score)

---

## 1. Personal Demographic

### GET - Retrieve Personal Demographic Information
```bash
curl -X GET http://localhost:8000/api/finance/personal-demographic/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

### POST - Create or Update Personal Demographic Information
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

### PATCH - Partial Update Personal Demographic Information
```bash
curl -X PATCH http://localhost:8000/api/finance/personal-demographic/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 36,
    "city_district": "Pune"
  }'
```

### PUT - Full Update Personal Demographic Information
```bash
curl -X PUT http://localhost:8000/api/finance/personal-demographic/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "age": 36,
    "gender": "Male",
    "state": "Maharashtra",
    "city_district": "Pune",
    "occupation_type": "Gig Worker",
    "marital_status": "Married",
    "children": "Yes",
    "dependents": 2,
    "education_level": "Graduate"
  }'
```

---

## 2. Income Employment

### GET - Retrieve Income Employment Information
```bash
curl -X GET http://localhost:8000/api/finance/income-employment/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

### POST - Create or Update Income Employment Information
```bash
curl -X POST http://localhost:8000/api/finance/income-employment/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_income_source": "Swiggy Delivery",
    "monthly_income_range": "20-30k",
    "working_days_per_month": 25,
    "income_variability": "Fluctuates",
    "mode_of_payment": "UPI"
  }'
```

### PATCH - Partial Update Income Employment Information
```bash
curl -X PATCH http://localhost:8000/api/finance/income-employment/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_income_range": "30-40k",
    "working_days_per_month": 28
  }'
```

### PUT - Full Update Income Employment Information
```bash
curl -X PUT http://localhost:8000/api/finance/income-employment/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_income_source": "Zomato Delivery",
    "monthly_income_range": "30-40k",
    "working_days_per_month": 28,
    "income_variability": "Same",
    "mode_of_payment": "Bank Transfer"
  }'
```

---

## 3. Banking Financial Access

### GET - Retrieve Banking Financial Access Information
```bash
curl -X GET http://localhost:8000/api/finance/banking-access/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

### POST - Create or Update Banking Financial Access Information
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

### PATCH - Partial Update Banking Financial Access Information
```bash
curl -X PATCH http://localhost:8000/api/finance/banking-access/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "has_credit_card_bnpl": true,
    "bank_txn_per_month": 20
  }'
```

### PUT - Full Update Banking Financial Access Information
```bash
curl -X PUT http://localhost:8000/api/finance/banking-access/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "has_bank_account": true,
    "type_of_account": "Current",
    "has_upi_wallet": true,
    "avg_monthly_bank_balance": "10000-20000",
    "bank_txn_per_month": 20,
    "has_credit_card_bnpl": true
  }'
```

---

## 4. Credit Liabilities

### GET - Retrieve Credit Liabilities Information
```bash
curl -X GET http://localhost:8000/api/finance/credit-liabilities/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

### POST - Create or Update Credit Liabilities Information
```bash
curl -X POST http://localhost:8000/api/finance/credit-liabilities/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "existing_loans": true,
    "type_of_loan": "Personal Loan",
    "monthly_emi": 5000,
    "missed_payments_6m": false,
    "informal_borrowing": false
  }'
```

### PATCH - Partial Update Credit Liabilities Information
```bash
curl -X PATCH http://localhost:8000/api/finance/credit-liabilities/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_emi": 6000,
    "missed_payments_6m": true
  }'
```

### PUT - Full Update Credit Liabilities Information
```bash
curl -X PUT http://localhost:8000/api/finance/credit-liabilities/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "existing_loans": false,
    "type_of_loan": null,
    "monthly_emi": null,
    "missed_payments_6m": false,
    "informal_borrowing": true
  }'
```

---

## 5. Savings Insurance

### GET - Retrieve Savings Insurance Information
```bash
curl -X GET http://localhost:8000/api/finance/savings-insurance/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

### POST - Create or Update Savings Insurance Information
```bash
curl -X POST http://localhost:8000/api/finance/savings-insurance/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "regular_savings_habit": true,
    "savings_amount_per_month": "2000-5000",
    "has_insurance": "Health,Life",
    "type_of_insurance": "Private",
    "has_pension_pf": false
  }'
```

### PATCH - Partial Update Savings Insurance Information
```bash
curl -X PATCH http://localhost:8000/api/finance/savings-insurance/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "has_pension_pf": true,
    "savings_amount_per_month": "5000-10000"
  }'
```

### PUT - Full Update Savings Insurance Information
```bash
curl -X PUT http://localhost:8000/api/finance/savings-insurance/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "regular_savings_habit": true,
    "savings_amount_per_month": "5000-10000",
    "has_insurance": "Health,Life,Accident",
    "type_of_insurance": "Govt",
    "has_pension_pf": true
  }'
```

---

## 6. Expenses Obligations

### GET - Retrieve Expenses Obligations Information
```bash
curl -X GET http://localhost:8000/api/finance/expenses-obligations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

### POST - Create or Update Expenses Obligations Information
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

### PATCH - Partial Update Expenses Obligations Information
```bash
curl -X PATCH http://localhost:8000/api/finance/expenses-obligations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "rent_per_month": 10000,
    "avg_household_spend": 18000
  }'
```

### PUT - Full Update Expenses Obligations Information
```bash
curl -X PUT http://localhost:8000/api/finance/expenses-obligations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "rent_per_month": 10000,
    "utilities_expense": 2500,
    "education_medical_expense": 4000,
    "avg_household_spend": 18000,
    "dependents_expense": 6000
  }'
```

---

## 7. Behavioral Psychometric

### GET - Retrieve Behavioral Psychometric Information
```bash
curl -X GET http://localhost:8000/api/finance/behavioral-psychometric/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

### POST - Create or Update Behavioral Psychometric Information
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

### PATCH - Partial Update Behavioral Psychometric Information
```bash
curl -X PATCH http://localhost:8000/api/finance/behavioral-psychometric/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "digital_comfort_level": 5,
    "extra_income_behaviour": "Both"
  }'
```

### PUT - Full Update Behavioral Psychometric Information
```bash
curl -X PUT http://localhost:8000/api/finance/behavioral-psychometric/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "set_monthly_savings_goals": false,
    "track_expenses": false,
    "extra_income_behaviour": "Spend",
    "payment_miss_frequency": "Sometimes",
    "digital_comfort_level": 3
  }'
```

---

## 8. Government Scheme Eligibility

### GET - Retrieve Government Scheme Eligibility Information
```bash
curl -X GET http://localhost:8000/api/finance/government-scheme/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

### POST - Create or Update Government Scheme Eligibility Information
```bash
curl -X POST http://localhost:8000/api/finance/government-scheme/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "has_aadhaar": true,
    "has_pan": true,
    "enrolled_in_scheme": true,
    "scheme_names": "PM-KISAN, Ayushman Bharat",
    "monthly_govt_benefit": 2000
  }'
```

### PATCH - Partial Update Government Scheme Eligibility Information
```bash
curl -X PATCH http://localhost:8000/api/finance/government-scheme/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_govt_benefit": 3000,
    "scheme_names": "PM-KISAN, Ayushman Bharat, PM Awas Yojana"
  }'
```

### PUT - Full Update Government Scheme Eligibility Information
```bash
curl -X PUT http://localhost:8000/api/finance/government-scheme/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "has_aadhaar": true,
    "has_pan": false,
    "enrolled_in_scheme": false,
    "scheme_names": null,
    "monthly_govt_benefit": null
  }'
```

---

## Complete Workflow Example

Here's a complete example of collecting all information step by step:

### Step 1: Get Authentication Token
```bash
# First, send OTP
curl -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'

# Then verify OTP and get token
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "otp_code": "123456"}'
```

### Step 2: Set Access Token Variable
```bash
# Extract access token from verify-otp response
export ACCESS_TOKEN="your_access_token_here"
```

### Step 3: Submit All Forms (Page by Page)

```bash
# Page 1: Personal Demographic
curl -X POST http://localhost:8000/api/finance/personal-demographic/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
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

# Page 2: Income Employment
curl -X POST http://localhost:8000/api/finance/income-employment/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_income_source": "Swiggy Delivery",
    "monthly_income_range": "20-30k",
    "working_days_per_month": 25,
    "income_variability": "Fluctuates",
    "mode_of_payment": "UPI"
  }'

# Page 3: Banking Financial Access
curl -X POST http://localhost:8000/api/finance/banking-access/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "has_bank_account": true,
    "type_of_account": "Savings",
    "has_upi_wallet": true,
    "avg_monthly_bank_balance": "5000-10000",
    "bank_txn_per_month": 15,
    "has_credit_card_bnpl": false
  }'

# Page 4: Credit Liabilities
curl -X POST http://localhost:8000/api/finance/credit-liabilities/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "existing_loans": true,
    "type_of_loan": "Personal Loan",
    "monthly_emi": 5000,
    "missed_payments_6m": false,
    "informal_borrowing": false
  }'

# Page 5: Savings Insurance
curl -X POST http://localhost:8000/api/finance/savings-insurance/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "regular_savings_habit": true,
    "savings_amount_per_month": "2000-5000",
    "has_insurance": "Health,Life",
    "type_of_insurance": "Private",
    "has_pension_pf": false
  }'

# Page 6: Expenses Obligations
curl -X POST http://localhost:8000/api/finance/expenses-obligations/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rent_per_month": 8000,
    "utilities_expense": 2000,
    "education_medical_expense": 3000,
    "avg_household_spend": 15000,
    "dependents_expense": 5000
  }'

# Page 7: Behavioral Psychometric
curl -X POST http://localhost:8000/api/finance/behavioral-psychometric/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "set_monthly_savings_goals": true,
    "track_expenses": true,
    "extra_income_behaviour": "Save",
    "payment_miss_frequency": "Never",
    "digital_comfort_level": 4
  }'

# Page 8: Government Scheme Eligibility
curl -X POST http://localhost:8000/api/finance/government-scheme/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "has_aadhaar": true,
    "has_pan": true,
    "enrolled_in_scheme": true,
    "scheme_names": "PM-KISAN, Ayushman Bharat",
    "monthly_govt_benefit": 2000
  }'

# Calculate UHFS Score (after submitting all data)
curl -X POST http://localhost:8000/api/finance/uhfs-score/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Response Format

### Success Response (200/201)
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2",
  ...
}
```

### Error Response (400/404)
```json
{
  "detail": "Error message here"
}
```

### Validation Error (400)
```json
{
  "field_name": ["Error message for this field"]
}
```

---

## 9. UHFS Score

### GET - Retrieve Current UHFS Score
```bash
curl -X GET http://localhost:8000/api/finance/uhfs-score/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Success Response (200):**
```json
{
  "id": 1,
  "score": 650,
  "last_updated": "2024-11-23T10:30:00Z"
}
```

### POST - Calculate and Update UHFS Score
```bash
curl -X POST http://localhost:8000/api/finance/uhfs-score/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Success Response (200):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "components": {
    "I": 0.65,
    "F": 0.72,
    "R": 0.58,
    "P": 0.45,
    "L": 0.60
  },
  "weights": {
    "I": 0.25,
    "F": 0.25,
    "R": 0.15,
    "P": 0.20,
    "L": 0.15
  },
  "composite": 0.625,
  "uhfs_score": 675,
  "domain_risk": {
    "income": "Medium",
    "financial_behavior": "Low",
    "reliability": "Low",
    "protection": "High",
    "literacy": "Medium"
  },
  "overall_risk": "Medium",
  "saved": true
}
```

**Note:** 
- The UHFS score is calculated based on data from all finance models
- Score range: 300-900 (300 = lowest, 900 = highest)
- Components:
  - **I (Income Stability)**: Based on income range, variability, working days
  - **F (Financial Behavior)**: Based on savings, payment behavior
  - **R (Reliability)**: Based on working patterns, digital comfort
  - **P (Protection)**: Based on insurance coverage, emergency funds
  - **L (Literacy)**: Based on financial literacy quiz scores
- Call POST endpoint after submitting financial data to recalculate the score

---

## Notes

1. **Authentication Required**: All endpoints require a valid authentication token obtained from `/api/auth/verify-otp/`

2. **POST vs PUT vs PATCH**:
   - **POST**: Creates new record or updates if exists (upsert behavior)
   - **PUT**: Full update (requires all fields)
   - **PATCH**: Partial update (only send fields you want to update)

3. **One Record Per User**: Each model has a OneToOne relationship with User, so each user can only have one record per model type.

4. **Optional Fields**: Most fields are optional (null=True, blank=True), so you can submit partial data and update later.

5. **Base URL**: Replace `http://localhost:8000` with your actual server URL in production.

