import json
import random
import os
from datetime import datetime
from groq import Groq

NICHES = [
    "best free AI tools",
    "new AI tools this week",
    "AI tools for productivity",
    "AI tools for students",
    "ChatGPT alternatives",
    "AI tools that save time",
    "underrated AI tools",
    "AI tools for content creators",
    "free AI image generators",
    "AI tools for writing",
    "best AI tools for beginners",
    "AI tools that feel like magic",
]

BACKGROUNDS = [
    "digital_circuit",
    "futuristic_hud",
    "neon_grid",
    "abstract_tech",
    "glowing_particles",
    "minimal_dark",
    "cyber_wave",
    "soft_gradient_tech",
]

COLOR_THEMES = [
    "electric_blue",
    "cyber_purple",
    "neon_cyan",
    "deep_navy",
    "tech_green",
]

def generate_script():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables")
    
    client = Groq(api_key=api_key)

    niche = random.choice(NICHES)
    background = random.choice(BACKGROUNDS)
    color_theme = random.choice(COLOR_THEMES)
    slot = "morning" if datetime.now().hour < 12 else "evening"

    prompt = (
        "You are a viral YouTube Shorts script writer specializing in AI tools content. "
        "Write a 55-60 second exciting and useful script for a Short about: " + niche + "\n\n"
        "The video is for the " + slot + " audience.\n\n"
        "Make it clear, energetic, and valuable. Speak like you're showing someone a cool new AI tool.\n"
        "Focus on real benefits and make the viewer curious.\n\n"
        "Return ONLY valid JSON with this exact structure:\n"
        "{\n"
        '  "title": "YouTube title (max 70 chars, clickbait but clean, AI tools style)",\n'
        '  "description": "YouTube description (2-3 sentences + hashtags like #AItools #shorts #ChatGPT #productivity)",\n'
        '  "tags": ["AI tools", "shorts", "ChatGPT", "productivity", "artificial intelligence"],\n'
        '  "hook": "First 3 seconds hook line (grab attention instantly)",\n'
        '  "lines": [\n'
        '    "Line 1 (short, clear, energetic)",\n'
        '    "Line 2",\n'
        '    "Line 3",\n'
        '    "Line 4",\n'
        '    "Line 5",\n'
        '    "Line 6",\n'
        '    "Line 7 - strong closing + follow for more AI tools"\n'
        '  ],\n'
        '  "background_style": "' + background + '",\n'
        '  "color_theme": "' + color_theme + '"\n'
        "}"
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.85,
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    script = json.loads(raw)
    script["niche"] = niche
    script["generated_at"] = datetime.utcnow().isoformat()

    with open("script.json", "w") as f:
        json.dump(script, f, indent=2)

    print("[OK] Script generated: " + script["title"])
    return script
