# Facial Recognition Login - cURL Commands & Integration Guide

## Prerequisites

1. **AWS Credentials** (in `.env` or `settings.py`):
   ```bash
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_S3_REGION_NAME=ap-south-1
   ```

2. **Run Migration**:
   ```bash
   python manage.py migrate accounts
   ```

3. **Test Image**: Have a clear face photo ready (JPEG/PNG, max 15MB)

---

## Step-by-Step Integration

### Step 1: User Registration/Login via OTP (Existing Flow)

First, user must authenticate via OTP to get an access token:

```bash
# 1. Send OTP
curl -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890"
  }'

# Response:
# {
#   "detail": "OTP sent.",
#   "otp_id": 123
# }
```

```bash
# 2. Verify OTP and get access token
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "otp_code": "123456"
  }'

# Response:
# {
#   "detail": "OTP verified.",
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "user": {
#     "id": "uuid-here",
#     "phone_number": "+1234567890"
#   },
#   "onboarding": { ... }
# }
```

**Save the `access` token for Step 2.**

---

### Step 2: Enroll Face (One-Time Setup)

After OTP login, user enrolls their face:

```bash
curl -X POST http://localhost:8000/api/auth/face/enroll/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_FROM_STEP_1" \
  -F "face_image=@/path/to/face_photo.jpg" \
  -F "phone_number=+1234567890"

# Response (200 OK):
# {
#   "detail": "Face enrolled successfully. You can now login using facial recognition.",
#   "face_profile": {
#     "is_enrolled": true,
#     "enrolled_at": "2024-01-15T10:30:00Z"
#   }
# }
```

**Alternative (without phone_number):**
```bash
curl -X POST http://localhost:8000/api/auth/face/enroll/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_FROM_STEP_1" \
  -F "face_image=@/path/to/face_photo.jpg"
```

**Error Responses:**
- `400 Bad Request`: "No face detected in the image. Please ensure a clear face is visible."
- `400 Bad Request`: "Image size (20.5 MB) exceeds maximum allowed size (15 MB)."
- `400 Bad Request`: "Image format must be one of: JPEG, JPG, PNG"
- `401 Unauthorized`: "Authentication credentials were not provided."

---

### Step 3: Login with Face Recognition

Now user can login using just their face:

```bash
curl -X POST http://localhost:8000/api/auth/face/login/ \
  -F "face_image=@/path/to/face_photo.jpg" \
  -F "phone_number=+1234567890"

# Response (200 OK):
# {
#   "detail": "Face recognized successfully (similarity: 95.23%).",
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "user": {
#     "id": "uuid-here",
#     "phone_number": "+1234567890"
#   },
#   "onboarding": { ... },
#   "face_match": {
#     "similarity": 95.23,
#     "face_id": "rekognition-face-id-123"
#   }
# }
```

**Alternative (without phone_number):**
```bash
curl -X POST http://localhost:8000/api/auth/face/login/ \
  -F "face_image=@/path/to/face_photo.jpg"
```

**Error Responses:**
- `400 Bad Request`: "Invalid image format. Please provide a valid JPEG or PNG image."
- `401 Unauthorized`: "Face not recognized. Please ensure you have enrolled your face, or use OTP login."
- `404 Not Found`: "User account not found for this face."
- `404 Not Found`: "Face profile not found. Please enroll your face first."

---

## Complete Integration Flow (Example)

### Full User Journey:

```bash
# ============================================
# PHASE 1: Initial Registration (OTP)
# ============================================

# 1.1 Send OTP
curl -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'

# 1.2 Verify OTP (save access token)
ACCESS_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "otp_code": "123456"}' \
  | jq -r '.access')

echo "Access Token: $ACCESS_TOKEN"

# ============================================
# PHASE 2: Face Enrollment (One-Time)
# ============================================

# 2.1 Enroll face
curl -X POST http://localhost:8000/api/auth/face/enroll/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "face_image=@/Users/satyendra/Downloads/my_face.jpg" \
  -F "phone_number=+1234567890"

# ============================================
# PHASE 3: Future Logins (Face Recognition)
# ============================================

# 3.1 Login with face (no OTP needed!)
curl -X POST http://localhost:8000/api/auth/face/login/ \
  -F "face_image=@/Users/satyendra/Downloads/my_face.jpg" \
  -F "phone_number=+1234567890"

# OR continue using OTP (backward compatible):
curl -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

---

## Frontend Integration (JavaScript/React Example)

### 1. Face Enrollment Component

```javascript
// FaceEnrollment.js
import React, { useState } from 'react';

function FaceEnrollment({ accessToken }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleEnroll = async () => {
    if (!file) {
      setMessage('Please select an image');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('face_image', file);
    formData.append('phone_number', '+1234567890'); // Optional

    try {
      const response = await fetch('http://localhost:8000/api/auth/face/enroll/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
        body: formData,
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage('Face enrolled successfully! You can now login with facial recognition.');
      } else {
        setMessage(`Error: ${data.detail}`);
      }
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept="image/jpeg,image/jpg,image/png"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={handleEnroll} disabled={loading}>
        {loading ? 'Enrolling...' : 'Enroll Face'}
      </button>
      {message && <p>{message}</p>}
    </div>
  );
}
```

### 2. Face Login Component

```javascript
// FaceLogin.js
import React, { useState } from 'react';

function FaceLogin({ onLoginSuccess }) {
  const [file, setFile] = useState(null);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async () => {
    if (!file) {
      setError('Please select an image');
      return;
    }

    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('face_image', file);
    if (phoneNumber) {
      formData.append('phone_number', phoneNumber);
    }

    try {
      const response = await fetch('http://localhost:8000/api/auth/face/login/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (response.ok) {
        // Save tokens
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        onLoginSuccess(data);
      } else {
        setError(data.detail || 'Login failed');
      }
    } catch (error) {
      setError(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept="image/jpeg,image/jpg,image/png"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <input
        type="text"
        placeholder="Phone number (optional)"
        value={phoneNumber}
        onChange={(e) => setPhoneNumber(e.target.value)}
      />
      <button onClick={handleLogin} disabled={loading}>
        {loading ? 'Logging in...' : 'Login with Face'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}
```

### 3. Camera Capture (Web API)

```javascript
// FaceCapture.js - Using device camera
import React, { useRef, useState } from 'react';

function FaceCapture({ onCapture }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user' } // Front camera
      });
      videoRef.current.srcObject = mediaStream;
      setStream(mediaStream);
    } catch (error) {
      console.error('Error accessing camera:', error);
    }
  };

  const capturePhoto = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    canvas.toBlob((blob) => {
      const file = new File([blob], 'face.jpg', { type: 'image/jpeg' });
      onCapture(file);
    }, 'image/jpeg', 0.95);
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  return (
    <div>
      <video ref={videoRef} autoPlay playsInline style={{ width: '100%', maxWidth: '400px' }} />
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      <div>
        <button onClick={startCamera}>Start Camera</button>
        <button onClick={capturePhoto} disabled={!stream}>Capture</button>
        <button onClick={stopCamera}>Stop Camera</button>
      </div>
    </div>
  );
}
```

---

## Mobile App Integration (React Native Example)

```javascript
// FaceLoginScreen.js
import React, { useState } from 'react';
import { View, Button, Image, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

export default function FaceLoginScreen({ navigation }) {
  const [image, setImage] = useState(null);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  const loginWithFace = async () => {
    if (!image) {
      Alert.alert('Error', 'Please select or capture an image');
      return;
    }

    const formData = new FormData();
    formData.append('face_image', {
      uri: image,
      type: 'image/jpeg',
      name: 'face.jpg',
    });

    try {
      const response = await fetch('http://your-api.com/api/auth/face/login/', {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = await response.json();
      
      if (response.ok) {
        // Save tokens and navigate
        await AsyncStorage.setItem('access_token', data.access);
        navigation.navigate('Home');
      } else {
        Alert.alert('Login Failed', data.detail);
      }
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  return (
    <View>
      <Button title="Pick Image" onPress={pickImage} />
      <Button title="Take Photo" onPress={takePhoto} />
      {image && <Image source={{ uri: image }} style={{ width: 200, height: 200 }} />}
      <Button title="Login with Face" onPress={loginWithFace} />
    </View>
  );
}
```

---

## Testing Checklist

- [ ] AWS credentials configured
- [ ] Migration run: `python manage.py migrate accounts`
- [ ] Test OTP login (existing flow)
- [ ] Test face enrollment with valid image
- [ ] Test face enrollment with invalid image (no face detected)
- [ ] Test face login with enrolled face
- [ ] Test face login with wrong face (should fail)
- [ ] Test face login without enrollment (should suggest OTP)
- [ ] Verify backward compatibility (OTP still works)

---

## Troubleshooting

### "AWS Rekognition credentials not configured"
- Check `.env` file has `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- Verify credentials have Rekognition permissions

### "No face detected in the image"
- Ensure image has a clear, front-facing face
- Check image is not too dark/blurry
- Try a different photo

### "Face not recognized"
- User must enroll face first via `/api/auth/face/enroll/`
- Ensure using the same face that was enrolled
- Check similarity threshold (default 80%)

### "Image is too large"
- Maximum size: 15MB
- Compress image before upload
- Use JPEG format for smaller file size

---

## API Summary

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/auth/face/enroll/` | POST | Yes (Bearer) | Enroll face for recognition |
| `/api/auth/face/login/` | POST | No | Login using face recognition |
| `/api/auth/send-otp/` | POST | No | Send OTP (backward compatible) |
| `/api/auth/verify-otp/` | POST | No | Verify OTP (backward compatible) |

