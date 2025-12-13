"""AIAssistant service class."""

from typing import List, Dict, Optional
import openai
import os

class AIAssistant:
    """Wrapper around OpenAI API for AI chat functionality."""

    def __init__(self, system_prompt: str = "You are a helpful assistant."):
        self._system_prompt = system_prompt
        self._history: List[Dict[str, str]] = []
        self._api_key_valid = False

        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            api_key = api_key.strip()
            if api_key.startswith("sk-"):
                openai.api_key = api_key
                self._api_key_valid = True

    def is_api_key_valid(self) -> bool:
        """Check if API key is configured."""
        return self._api_key_valid

    def set_system_prompt(self, prompt: str) -> None:
        """Update the system prompt."""
        self._system_prompt = prompt

    def send_message(self, user_message: str) -> str:
        """Send a message and get AI response."""
        if not self._api_key_valid:
            return "❌ OpenAI API key not configured or invalid. Please check your .env file."

        try:
            # Add user message to history
            self._history.append({"role": "user", "content": user_message})

            # Build messages for API
            messages = [
                {"role": "system", "content": self._system_prompt}
            ] + self._history

            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                max_tokens=500
            )

            # Extract response
            answer = response.choices[0].message.content

            # Add to history
            self._history.append({"role": "assistant", "content": answer})

            return answer

        except openai.AuthenticationError:
            return "❌ Invalid API key. Please add billing at https://platform.openai.com/settings/organization/billing"
        except openai.RateLimitError:
            return "⚠️ Rate limit exceeded. Please add billing or wait a moment."
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def clear_history(self) -> None:
        """Clear conversation history."""
        self._history.clear()

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self._history.copy()
