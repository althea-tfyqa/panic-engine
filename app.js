// THE PANIC ENGINE - Frontend Logic

const API_BASE = window.location.origin;

// State
let currentGenerationCost = 0;
let currentManifestoPlainText = '';

// DOM Elements
const techInput = document.getElementById('tech-input');
const styleSelect = document.getElementById('style-select');
const modelSelect = document.getElementById('model-select');
const generateBtn = document.getElementById('generate-btn');
const indieStylesheet = document.getElementById('indie-styles');
const outputZone = document.querySelector('.output-zone');
const manifestoText = document.getElementById('manifesto-text');
const panicCard = document.getElementById('panic-card');
const copyBtn = document.getElementById('copy-btn');
const statusMessage = document.getElementById('status');
const costAmount = document.getElementById('cost-amount');
const statsVisits = document.getElementById('stats-visits');
const statsTotalCost = document.getElementById('stats-total-cost');

// Initialize on page load
async function init() {
    console.log('🚨 THE PANIC ENGINE initialized');

    // Track visit
    await trackVisit();

    // Fetch and display stats
    await fetchStats();

    // Set up event listeners
    generateBtn.addEventListener('click', generatePanic);
    copyBtn.addEventListener('click', copyToClipboard);
    styleSelect.addEventListener('change', switchStyle);

    // Allow Enter key in input
    techInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            generatePanic();
        }
    });
}

// Track page visit
async function trackVisit() {
    try {
        const response = await fetch(`${API_BASE}/api/track-visit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        console.log('Visit tracked:', data);
    } catch (error) {
        console.error('Failed to track visit:', error);
    }
}

// Fetch server-wide statistics
async function fetchStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const stats = await response.json();
        updateStatsDisplay(stats);
    } catch (error) {
        console.error('Failed to fetch stats:', error);
    }
}

// Update stats display
function updateStatsDisplay(stats) {
    if (statsVisits) statsVisits.textContent = stats.visits.toLocaleString();
    if (statsTotalCost) statsTotalCost.textContent = `$${stats.total_cost.toFixed(4)}`;
}

// Main generation orchestrator
async function generatePanic() {
    const technology = techInput.value.trim();

    // Validation
    if (!technology) {
        showStatus('Please enter a technology to fear.', true);
        return;
    }

    // Reset state
    currentGenerationCost = 0;
    updateCostDisplay(0);

    // Show loading state
    generateBtn.disabled = true;
    generateBtn.textContent = 'ANALYZING...';
    outputZone.classList.add('hidden');
    manifestoText.textContent = '';
    // Remove existing panic card if present
    const existingCard = document.getElementById('panic-card');
    if (existingCard) {
        existingCard.remove();
    }

    try {
        // Step 1: Generate manifesto (AI auto-selects era and category)
        showStatus('Analyzing technology and selecting era...');
        const manifestoData = await generateManifesto(technology);

        // Display manifesto as HTML immediately
        manifestoText.innerHTML = manifestoData.manifesto;
        currentManifestoPlainText = manifestoData.manifesto_plain || manifestoData.manifesto;

        // Insert panic card after the h3 headline (so it floats within paragraphs, not headline)
        const headline = manifestoText.querySelector('h3');
        if (headline && !document.getElementById('panic-card')) {
            const cardImg = document.createElement('img');
            cardImg.id = 'panic-card';
            cardImg.className = 'panic-card loading';
            cardImg.src = '/images/placeholder-visualizing-panic.jpg';
            cardImg.alt = 'Panic Card';
            headline.insertAdjacentElement('afterend', cardImg);
        } else if (document.getElementById('panic-card')) {
            // Card already exists, just reset it
            panicCard.src = '/images/placeholder-visualizing-panic.jpg';
            panicCard.classList.remove('loaded');
            panicCard.classList.add('loading');
        }

        // Apply dynamic font based on category
        const category = manifestoData.category || 'domestic';
        const manifestoContainer = document.querySelector('.manifesto-container');

        // Remove any existing font classes
        manifestoContainer.classList.remove('font-industrial', 'font-domestic', 'font-media', 'font-medical', 'font-digital');

        // Add new font class
        manifestoContainer.classList.add(`font-${category}`);

        // Update cost
        currentGenerationCost += manifestoData.cost;
        updateCostDisplay(currentGenerationCost);

        // Show output zone NOW (so manifesto is visible even if image fails)
        outputZone.classList.remove('hidden');

        // Use the era returned from manifesto
        const chosenEra = manifestoData.era;

        // Step 2: Generate image (use chosen era, selected model, and visual style)
        showStatus('Generating panic card...');
        const selectedModel = modelSelect.value;
        const visualStyle = styleSelect.value;
        const imageData = await generateImage(technology, chosenEra, currentManifestoPlainText, selectedModel, visualStyle);

        // Display card with loaded state
        const panicCardElement = document.getElementById('panic-card');
        if (panicCardElement) {
            panicCardElement.src = imageData.image_url;

            // Wait for image to actually load, then transition to loaded state
            panicCardElement.onload = function() {
                panicCardElement.classList.remove('loading');
                panicCardElement.classList.add('loaded');
            };
        }

        // Update cost
        currentGenerationCost += imageData.cost;
        updateCostDisplay(currentGenerationCost);

        // Refresh server stats
        await fetchStats();

        // Success message
        showStatus(`Panic generated! Cost: $${currentGenerationCost.toFixed(4)}`);

    } catch (error) {
        console.error('Generation error:', error);
        showStatus(`Generation failed: ${error.message}`, true);
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = 'GENERATE PANIC';
    }
}

// Generate manifesto via API
async function generateManifesto(technology) {
    const response = await fetch(`${API_BASE}/api/generate-manifesto`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ technology })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Manifesto generation failed');
    }

    return await response.json();
}

// Generate image via API
async function generateImage(technology, era, manifesto, model, visualStyle) {
    const response = await fetch(`${API_BASE}/api/generate-image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ technology, era, manifesto, model, visualStyle })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Image generation failed');
    }

    return await response.json();
}

// Typewriter effect
function typewriterEffect(text, element) {
    return new Promise((resolve) => {
        element.textContent = '';
        let index = 0;

        // Remove cursor while typing
        element.style.setProperty('--cursor', 'none');

        const interval = setInterval(() => {
            if (index < text.length) {
                element.textContent += text[index];
                index++;

                // Auto-scroll to bottom
                element.scrollTop = element.scrollHeight;
            } else {
                clearInterval(interval);
                // Restore cursor
                element.style.removeProperty('--cursor');
                resolve();
            }
        }, 30); // 30ms per character
    });
}

// Copy manifesto to clipboard
async function copyToClipboard() {
    const text = currentManifestoPlainText || manifestoText.textContent;

    try {
        await navigator.clipboard.writeText(text);
        showStatus('Manifesto copied to clipboard!');

        // Visual feedback
        copyBtn.textContent = '✓ COPIED';
        setTimeout(() => {
            copyBtn.textContent = '📋 COPY TEXT';
        }, 2000);
    } catch (error) {
        console.error('Failed to copy:', error);
        showStatus('Copy failed. Please select and copy manually.', true);
    }
}


// Update this-generation cost display
function updateCostDisplay(cost) {
    costAmount.textContent = `$${cost.toFixed(4)}`;
}

// Show status message
function showStatus(message, isError = false) {
    statusMessage.textContent = message;
    statusMessage.className = 'status-message show';

    if (isError) {
        statusMessage.classList.add('error');
    }

    // Auto-hide after 5 seconds (unless error)
    if (!isError) {
        setTimeout(() => {
            statusMessage.classList.remove('show');
        }, 5000);
    }
}

// Switch visual style
function switchStyle() {
    const style = styleSelect.value;
    if (style === 'indie') {
        indieStylesheet.disabled = false;
    } else {
        indieStylesheet.disabled = true;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
