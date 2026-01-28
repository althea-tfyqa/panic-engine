# THE PANIC ENGINE

Build your own deck of panic! A satirical "Moral Panic Trading Card Generator" that creates collectible soundbite cards expressing historical anxieties about any technology.

## Overview

Every technology has been feared. From writing (Socrates warned it would destroy memory) to bicycles (Victorian doctors claimed they'd cause hysteria) to smartphones (today's dopamine panic), history repeats its patterns of technophobia.

The Panic Engine generates **collectible trading cards** with punchy panic soundbites. Each card features:
- A dramatic title
- A square propaganda illustration
- A 30-35 word soundbite expressing one vivid fear
- Period-appropriate vocabulary from the era

**Build a collection**: Cards accumulate across the screen like being dealt playing cards. Generate multiple cards to see how different technologies get framed through different historical lenses.

## Features

### Quick Card Mode (Default)
- **Type & Generate**: Minimal interface—just enter a technology and click generate
- **Accumulating Collection**: Each generation adds a new card to your spread (doesn't replace previous cards)
- **Trading Card Format**: 240px wide portrait cards matching Magic/Pokemon dimensions
- **Random Rotation**: Each card gets a slight tilt (-3° to +3°) for organic "dealt" feel
- **Soundbite Generation**: Punchy 30-35 word panic statements (not long manifestos)
- **Hover Effects**: Cards "lift up" when you hover over them

### AI-Driven Intelligence
- **Auto Era Selection**: AI analyzes when the panic would occur (not when invented)
  - Antiquity: Writing, books, literacy → soul/memory/truth concerns
  - Victorian: Bicycles, trains, photography → virtue/nature/corruption fears
  - Atomic: TV, comic books, rock music → conformity/mass mind/automation worries
  - Contemporary: Social media, smartphones, streaming → dopamine/attention/capitalism critiques
- **Period-Specific Language**: Each era uses authentic vocabulary and concerns from that time period
- **Category Detection**: Auto-identifies if technology is industrial/domestic/media/medical/digital
- **Dynamic Fonts**: Five Google Fonts auto-selected based on category

### Visual Style System (CSS Zen Garden Pattern)
Three complete aesthetic modes available in footer settings:

**Indie Comics (Default)**
- Flat-color pastel illustrations
- Clean line work, contemporary graphic novel aesthetic
- Category-specific accent colors
- Daniel Clowes / Adrian Tomine vibes

**Vintage Propaganda**
- B&W ink illustrations, woodcut textures
- Heavy cross-hatching, grotesque expressions
- 1930s-50s moral panic pamphlet feel
- Underground comix influence

**Mid-Century Modern**
- Atomic age geometric shapes
- Limited color palette (navy, cyan, orange, magenta)
- Clean sophisticated 1950s-60s design
- Educational filmstrip aesthetic

### Technical Features
- **Animated Loading States**: "Thinking dots" animation while generating
- **Cost Accumulation**: Tracks total cost across all cards in session
- **Anonymous Stats**: Server-wide visit and generation tracking
- **Image Model Selection**: Choose between Gemini, GPT-5, or Flux (default) in footer
- **Minimal UI**: Top toolbar is just input + generate button; settings tucked in footer

## Tech Stack

- **Backend**: Flask (Python) with OpenRouter API proxy
- **Frontend**: Pure HTML/CSS/JS (no build step, CSS Zen Garden pattern)
- **AI Models via OpenRouter**:
  - Text Generation: `google/gemini-3-flash-preview` (~$0.0003/1K tokens)
  - Era Analysis: `google/gemini-3-flash-preview` (minimal tokens)
  - Image Generation: `black-forest-labs/flux.2-klein-4b` or `google/gemini-3-pro-image-preview` or `openai/gpt-5-image-mini` (~$0.015/image)
- **Typography**: Google Fonts (Oswald, Special Elite, Archivo Black, Courier Prime, VT323)

## Installation

### Prerequisites

- Python 3.8+
- OpenRouter API key ([get one here](https://openrouter.ai/))

### Setup

1. Clone or download this repository

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

4. Run the server:
```bash
python3 server.py 5002
```

Or use the one-click launcher:
```bash
./launch.sh
```

5. Open http://localhost:5002 in your browser

## Usage

**Quick Card Mode (Default):**

1. **Enter a technology** (e.g., "toaster", "comic books", "TikTok", "smartphones")
2. **Click GENERATE**
3. Watch your card appear with a slight random rotation
4. **Generate more!** Each new card adds to your collection
5. **Hover over cards** to see them lift up
6. **Screenshot your spread** when you have a collection you like

The AI automatically:
- Detects when the panic would historically occur (not when invented)
- Chooses appropriate era and period-specific vocabulary
- Generates a 30-35 word soundbite
- Creates a square propaganda illustration
- Applies category-specific font
- Styles card in current visual theme

**Optional Settings (footer):**
- Change visual style: Indie (default), Vintage, or Mid-Century
- Change image model: Flux (default), Gemini, or GPT-5

**Tips:**
- Try mixing modern and historical technologies to see different eras
- Generate 5-6 cards to build a collectible spread
- Modern appliances default to "contemporary" era (dopamine/attention language)
- Historical tech (bicycles, books) get their authentic era

## Cost Estimates

Per Card:
- Era Analysis (Gemini Flash, ~100 tokens): $0.0001
- Soundbite (Gemini Flash, ~50 tokens): $0.00015
- Image Generation (Flux 2 Klein): $0.015
- **Total per card: ~$0.0153**

Session Costs:
- 10 cards: $0.15
- 20 cards: $0.31
- 50 cards: $0.77

Cost accumulates across all cards in your session and displays in the footer.

## Project Structure

```
panic-engine/
├── server.py                 # Flask backend with API proxies, era analysis, dual image prompts
├── app.js                    # Frontend logic, style switcher, dynamic card insertion, loading states
├── index.html                # Main interface with style selector
├── styles.css                # Base styling + vintage propaganda aesthetic
├── styles-indie.css          # Contemporary indie comics aesthetic overlay
├── config.py                 # Dual image style prompts + model pricing
├── requirements.txt          # Python dependencies
├── .env                      # API keys (not in repo)
├── usage_stats.json          # Server-wide metrics
├── cleanup-ports.sh          # Port cleanup utility
├── launch.sh                 # One-click startup
├── font-preview.html         # Design reference for all fonts/eras
├── DESIGN_NOTES.md          # Visual reference analysis
└── images/
    ├── placeholder-visualizing-panic.jpg  # Loading state card
    ├── moodboard.jpg                      # Design reference (indie comics)
    └── moral-panic-*.jpg                  # Reference propaganda cards
```

## Configuration

### Visual Styles

The app uses a **CSS Zen Garden pattern** with two complete visual themes:
- Base styles in `styles.css` (vintage propaganda)
- Indie overlay in `styles-indie.css` (loaded with `disabled` attribute)
- JavaScript toggles stylesheet on/off via style switcher dropdown

### Image Prompts

Edit `config.py` to customize image generation for each visual style:

```python
IMAGE_PROMPTS = {
    'vintage': """Your vintage woodcut style prompt...""",
    'indie': """Your contemporary indie comics prompt..."""
}
```

### Image Model Testing

Use the model selector dropdown to test different image generation models:
- `google/gemini-3-pro-image-preview` (better for contemporary comics with text)
- `openai/gpt-5-image-mini` (fast, clean lettering)
- `black-forest-labs/flux.2-klein-4b` (detailed illustrations)

### Port

Change the default port (5002) by passing as argument:

```bash
python3 server.py 8080
```

## Design Evolution

The Panic Engine went through a fascinating aesthetic journey:

1. **Initial concept**: Cyberpunk terminal (neon green on black, Matrix vibes)
2. **Visual reference analysis**: Study of actual 1930s-50s moral panic pamphlets revealed cream paper, black ink, woodcut aesthetic
3. **Vintage propaganda mode**: Complete redesign to match historical references (thick borders, grotesque illustrations, typewriter fonts)
4. **Contemporary expansion**: Added second visual style inspired by indie comics (Daniel Clowes, Adrian Tomine) with pastel colors and flat illustration
5. **Dynamic typography**: Evolved from single typewriter font to 5-font system auto-selected by technology category
6. **AI-driven UX**: Removed user-facing era dropdown in favor of automatic AI selection based on technology context

The result: Same functionality, two completely different aesthetic experiences that both serve the satirical concept.

## Ubuntu Deployment

For deployment on a department server:

1. Upload project files (ensure `.git` folder excluded if needed)
2. Set up `.env` with production API key
3. Install dependencies: `pip3 install -r requirements.txt`
4. Run server: `python3 server.py 80` (or your preferred port)
5. Configure firewall to allow port access
6. Optional: Set up as systemd service for auto-restart
7. Consider nginx reverse proxy for production use

## Privacy & Data

- **No user data stored**: Completely stateless and anonymous
- **Usage tracking**: Only aggregates (visits, generations, costs) stored in `usage_stats.json`
- **Images**: Generated dynamically, not saved server-side
- **No cookies, no analytics, no tracking**
- **API calls**: Proxied through backend to keep API keys secure

## Rhetorical Framework

The manifesto generator uses three core "Rhetorical Pillars" that MUST be present in every generated manifesto (strengthened instruction to ensure consistency):

1. **SUBSTITUTION**: Technology replaces human capacity (doesn't aid it)
2. **AGENT OF ATROPHY**: Technology is predatory; user is passive victim
3. **REAL vs FAKE**: Romanticize difficulty vs demonize ease

Each historical era applies these pillars through period-specific anxieties and vocabulary:
- **Antiquity**: Soul, memory, truth, virtue corruption
- **Victorian**: Moral fiber, nature, hysteria, domestic order
- **Atomic Age**: Mass mind, conformity, automation, standardization
- **Contemporary**: Attention economy, dopamine, brain rot, surveillance capitalism

## Technical Innovations

This project showcases several interesting patterns:

1. **Accumulating Collection Interface**: Cards append to the spread rather than replacing—builds a collection over time
2. **Random Rotation for Organic Feel**: Each card gets -3° to +3° rotation to mimic physical card dealing
3. **Trading Card Aspect Ratio**: 240px wide portrait format matches Magic/Pokemon card proportions
4. **AI-Driven Era Detection**: "When did the panic happen?" logic, not "when was it invented?"—crucial for authentic tone
5. **Soundbite Constraints**: 40-word maximum forces distillation to essence—better output than 150+ words
6. **CSS Zen Garden Pattern**: Three visual themes over same HTML via stylesheet toggling
7. **Dynamic Typography**: Five fonts auto-selected based on AI-analyzed technology category
8. **Style-Responsive Backend**: Server generates different image prompts for each visual style
9. **Animated Loading Dots**: CSS-only "..." animation provides feedback without JS timers
10. **Progressive Defaults**: Minimal UI with best defaults (Indie + Flux); settings hidden in footer
11. **Flex Grid Spread**: Cards naturally distribute across available screen space
12. **Period-Specific Vocabulary**: Strengthened prompts ensure era-authentic language (no Victorian words for TikTok)

## Examples

Try building a deck with these:
- **Classic Panics**: "television", "comic books", "jazz music", "video games", "rock and roll"
- **Modern Anxieties**: "TikTok", "smartphones", "streaming", "social media", "AI chatbots"
- **Mundane Tech**: "toaster", "microwave", "hot water", "bicycles", "escalators"
- **Media Formats**: "podcasts", "memes", "e-books", "audiobooks", "vlogs"
- **Absurdist**: "left-handed pencils", "sandwiches", "the color blue", "bubble wrap"

**Pro tip**: Mix eras in one session to see vocabulary shifts—generate "books" (antiquity language) next to "TikTok" (contemporary language) for striking contrast.

## Design Philosophy

**Collections > Single Artifacts**: The shift from "generate one manifesto" to "build a deck of cards" fundamentally changes engagement. Collections create replayability (users want variety), comparison (cards side-by-side show how framing differs), and shareability (screenshot a spread of 6 cards beats sharing one text blob). Each addition feels like progress, not replacement.

**Constraints Drive Quality**: Forcing soundbites to 40 words made output sharper. The AI can't ramble—it distills to the single most vivid image or claim. Sometimes the best way to improve AI output is to restrict it more severely.

**Defaults as Design**: Moving settings to the footer isn't just clean UI—it's designing the default experience. By choosing Indie + Flux, we're saying "this is the intended aesthetic." Power users can change it, but most users get the curated experience. This is generous software: make the right choices so users don't have to think.

**Physical Metaphors in Digital UI**: Random rotation, hover lift, card accumulation—these invoke the physical experience of dealing and collecting trading cards. Digital doesn't have to feel digital. Skeuomorphism serves meaning when it taps into existing mental models people already understand.

**Era Timing Matters**: Contemporary technologies need contemporary vocabulary. Using Victorian language for smartphones is funny once, but breaks immersion. The panic needs to sound like it came from the right time period to feel authentic—that means defaulting post-1970 tech to "contemporary" era.

## License

MIT License - Free to use, modify, and distribute.

## Credits

Built by **Althea** during a creative AI sabbatical (2026).

Inspired by recurring patterns in technophobia across human history—from Socrates fearing writing would destroy memory, to Victorian doctors warning bicycles would cause hysteria, to contemporary dopamine panic about smartphones. History repeats its patterns; this engine makes that repetition visible.

Visual references: 1930s-50s moral panic pamphlets, underground comix, contemporary indie comics (Daniel Clowes, Adrian Tomine).

Technical patterns learned from: tarot oracle project (API proxy), Crown Affair (image generation), cross-project debugging sessions.
