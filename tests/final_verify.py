import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Debug print to confirm key is actually loaded
# Masking key for security in logs, showing first 4 and last 4 chars
key = os.getenv("GROQ_API_KEY")
if key:
    print(f"Loaded key: {key[:4]}...{key[-4:]}")
else:
    print("Loaded key: None")

try:
    client = Groq(api_key=key)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": "Hello from test"}
        ],
        max_tokens=20  # Corrected from max_output_tokens which tends to error
    )

    print(response.choices[0].message.content) # Corrected dict access to attribute
except Exception as e:
    print(f"Error: {e}")
