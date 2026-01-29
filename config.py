# Editable image style configuration
IMAGE_STYLE_PROMPT = """A black and white ink illustration in the style of an underground comix flashcard. The card has a thick black rounded border. At the top, bold outlined block text reads "[TECHNOLOGY]". The central art features [SUBJECT] rendered with heavy cross-hatching, woodcut textures, and manic, grotesque facial expressions. High contrast, vintage 1930s moral panic propaganda aesthetic, satirical and surreal."""

# OpenRouter pricing (for cost tracking)
# Models: anthropic/claude-3.5-sonnet (text), google/gemini-3-pro-image-preview and openai/gpt-5-image-mini (images)
PRICING = {
    'claude_sonnet': {
        'input': 0.003 / 1000,   # per token ($3 per 1M input tokens)
        'output': 0.015 / 1000   # per token ($15 per 1M output tokens)
    },
    'gemini_flash': {
        'input': 0.000075 / 1000,   # per token (keeping for reference)
        'output': 0.0003 / 1000     # per token
    },
    'image_generation': 0.015  # per image for both gemini-3-pro-image-preview and gpt-5-image-mini
}
