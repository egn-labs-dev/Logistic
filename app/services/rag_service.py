import logging
import os
from google.cloud import discoveryengine_v1 as discoveryengine

logger = logging.getLogger(__name__)

async def query_logistics_knowledge(
    user_query: str,
    project_id: str = None,
    data_store_id: str = "logistics-compliance-store",
    location: str = "global"
) -> str | None:
    """Асинхронно шукає відповідь у Vertex AI Agent Builder Data Store."""
    project_id = project_id or os.getenv("GCP_PROJECT_ID", "n8n-automations-497913")

    try:
        client = discoveryengine.SearchServiceAsyncClient()
        serving_config = (
            f"projects/{project_id}/locations/{location}"
            f"/dataStores/{data_store_id}/servingConfigs/default_serving_config"
        )
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=user_query,
            page_size=3
        )
        response = await client.search(request)

        if response.summary and response.summary.summary_text:
            return response.summary.summary_text
        elif response.results:
            snippets = []
            for r in response.results[:3]:
                doc = r.document.derived_struct_data
                if "snippets" in doc:
                    for s in doc["snippets"]:
                        snippets.append(s.get("snippet", ""))
            return "\n".join(snippets) if snippets else None

        return None
    except Exception as e:
        logger.error(f"RAG search error: {e}")
        return None
