import os
import base64
import io
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI app
app = FastAPI(
    title="GPT-5 Multimodal Chat API",
    description="A FastAPI backend for GPT-5 multimodal chat with image and text support",
    version="1.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TextChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []

class TextChatResponse(BaseModel):
    response: str
    conversation_history: List[dict]

class ImageAnalysisRequest(BaseModel):
    image_base64: str
    prompt: Optional[str] = "Analyze this image"
    preset_action: Optional[str] = None  # "analyze", "summarize", "describe", etc.

class ImageAnalysisResponse(BaseModel):
    response: str
    analysis_type: str

# Helper functions
def encode_image_to_base64(image_file: UploadFile) -> str:
    """Convert uploaded image to base64 string"""
    try:
        image_data = image_file.file.read()
        base64_string = base64.b64encode(image_data).decode('utf-8')
        return base64_string
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

def get_preset_prompt(action: str) -> str:
    """Get predefined prompts for preset actions"""
    presets = {
        "analyze": "Analyze this image in detail. Describe what you see, identify key elements, colors, composition, and any notable features.",
        "summarize": "Provide a concise summary of what's shown in this image in 2-3 sentences.",
        "describe": "Describe this image as if you're explaining it to someone who cannot see it. Be detailed and specific.",
        "extract_text": "Extract and transcribe any text visible in this image. If no text is present, say 'No text detected'.",
        "identify_objects": "Identify and list all the objects, people, or items you can see in this image.",
        "explain_context": "Explain the context and setting of this image. What's happening? Where might this be taken?"
    }
    return presets.get(action, "Analyze this image")

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "GPT-5 Multimodal Chat API",
        "version": "1.0.0",
        "endpoints": {
            "/chat/text": "Text-only chat with GPT-5",
            "/chat/image-upload": "Upload image and chat with GPT-5",
            "/chat/image-base64": "Send base64 image and chat with GPT-5",
            "/presets": "Get available preset actions for images"
        }
    }

@app.get("/presets")
async def get_presets():
    """Get available preset actions for image analysis"""
    return {
        "presets": [
            {"key": "analyze", "label": "Analyze Image", "description": "Detailed analysis of the image"},
            {"key": "summarize", "label": "Summarize", "description": "Quick summary of image content"},
            {"key": "describe", "label": "Describe", "description": "Detailed description for accessibility"},
            {"key": "extract_text", "label": "Extract Text", "description": "Extract any text from the image"},
            {"key": "identify_objects", "label": "Identify Objects", "description": "List objects and items in the image"},
            {"key": "explain_context", "label": "Explain Context", "description": "Explain the setting and context"}
        ]
    }

@app.post("/chat/text", response_model=TextChatResponse)
async def text_chat(request: TextChatRequest):
    """Text-only chat with GPT-5"""
    try:
        # Prepare conversation history
        messages = request.conversation_history.copy() if request.conversation_history else []
        messages.append({"role": "user", "content": request.message})
        
        # Call GPT-5 API
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o as GPT-5 might not be available yet
            messages=messages,
            max_tokens=2048,
            temperature=0.7
        )
        
        assistant_response = response.choices[0].message.content
        
        # Update conversation history
        messages.append({"role": "assistant", "content": assistant_response})
        
        return TextChatResponse(
            response=assistant_response,
            conversation_history=messages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.post("/chat/image-upload")
async def image_upload_chat(
    image: UploadFile = File(...),
    prompt: Optional[str] = Form(None),
    preset_action: Optional[str] = Form(None)
):
    """Upload an image file and chat with GPT-5"""
    try:
        # Validate image file
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Convert image to base64
        base64_image = encode_image_to_base64(image)
        
        # Determine the prompt to use
        if preset_action:
            final_prompt = get_preset_prompt(preset_action)
            analysis_type = preset_action
        elif prompt:
            final_prompt = prompt
            analysis_type = "custom"
        else:
            final_prompt = "Analyze this image"
            analysis_type = "default"
        
        # Prepare the message for GPT-5
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": final_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        # Call GPT-5 API
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o for vision capabilities
            messages=messages,
            max_tokens=2048,
            temperature=0.7
        )
        
        assistant_response = response.choices[0].message.content
        
        return ImageAnalysisResponse(
            response=assistant_response,
            analysis_type=analysis_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/chat/image-base64", response_model=ImageAnalysisResponse)
async def image_base64_chat(request: ImageAnalysisRequest):
    """Send base64 encoded image and chat with GPT-5"""
    try:
        # Determine the prompt to use
        if request.preset_action:
            final_prompt = get_preset_prompt(request.preset_action)
            analysis_type = request.preset_action
        else:
            final_prompt = request.prompt or "Analyze this image"
            analysis_type = "custom" if request.prompt else "default"
        
        # Prepare the message for GPT-5
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": final_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{request.image_base64}"
                        }
                    }
                ]
            }
        ]
        
        # Call GPT-5 API
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o for vision capabilities
            messages=messages,
            max_tokens=2048,
            temperature=0.7
        )
        
        assistant_response = response.choices[0].message.content
        
        return ImageAnalysisResponse(
            response=assistant_response,
            analysis_type=analysis_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/chat/multimodal")
async def multimodal_chat(
    message: str = Form(...),
    image: Optional[UploadFile] = File(None),
    conversation_history: Optional[str] = Form(None)  # JSON string
):
    """Combined endpoint for both text and image input"""
    try:
        import json
        
        # Parse conversation history if provided
        messages = []
        if conversation_history:
            try:
                messages = json.loads(conversation_history)
            except json.JSONDecodeError:
                messages = []
        
        # Prepare the current message
        current_message = {
            "role": "user",
            "content": []
        }
        
        # Add text content
        current_message["content"].append({"type": "text", "text": message})
        
        # Add image if provided
        if image and image.content_type.startswith('image/'):
            base64_image = encode_image_to_base64(image)
            current_message["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
        
        messages.append(current_message)
        
        # Call GPT-5 API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=2048,
            temperature=0.7
        )
        
        assistant_response = response.choices[0].message.content
        
        # Update conversation history
        messages.append({"role": "assistant", "content": assistant_response})
        
        return {
            "response": assistant_response,
            "conversation_history": messages,
            "has_image": image is not None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing multimodal chat: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
