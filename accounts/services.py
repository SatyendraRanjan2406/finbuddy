import random
import logging
from django.conf import settings
from twilio.rest import Client
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def generate_otp(length=6):
    """Generate a random OTP code."""
    return str(random.randint(10 ** (length - 1), 10 ** length - 1))


def send_otp_via_twilio(phone_number, otp_code):
    """
    Send OTP via Twilio SMS.
    Returns (is_sent: bool, message: str)
    """
    try:
        account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
        auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
        # Try TWILIO_PHONE_NUMBER first, fallback to DEFAULT_FROM_PHONE_NUMBER
        from_number = getattr(settings, "TWILIO_PHONE_NUMBER", None) or getattr(settings, "DEFAULT_FROM_PHONE_NUMBER", None)
        messaging_service_sid = getattr(settings, "TWILIO_MESSAGING_SERVICE_SID", None)

        # Check if we have at least account_sid and auth_token
        if not account_sid or not auth_token:
            return False, "Twilio credentials not configured. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env"
        
        # If no phone number or messaging service, provide helpful error
        if not from_number and not messaging_service_sid:
            return False, "Twilio phone number not configured. Please set TWILIO_PHONE_NUMBER or TWILIO_MESSAGING_SERVICE_SID in .env"

        client = Client(account_sid, auth_token)
        
        # Use messaging service if available, otherwise use phone number
        message_params = {
            "body": f"Your FinMate OTP code is: {otp_code}. Valid for {getattr(settings, 'OTP_EXPIRATION_MINUTES', 5)} minutes.",
            "to": phone_number,
        }
        
        if messaging_service_sid:
            message_params["messaging_service_sid"] = messaging_service_sid
        elif from_number:
            message_params["from_"] = from_number
        else:
            return False, "Twilio phone number or messaging service not configured."
        
        message = client.messages.create(**message_params)
        return True, "OTP sent successfully."
    except Exception as e:
        logger.error(f"Error sending OTP via Twilio: {e}")
        return False, str(e)


# AWS Rekognition services
def get_rekognition_client():
    """Get AWS Rekognition client."""
    aws_region = getattr(settings, "AWS_S3_REGION_NAME", "ap-south-1")
    aws_access_key = getattr(settings, "AWS_ACCESS_KEY_ID", None)
    aws_secret_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", None)
    
    if not aws_access_key or not aws_secret_key:
        return None
    
    return boto3.client(
        "rekognition",
        region_name=aws_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
    )


def ensure_face_collection(collection_id="finmate-users"):
    """
    Ensure a Rekognition collection exists. Create if it doesn't.
    Returns (success: bool, message: str, collection_id: str)
    """
    rekognition = get_rekognition_client()
    if not rekognition:
        return False, "AWS Rekognition credentials not configured.", None
    
    try:
        # Try to describe the collection (check if it exists)
        rekognition.describe_collection(CollectionId=collection_id)
        return True, f"Collection '{collection_id}' already exists.", collection_id
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "ResourceNotFoundException":
            # Collection doesn't exist, create it
            try:
                rekognition.create_collection(CollectionId=collection_id)
                return True, f"Collection '{collection_id}' created successfully.", collection_id
            except Exception as create_error:
                logger.error(f"Error creating Rekognition collection: {create_error}")
                return False, f"Failed to create collection: {str(create_error)}", None
        else:
            logger.error(f"Error describing Rekognition collection: {e}")
            return False, f"AWS Rekognition error: {str(e)}", None
    except Exception as e:
        logger.error(f"Unexpected error with Rekognition: {e}")
        return False, f"Unexpected error: {str(e)}", None


def index_face_in_rekognition(image_bytes, collection_id="finmate-users", external_image_id=None):
    """
    Index a face in AWS Rekognition collection.
    
    Args:
        image_bytes: Bytes of the image (JPEG/PNG)
        collection_id: Rekognition collection ID
        external_image_id: Optional external ID (e.g., user UUID)
    
    Returns:
        (success: bool, face_id: str or None, message: str)
    """
    rekognition = get_rekognition_client()
    if not rekognition:
        return False, None, "AWS Rekognition credentials not configured."
    
    # Ensure collection exists
    success, msg, _ = ensure_face_collection(collection_id)
    if not success:
        return False, None, msg
    
    try:
        response = rekognition.index_faces(
            CollectionId=collection_id,
            Image={"Bytes": image_bytes},
            ExternalImageId=external_image_id,
            MaxFaces=1,  # Only index one face per image
            QualityFilter="AUTO",
            DetectionAttributes=["DEFAULT"],
        )
        
        if response.get("FaceRecords"):
            face_record = response["FaceRecords"][0]
            face_id = face_record["Face"]["FaceId"]
            return True, face_id, "Face indexed successfully."
        else:
            return False, None, "No face detected in the image. Please ensure a clear face is visible."
    
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "InvalidParameterException":
            return False, None, "Invalid image format. Please provide a valid JPEG or PNG image."
        elif error_code == "ImageTooLargeException":
            return False, None, "Image is too large. Maximum size is 15MB."
        else:
            logger.error(f"AWS Rekognition error: {e}")
            return False, None, f"AWS Rekognition error: {str(e)}"
    except Exception as e:
        logger.error(f"Error indexing face: {e}")
        return False, None, f"Error indexing face: {str(e)}"


def search_face_in_rekognition(image_bytes, collection_id="finmate-users", max_faces=1, face_match_threshold=80):
    """
    Search for a face in AWS Rekognition collection.
    
    Args:
        image_bytes: Bytes of the image (JPEG/PNG)
        collection_id: Rekognition collection ID
        max_faces: Maximum number of faces to return
        face_match_threshold: Minimum confidence (0-100) for a match
    
    Returns:
        (success: bool, matches: list of dicts with face_id and similarity, message: str)
    """
    rekognition = get_rekognition_client()
    if not rekognition:
        return False, [], "AWS Rekognition credentials not configured."
    
    try:
        response = rekognition.search_faces_by_image(
            CollectionId=collection_id,
            Image={"Bytes": image_bytes},
            MaxFaces=max_faces,
            FaceMatchThreshold=face_match_threshold,
        )
        
        matches = []
        for match in response.get("FaceMatches", []):
            matches.append({
                "face_id": match["Face"]["FaceId"],
                "similarity": match["Similarity"],
                "external_image_id": match["Face"].get("ExternalImageId"),
            })
        
        if matches:
            return True, matches, "Face match found."
        else:
            return True, [], "No matching face found in the collection."
    
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "InvalidParameterException":
            return False, [], "Invalid image format. Please provide a valid JPEG or PNG image."
        elif error_code == "ImageTooLargeException":
            return False, [], "Image is too large. Maximum size is 15MB."
        else:
            logger.error(f"AWS Rekognition error: {e}")
            return False, [], f"AWS Rekognition error: {str(e)}"
    except Exception as e:
        logger.error(f"Error searching face: {e}")
        return False, [], f"Error searching face: {str(e)}"


def delete_face_from_rekognition(face_id, collection_id="finmate-users"):
    """
    Delete a face from AWS Rekognition collection.
    
    Returns:
        (success: bool, message: str)
    """
    rekognition = get_rekognition_client()
    if not rekognition:
        return False, "AWS Rekognition credentials not configured."
    
    try:
        rekognition.delete_faces(
            CollectionId=collection_id,
            FaceIds=[face_id],
        )
        return True, "Face deleted successfully."
    except ClientError as e:
        logger.error(f"Error deleting face from Rekognition: {e}")
        return False, f"AWS Rekognition error: {str(e)}"
    except Exception as e:
        logger.error(f"Error deleting face: {e}")
        return False, f"Error deleting face: {str(e)}"
