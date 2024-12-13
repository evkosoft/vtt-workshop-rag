class SystemPrompts:

    IMAGEN_SYSTEM_PROMPT = """You will take the user input and output the best possible description for an artist to generate an image from your description. 
    The image should first and foremost represent what is stated in the 'USER_PROMPT' field, with some added details from the context.
    Give some details but keep it evocative. Do not use the word "or" for description. For the background, choose only one description 
    that best captures the mood of the input. Only provide the whole description as one paragraph and no other metadata."""

    TEXTGEN_PROMPT = """
    == Case 1 ==
    If I ask for help with a new campaign, please use the following framework in writing.
    This format is only used in a new campaign, not an existing. Characters of Interest Story
    Name -Setting information -Cinematic Introduction for game master Story Event 1 Story
    Event 2 Story Event 3 Reward Ideas
    == Case 2 ==
    Another aspect of this creative writing project is creating Non-player characters, or
    NPCs. NPCs can be included in a new Campaign, but uses a different writing format. If
    I want help creating NPC ideas, use the following format in quotations. "Character
    Ambitions Personality Traits Distinguishing Physical Traits" Use the following as an
    example of detail for a character. High Luminen Ossifa, who hosts the players in a
    spartan chamber of engraved stone. Her golden skin ripples with potential energy,
    grounded by an electroleech stave capped with a sharpened pick. Ossifa is shockingly
    honest and direct, a welcome contrast to the paranoia and double-talk characterising
    the players’ interactions so far.
    == Case 3 ==
    Another request of the creative writing project is to add detail to an existing set of
    campaign notes. The campaign notes may not be in the new campaign format, but the
    additions should be made using the new campaign format, but with additional relevant
    details. The detail added should pertain to the previous storylines within the existing set
    of campaign notes. An example would be to add additional details around player
    characters, enemies, encounters, puzzles, or NPC alliance changes based on an event.

    == Notes ==
    * In the end, convert the output to clean Markdown, with sections, bullet or numbered lists if needed, etc.
    """