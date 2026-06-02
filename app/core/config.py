import os
import json
import logging

VAULT_SECRETS_PATH = "/vault/secrets/config.json"

class Settings:
    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql+asyncpg://postgres:postgres@localhost:5434/logistics_db"
        )
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.load_vault_secrets()

    def load_vault_secrets(self):
        """Loads configuration from Vault Agent Sidecar JSON file if it exists."""
        if os.path.exists(VAULT_SECRETS_PATH):
            try:
                with open(VAULT_SECRETS_PATH, 'r') as f:
                    secrets = json.load(f)
                    if "database_url" in secrets and secrets["database_url"]:
                        self.database_url = secrets["database_url"]
                    if "gemini_api_key" in secrets and secrets["gemini_api_key"]:
                        self.gemini_api_key = secrets["gemini_api_key"]
                logging.info("Successfully loaded configuration from Vault Agent Sidecar")
            except Exception as e:
                logging.error(f"Failed to load secrets from Vault Agent: {e}")
        else:
            logging.info("Vault Agent secrets file not found. Falling back to environment variables.")

settings = Settings()
