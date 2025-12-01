from rest_framework.exceptions import APIException


class BusinessException(APIException):
    status_code = 400
    default_detail = "Business rule violated."


class OTPException(APIException):
    status_code = 400
    default_detail = "Invalid OTP."
