import os
import datetime
import logging
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai.errors import APIError

from kms.key_manager import KeyManager
from kms.config import KMSConfig
from kms.utils import hash_data_40_chars

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Key Manager Standalone Server (KMS)")

# Initialize Config and KeyManager
config = KMSConfig()
logger.info(f"KMS starting on port {config.get_port()}")
keys = config.get_gemini_keys()
if not keys:
    logger.error("No API keys found. KMS will not be able to process requests.")
key_manager = KeyManager(keys, config.get_rpm())

HISTORY_DIR = config.get_history_path()
os.makedirs(HISTORY_DIR, exist_ok=True)

class CompletionRequest(BaseModel):
    prompt: str
    context: List[str] = []
    model_type: str = "gemini-2.5-flash"
    force_refresh: bool = False

class CompletionResponseData(BaseModel):
    text: str
    usage: dict
    model_used: str
    cached: bool

class CompletionResponse(BaseModel):
    status: str
    data: Optional[CompletionResponseData] = None
    error_code: Optional[str] = None
    error_text: Optional[str] = None

def load_from_cache(request: CompletionRequest) -> Optional[dict]:
    if request.force_refresh:
        return None
    
    cache_key = {
        "prompt": request.prompt,
        "context": request.context,
        "model": request.model_type
    }
    file_hash = hash_data_40_chars(cache_key)
    
    # Check last 30 days
    for i in range(30):
        d = datetime.datetime.now() - datetime.timedelta(days=i)
        date_str = d.strftime('%Y-%m-%d')
        path = os.path.join(HISTORY_DIR, f"{date_str}_{file_hash}.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    return None

def save_to_cache(request: CompletionRequest, data: dict):
    cache_key = {
        "prompt": request.prompt,
        "context": request.context,
        "model": request.model_type
    }
    file_hash = hash_data_40_chars(cache_key)
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    path = os.path.join(HISTORY_DIR, f"{date_str}_{file_hash}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.post("/v1/chat/completions", response_model=CompletionResponse)
async def chat_completions(request: CompletionRequest):
    # 1. Check Cache
    cached_data = load_from_cache(request)
    if cached_data:
        logger.info("Cache hit.")
        return CompletionResponse(
            status="success",
            data=CompletionResponseData(
                text=cached_data["text"],
                usage=cached_data.get("usage", {}),
                model_used=request.model_type,
                cached=True
            )
        )

    # 2. Get API Key
    try:
        api_key = await key_manager.get_key_and_wait()
    except Exception as e:
        logger.error(f"Failed to get API key: {e}")
        return CompletionResponse(status="error", error_code="KEY_ERROR", error_text=str(e))

    # 3. Call Model
    try:
        client = genai.Client(api_key=api_key)
        contents = request.context + [request.prompt]
        
        response = await client.aio.models.generate_content(
            model=request.model_type,
            contents=contents
        )
        
        result_text = response.text
        usage = {
            "prompt_tokens": response.usage_metadata.prompt_token_count,
            "candidates_tokens": response.usage_metadata.candidates_token_count,
            "total_tokens": response.usage_metadata.total_token_count
        }

        # 4. Cache Result
        save_to_cache(request, {"text": result_text, "usage": usage})

        return CompletionResponse(
            status="success",
            data=CompletionResponseData(
                text=result_text,
                usage=usage,
                model_used=request.model_type,
                cached=False
            )
        )

    except APIError as e:
        logger.error(f"API Error: {e}")
        return CompletionResponse(status="error", error_code="API_ERROR", error_text=str(e))
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        return CompletionResponse(status="error", error_code="INTERNAL_ERROR", error_text=str(e))
    finally:
        key_manager.release_key(api_key)

@app.get("/health")
async def health():
    return {"status": "ok", "keys_configured": len(keys)}
