from fastapi import APIRouter, BackgroundTasks, Depends, Request
from private_gpt.open_ai.extensions.context_filter import ContextFilter
from private_gpt.open_ai.openai_models import OpenAICompletion, OpenAIMessage
from private_gpt.server.completions.completions_router import CompletionsBody, prompt_completion
from private_gpt.server.recipes.generate.generate_service import GenerateService
from private_gpt.server.recipes.generate.system_prompts import SystemPrompts
from pydantic import BaseModel

from private_gpt.server.utils.auth import authenticated

generate_router = APIRouter(prefix="/v1/generate", dependencies=[Depends(authenticated)])

class ImagenInput(BaseModel):
    prompt: str
    tags: list[str]
    width: int=896
    height: int=896
    style: str="DYNAMIC"    

class ImagenResponse(BaseModel):
    pass

class TextgenInput(BaseModel):
    prompt: str
    messages: list[OpenAIMessage]
    tags: list[str]

class TextgenResponse(BaseModel):
    pass

@generate_router.post(
    "/image",
    response_model=None,
    summary="Image Generation",
    responses={200: {"model": ImagenResponse}},
    tags=["Recipes"],
)
def generate_image(request: Request, input: ImagenInput) :
    """
    Generate an image based on the provided input.
    This will return an image generation job, as well as the generated image URL
    """
    service: GenerateService = request.state.injector.get(GenerateService)
    
    # First do a text completion
    body= CompletionsBody(prompt = f'USER_PROMPT:"""{input.prompt}"""',
                          system_prompt = SystemPrompts.IMAGEN_SYSTEM_PROMPT, 
                          use_context = True,
                          context_filter = ContextFilter(docs_ids=None, tags = set(input.tags)),
                          stream = False)

    # TODO : make it async here
    openai_completion: OpenAICompletion = prompt_completion(request, body)    

    # Validate the OpenAICompletion object
    image_description, rag = _get_image_desc(openai_completion)
        
    result = service.generate_image_using_leonardo(image_description, input.width, input.height, input.style)
    #if len(result['generated_images']) == 0:        
        #background_tasks.add_task(service.poll_for_generated_images, result['id'])
    result['rag'] = rag
    return result

def _get_image_desc(openai_completion):
    if not openai_completion:
        raise ValueError("OpenAICompletion object is empty or None")
    
    if not openai_completion.choices:
        raise ValueError("No choices available in OpenAICompletion")
    
    first_choice = openai_completion.choices[0]
    if not first_choice:
        raise ValueError("First choice in OpenAICompletion is empty or None")
    
    if not first_choice.message:
        raise ValueError("Message in first choice is empty or None")
    
    if not first_choice.message.content:
        raise ValueError("Content in message is empty or None")
    
    # Extract the content
    image_description = first_choice.message.content.strip()
    rag = len(first_choice.sources) > 0
    return image_description, rag

    
@generate_router.post(
    "/text",
    response_model=None,
    summary="Text Generation",
    responses={200: {"model": TextgenResponse}},
    tags=["Recipes"],
)
def generate_text(request: Request, input: TextgenInput) :    
    # Do a text completion
    body= CompletionsBody(
                          prompt = f'{input.prompt}',
                          system_prompt = SystemPrompts.TEXTGEN_PROMPT,
                         )

    # TODO : make it async here
    openai_completion: OpenAICompletion = prompt_completion(request, body)    

    # Validate the OpenAICompletion object
    return openai_completion