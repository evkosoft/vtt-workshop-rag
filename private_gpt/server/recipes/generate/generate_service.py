from typing import Any
import fal_client
from injector import inject, singleton
from private_gpt.settings.settings import Settings

@singleton
class GenerateService:
    @inject
    def __init__(
        self,
        settings: Settings):
        self.settings = settings

    def generate_image(self, image_desc: str) -> Any:

        # Temporary : use FLUX.1[schnell] for image gen
        handler = fal_client.submit(
            #"fal-ai/flux/schnell",
            "fal-ai/flux-pro/v1.1",
            arguments={
                "prompt": image_desc,
                "image_size": "landscape_4_3",  # square, square_hd
                "sync_mode": True       # TB modified !!
            },
        )

        result = handler.get()
        return result