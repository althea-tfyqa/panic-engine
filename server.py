import json
import os
import sys
from pathlib import Path
from datetime import datetime
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from config import IMAGE_STYLE_PROMPT, PRICING

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
STATS_FILE = Path(__file__).parent / 'usage_stats.json'
IMAGES_DIR = Path(__file__).parent / 'images'

# Usage tracking functions
def load_stats():
    """Load usage stats from JSON file, create if doesn't exist"""
    if not STATS_FILE.exists():
        return {'visits': 0, 'generations': 0, 'total_cost': 0.0}
    with open(STATS_FILE, 'r') as f:
        return json.load(f)

def save_stats(stats):
    """Save usage stats to JSON file"""
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def increment_visits():
    stats = load_stats()
    stats['visits'] += 1
    save_stats(stats)
    return stats

def increment_generation(cost):
    stats = load_stats()
    stats['generations'] += 1
    stats['total_cost'] += cost
    save_stats(stats)
    return stats

def calculate_text_cost(input_tokens, output_tokens):
    """Calculate cost for text generation"""
    input_cost = input_tokens * PRICING['gemini_flash']['input']
    output_cost = output_tokens * PRICING['gemini_flash']['output']
    return input_cost + output_cost

def extract_image_url(api_response):
    """Extract image URL from OpenRouter response (handles multiple formats)"""
    # Try choices[0].message.images (Flux format)
    if 'choices' in api_response and len(api_response['choices']) > 0:
        message = api_response['choices'][0].get('message', {})

        # Check for images array (Flux Klein format)
        images = message.get('images', [])
        if images and len(images) > 0:
            image_url_obj = images[0].get('image_url', {})
            url = image_url_obj.get('url', '')
            if url:
                print(f"✅ Found image URL in images array")
                return url

        # Check if content is a URL (fallback)
        content = message.get('content', '')
        if content and (content.startswith('http') or content.startswith('data:image')):
            print(f"✅ Found image URL in content")
            return content

    # Try data array format (other providers)
    if 'data' in api_response and len(api_response['data']) > 0:
        data_item = api_response['data'][0]
        if 'url' in data_item:
            return data_item['url']
        if 'b64_json' in data_item:
            return f"data:image/png;base64,{data_item['b64_json']}"

    return None

def format_manifesto_as_html(text):
    """Convert manifesto text to styled HTML, stripping all markdown formatting"""
    import re

    lines = text.strip().split('\n')
    html_parts = []

    # Check if first line is a title (all caps or starts with special formatting)
    if lines:
        first_line = lines[0].strip()
        # Remove ALL markdown formatting from title
        first_line = re.sub(r'\*\*(.*?)\*\*', r'\1', first_line)
        first_line = re.sub(r'\*(.*?)\*', r'\1', first_line)

        # If it looks like a title (all caps, short, or has special chars)
        if (first_line.isupper() or len(first_line) < 80) and first_line:
            html_parts.append(f'<h3>{first_line}</h3>')
            remaining_lines = lines[1:]
        else:
            remaining_lines = lines

        # Group remaining lines into paragraphs
        current_paragraph = []
        for line in remaining_lines:
            line = line.strip()
            if line:
                # STRIP all markdown bold/italic formatting (no conversion to HTML)
                line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
                line = re.sub(r'\*(.*?)\*', r'\1', line)
                current_paragraph.append(line)
            elif current_paragraph:
                # Empty line signals end of paragraph
                html_parts.append(f'<p>{" ".join(current_paragraph)}</p>')
                current_paragraph = []

        # Don't forget last paragraph
        if current_paragraph:
            html_parts.append(f'<p>{" ".join(current_paragraph)}</p>')

    return '\n'.join(html_parts)

def analyze_technology(technology):
    """Analyze technology to determine era and visual category"""
    print(f"\n=== ANALYZING TECHNOLOGY: {technology} ===")
    try:
        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5001',
            'X-Title': 'The Panic Engine'
        }

        prompt = f"""Analyze this technology: "{technology}"

Determine which historical era would produce the MOST panic about this technology.

ERA DEFINITIONS (choose ONE):
   - antiquity (Ancient Greece/Rome, pre-1800) - ONLY for: writing, books, literacy, philosophy, scrolls
   - victorian (19th century, 1800-1899) - for: bicycles, trains, photography, telegraphs, sewing machines, typewriters
   - atomic (20th century, 1900-1999) - for: TV, radio, comic books, rock music, video games, microwaves, processed foods, suburbs, computers (pre-internet)
   - contemporary (21st century, 2000-now) - for: social media, smartphones, streaming, AI, TikTok, modern internet technologies

CRITICAL RULES:
- Anything invented after 2000 = contemporary
- Anything commonly used today (smartphones, social media, streaming) = contemporary
- Video games = atomic (panic was 1970s-1990s arcade/console era)
- Internet/web = atomic if referring to 1990s dialup, contemporary if referring to modern social media

Respond ONLY in this exact format (no extra text):
era: [era name]"""

        payload = {
            'model': 'google/gemini-3-flash-preview',
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }

        print("Calling OpenRouter to analyze technology...")
        response = requests.post(OPENROUTER_URL, json=payload, headers=headers)
        print(f"Analysis response status: {response.status_code}")

        if response.status_code == 429:
            print(f"❌ RATE LIMIT HIT in analysis - Response: {response.text}")
            return {'era': 'contemporary', 'category': 'domestic'}

        response.raise_for_status()

        result = response.json()
        analysis_text = result['choices'][0]['message']['content'].strip().lower()
        print(f"Analysis result: {analysis_text}")

        # Parse the response
        era = 'contemporary'

        for line in analysis_text.split('\n'):
            if 'era:' in line:
                era_text = line.split('era:')[1].strip()
                valid_eras = ['antiquity', 'victorian', 'atomic', 'contemporary']
                for valid_era in valid_eras:
                    if valid_era in era_text:
                        era = valid_era
                        break

        print(f"✅ Analysis complete: era={era}")
        return {'era': era}

    except Exception as e:
        print(f"Error analyzing technology: {str(e)}")
        return {'era': 'contemporary'}

# Routes
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Return server-wide usage statistics"""
    return jsonify(load_stats())

@app.route('/api/track-visit', methods=['POST'])
def track_visit():
    """Increment visit counter"""
    print("📊 Visit tracked")
    stats = increment_visits()
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/generate-manifesto', methods=['POST'])
def generate_manifesto():
    """Generate panic manifesto using Gemini Flash"""
    try:
        data = request.json
        technology = data.get('technology', 'technology')

        print(f"\n=== MANIFESTO REQUEST ===")
        print(f"Technology: {technology}")

        # AI analyzes technology to determine era
        analysis = analyze_technology(technology)
        era = analysis['era']

        print(f"AI analysis: era={era}")

        # Build era-specific system prompt
        era_prompts = {
            'antiquity': {
                'name': 'An Ancient Philosopher',
                'century': 'Ancient Greece/Rome (pre-1800)',
                'focus': 'The Soul, Memory, Truth, The Gods, Virtue',
                'anxiety': 'Illusion vs Reality, corruption of the spirit',
                'keywords': 'soul, memory, simulacrum, shadow, spirit, void, the gods, virtue, corruption',
                'forbidden': 'NO modern words: brain, dopamine, algorithm, content, product, automation, Victorian language'
            },
            'victorian': {
                'name': 'A Victorian Moralist',
                'century': '19th century (1800s)',
                'focus': 'Moral Fiber, Nature, Propriety, Hygiene, Feminine Virtue',
                'anxiety': 'Hysteria, Unnatural Speed, Moral Corruption',
                'keywords': 'vapors, constitution, unseemly, artificial, godless, hysteria, improper, unnatural, degeneracy',
                'forbidden': 'NO ancient Greek terms, NO 20th/21st century words like dopamine, algorithm, automation, content'
            },
            'atomic': {
                'name': 'A Mid-Century Social Critic',
                'century': '20th century (1900-1999)',
                'focus': 'Individualism, Mass Culture, Conformity, The Machine',
                'anxiety': 'Becoming robots, loss of humanity, brainwashing, standardization',
                'keywords': 'automation, programming, conformity, mass-produced, the machine, standardized, mechanized, dehumanizing',
                'forbidden': 'NO 21st century language: dopamine, algorithm, content, product (as in "you are the product"), brain rot'
            },
            'contemporary': {
                'name': 'A 21st Century Digital Critic',
                'century': '21st century (2000-now)',
                'focus': 'Attention Economy, Brain Chemistry, Platform Capitalism, Surveillance',
                'anxiety': 'Brain rot, dopamine hijacking, algorithmic manipulation, you are the product',
                'keywords': 'algorithm, dopamine, content, engagement, the product, brain rot, surveillance capitalism, engineered addiction, infinite scroll',
                'forbidden': 'NO Victorian language (vapors, hysteria), NO ancient philosophy terms'
            }
        }

        era_data = era_prompts.get(era, era_prompts['contemporary'])

        system_prompt = f"""You are {era_data['name']} writing in the {era_data['century']}.

CRITICAL - RHETORICAL PILLARS (you must incorporate ALL THREE):

1. SUBSTITUTION: The technology REPLACES human capacity, not aids it. Frame the friction it removes as the source of virtue.

2. AGENT OF ATROPHY: The technology is predatory. It "seduces," "demands," "steals." The user is passive victim.

3. REAL vs FAKE: Romanticize the difficulty of the old way (blood, sweat, vitality) vs the sterility of the new way (plastic, grid, dead).

VOCABULARY ENFORCEMENT - THIS IS CRITICAL:
- You are writing in the {era_data['century']}
- Focus ONLY on: {era_data['focus']}
- Core anxieties: {era_data['anxiety']}
- REQUIRED keywords to use: {era_data['keywords']}
- {era_data['forbidden']}

You MUST write ONLY in the vocabulary and concerns of the {era_data['century']}. Using vocabulary from other eras is FORBIDDEN and will ruin the output.

Write a 200-300 word manifesto against this technology. Be harsh, alarmist, and convincing. Ground your argument in the rhetorical pillars and make it specific to {era} anxieties using ONLY {era} vocabulary. No hedging, no nuance—pure panic.

Start with a bold, dramatic title (like "THE SCOURGE OF THE {technology.upper()}" or "{technology.upper()}: A CRISIS OF CIVILIZATION"), then write the manifesto body.

IMPORTANT FORMATTING:
- Use SHORT paragraphs (2-4 sentences each) for contemporary readability
- Include frequent line breaks between paragraphs
- Write 4-6 short paragraphs instead of 2-3 long ones
- Each paragraph should be punchy and focused
- Use vivid, intense language from the {era_data['century']}
- DO NOT use any markdown formatting (no **bold**, no *italics*). Write in plain text only."""

        # Call OpenRouter API
        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5001',
            'X-Title': 'The Panic Engine'
        }

        payload = {
            'model': 'google/gemini-3-flash-preview',
            'messages': [
                {'role': 'user', 'content': f'{system_prompt}\n\nWrite a manifesto against: {technology}'}
            ]
        }

        print(f"Calling OpenRouter for manifesto generation...")
        response = requests.post(OPENROUTER_URL, json=payload, headers=headers)
        print(f"✅ Manifesto response status: {response.status_code}")

        if response.status_code == 429:
            print(f"❌ RATE LIMIT HIT - Response: {response.text}")
            return jsonify({'error': 'Rate limit exceeded. Please wait a moment and try again.'}), 429

        response.raise_for_status()

        result = response.json()
        manifesto_text = result['choices'][0]['message']['content']

        # Convert to HTML
        manifesto_html = format_manifesto_as_html(manifesto_text)

        # Extract token usage
        usage = result.get('usage', {})
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)

        # Calculate cost
        cost = calculate_text_cost(input_tokens, output_tokens)

        # Update stats
        increment_generation(cost)

        return jsonify({
            'manifesto': manifesto_html,
            'manifesto_plain': manifesto_text,  # For copying
            'tokens': {
                'input': input_tokens,
                'output': output_tokens
            },
            'cost': cost,
            'era': era  # Return the chosen era for image generation and font selection
        })

    except Exception as e:
        print(f"Error generating manifesto: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-quick-card', methods=['POST'])
def generate_quick_card():
    """Generate quick panic card: short text + square image (no text in image)"""
    try:
        data = request.json
        technology = data.get('technology', 'technology')
        model = data.get('model', 'google/gemini-3-pro-image-preview')
        visual_style = data.get('visualStyle', 'vintage')

        print(f"\n=== QUICK CARD REQUEST ===")
        print(f"Technology: {technology}")

        # AI analyzes technology to determine era
        analysis = analyze_technology(technology)
        era = analysis['era']

        print(f"AI analysis: era={era}")

        # Build era-specific system prompt for SHORT soundbite
        era_prompts = {
            'antiquity': {
                'name': 'An Ancient Philosopher',
                'century': 'Ancient Greece/Rome',
                'focus': 'The Soul, Memory, Truth',
                'keywords': 'soul, memory, simulacrum, shadow, spirit, void, virtue, corruption',
                'forbidden': 'NO modern words: brain, dopamine, algorithm, automation, vapors, hysteria'
            },
            'victorian': {
                'name': 'A Victorian Moralist',
                'century': '19th century',
                'focus': 'Moral Fiber, Propriety, Virtue',
                'keywords': 'vapors, constitution, unseemly, artificial, hysteria, improper, degeneracy',
                'forbidden': 'NO ancient or modern terms: soul, simulacrum, dopamine, algorithm, automation'
            },
            'atomic': {
                'name': 'A Mid-Century Critic',
                'century': '20th century',
                'focus': 'Individualism, Conformity, The Machine',
                'keywords': 'automation, programming, conformity, the machine, standardized, dehumanizing',
                'forbidden': 'NO 21st century words: dopamine, algorithm, content, brain rot'
            },
            'contemporary': {
                'name': 'A Digital Age Critic',
                'century': '21st century',
                'focus': 'Attention Economy, Brain Chemistry, Surveillance',
                'keywords': 'algorithm, dopamine, content, engagement, brain rot, surveillance, addiction, infinite scroll',
                'forbidden': 'NO Victorian or ancient language: vapors, hysteria, soul, simulacrum'
            }
        }

        era_data = era_prompts.get(era, era_prompts['contemporary'])

        system_prompt = f"""You are {era_data['name']} writing in the {era_data['century']}.

Write a SOUNDBITE against {technology}. Maximum 40 words total.

Your response MUST have this exact structure:
- Line 1: Dramatic all-caps title (3-5 words)
- Line 2: Single punchy sentence (30-35 words) expressing ONE vivid fear

VOCABULARY ENFORCEMENT - THIS IS CRITICAL:
- You are writing in the {era_data['century']}
- Focus ONLY on: {era_data['focus']}
- REQUIRED keywords to use: {era_data['keywords']}
- {era_data['forbidden']}

You MUST write ONLY in the vocabulary of the {era_data['century']}. Using vocabulary from other eras is FORBIDDEN.
Make it visceral and dramatic. ONE sentence only for the soundbite."""

        user_prompt = f"Write a panic manifesto against: {technology}"

        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5001',
            'X-Title': 'The Panic Engine - Quick Card'
        }

        payload = {
            'model': 'google/gemini-3-flash-preview',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
        }

        print("Calling OpenRouter for short manifesto generation...")
        response = requests.post(OPENROUTER_URL, json=payload, headers=headers)

        if response.status_code == 429:
            print(f"❌ RATE LIMIT HIT - Response: {response.text}")
            return jsonify({'error': 'Rate limit exceeded. Please wait a moment.'}), 429

        response.raise_for_status()

        result = response.json()
        manifesto_text = result['choices'][0]['message']['content'].strip()

        # Track token usage
        usage = result.get('usage', {})
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)

        text_cost = (input_tokens * PRICING['gemini_flash']['input'] +
                    output_tokens * PRICING['gemini_flash']['output'])

        print(f"✅ Short manifesto generated ({output_tokens} tokens)")

        # Extract title and passage
        lines = manifesto_text.split('\n', 1)
        title = lines[0].strip()
        passage = lines[1].strip() if len(lines) > 1 else manifesto_text

        # Generate SQUARE image with NO TEXT - just the visual
        # White background so it blends with card
        era_styles = {
            'antiquity': 'ancient Greek pottery patterns, marble columns',
            'victorian': 'ornate Victorian frames, steam engines',
            'atomic': 'retro 1950s advertising, nuclear symbols',
            'contemporary': 'smartphone screens, wifi symbols'
        }

        era_visual_style = era_styles.get(era, era_styles['contemporary'])

        # Build image prompt - SQUARE format, NO TEXT, white background
        image_prompt = f"""Create a square propaganda illustration of {technology}.

REQUIREMENTS:
- SQUARE FORMAT (1:1 aspect ratio, not portrait/landscape)
- WHITE BACKGROUND (clean white, #FFFFFF)
- NO TEXT - illustration only
- Centered subject
- {era_visual_style}

STYLE: {visual_style} aesthetic - {"vintage 1930s propaganda, black & white ink, heavy cross-hatching" if visual_style == "vintage" else "contemporary indie comics, flat colors, pastels" if visual_style == "indie" else "mid-century modern, geometric shapes, limited color palette (navy, cyan, orange, magenta)"}

Clean, bold, iconic image. Square format. White background."""

        print(f"Generating square image with white background...")

        payload = {
            'model': model,
            'messages': [
                {'role': 'user', 'content': image_prompt}
            ]
        }

        response = requests.post(OPENROUTER_URL, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        print(f"Image API Response status: {response.status_code}")

        # Extract image URL
        image_url = extract_image_url(result)

        if not image_url:
            raise ValueError("No image URL found in response")

        # Fixed cost for image generation
        image_cost = PRICING['image_generation']
        total_cost = text_cost + image_cost

        # Update stats
        increment_generation(total_cost)

        return jsonify({
            'title': title,
            'passage': passage,
            'image_url': image_url,
            'era': era,
            'cost': total_cost,
            'tokens': {
                'input': input_tokens,
                'output': output_tokens
            }
        })

    except Exception as e:
        print(f"Error generating quick card: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Generate panic card image using selected model and visual style"""
    try:
        data = request.json
        technology = data.get('technology', 'technology')
        era = data.get('era', 'contemporary')
        manifesto = data.get('manifesto', '')
        model = data.get('model', 'google/gemini-3-pro-image-preview')
        visual_style = data.get('visualStyle', 'vintage')

        print(f"\n=== IMAGE REQUEST ===")
        print(f"Technology: {technology}")
        print(f"Era received from manifesto: {era}")
        print(f"Model: {model}")
        print(f"Visual Style: {visual_style}")

        # Build era-specific visual style
        era_styles = {
            'antiquity': 'ancient Greek pottery patterns, marble columns, scrolls',
            'victorian': 'ornate Victorian frames, steam engines, corsets',
            'atomic': 'retro 1950s advertising, nuclear symbols, TVs',
            'contemporary': 'smartphone screens, wifi symbols, brain scans'
        }

        era_visual_style = era_styles.get(era, era_styles['contemporary'])

        # Extract title and punchy quote from manifesto for indie cards
        manifesto_lines = manifesto.split('\n')
        manifesto_title = manifesto_lines[0] if manifesto_lines else f"THE {technology.upper()} MENACE"

        # Extract a punchy outrage phrase (first sentence with strong language)
        manifesto_body = ' '.join(manifesto_lines[1:]) if len(manifesto_lines) > 1 else manifesto
        # Take first sentence or ~100 chars as the outrage phrase
        outrage_phrase = manifesto_body[:150].split('.')[0] + '.'

        print(f"Card title: {manifesto_title}")
        print(f"Outrage phrase: {outrage_phrase}")

        # Build image prompt based on selected visual style
        if visual_style == 'indie':
            # Contemporary indie comics style with text elements
            prompt = f"""Design a propaganda card in contemporary indie comics style (Daniel Clowes, Adrian Tomine). Portrait orientation, vertical format.

CARD STRUCTURE (top to bottom):
1. TITLE at top: "{manifesto_title}" - bold, all caps, comic book lettering
2. CENTRAL ILLUSTRATION: A flat-color illustration of a {technology} with {era_visual_style}. Clean line work, flat pastel colors (yellows, blues, pinks), simple geometric shapes, ironic deadpan tone. Style of indie graphic novels.
3. OUTRAGE PHRASE at bottom: "{outrage_phrase}" - smaller text, all caps

Overall aesthetic: Contemporary graphic novel, limited color palette, simple border, satirical tone. Portrait orientation."""

        elif visual_style == 'midcentury':
            # Mid-Century Modern 1950s-60s atomic age style
            prompt = f"""Design a propaganda card in mid-century modern 1950s-60s atomic age style. Portrait orientation, vertical format.

CARD STRUCTURE AND STYLE:
1. TITLE at top: "{manifesto_title}" - bold sans-serif lettering, clean geometric type
2. CENTRAL ILLUSTRATION: A stylized geometric illustration of a {technology} with {era_visual_style}.
   - Limited color palette: navy blue (#0d2c40), cyan (#31c5da), orange (#f15a30), magenta (#c879b2), cream (#f6efe5)
   - Clean lines, geometric shapes, atomic-age symbols (circles, starbursts, concentric rings)
   - Sophisticated retro aesthetic like vintage educational filmstrips or 1960s science magazines
   - Bold color blocking, minimalist modern design
3. OUTRAGE PHRASE at bottom: "{outrage_phrase}" - clean sans-serif text

Overall aesthetic: Mid-century modern graphic design, California modernist sophistication, atomic age optimism turned sinister. Clean, geometric, bold. Portrait orientation."""

        else:
            # Vintage propaganda style (default) - no text, AI struggles with vintage lettering
            prompt = f"""A black and white ink illustration in vintage 1930s moral panic propaganda style. Portrait orientation (taller than wide), vertical format.

The central art features a {technology} with {era_visual_style}, rendered with heavy cross-hatching, woodcut textures, manic, grotesque facial expressions. High contrast vintage propaganda aesthetic, satirical and surreal.

Thick black rounded border around entire image. Underground comix style. Portrait orientation, NOT square."""

        # Call OpenRouter API using chat completions (same as text generation)
        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5001',
            'X-Title': 'The Panic Engine'
        }

        payload = {
            'model': model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }

        response = requests.post(OPENROUTER_URL, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        print(f"Image API Response: {result}")  # Debug logging

        # Extract image URL from response
        image_url = extract_image_url(result)

        if not image_url:
            print(f"Failed to extract image URL from: {result}")  # Debug
            raise ValueError("No image URL found in response")

        # Fixed cost for image generation
        cost = PRICING['image_generation']

        # Update stats
        increment_generation(cost)

        return jsonify({
            'image_url': image_url,
            'cost': cost
        })

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-card', methods=['POST'])
def save_card():
    """Optional: Save generated card image to disk"""
    try:
        data = request.json
        image_url = data.get('image_url')
        technology = data.get('technology', 'unknown')

        if not image_url:
            return jsonify({'error': 'No image URL provided'}), 400

        # Create date-organized directory
        today = datetime.now().strftime('%Y-%m-%d')
        save_dir = IMAGES_DIR / today
        save_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime('%H%M%S')
        safe_tech = ''.join(c for c in technology if c.isalnum() or c in '-_')[:30]
        filename = f"{timestamp}_{safe_tech}.png"
        filepath = save_dir / filename

        # Download and save image
        if image_url.startswith('data:image'):
            # Handle base64 encoded image
            import base64
            base64_data = image_url.split(',')[1]
            image_data = base64.b64decode(base64_data)
            with open(filepath, 'wb') as f:
                f.write(image_data)
        else:
            # Download from URL
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            with open(filepath, 'wb') as f:
                f.write(img_response.content)

        return jsonify({
            'success': True,
            'filepath': str(filepath)
        })

    except Exception as e:
        print(f"Error saving card: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Allow custom port via command line
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    print(f"🚨 THE PANIC ENGINE 🚨")
    print(f"Server running on http://localhost:{port}")
    app.run(debug=True, port=port, host='0.0.0.0')
