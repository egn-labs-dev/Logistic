import re
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Патерни для блокування Prompt Injection
FORBIDDEN_PATTERNS = [
    # Загальні маніпуляції системним промптом
    r"(?i)ignore\s+(all\s+)?previous\s+instructions",
    r"(?i)bypass\s+system\s+prompt",
    r"(?i)you\s+are\s+now\s+a",
    r"(?i)forget\s+(all\s+)?(your\s+)?(rules|instructions)",
    r"(?i)act\s+as\s+if\s+you\s+have\s+no\s+restrictions",
    r"(?i)system[_\s]?hacked",
    # Логістично-специфічні маніпуляції (UA + EN)
    r"(?i)(ігноруй|забудь|скасуй|відмін).{0,30}(правил|інструкц|ADR|обмежен)",
    r"(?i)(пропусти|дозволь).{0,30}без\s+(документ|дозвол|перевірк)",
    r"(?i)(ignore|skip|bypass).{0,30}(ADR|hazard|dangerous|safety)",
]

_COMPILED = [re.compile(p) for p in FORBIDDEN_PATTERNS]


def validate_against_injection(text: str) -> str:
    """Перевіряє текст на наявність Prompt Injection патернів.
    Повертає текст якщо безпечний, або кидає HTTPException."""
    for pattern in _COMPILED:
        if pattern.search(text):
            logger.warning(f"⚠️ [Security Alert] Prompt Injection blocked: {text[:100]}...")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request rejected by security system: suspicious instructions detected."
            )
    return text
