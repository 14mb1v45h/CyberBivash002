import os
import time
from openai import OpenAI
from collections import deque
from datetime import datetime, timedelta

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

# Rate limiting settings
MAX_REQUESTS_PER_MINUTE = 20
request_timestamps = deque(maxlen=MAX_REQUESTS_PER_MINUTE)

# Initialize OpenAI client
openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def is_rate_limited():
    """Check if requests are being made too frequently"""
    now = datetime.now()
    # Remove timestamps older than 1 minute
    while request_timestamps and (now - request_timestamps[0]) > timedelta(minutes=1):
        request_timestamps.popleft()

    return len(request_timestamps) >= MAX_REQUESTS_PER_MINUTE

def validate_input(message):
    """Validate user input for security"""
    if not message or not isinstance(message, str):
        raise ValueError("Invalid input: Message must be a non-empty string")
    if len(message) > 2000:  # Reasonable limit for message length
        raise ValueError("Message exceeds maximum length of 2000 characters")
    return message

def get_ai_response(message):
    """
    Get response from OpenAI API with security considerations
    """
    try:
        # Input validation
        message = validate_input(message)

        # Rate limiting
        if is_rate_limited():
            raise Exception("Rate limit exceeded. Please try again later.")

        # Add timestamp for rate limiting
        request_timestamps.append(datetime.now())

        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are a knowledgeable cybersecurity assistant. 
                    Provide clear, accurate information about cybersecurity concepts, 
                    best practices, and threat mitigation strategies. Always promote 
                    ethical security practices and avoid providing information about 
                    harmful exploits or attacks. When discussing security measures, 
                    emphasize the importance of:
                    1. Data protection and privacy
                    2. Secure coding practices
                    3. Network security
                    4. Authentication and authorization
                    5. Security awareness and training"""
                },
                {"role": "user", "content": message}
            ],
            max_tokens=500
        )

        # Content filtering - ensure response doesn't contain harmful content
        ai_response = response.choices[0].message.content
        if any(harmful_term in ai_response.lower() for harmful_term in ['hack', 'exploit', 'vulnerability', 'payload']):
            return "I apologize, but I cannot provide specific information about security exploits or vulnerabilities. Instead, I can offer guidance on security best practices and defensive measures."

        return ai_response

    except ValueError as ve:
        raise Exception(f"Input validation error: {str(ve)}")
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")