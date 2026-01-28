# THE PANIC ENGINE

A satirical "Moral Panic Generator" that uses AI to create alarmist manifestos against any user-inputted technology, filtered through historical era anxieties—with dual visual styles and dynamic typography.

## Overview

Every technology has been feared. From writing (Socrates warned it would destroy memory) to bicycles (Victorian doctors claimed they'd cause hysteria) to smartphones (today's dopamine panic), history repeats its patterns of technophobia.

The Panic Engine lets you generate your own moral panic manifesto and propaganda card for any technology—real or imagined. The AI automatically chooses the appropriate historical era and visual style based on the technology itself, creating unique aesthetic experiences every time.

## Features

### Core Generation
- **AI-Driven Era Selection**: The engine automatically analyzes your technology and chooses the most appropriate historical lens (antiquity/victorian/atomic/contemporary)
- **Dynamic Manifesto Generation**: Alarmist text using era-specific rhetorical patterns and contemporary reading formats (4-6 short, scannable paragraphs)
- **Propaganda Card Illustrations**: AI-generated images styled to match the selected visual aesthetic

### Visual Style System (CSS Zen Garden Pattern)
Choose between two complete aesthetic modes:

**Style 1: Vintage Propaganda (Default)**
- Cream paper (#f5f1e8) with black ink aesthetic
- Heavy borders, woodcut textures, B&W illustrations
- 1930s-50s moral panic pamphlet feel
- Grotesque expressions, underground comix influence

**Style 2: Contemporary Indie Comics**
- White backgrounds with pastel accent colors
- Flat-color illustrations with clean line work
- Gradient headers (blue→pink, yellow tones)
- Category-specific accent colors (industrial/grey, domestic/yellow, media/pink, medical/blue, digital/purple)
- Daniel Clowes / Adrian Tomine vibes

### Dynamic Typography System
Five Google Fonts automatically selected based on technology category:
- **Industrial** (engines, machinery): Oswald - bold condensed sans
- **Domestic** (appliances, household): Special Elite - typewriter feel
- **Media** (books, comics, TV): Archivo Black - bold headlines
- **Medical** (pills, procedures): Courier Prime - clinical coldness
- **Digital** (algorithms, phones): VT323 - retro computer terminal

Every generation looks visually distinct!

### User Experience
- **Loading State Animations**: Custom "VISUALIZING PANIC" placeholder with warm yellow/red pulsing glow
- **Magazine-Style Layout**: Card floats within manifesto text (old-school editorial design)
- **Real-Time Cost Tracking**: Transparent API usage display
- **Anonymous Usage Stats**: Track total generations and server costs
- **No friction UX**: Type technology name → AI does everything else

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

1. **Enter a technology** (e.g., "The Toaster", "Email", "Comic Books", "Hot Water")
2. **Click "GENERATE PANIC"** - The AI automatically:
   - Analyzes the technology to determine invention era/cultural context
   - Selects the most appropriate historical era for moral panic framing
   - Chooses matching font based on technology category
   - Generates manifesto with era-specific rhetoric
   - Creates propaganda card styled to match selected visual mode
3. **Optional**: Toggle between Vintage Propaganda and Indie Comics styles using the style switcher
4. **Copy manifesto text** or enjoy the visual card

## Cost Estimates

- Era Analysis (Gemini Flash, ~100 tokens): $0.0001
- Manifesto (Gemini Flash, ~300 tokens): $0.0003
- Image Generation: $0.015
- **Total per generation: ~$0.0154**

At 50 generations/day: ~$0.77/day or ~$23/month
At 20 generations/day: ~$0.31/day or ~$9/month

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

1. **AI-Driven UX**: Let AI make categorical decisions (era, font, category) instead of user dropdowns → less friction, more surprise
2. **CSS Zen Garden Pattern**: Multiple visual themes over same HTML structure with stylesheet toggling
3. **Dynamic Typography**: Font automatically selected based on AI-analyzed technology category
4. **Style-Responsive Backend**: Server generates different image prompts based on frontend style selection
5. **Progressive Enhancement**: Show manifesto immediately even if image generation is slow/fails
6. **Contemporary Reading Patterns**: 4-6 short paragraphs instead of dense text walls
7. **Loading State Choreography**: Animated placeholder → smooth transition to loaded state
8. **Context Extraction**: Backend extracts structural elements (title, outrage phrase) from AI text for reuse in image prompts

## Examples

Try these technologies and media:
- **Classic Panics**: "The Telephone", "Television", "Comic Books", "Jazz Music", "Video Games"
- **Mundane Objects**: "The Toaster", "Spoon", "Umbrellas", "Shoelaces", "Hot Water"
- **Modern Tech**: "The Cloud", "NFTs", "AI Chatbots", "Social Media", "Smartphones"
- **Media Formats**: "Pulp Fiction", "Podcasts", "TikTok", "Memes", "E-Books"
- **Absurdist**: "Left-Handed Pencils", "Sandwiches", "The Color Blue", "Tamagotchi"

## Design Philosophy

**Automated decision-making as UX**: The shift from user-controlled era selection to AI-automatic is intentional. Instead of "which era do you want?" (requires knowledge, creates decision paralysis), the system figures it out. Users provide minimal input (technology name) and get maximal output (era-appropriate manifesto in matching font with styled card). This is **generous software design**: do the hard work so users don't have to.

**Visual variety as engagement**: Every generation looks different because font changes based on category, era shifts tone, style switcher offers two aesthetics, and illustrations are unique. This creates compulsive replayability—users want to see how different technologies get styled.

**Contemporary reading patterns**: Short paragraphs, scannable text, visual breaks aren't dumbing down—they're respecting how people consume content in 2026. The manifesto is more likely to be read because it's formatted for modern attention spans.

**CSS as design system**: The Zen Garden approach means the same HTML can look radically different. This enables A/B testing aesthetics, user preferences, seasonal themes, and future expansions without touching backend logic.

## License

MIT License - Free to use, modify, and distribute.

## Credits

Built by **Althea** during a creative AI sabbatical (2026).

Inspired by recurring patterns in technophobia across human history—from Socrates fearing writing would destroy memory, to Victorian doctors warning bicycles would cause hysteria, to contemporary dopamine panic about smartphones. History repeats its patterns; this engine makes that repetition visible.

Visual references: 1930s-50s moral panic pamphlets, underground comix, contemporary indie comics (Daniel Clowes, Adrian Tomine).

Technical patterns learned from: tarot oracle project (API proxy), Crown Affair (image generation), cross-project debugging sessions.
