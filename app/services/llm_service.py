# app/services/llm_service.py
from groq import Groq
import json
from typing import List, Dict, Optional
from app.config.settings import settings
from app.models.schemas import ChatMessage, BookingInfo
import logging

logger = logging.getLogger(__name__)

class LLMService:
    _client: Optional[Groq] = None

    @classmethod
    def get_client(cls) -> Groq:
        if cls._client is None:
            # Explicitly clear out proxies config to avoid the httpx error entirely
            cls._client = Groq(api_key=settings.GROQ_API_KEY, http_client=None)
        return cls._client

    @classmethod
    def generate_rag_response(cls, query: str, context_chunks: List[str], chat_history: List[ChatMessage]) -> str:
        """Generates a conversational response using the retrieved document chunks."""
        try:
            client = cls.get_client()
            
            context_str = "\n\n".join([f"[Context {i+1}]: {text}" for i, text in enumerate(context_chunks)])
            
            system_prompt = (
                "You are an intelligent, professional AI assistant matching user queries against provided documents.\n"
                "Use the following pieces of context to answer the user's question. If you don't know the answer, "
                "say that you don't know—do not make things up.\n\n"
                f"--- DOCUMENT CONTEXT ---\n{context_str}\n-------------------------\n\n"
                "CRITICAL: If the user asks to book or schedule an interview, politely guide them to provide "
                "their Full Name, Email, Date, and Time."
            )

            messages = [{"role": "system", "content": system_prompt}]
            for msg in chat_history:
                messages.append({"role": msg.role, "content": msg.content})
            
            messages.append({"role": "user", "content": query})

            # Using a highly stable, widely supported Groq model string
            response = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
            return response.choices[0].message.content

        except Exception as e:
            # This prints the raw, real error to your Uvicorn terminal so you can read it!
            print(f"\n❌ REAL GROQ ERROR ENCOUNTERED: {str(e)}\n")
            logger.error(f"Groq API call failed: {e}")
            return f"I'm sorry, I encountered an issue communicating with my core intelligence system. Details: {str(e)[:50]}"

    @classmethod
    def check_and_extract_booking(cls, last_user_message: str) -> Optional[BookingInfo]:
        """Detects if an interview booking is present and extracts structured data."""
        try:
            client = cls.get_client()
            
            extraction_prompt = (
                "Analyze the text. Determine if the user is providing details to book an interview.\n"
                "Extract it into a strictly formatted JSON object.\n"
                "Template:\n"
                "{\n"
                '  "is_booking": true or false,\n'
                '  "name": "Name or null",\n'
                '  "email": "Email or null",\n'
                '  "date": "YYYY-MM-DD or null",\n'
                '  "time": "HH:MM or null"\n'
                "}\n"
                "Output ONLY valid JSON."
            )

            response = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": extraction_prompt},
                    {"role": "user", "content": last_user_message}
                ],
                temperature=0.0
            )
            
            result_text = response.choices[0].message.content.strip()
            data = json.loads(result_text)
            
            if data.get("is_booking") and all([data.get("name"), data.get("email"), data.get("date"), data.get("time")]):
                return BookingInfo(
                    name=data["name"],
                    email=data["email"],
                    date=data["date"],
                    time=data["time"]
                )
            return None
        except Exception as e:
            print(f"Booking extraction error: {e}")
            return None