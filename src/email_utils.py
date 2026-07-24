# src/email_utils.py
import os
from groq import Groq
from dotenv import load_dotenv
from src.prompts import *

load_dotenv()

class EmailAssistant:
    def __init__(self, model=None):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # ========== FIX: Simple client initialization ==========
        # Remove all extra parameters
        self.client = Groq(api_key=self.api_key)
        
        self.model = model or os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")
        self.max_tokens = int(os.getenv("MAX_TOKENS", 2048))
        self.temperature = float(os.getenv("TEMPERATURE", 0.7))
    
    def _generate(self, prompt, temperature=None, max_tokens=None):
        try:
            temp = temperature if temperature is not None else self.temperature
            tokens = max_tokens if max_tokens is not None else self.max_tokens
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional email assistant with expertise in business communication, grammar, and writing styles."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temp,
                max_tokens=tokens,
                top_p=1,
                stream=False
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_reply(self, email_content, reply_type="general"):
        try:
            if reply_type in REPLY_TYPES:
                prompt = f"{REPLY_TYPES[reply_type]}\n\nOriginal Email:\n{email_content}\n\nReply:"
            else:
                prompt = f"{REPLY_PROMPT}\n\nEmail:\n{email_content}\n\nReply:"
            return self._generate(prompt, temperature=0.7)
        except Exception as e:
            return f"Error generating reply: {str(e)}"
    
    def correct_grammar(self, email_content):
        try:
            prompt = f"{GRAMMAR_CORRECTION_PROMPT}\n\nEmail:\n{email_content}\n\nCorrected Email:"
            return self._generate(prompt, temperature=0.3)
        except Exception as e:
            return f"Error correcting grammar: {str(e)}"
    
    def change_tone(self, email_content, tone):
        try:
            prompt = TONE_CONVERSION_PROMPT.format(tone=tone)
            prompt = f"{prompt}\n\nEmail:\n{email_content}\n\nRewritten Email:"
            return self._generate(prompt, temperature=0.7)
        except Exception as e:
            return f"Error changing tone: {str(e)}"
    
    def shorten_email(self, email_content):
        try:
            prompt = f"{SHORTEN_PROMPT}\n\nEmail:\n{email_content}\n\nShortened Email:"
            return self._generate(prompt, temperature=0.5)
        except Exception as e:
            return f"Error shortening email: {str(e)}"
    
    def medium_email(self, email_content):
        try:
            prompt = f"""
            Create a medium-length version of this email. 
            Keep it balanced - not too short like a summary, 
            but not as detailed as the full version.
            Aim for about 60-70% of the original length.
            Make it clear, professional, and easy to read.
            
            Original Email:
            {email_content}
            
            Medium Version:
            """
            return self._generate(prompt, temperature=0.6)
        except Exception as e:
            return f"Error generating medium version: {str(e)}"
    
    def expand_email(self, email_content):
        try:
            prompt = f"{EXPAND_PROMPT}\n\nEmail:\n{email_content}\n\nExpanded Email:"
            return self._generate(prompt, temperature=0.7)
        except Exception as e:
            return f"Error expanding email: {str(e)}"
    
    def generate_subject_lines(self, email_content):
        try:
            prompt = f"{SUBJECT_LINE_PROMPT}\n\nEmail:\n{email_content}\n\nSubject Lines:"
            return self._generate(prompt, temperature=0.8, max_tokens=1024)
        except Exception as e:
            return f"Error generating subject lines: {str(e)}"
    
    def get_improvement_suggestions(self, email_content):
        try:
            prompt = f"{IMPROVEMENT_PROMPT}\n\nEmail:\n{email_content}\n\nSuggestions:"
            return self._generate(prompt, temperature=0.5, max_tokens=3072)
        except Exception as e:
            return f"Error getting suggestions: {str(e)}"
    
    def translate_email(self, email_content, language):
        try:
            prompt = TRANSLATION_PROMPT.format(language=language)
            prompt = f"{prompt}\n\nEmail:\n{email_content}\n\nTranslated Email:"
            return self._generate(prompt, temperature=0.3)
        except Exception as e:
            return f"Error translating email: {str(e)}"
    
    def analyze_sentiment(self, email_content):
        try:
            prompt = f"{SENTIMENT_ANALYSIS_PROMPT}\n\nEmail:\n{email_content}\n\nAnalysis:"
            return self._generate(prompt, temperature=0.3)
        except Exception as e:
            return f"Error analyzing sentiment: {str(e)}"
    
    def set_model(self, model_name):
        self.model = model_name
    
    def get_available_models(self):
        return {
            "Llama 3.3 70B (Best Quality)": "llama-3.3-70b-versatile",
            "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant",
            "Llama 3 70B": "llama3-70b-8192",
            "Llama 3 8B (Fastest)": "llama3-8b-8192",
            "Gemma 2 9B": "gemma2-9b-it"
        }