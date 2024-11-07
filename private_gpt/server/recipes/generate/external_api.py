# services/external_api_service.py
import httpx
from fastapi import HTTPException

class ExternalAPIService:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = httpx.Timeout(30.0, connect=5.0, read=20.0, write=5.0)

    async def fetch_data(self, endpoint: str, params: dict = None):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Make an async GET request to the external API
                response = await client.get(f"{self.base_url}{endpoint}", params=params)
                
                # Raise an HTTP error if the status is not 200
                response.raise_for_status()

                # Return the JSON response data
                return response.json()

            except httpx.HTTPStatusError as e:
                # Handle error response from the external API
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"External API request failed: {e.response.text}"
                )

            except httpx.RequestError as e:
                # Handle request-related errors (e.g., connection issues)
                raise HTTPException(
                    status_code=500,
                    detail=f"Request error: {str(e)}"
                )

    async def post_data(self, endpoint: str="", data: dict={}, params: dict = None):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Make an async POST request to the external API
                response = await client.post(f"{self.base_url}{endpoint}", json=data, params=params)
                
                # Raise an HTTP error if the status is not in the 2xx range
                response.raise_for_status()

                # Return the JSON response data
                return response.json()

            except httpx.HTTPStatusError as e:
                # Handle error response from the external API
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"External API request failed: {e.response.text}"
                )

            except httpx.RequestError as e:
                # Handle request-related errors (e.g., connection issues)
                raise HTTPException(
                    status_code=500,
                    detail=f"Request error: {str(e)}"
                )
