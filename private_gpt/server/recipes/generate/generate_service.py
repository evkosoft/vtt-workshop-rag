import asyncio
import logging
import time
from typing import Any
import fal_client
from injector import inject, singleton
from private_gpt.server.recipes.generate.external_api import ExternalAPIService
from private_gpt.settings.settings import Settings
from leonardo_ai_sdk import LeonardoAiSDK

logger = logging.getLogger(__name__)

@singleton
class GenerateService:
    @inject
    def __init__(
        self,
        settings: Settings):
        self.settings = settings
        self.leonardo_client = LeonardoAiSDK(bearer_auth=self.settings.imagegen.leo_api_key)        
        self.vtt_backend_api = ExternalAPIService(base_url=self.settings.imagegen.vtt_webhook_url)
        
    def generate_image_using_flux(self, image_desc: str) -> Any:
        
        # Temporary : use FLUX.1[schnell] for image gen
        handler = fal_client.submit(
            #"fal-ai/flux/schnell",
            "fal-ai/flux-pro/v1.1",
            arguments={
                "prompt": image_desc,
                "image_size": "landscape_4_3",  # square, square_hd
                "safety_tolerance": "2",
                "enable_safety_checker": False,
                "sync_mode": True       # TB modified !!
            },
        )

        result = handler.get()        
        return result
    
    def generate_image_using_leonardo(self, image_desc: str, width: int, height: int , style: str) -> Any:
        if width%8 != 0 or height%8 != 0:
            raise ValueError("Width and height must be a multiple of 8.")
        
        res = self.leonardo_client.image.create_generation(request={
            "model_id": self.settings.imagegen.leo_model_id,
            "prompt": image_desc,
            "num_images": 1,
            "width": width,
            "height": height,
            "alchemy": True,
            "preset_style": style if style is not None else self.settings.imagegen.leo_preset_style,
            "prompt_magic": False
        })

        if res.object is not None:
            # handle response
            gen_job = res.object.sd_generation_job
            # Get the generation data
            gen_data = self._fetch_and_extract_gen_data(gen_job.generation_id)
            if gen_data['status'] == "PENDING":
                # Poll for generation data
                gen_data = self.poll_for_generated_images(gen_job.generation_id)
            return gen_data
        else:
            return None 
    
    def _fetch_and_extract_gen_data(self, generation_id: str) -> Any:
        result = self.leonardo_client.image.get_generation_by_id(id=generation_id)
        if result.object is not None:
            imagen_data = result.object.generations_by_pk
            # return only wanted fields from imagen_data
            return {
                "created_at": imagen_data.created_at,
                "generated_images": [
                    {
                        "id": image.id,
                        "url": image.url
                    }
                    for image in imagen_data.generated_images
                ],
                "id": imagen_data.id,
                "image_height": imagen_data.image_height,
                "image_width": imagen_data.image_width,
                "model_id": imagen_data.model_id,
                "prompt": imagen_data.prompt,
                "preset_style": imagen_data.preset_style,
                "status": imagen_data.status,
                "seed": imagen_data.seed
            }
            
        
    async def poll_for_generated_images_async(self, generation_id: str) -> Any:
        for _ in range(60):
            logger.debug(f"Polling for generation_id={generation_id}")
            gen_data = self._fetch_and_extract_gen_data(generation_id)
            if gen_data['status'] != "PENDING":
                return await self.vtt_backend_api.post_data(data= {"image_generation": gen_data})
            await asyncio.sleep(1)

    def poll_for_generated_images(self, generation_id: str) -> Any:
        """ TODO : improve this because it will block the event loop """
        for _ in range(60):            
            gen_data = self._fetch_and_extract_gen_data(generation_id)
            if gen_data['status'] != "PENDING":
                return gen_data
            time.sleep(1)
