from pathlib import Path
from typing import Dict, List, Optional, Sequence
import json

from private_gpt.settings.settings import settings
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document, ImageNode
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llama_index.core.multi_modal_llms.generic_utils import encode_image

system_prompt = (
    """You are an AI assistant that takes images and generates a short description and a long description for the image.
    The short description is a single sentence that captures the essence of the image.
    The long description is a paragraph that provides more details about the image : elements, colors, textures, background, mood, movement, etc.
    Please provide the short description and the long description in the following JSON format {sd: 'short description', ld: 'long description'}.
    Output only the resulting JSON, no other text or characters.
    """
)

class ImageVisionOpenAIReader(BaseReader):
    """Image parser.

    Extract short description and long description from images using OpenAI multimodal LLM (GPT-4V).

    """ 
    def __init__(self):                
        # Use Gemini for image processing
        openai_settings = settings().openai
        self.llm = OpenAIMultiModal(
            model=openai_settings.vision_model,
            api_key=openai_settings.api_key,
            max_new_tokens=300
        )
    
    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs = None,
    ) -> List[Document]:
        """Generate a short description and a long description for the image."""
        # Local image
        image = encode_image(file.absolute())
        image_documents: Sequence[ImageNode] = [ImageNode(image=image)]
        response = self.llm.complete(system_prompt, image_documents)

        # Convert response into ImageDocument
        resp = response.text.replace('\n', '').replace('json', '').replace("```", '')
                
        try:
            parsed_response = json.loads(resp)
            short_description = parsed_response.get('sd', '')
            long_description = parsed_response.get('ld', '')

            return [Document(                
                text=long_description,
                metadata={
                    "short_description": short_description,                    
                    "file_path": str(file),
                    "file_name": str(file.name)
                }
            )]
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from response: {response.text}")
            return []
