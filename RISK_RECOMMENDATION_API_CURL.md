# Risk Recommendation API - cURL Commands

## API Endpoint

**POST** `/api/finance/risk-recommendation/`

## Setup

### 1. Run Migration
```bash
python manage.py migrate finance
```

### 2. Populate Risk Recommendation Data
```bash
# Preview (dry run)
python manage.py populate_risk_recommendations --dry-run

# Actually populate
python manage.py populate_risk_recommendations

# Clear and repopulate
python manage.py populate_risk_recommendations --clear
```

---

## cURL Examples

### Example 1: Income Stability - High Risk

```bash
curl -X POST http://localhost:8000/api/finance/risk-recommendation/ \
  -H "Content-Type: application/json" \
  -d '{
    "risk": "Income Stability",
    "risk_level": "High"
  }'
```

**Response:**
```json
{
  "id": 1,
  "risk_category": "Income Stability",
  "risk_trigger": "Income volatility > 40% or <15 days active/month",
  "risk_level": "🔴 High",
  "recommended_instruments": [
    "PMMY (Mudra Loan)",
    "PM SVANidhi",
    "Post Office RD",
    "PMJDY",
    "PDS/ONORC"
  ],
  "behavioral_tag": "Manage Income Volatility / Emergency Corpus",
  "intro_section": "Your income is fluctuating right now. Let's help you build a safety cushion so slow weeks don't create stress. These options can stabilise your income and help you handle lean periods better."
}
```

---

### Example 2: Income Stability - Medium Risk

```bash
curl -X POST http://localhost:8000/api/finance/risk-recommendation/ \
  -H "Content-Type: application/json" \
  -d '{
    "risk": "Income Stability",
    "risk_level": "Medium"
  }'
```

**Response:**
```json
{
  "id": 2,
  "risk_category": "Income Stability",
  "risk_trigger": "Low consistent income (<₹10k/month)",
  "risk_level": "🟠 Medium",
  "recommended_instruments": [
    "PMEGP",
    "PMJDY",
    "RD",
    "PDS"
  ],
  "behavioral_tag": "Growth Funding / Stability",
  "intro_section": "Your income is steady but on the lower side. These government-backed plans can support you with subsidised loans and short-term savings to increase your income and stability."
}
```

---

### Example 3: Income Stability - Low Risk

```bash
curl -X POST http://localhost:8000/api/finance/risk-recommendation/ \
  -H "Content-Type: application/json" \
  -d '{
    "risk": "Income Stability",
    "risk_level": "Low"
  }'
```

---

### Example 4: Financial Behavior - High Risk

```bash
curl -X POST http://localhost:8000/api/finance/risk-recommendation/ \
  -H "Content-Type: application/json" \
  -d '{
    "risk": "Financial Behavior",
    "risk_level": "High"
  }'
```

**Note:** This may return multiple results if there are multiple high-risk triggers for Financial Behavior.

---

### Example 5: Reliability & Tenure - Medium Risk

```bash
curl -X POST http://localhost:8000/api/finance/risk-recommendation/ \
  -H "Content-Type: application/json" \
  -d '{
    "risk": "Reliability & Tenure",
    "risk_level": "Medium"
  }'
```

---

### Example 6: Protection Readiness - High Risk

```bash
curl -X POST http://localhost:8000/api/finance/risk-recommendation/ \
  -H "Content-Type: application/json" \
  -d '{
    "risk": "Protection Readiness",
    "risk_level": "High"
  }'
```

---

### Example 7: Using Emoji Risk Levels

```bash
curl -X POST http://localhost:8000/api/finance/risk-recommendation/ \
  -H "Content-Type: application/json" \
  -d '{
    "risk": "Income Stability",
    "risk_level": "🔴 High"
  }'
```

---

## All Available Risk Categories

1. **Income Stability**
   - Risk Levels: High, Medium, Low

2. **Financial Behavior**
   - Risk Levels: High, Medium, Low

3. **Reliability & Tenure**
   - Risk Levels: High, Medium, Low

4. **Protection Readiness**
   - Risk Levels: High, Medium, Low

---

## Request Format

```json
{
  "risk": "Income Stability" | "Financial Behavior" | "Reliability & Tenure" | "Protection Readiness",
  "risk_level": "High" | "Medium" | "Low" | "🔴 High" | "🟠 Medium" | "🟢 Low"
}
```

---

## Response Format

### Single Result:
```json
{
  "id": 1,
  "risk_category": "Income Stability",
  "risk_trigger": "Income volatility > 40% or <15 days active/month",
  "risk_level": "🔴 High",
  "recommended_instruments": ["PMMY (Mudra Loan)", "PM SVANidhi", ...],
  "behavioral_tag": "Manage Income Volatility / Emergency Corpus",
  "intro_section": "Your income is fluctuating right now..."
}
```

### Multiple Results:
```json
{
  "count": 2,
  "results": [
    { ... },
    { ... }
  ]
}
```

### Error Response (404):
```json
{
  "error": "No recommendations found",
  "message": "No recommendations found for risk category 'Income Stability' and risk level 'High'"
}
```

---

## Error Responses

### 400 Bad Request (Invalid Input):
```json
{
  "risk": ["This field is required."],
  "risk_level": ["Invalid choice."]
}
```

### 404 Not Found:
```json
{
  "error": "No recommendations found",
  "message": "No recommendations found for risk category 'Income Stability' and risk level 'High'"
}
```

---

## Quick Test Script

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/finance/risk-recommendation"

# Test all risk categories and levels
for risk in "Income Stability" "Financial Behavior" "Reliability & Tenure" "Protection Readiness"; do
  for level in "High" "Medium" "Low"; do
    echo "Testing: $risk - $level"
    curl -X POST "$BASE_URL/" \
      -H "Content-Type: application/json" \
      -d "{\"risk\": \"$risk\", \"risk_level\": \"$level\"}" \
      | jq '.'
    echo "---"
  done
done
```

---

## Integration Example (JavaScript/React)

```javascript
async function getRiskRecommendation(risk, riskLevel) {
  try {
    const response = await fetch('http://localhost:8000/api/finance/risk-recommendation/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        risk: risk,
        risk_level: riskLevel,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to get recommendations');
    }

    const data = await response.json();
    
    // Handle single result or multiple results
    if (data.results) {
      return data.results; // Multiple results
    } else {
      return [data]; // Single result as array
    }
  } catch (error) {
    console.error('Error fetching risk recommendations:', error);
    throw error;
  }
}

// Usage
const recommendations = await getRiskRecommendation('Income Stability', 'High');
console.log(recommendations);
```

---

## Notes

- **No Authentication Required**: This endpoint is publicly accessible (AllowAny permission)
- **Case Insensitive**: Risk levels can be provided with or without emoji
- **Multiple Results**: If multiple recommendations match, all are returned
- **Ordered Results**: Results are ordered by the `order` field within each risk category/level

