# GPT-5 Multimodal Chat App

A chat app built using GPT-5 model.

- Chat with GPT-5 using text-only messages
- Upload images and ask questions about them
- Use preset actions for common image analysis tasks
- Maintain conversation history

## Features

✨ **Text Chat**: Simple text-based conversations with GPT-5

🖼️ **Image Analysis**: Upload images and get AI-powered analysis

🎯 **Preset Actions**: Quick actions like "Analyze", "Summarize", "Extract Text"

💬 **Conversation History**: Maintain context across multiple messages

🔄 **Multiple Input Methods**: Support for file uploads and base64 encoded images

## Quick Start

### 1. Environment Setup

Copy the example environment file and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Install Dependencies

This project uses `uv` for dependency management. If you haven't already:

```bash
uv sync
```

### 3. Run the Server

```bash
python3 main.py
```

The API will be available at `http://localhost:8000`

### 4. View API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Frontend Setup (React)

The frontend is a React application with TypeScript that provides a modern chat interface for the GPT-5 multimodal API.

### Prerequisites

- Node.js 16+ and npm (or yarn)
- Backend server running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Running the Frontend

1. Start the development server:
   ```bash
   npm start
   ```

2. The React app will start on `http://localhost:3000`

3. Open your browser and navigate to `http://localhost:3000`

### Frontend Features

- **Multimodal Chat Interface**: Text and image input support
- **Drag & Drop Image Upload**: Easy image uploading with preview
- **Preset Actions**: Quick analysis buttons after image upload (Analyze, Summarize, Describe, Extract Text)
- **Default Questions**: 4 sample questions to get started quickly
- **Markdown Rendering**: AI responses rendered with syntax highlighting
- **Copy to Clipboard**: Copy AI responses with one click
- **Responsive Design**: Works on desktop and mobile devices
- **Loading Animation**: Bouncing dots while waiting for AI responses
- **Message Avatars**: Visual distinction between user and AI messages

### Frontend Dependencies

- **React 18**: Modern React with TypeScript
- **Axios**: HTTP client for API requests
- **React Dropzone**: Drag and drop file uploads
- **React Markdown**: Markdown rendering with syntax highlighting
- **Lucide React**: Beautiful icons
- **Highlight.js**: Code syntax highlighting

### Usage

1. **Text Chat**: Type a message and press Enter or click Send
2. **Image Upload**: Drag and drop an image or click the upload area
3. **Preset Actions**: After uploading an image, use quick action buttons
4. **Custom Image Questions**: Upload an image and type a custom question
5. **Copy Responses**: Click the copy button on any AI responses

## API Endpoints

### 🏠 Root Endpoint

```http
GET /
```

Returns API information and available endpoints.

### 💬 Text Chat

```http
POST /chat/text
```

Chat with GPT-5 using text only.

**Request Body:**
```json
{
  "message": "Hello! How are you?",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "Hello! I'm doing well, thank you for asking...",
  "conversation_history": [
    {"role": "user", "content": "Hello! How are you?"},
    {"role": "assistant", "content": "Hello! I'm doing well..."}
  ]
}
```

### 🖼️ Image Upload Chat

```http
POST /chat/image-upload
```

Upload an image file and chat about it.

**Form Data:**
- `image`: Image file (required)
- `prompt`: Custom prompt (optional)
- `preset_action`: Preset action key (optional)

**Response:**
```json
{
  "response": "I can see this is an image of...",
  "analysis_type": "custom"
}
```

### 🔗 Base64 Image Chat

```http
POST /chat/image-base64
```

Send a base64 encoded image for analysis.

**Request Body:**
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB...",
  "prompt": "What do you see in this image?",
  "preset_action": "analyze"
}
```

### 🎯 Preset Actions

```http
GET /presets
```

Get available preset actions for image analysis.

**Available Presets:**
- `analyze`: Detailed analysis of the image
- `summarize`: Quick summary of image content
- `describe`: Detailed description for accessibility
- `extract_text`: Extract any text from the image
- `identify_objects`: List objects and items in the image
- `explain_context`: Explain the setting and context

### 🔄 Multimodal Chat

```http
POST /chat/multimodal
```

Combined endpoint for both text and image input with conversation history.

**Form Data:**
- `message`: Text message (required)
- `image`: Image file (optional)
- `conversation_history`: JSON string of previous messages (optional)

## Usage Examples

### Python Example

```python
import requests
import base64

# Text chat
response = requests.post('http://localhost:8000/chat/text', json={
    'message': 'Tell me a joke',
    'conversation_history': []
})
print(response.json()['response'])

# Image analysis
with open('image.jpg', 'rb') as f:
    files = {'image': f}
    data = {'prompt': 'What is in this image?'}
    response = requests.post('http://localhost:8000/chat/image-upload', 
                           files=files, data=data)
print(response.json()['response'])
```

### JavaScript/React Example

```javascript
// Text chat
const textChat = async (message) => {
  const response = await fetch('http://localhost:8000/chat/text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      conversation_history: []
    })
  });
  return await response.json();
};

// Image upload
const imageChat = async (imageFile, prompt) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('prompt', prompt);
  
  const response = await fetch('http://localhost:8000/chat/image-upload', {
    method: 'POST',
    body: formData
  });
  return await response.json();
};
```

### cURL Examples

```bash
# Text chat
curl -X POST "http://localhost:8000/chat/text" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "conversation_history": []
  }'

# Image upload
curl -X POST "http://localhost:8000/chat/image-upload" \
  -F "image=@/path/to/your/image.jpg" \
  -F "prompt=What do you see in this image?"

# Get presets
curl "http://localhost:8000/presets"
```

## Testing

Run the test script to verify all endpoints:

```bash
python3 test_api.py
```

This will test:
- Root endpoint
- Presets endpoint
- Text chat
- Image analysis
- Preset actions

## Project Structure

```
gpt-5-demo/
├── main.py              # FastAPI backend application
├── test_api.py          # Backend API test script
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Environment variables template
├── pyproject.toml       # Backend dependencies
├── README.md            # This file
├── uv.lock             # Backend dependency lock file
└── frontend/            # React frontend application
    ├── public/          # Static assets
    ├── src/             # React source code
    │   ├── App.tsx      # Main React component
    │   ├── App.css      # Main styles
    │   ├── markdown.css # Markdown rendering styles
    │   └── index.tsx    # React entry point
    ├── package.json     # Frontend dependencies
    └── package-lock.json # Frontend dependency lock
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **OpenAI**: Official OpenAI Python client
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation using Python type hints
- **python-dotenv**: Load environment variables from .env file
- **Requests**: HTTP library for testing

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (optional, defaults to gpt-4o)
- `HOST`: Server host (optional, defaults to 0.0.0.0)
- `PORT`: Server port (optional, defaults to 8000)

### Model Configuration

The API currently uses `gpt-4o` for both text and vision capabilities. When GPT-5 becomes available, you can update the model name in the code.

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input (e.g., non-image file)
- **500 Internal Server Error**: API errors or processing failures

All errors return JSON with a `detail` field explaining the issue.

## CORS Support

The API includes CORS middleware configured to allow all origins during development. For production, update the `allow_origins` list in `main.py` to include only your frontend domains.

## Next Steps

1. **Frontend Development**: Build a React frontend to interact with these APIs
2. **Authentication**: Add user authentication and API key management
3. **Rate Limiting**: Implement rate limiting for production use
4. **Caching**: Add response caching for frequently requested analyses
5. **File Storage**: Implement proper file storage for uploaded images
6. **Monitoring**: Add logging and monitoring for production deployment

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the [MIT License](LICENSE).
