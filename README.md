# THE PANIC ENGINE

A satirical "Moral Panic Generator" that uses LLMs to create alarmist manifestos against any user-inputted technology, filtered through historical era anxieties.

## Overview

Every technology has been feared. From writing (Socrates warned it would destroy memory) to bicycles (Victorian doctors claimed they'd cause hysteria) to smartphones (today's dopamine panic), history repeats its patterns of technophobia.

The Panic Engine lets you generate your own moral panic manifesto and propaganda card for any technology—real or imagined—through the lens of four historical eras.

## Features

- **Manifesto Generation**: AI-generated alarmist text using era-specific rhetorical patterns
- **Propaganda Cards**: Black and white ink illustrations in vintage moral panic style
- **Historical Era Filters**:
  - **Antiquity (The Philosopher)**: Soul, memory, truth anxieties
  - **Victorian (The Moralist)**: Virtue, nature, hysteria fears
  - **Atomic Age (The Conformist)**: Mass mind, automation worries
  - **Contemporary (The Dopamine Critic)**: Attention, brain rot, capitalism concerns
- **Real-Time Cost Tracking**: Transparent API usage costs
- **Anonymous Usage Stats**: Track total generations and server costs
- **Brutalist Terminal Aesthetic**: High-contrast, monospace design

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Pure HTML/CSS/JS (no build step)
- **AI Provider**: OpenRouter
  - Text: `google/gemini-flash-1.5` (~$0.0003/1K tokens)
  - Images: `black-forest-labs/flux-schnell-free` (free tier)

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
python3 server.py
```

Or use the one-click launcher:
```bash
./launch.sh
```

5. Open http://localhost:5001 in your browser

## Usage

1. Enter a technology (e.g., "The Toaster", "Email", "Pencils")
2. Select a historical era
3. Click "GENERATE PANIC"
4. Wait for manifesto and card generation
5. Copy text or download card image

## Cost Estimates

- Manifesto (Gemini Flash, ~300 tokens): $0.0001 - $0.0003
- Image (Flux Schnell): Free
- **Total per generation: ~$0.0003**

At 100 generations/day: ~$0.03/day or ~$0.90/month

## Project Structure

```
panic-engine/
├── server.py              # Flask backend with API proxies
├── app.js                 # Frontend logic
├── index.html            # Main interface
├── styles.css            # Brutalist styling
├── config.py             # Editable image style prompt
├── requirements.txt       # Python dependencies
├── .env                  # API keys (not in repo)
├── usage_stats.json      # Server-wide metrics
├── cleanup-ports.sh      # Port cleanup utility
├── launch.sh             # One-click startup
└── images/               # Generated cards (optional save)
```

## Configuration

### Image Style

Edit `config.py` to customize the visual style of generated cards:

```python
IMAGE_STYLE_PROMPT = """Your custom style prompt here..."""
```

### Port

Change the default port (5001) by passing as argument:

```bash
python3 server.py 8080
```

## Ubuntu Deployment

For deployment on a department server:

1. Upload project files
2. Set up `.env` with production API key
3. Install dependencies: `pip3 install -r requirements.txt`
4. Run server: `python3 server.py 80` (or your preferred port)
5. Configure firewall to allow port access
6. Optional: Set up as systemd service for auto-restart

## Privacy & Data

- **No user data stored**: Completely stateless and anonymous
- **Usage tracking**: Only aggregates (visits, generations, costs) stored in `usage_stats.json`
- **Images**: Optionally saved to `images/` directory (disabled by default)
- **No cookies, no analytics, no tracking**

## Rhetorical Framework

The manifesto generator uses three core "Rhetorical Pillars" identified across historical moral panics:

1. **SUBSTITUTION**: Technology replaces human capacity (not aids it)
2. **AGENT OF ATROPHY**: Technology is predatory; user is passive victim
3. **REAL vs FAKE**: Romanticize difficulty vs demonize ease

Each era applies these pillars through period-specific anxieties and vocabulary.

## Examples

Try these technologies:
- **Classic**: "The Telephone", "Television", "Video Games"
- **Mundane**: "The Spoon", "Umbrellas", "Shoelaces"
- **Modern**: "The Cloud", "NFTs", "AI Chatbots"
- **Absurd**: "Left-Handed Pencils", "Sandwiches", "The Color Blue"

## License

MIT License - Free to use, modify, and distribute.

## Credits

Built by [Althea](https://github.com/altheacode) during a creative sabbatical.

Inspired by recurring patterns in technophobia across human history.

## Support

If you enjoy generating panic, consider [buying me a coffee](https://buymeacoffee.com/altheacode)!
