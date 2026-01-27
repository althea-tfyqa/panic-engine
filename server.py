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

Determine TWO things:

1. Which historical era would be MOST likely to have a moral panic about it?
   - antiquity (ancient philosophers worried about soul/memory/truth)
   - victorian (19th century moralists worried about virtue/nature/corruption)
   - atomic (1950s-60s worried about conformity/mass mind/automation)
   - contemporary (modern dopamine/attention/capitalism concerns)

2. Which category does this technology belong to?
   - industrial (engines, factories, heavy machinery, manufacturing)
   - domestic (appliances, furniture, household items, cleaning tools)
   - media (books, radio, comics, television, film, music)
   - medical (pills, treatments, procedures, diagnostic tools)
   - digital (computers, phones, software, algorithms, internet)

Respond ONLY in this exact format (no extra text):
era: [era name]
category: [category name]"""

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
        category = 'domestic'

        for line in analysis_text.split('\n'):
            if 'era:' in line:
                era_text = line.split('era:')[1].strip()
                valid_eras = ['antiquity', 'victorian', 'atomic', 'contemporary']
                for valid_era in valid_eras:
                    if valid_era in era_text:
                        era = valid_era
                        break

            if 'category:' in line:
                cat_text = line.split('category:')[1].strip()
                valid_categories = ['industrial', 'domestic', 'media', 'medical', 'digital']
                for valid_cat in valid_categories:
                    if valid_cat in cat_text:
                        category = valid_cat
                        break

        print(f"✅ Analysis complete: era={era}, category={category}")
        return {'era': era, 'category': category}

    except Exception as e:
        print(f"Error analyzing technology: {str(e)}")
        return {'era': 'contemporary', 'category': 'domestic'}

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

        # AI analyzes technology to determine era and category
        analysis = analyze_technology(technology)
        era = analysis['era']
        category = analysis['category']

        print(f"AI analysis: era={era}, category={category}")

        # Build era-specific system prompt
        era_prompts = {
            'antiquity': {
                'name': 'The Philosopher',
                'focus': 'The Soul, Memory, Truth, The Gods',
                'anxiety': 'Illusion vs Reality',
                'keywords': 'simulacrum, shadow, spirit, void'
            },
            'victorian': {
                'name': 'The Moralist',
                'focus': 'Virtue, Nature, Gender Roles, Hygiene',
                'anxiety': 'Corruption, Hysteria, Unnatural Speed',
                'keywords': 'vapors, constitution, unseemly, artificial, godless'
            },
            'atomic': {
                'name': 'The Conformist Critic',
                'focus': 'Individuality, The Mass Mind, Brainwashing',
                'anxiety': 'Becoming robots/cogs',
                'keywords': 'automation, programming, soft, dependent, the machine'
            },
            'contemporary': {
                'name': 'The Dopamine Critic',
                'focus': 'Attention, Neurochemistry, Capitalism',
                'anxiety': 'Brain rot, corporate extraction',
                'keywords': 'algorithm, product, content, shriveled, counterfeit'
            }
        }

        era_data = era_prompts.get(era, era_prompts['contemporary'])

        system_prompt = f"""You are {era_data['name']}, writing in the voice of {era} panic literature.

CRITICAL - RHETORICAL PILLARS (you must incorporate ALL THREE):

1. SUBSTITUTION: The technology REPLACES human capacity, not aids it. Frame the friction it removes as the source of virtue.

2. AGENT OF ATROPHY: The technology is predatory. It "seduces," "demands," "steals." The user is passive victim.

3. REAL vs FAKE: Romanticize the difficulty of the old way (blood, sweat, vitality) vs the sterility of the new way (plastic, grid, dead).

Each pillar should be clearly present in your manifesto. Make the arguments specific and visceral.

ERA FILTER:
- Focus: {era_data['focus']}
- Core Anxiety: {era_data['anxiety']}
- Keywords to use: {era_data['keywords']}

Write a 200-300 word manifesto against this technology. Be harsh, alarmist, and convincing. Ground your argument in the rhetorical pillars and make it specific to {era} anxieties. No hedging, no nuance—pure panic.

Start with a bold, dramatic title (like "THE SCOURGE OF THE {technology.upper()}" or "{technology.upper()}: A CRISIS OF CIVILIZATION"), then write the manifesto body.

IMPORTANT FORMATTING:
- Use SHORT paragraphs (2-4 sentences each) for contemporary readability
- Include frequent line breaks between paragraphs
- Write 4-6 short paragraphs instead of 2-3 long ones
- Each paragraph should be punchy and focused
- Use vivid, intense language
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
            'era': era,  # Return the chosen era so image generation can reuse it
            'category': category  # Return category for dynamic font selection
        })

    except Exception as e:
        print(f"Error generating manifesto: {str(e)}")
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
