#!/bin/bash
# Quick API Reference - OTP Twilio Backend
# Base URL (change if needed)
BASE_URL="http://localhost:8000"

echo "=== OTP Twilio Backend API Quick Reference ==="
echo ""

# 1. Send OTP
echo "1. SEND OTP:"
echo "curl -X POST $BASE_URL/api/auth/send-otp/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"phone_number\": \"+1234567890\"}'"
echo ""

# 2. Verify OTP
echo "2. VERIFY OTP:"
echo "curl -X POST $BASE_URL/api/auth/verify-otp/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"phone_number\": \"+1234567890\", \"otp_code\": \"123456\"}'"
echo ""

# Example: Send OTP (ready to use)
echo "=== READY-TO-USE COMMANDS ==="
echo ""
echo "# Send OTP (replace +1234567890 with actual phone number)"
echo "curl -X POST $BASE_URL/api/auth/send-otp/ -H 'Content-Type: application/json' -d '{\"phone_number\": \"+1234567890\"}'"
echo ""
echo "# Verify OTP (replace values with actual OTP code received)"
echo "curl -X POST $BASE_URL/api/auth/verify-otp/ -H 'Content-Type: application/json' -d '{\"phone_number\": \"+1234567890\", \"otp_code\": \"123456\"}'"
echo ""
echo "# Test with Indian phone number"
echo "curl -X POST $BASE_URL/api/auth/send-otp/ -H 'Content-Type: application/json' -d '{\"phone_number\": \"+919876543210\"}'"
echo ""
echo "# Verify with pretty JSON output"
echo "curl -X POST $BASE_URL/api/auth/send-otp/ -H 'Content-Type: application/json' -d '{\"phone_number\": \"+1234567890\"}' | python -m json.tool"
echo ""
echo "=== NOTE ==="
echo "Make sure the Django server is running: python manage.py runserver"
echo "Update BASE_URL variable if using a different server/port"






