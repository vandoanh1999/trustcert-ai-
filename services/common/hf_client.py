import httpx
from . import config

API_URL_TEMPLATE = "https://api-inference.huggingface.co/models/{}"
LLM_API_URL_TEMPLATE = "https://api-inference.huggingface.co/pipeline/text-generation/{}"

class HuggingFaceClient:
    def __init__(self, token: str):
        self.headers = {"Authorization": f"Bearer {token}"}
        self.async_client = httpx.AsyncClient(headers=self.headers, timeout=60.0)

    async def get_embedding(self, text: str, model: str):
        api_url = API_URL_TEMPLATE.format(model)
        response = await self.async_client.post(api_url, json={"inputs": text, "options": {"wait_for_model": True}})
        response.raise_for_status()
        # The embedding is usually the first (and only) item in the list
        return response.json()[0]

    async def get_embeddings(self, texts: list[str], model: str):
        api_url = API_URL_TEMPLATE.format(model)
        response = await self.async_client.post(api_url, json={"inputs": texts, "options": {"wait_for_model": True}})
        response.raise_for_status()
        return response.json()

    async def chat_completion(self, prompt: str, model: str):
        # Note: Text Generation API is slightly different
        api_url = LLM_API_URL_TEMPLATE.format(model)
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 256,
                "return_full_text": False,
            }
        }
        response = await self.async_client.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()[0]['generated_text']

# Global client instance
hf_client = HuggingFaceClient(token=config.HF_TOKEN)
