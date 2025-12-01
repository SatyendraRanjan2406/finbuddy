import re
from django.core.exceptions import ValidationError


def validate_indian_phone(value):
    """Validates a 10-digit Indian phone number"""
    if not re.match(r"^[6-9]\d{9}$", str(value)):
        raise ValidationError("Invalid Indian phone number.")
