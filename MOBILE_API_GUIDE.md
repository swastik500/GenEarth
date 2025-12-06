# EcoMitra Mobile API Documentation

Complete REST API documentation for building mobile applications (Android/iOS/React Native/Flutter)

## Base URL

```
http://your-server-url:8000/api/mobile
```

## API Features

- ✅ Multi-language chatbot (22 languages)
- ✅ AI-powered waste image classification
- ✅ Gamification system (profiles, badges, leaderboard)
- ✅ NGO directory
- ✅ Government schemes
- ✅ Marketplace for recycled items
- ✅ Carbon footprint calculator

---

## 🔐 Authentication

### Login/Register

**Endpoint:** `POST /api/mobile/auth/login`

**Request:**

```json
{
  "username": "user123",
  "device_id": "optional_device_identifier"
}
```

**Response:**

```json
{
  "success": true,
  "user": {
    "username": "user123",
    "ecoscore": 150,
    "badges": ["waste_warrior"],
    "current_streak": 5
  },
  "token": "eco_user123_device123",
  "message": "Login successful"
}
```

---

## 💬 Chat API

### Send Message to Chatbot

**Endpoint:** `POST /api/mobile/chat`

**Request:**

```json
{
  "message": "How do I recycle plastic bottles?",
  "language": "en",
  "user_id": "user123",
  "session_id": "optional_session_id"
}
```

**Supported Languages:**

- `en` - English
- `hi` - Hindi
- `mr` - Marathi
- `bn` - Bengali
- `ta` - Tamil
- `te` - Telugu
- `gu` - Gujarati
- `kn` - Kannada
- `ml` - Malayalam
- `pa` - Punjabi
- `or` - Odia
- `as` - Assamese
- `ur` - Urdu
- `es` - Spanish
- `fr` - French
- `de` - German
- `pt` - Portuguese
- `zh` - Chinese
- `ja` - Japanese
- `ko` - Korean
- `ar` - Arabic
- `ru` - Russian

**Response:**

```json
{
  "response": "To recycle plastic bottles: 1. Rinse them clean, 2. Remove caps and labels...",
  "timestamp": "2025-12-06T10:30:00",
  "language": "en"
}
```

### Get Chat History

**Endpoint:** `GET /api/mobile/chat/history/{user_id}?limit=50`

**Response:**

```json
{
  "user_id": "user123",
  "history": [],
  "message": "Chat history storage not yet implemented"
}
```

---

## 📸 Image Analysis API

### Analyze Waste Image (Base64)

**Endpoint:** `POST /api/mobile/vision/analyze`

**Request:**

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "user_id": "user123"
}
```

**Response:**

```json
{
  "classification": "Plastic Bottle",
  "category": "recyclable",
  "disposal_method": "Clean and place in recycling bin",
  "confidence": 0.95,
  "environmental_impact": "Can take 450 years to decompose",
  "recycling_tips": [
    "Remove cap and label",
    "Rinse clean",
    "Flatten to save space"
  ]
}
```

### Analyze Waste Image (File Upload)

**Endpoint:** `POST /api/mobile/vision/analyze-multipart`

**Form Data:**

- `file`: Image file (JPEG/PNG)
- `user_id`: User identifier (optional)

**Example (Flutter):**

```dart
var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/vision/analyze-multipart'));
request.files.add(await http.MultipartFile.fromPath('file', imagePath));
request.fields['user_id'] = 'user123';
var response = await request.send();
```

---

## 🏆 Gamification API

### Get User Profile

**Endpoint:** `POST /api/mobile/profile`

**Request:**

```json
{
  "username": "user123"
}
```

**Response:**

```json
{
  "username": "user123",
  "ecoscore": 250,
  "current_streak": 7,
  "longest_streak": 15,
  "images_analyzed": 45,
  "chat_questions": 120,
  "ngos_viewed": 8,
  "schemes_viewed": 12,
  "badges": ["waste_warrior", "energy_saver", "streak_starter"],
  "badge_count": 3
}
```

### Track Activity

**Endpoint:** `POST /api/mobile/activity/track`

**Activity Types:**

- `chat_message` - User sends chat message
- `image_analysis` - User analyzes waste image
- `ngo_view` - User views NGO profile
- `scheme_view` - User views government scheme
- `quiz_complete` - User completes quiz
- `marketplace_post` - User posts marketplace item

**Request:**

```json
{
  "username": "user123",
  "activity_type": "image_analysis",
  "metadata": {
    "category": "plastic"
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "Activity tracked",
  "result": {
    "points_earned": 10,
    "new_badge": null
  }
}
```

### Get Leaderboard

**Endpoint:** `GET /api/mobile/leaderboard?limit=10`

**Response:**

```json
{
  "leaderboard": [
    {
      "username": "eco_hero",
      "ecoscore": 1500,
      "current_streak": 30,
      "badge_count": 6
    },
    {
      "username": "user123",
      "ecoscore": 250,
      "current_streak": 7,
      "badge_count": 3
    }
  ]
}
```

### Submit Quiz Answer

**Endpoint:** `POST /api/mobile/quiz/answer`

**Request:**

```json
{
  "username": "user123",
  "question_id": 1,
  "answer": "biodegradable"
}
```

**Response:**

```json
{
  "correct": true,
  "points_earned": 20,
  "explanation": "Correct! Food waste is biodegradable..."
}
```

---

## 🌿 NGO Directory API

### Get NGO List

**Endpoint:** `GET /api/mobile/ngos?category=waste_management&location=Mumbai`

**Query Parameters:**

- `category` (optional): Filter by category
- `location` (optional): Filter by location

**Categories:**

- `waste_management`
- `water_conservation`
- `tree_plantation`
- `renewable_energy`
- `wildlife_protection`
- `education`

**Response:**

```json
{
  "count": 5,
  "ngos": [
    {
      "name": "Green Earth Initiative",
      "category": "waste_management",
      "location": "Mumbai, Maharashtra",
      "description": "Community-driven waste management...",
      "contact": "contact@greenearth.org",
      "website": "https://greenearth.org"
    }
  ]
}
```

---

## 🏛️ Government Schemes API

### Get Government Schemes

**Endpoint:** `GET /api/mobile/government/schemes?category=renewable_energy&state=Maharashtra`

**Query Parameters:**

- `category` (optional): Filter by category
- `state` (optional): Filter by state

**Response:**

```json
{
  "count": 3,
  "schemes": [
    {
      "name": "Pradhan Mantri Solar Panel Yojana",
      "category": "renewable_energy",
      "states": "All India",
      "description": "Subsidy for solar panel installation...",
      "eligibility": "Residential and commercial properties",
      "benefits": "40% subsidy on solar panel installation"
    }
  ]
}
```

---

## 🛒 Marketplace API

### Create Marketplace Item

**Endpoint:** `POST /api/mobile/marketplace/items`

**Request:**

```json
{
  "title": "Used Cardboard Boxes",
  "category": "cardboard",
  "description": "50 large moving boxes in good condition",
  "contact": "user123@email.com",
  "user_id": "user123"
}
```

**Categories:**

- `cardboard`, `scrap`, `clothing`, `electronics`
- `plastic`, `paper`, `metal`, `glass`

**Response:**

```json
{
  "success": true,
  "item_id": 42,
  "message": "Item posted successfully"
}
```

### Get Marketplace Items

**Endpoint:** `GET /api/mobile/marketplace/items?category=electronics&search=laptop&limit=20`

**Query Parameters:**

- `category` (optional): Filter by category
- `search` (optional): Search in titles
- `limit` (optional): Max results (default: 20)

**Response:**

```json
{
  "count": 3,
  "items": [
    {
      "id": 42,
      "title": "Old Laptop for Parts",
      "category": "electronics",
      "description": "Working screen, dead battery",
      "contact": "seller@email.com",
      "posted_by": "user456",
      "created_at": "2025-12-06T10:00:00"
    }
  ]
}
```

---

## 🌍 Carbon Footprint API

### Calculate Carbon Footprint

**Endpoint:** `POST /api/mobile/carbon/calculate`

**Request:**

```json
{
  "electricity": 300,
  "gas": 50,
  "fuel": 100,
  "waste": 80,
  "travel": 500
}
```

**Units:**

- `electricity`: kWh per month
- `gas`: therms per month
- `fuel`: liters per month
- `waste`: kg per month
- `travel`: km per month

**Response:**

```json
{
  "total_carbon_kg": 523.6,
  "breakdown": {
    "electricity": 276.0,
    "gas": 265.0,
    "fuel": 231.0,
    "waste": 45.6,
    "travel": 70.0
  },
  "recommendations": [
    "Switch to LED bulbs and energy-efficient appliances",
    "Consider carpooling or using public transport",
    "Reduce waste by composting and recycling"
  ],
  "rating": "Moderate"
}
```

---

## ⚙️ Configuration API

### Get App Configuration

**Endpoint:** `GET /api/mobile/config`

**Response:**

```json
{
  "languages": [
    { "code": "en", "name": "English" },
    { "code": "hi", "name": "हिंदी (Hindi)" }
  ],
  "marketplace_categories": ["cardboard", "scrap", "clothing", "electronics"],
  "ngo_categories": ["waste_management", "water_conservation"],
  "waste_categories": ["biodegradable", "recyclable", "hazardous"],
  "api_version": "1.0.0",
  "features": ["chat", "image_analysis", "gamification", "marketplace"]
}
```

---

## 📱 Example Usage

### React Native Example

```javascript
// Chat Request
const sendMessage = async (message, language = "en") => {
  const response = await fetch("http://localhost:8000/api/mobile/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,
      language: language,
      user_id: "user123",
    }),
  });
  const data = await response.json();
  return data.response;
};

// Image Analysis
const analyzeImage = async (base64Image) => {
  const response = await fetch(
    "http://localhost:8000/api/mobile/vision/analyze",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        image_base64: base64Image,
        user_id: "user123",
      }),
    }
  );
  return await response.json();
};
```

### Flutter Example

```dart
// Chat Request
Future<String> sendMessage(String message, String language) async {
  final response = await http.post(
    Uri.parse('http://localhost:8000/api/mobile/chat'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'message': message,
      'language': language,
      'user_id': 'user123'
    }),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return data['response'];
  }
  throw Exception('Failed to send message');
}

// Get User Profile
Future<Map<String, dynamic>> getUserProfile(String username) async {
  final response = await http.post(
    Uri.parse('http://localhost:8000/api/mobile/profile'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'username': username}),
  );

  return jsonDecode(response.body);
}
```

### Android (Kotlin) Example

```kotlin
// Using Retrofit
interface EcoMitraAPI {
    @POST("/api/mobile/chat")
    suspend fun sendMessage(@Body request: ChatRequest): ChatResponse

    @Multipart
    @POST("/api/mobile/vision/analyze-multipart")
    suspend fun analyzeImage(
        @Part file: MultipartBody.Part,
        @Part("user_id") userId: RequestBody
    ): ImageAnalysisResponse

    @POST("/api/mobile/profile")
    suspend fun getProfile(@Body request: ProfileRequest): UserProfile
}

// Usage
val response = api.sendMessage(
    ChatRequest(
        message = "How to recycle?",
        language = "en",
        userId = "user123"
    )
)
```

---

## 🔧 Error Handling

All endpoints return standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource doesn't exist)
- `500` - Server Error

**Error Response Format:**

```json
{
  "detail": "Error description here"
}
```

---

## 🚀 Testing the API

### Using cURL

```bash
# Chat
curl -X POST "http://localhost:8000/api/mobile/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How to recycle plastic?", "language": "en", "user_id": "user123"}'

# Get Profile
curl -X POST "http://localhost:8000/api/mobile/profile" \
  -H "Content-Type: application/json" \
  -d '{"username": "user123"}'

# Get NGOs
curl "http://localhost:8000/api/mobile/ngos?category=waste_management"
```

### Using Postman

1. Import the endpoints from the documentation
2. Set base URL: `http://localhost:8000`
3. Test each endpoint with sample data

---

## 📊 Rate Limits

Currently no rate limits implemented. Consider adding rate limiting for production deployment.

## 🔒 Security Notes

- Current authentication is basic (token-based)
- Consider implementing JWT tokens for production
- Add HTTPS in production
- Validate and sanitize all inputs
- Store sensitive data securely

---

## 📞 Support

For issues or questions:

- GitHub: swastik500/GenEarth
- API Version: 1.0.0
- Last Updated: December 2025
