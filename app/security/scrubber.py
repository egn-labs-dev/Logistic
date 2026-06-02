import re
from typing import Dict
from app.schemas.chat import ScrubbedContext

class DataScrubber:
    @staticmethod
    def anonymize(text: str) -> ScrubbedContext:
        vault = {}
        modified_text = text
        
        # Simplified regex patterns for MVP
        # Phone numbers (basic pattern)
        phone_pattern = r"\+?\d{10,13}"
        phones = set(re.findall(phone_pattern, text))
        
        for idx, phone in enumerate(phones):
            placeholder = f"[PHONE_{idx}]"
            vault[placeholder] = phone
            modified_text = modified_text.replace(phone, placeholder)
            
        # Email addresses (basic pattern)
        email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+"
        emails = set(re.findall(email_pattern, modified_text))
        
        for idx, email in enumerate(emails):
            placeholder = f"[EMAIL_{idx}]"
            vault[placeholder] = email
            modified_text = modified_text.replace(email, placeholder)
            
        return ScrubbedContext(original_text=text, clean_text=modified_text, vault=vault)

    @staticmethod
    def deanonymize(text: str, vault: Dict[str, str]) -> str:
        restored_text = text
        for placeholder, original_value in vault.items():
            restored_text = restored_text.replace(placeholder, original_value)
        return restored_text
