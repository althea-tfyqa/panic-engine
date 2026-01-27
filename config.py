# Editable image style configuration
IMAGE_STYLE_PROMPT = """A black and white ink illustration in the style of an underground comix flashcard. The card has a thick black rounded border. At the top, bold outlined block text reads "[TECHNOLOGY]". The central art features [SUBJECT] rendered with heavy cross-hatching, woodcut textures, and manic, grotesque facial expressions. High contrast, vintage 1930s moral panic propaganda aesthetic, satirical and surreal."""

# OpenRouter pricing (for cost tracking)
# Models: google/gemini-3-flash-preview (text), google/gemini-3-pro-image-preview and openai/gpt-5-image-mini (images)
PRICING = {
    'gemini_flash': {
        'input': 0.000075 / 1000,   # per token
        'output': 0.0003 / 1000     # per token
    },
    'image_generation': 0.015  # per image for both gemini-3-pro-image-preview and gpt-5-image-mini
}
