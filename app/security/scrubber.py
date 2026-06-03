import re
from typing import Dict
from app.schemas.chat import ScrubbedContext


class DataScrubber:
    """PII scrubber that anonymizes sensitive data before it reaches the LLM."""

    # Compiled regex patterns for performance
    _PATTERNS = [
        # Phone numbers (international format, 10-13 digits)
        ("PHONE", re.compile(r"\+?\d{10,13}")),
        # Email addresses
        ("EMAIL", re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")),
        # Ukrainian license plates: AA1234BB, AA 1234 BB
        ("PLATE", re.compile(r"\b[A-ZА-ЯІЇЄҐ]{2}[\s-]?\d{4}[\s-]?[A-ZА-ЯІЇЄҐ]{2}\b")),
        # European license plates: common formats like ABC-1234, AB 123 CD
        ("PLATE_EU", re.compile(r"\b[A-Z]{1,3}[\s-]\d{1,4}[\s-][A-Z]{1,3}\b")),
        # IBAN (International Bank Account Number)
        ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{0,4}\b")),
    ]

    @staticmethod
    def anonymize(text: str) -> ScrubbedContext:
        vault = {}
        modified_text = text

        # Phones
        phone_pattern = r"\+?\d{10,13}"
        phones = set(re.findall(phone_pattern, text))
        for idx, phone in enumerate(phones):
            placeholder = f"[PHONE_{idx}]"
            vault[placeholder] = phone
            modified_text = modified_text.replace(phone, placeholder)
            
        # Emails
        email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+"
        emails = set(re.findall(email_pattern, modified_text))
        for idx, email in enumerate(emails):
            placeholder = f"[EMAIL_{idx}]"
            vault[placeholder] = email
            modified_text = modified_text.replace(email, placeholder)
            
        # License Plates (UA: AA1234BB, EU general pattern)
        plate_pattern = r"\b[A-ZА-ЯІЄЇ]{2}\s?\d{4}\s?[A-ZА-ЯІЄЇ]{2}\b|\b[A-Z]{1,3}[-\s]?\d{1,4}[-\s]?[A-Z]{1,3}\b"
        plates = set(re.findall(plate_pattern, modified_text))
        for idx, plate in enumerate(plates):
            placeholder = f"[PLATE_{idx}]"
            vault[placeholder] = plate
            modified_text = modified_text.replace(plate, placeholder)
            
        # IBANs
        iban_pattern = r"\b[A-Z]{2}\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{0,4}\b"
        ibans = set(re.findall(iban_pattern, modified_text))
        for idx, iban in enumerate(ibans):
            placeholder = f"[IBAN_{idx}]"
            vault[placeholder] = iban
            modified_text = modified_text.replace(iban, placeholder)
            
        return ScrubbedContext(original_text=text, clean_text=modified_text, vault=vault)

    @staticmethod
    def deanonymize(text: str, vault: Dict[str, str]) -> str:
        restored_text = text
        for placeholder, original_value in vault.items():
            restored_text = restored_text.replace(placeholder, original_value)
        return restored_text
