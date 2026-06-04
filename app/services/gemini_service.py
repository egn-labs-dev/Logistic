import os
import json
import asyncio
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.schemas.dispatcher import DispatcherLLMOutput, ExtractedCargoDetails

class GeminiDispatcherService:
    def __init__(self):
        from app.core.config import settings
        self.client = genai.Client(api_key=settings.gemini_api_key)
        # Using a model that fits within your billing limits
        self.model_name = "gemini-3.1-flash-lite"

    async def analyze_dispatched_text(self, clean_text: str, custom_prompt: str = None) -> DispatcherLLMOutput:
        system_instruction = (
            "You are a leading logistics AI dispatcher of an international freight forwarding company.\n"
            "Analyze the input text and structure it according to the provided JSON schema.\n\n"
            "PARAMETER DETERMINATION RULES:\n"
            "1. Weight Conversion: Always record the weight in TONS in the weight_tons field. If the client writes '500 kg', write 0.5. If '20 tons', write 20.0.\n"
            "2. Body Type (body_type_required): If perishable goods or deep freezing is mentioned, set 'refrigerator'. If regular boxes or pallets, set 'tent'. If oversized cargo or pipes, set 'platform'.\n"
            "3. Temperature Control: If a refrigerator is required, you must specify the temperature regime. If the client writes '+4', set min_celsius=4.0, max_celsius=4.0.\n"
            "4. ADR (Hazardous Cargo): Chemicals, batteries, varnishes, paints, gasoline signify hazardous cargo. Set embraces_adr=True and specify the class if it can be inferred from the context.\n"
            "5. Security: Client data is anonymized with masks like [PHONE_0]. In the response_to_user field, respond politely, confirm the route and cargo parameters you were able to recognize. If you mention their contacts, write them strictly as the mask [PHONE_0].\n"
            "6. Lead Qualification: If the client simply says 'Hello' or writes spam, set is_qualified_lead=False.\n"
        )
        
        if custom_prompt:
            system_instruction += f"\nCUSTOM ORGANIZATION RULES (CRITICAL, MUST FOLLOW):\n{custom_prompt}\n"
            
        system_instruction += f"\nOUTPUT FORMAT: You MUST return a valid JSON object matching this JSON Schema:\n{json.dumps(DispatcherLLMOutput.model_json_schema())}\n"

        user_content = f"<user_input>\n{clean_text}\n</user_input>"

        try:
            @retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=2, max=10),
                reraise=True
            )
            def _generate():
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_content,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        temperature=0.1,
                    ),
                )
            
            response = await asyncio.to_thread(_generate)
            data_dict = json.loads(response.text)
            return DispatcherLLMOutput(**data_dict)
        except Exception as e:
            import logging
            logging.error(f"Gemini Service Error: {e}")
            # Our robust Fail-safe contour
            return DispatcherLLMOutput(
                is_qualified_lead=False,
                requires_human_intervention=True,
                extracted_data=ExtractedCargoDetails(detected_placeholders=[]),
                response_to_user="We apologize, there was a technical delay while analyzing the cargo specification. Transferring the dialogue to an operator."
            )
