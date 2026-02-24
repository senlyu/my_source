import httpx
import asyncio
import json

async def test_completion():
    # Dynamically get port from config
    port = 4001
    try:
        with open('config.json', 'r') as f:
            data = json.load(f)
            port = data.get('kms', {}).get('port', 4001)
    except:
        pass

    url = f"http://127.0.0.1:{port}/v1/chat/completions"
    payload = {
        "prompt": "Hello, how are you?",
        "context": ["The user is greeting you."],
        "model_type": "gemini-2.5-flash"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=60.0)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_completion())
