import os
import google.generativeai as genai

def generate_report(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: raise RuntimeError("GEMINI_API_KEY is not configured")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
    response = model.generate_content(prompt)
    if not response.text: raise RuntimeError("Gemini returned an empty response")
    return response.text
