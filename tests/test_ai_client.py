import pytest
from unittest.mock import patch, AsyncMock
from services.ai_client import generate_ai_response

@pytest.mark.asyncio
async def test_generate_ai_response_success():
    mock_response = {
        "result": {
            "alternatives": [
                {"message": {"text": "Hello from AI"}}
            ]
        }
    }
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=mock_response)
        mock_post.return_value.__aenter__.return_value = mock_resp
        result = await generate_ai_response("test prompt", lang="en")
        assert result == "Hello from AI"

@pytest.mark.asyncio
async def test_generate_ai_response_fallback():
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status = 500
        mock_resp.text = AsyncMock(return_value="Internal error")
        mock_post.return_value.__aenter__.return_value = mock_resp
        result = await generate_ai_response("test prompt", lang="en", max_retries=1)
        assert "temporarily overloaded" in result