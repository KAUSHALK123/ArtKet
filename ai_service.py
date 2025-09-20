import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# IMPORTANT: KEEP THIS COMMENT
# Follow these instructions when using this blueprint:
# - Note that the newest Gemini model series is "gemini-2.5-flash" or gemini-2.5-pro"
#   - do not change this unless explicitly requested by the user

# This API key is from Gemini Developer API Key, not vertex AI API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def generate_caption_and_hashtags(image_description, craft_type=None):
    """Generate engaging caption and hashtags for artisan posts"""
    if not client:
        return {
            'caption': 'Beautiful handcrafted piece showcasing traditional artistry',
            'hashtags': '#handmade #artisan #craft #local #art',
            'story': 'This piece represents the rich tradition of handcrafted artistry.'
        }
    
    try:
        craft_context = f" specializing in {craft_type}" if craft_type else ""
        
        system_prompt = (
            "You are an expert social media content creator for artisans. "
            "Generate engaging, authentic captions and hashtags that tell stories "
            "about handcrafted items and connect with audiences emotionally. "
            "Respond with JSON in this format: "
            "{'caption': 'engaging caption', 'hashtags': '#hashtag1 #hashtag2', 'story': 'longer background story'}"
        )
        
        user_prompt = (
            f"Create an engaging social media post for an artisan{craft_context} "
            f"sharing this item: {image_description}. "
            "Make it authentic, storytelling-focused, and include relevant hashtags."
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json"
            ),
        )
        
        if response.text:
            result = json.loads(response.text)
            return {
                'caption': result.get('caption', 'Beautiful handcrafted piece'),
                'hashtags': result.get('hashtags', '#handmade #artisan'),
                'story': result.get('story', 'A unique creation with its own story.')
            }
        else:
            raise ValueError("Empty response from Gemini")
        
    except Exception as e:
        print(f"AI caption generation error: {e}")
        return {
            'caption': 'Beautiful handcrafted piece showcasing traditional artistry',
            'hashtags': '#handmade #artisan #craft #local #art',
            'story': 'This piece represents the rich tradition of handcrafted artistry.'
        }

def generate_product_description(title, basic_description, craft_type=None, price=None):
    """Generate compelling product descriptions for marketplace listings"""
    if not client:
        return f"Beautifully crafted {title}. {basic_description} Perfect for adding artisanal charm to any space."
    
    try:
        craft_context = f" in the {craft_type} tradition" if craft_type else ""
        price_context = f" priced at ${price}" if price else ""
        
        system_prompt = (
            "You are an expert product copywriter for artisan marketplaces. "
            "Create compelling, authentic product descriptions that highlight "
            "craftsmanship, uniqueness, and emotional appeal while being practical for buyers. "
            "Keep descriptions concise but engaging."
        )
        
        user_prompt = (
            f"Write a compelling product description for: {title}. "
            f"Basic details: {basic_description}. "
            f"Craft type: {craft_type or 'handmade'}. "
            f"Price context: {price_context}. "
            "Focus on quality, uniqueness, and the story behind the craft."
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
        
        return response.text.strip() if response.text else f"Beautifully crafted {title}. {basic_description}"
        
    except Exception as e:
        print(f"AI description generation error: {e}")
        return f"Beautifully crafted {title}. {basic_description} A unique piece that showcases skilled artisanship and attention to detail."

def analyze_image_for_content(base64_image):
    """Analyze uploaded images to suggest content"""
    if not client:
        return "A beautiful handcrafted item showcasing traditional artistry and skill."
    
    try:
        # Convert base64 to bytes for Gemini
        import base64
        image_bytes = base64.b64decode(base64_image)
        
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg"
                ),
                types.Part(text=(
                    "Analyze this image of handcrafted artwork. Describe the item, "
                    "materials used, crafting technique, colors, style, and any cultural "
                    "or artistic elements. Keep it concise but detailed for social media."
                ))
            ]
        )
        
        return response.text.strip() if response.text else "A beautiful handcrafted item showcasing traditional artistry and skill."
        
    except Exception as e:
        print(f"AI image analysis error: {e}")
        return "A beautiful handcrafted item showcasing traditional artistry and skill."

def recommend_similar_artisans(user_interests, craft_type=None):
    """Generate recommendations for similar artisans (basic version)"""
    # This would typically use embeddings and ML models
    # For now, return a simple recommendation logic
    return {
        'message': 'AI recommendations coming soon!',
        'suggested_searches': [craft_type] if craft_type else ['pottery', 'jewelry', 'textiles']
    }