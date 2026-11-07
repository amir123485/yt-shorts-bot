import json
import math
import os
import random
import subprocess
import tempfile
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

WIDTH, HEIGHT = 1080, 1920
FPS = 30

COLOR_THEMES = {
    "electric_blue":   {"bg": (5, 10, 25),   "accent": (0, 180, 255),  "text": (255, 255, 255), "sub": (150, 220, 255), "glow": (0, 140, 255)},
    "cyber_purple":    {"bg": (15, 5, 30),   "accent": (180, 50, 255), "text": (255, 255, 255), "sub": (220, 150, 255), "glow": (160, 40, 255)},
    "neon_cyan":       {"bg": (0, 15, 20),   "accent": (0, 255, 220),  "text": (255, 255, 255), "sub": (100, 255, 230), "glow": (0, 220, 200)},
    "deep_navy":       {"bg": (5, 8, 25),    "accent": (50, 120, 255), "text": (255, 255, 255), "sub": (140, 180, 255), "glow": (40, 100, 255)},
    "tech_green":      {"bg": (0, 15, 10),   "accent": (0, 255, 120),  "text": (255, 255, 255), "sub": (100, 255, 180), "glow": (0, 220, 100)},
}

def get_font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def get_audio_duration(audio_path):
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ], capture_output=True, text=True)
    return float(result.stdout.strip())

def draw_glow_text(draw, text, font, x, y, text_color, glow_color):
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=glow_color)
    draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=text_color)

def download_ai_background(niche, theme_name):
    """Download a free AI-generated background from Pollinations (no API key needed)."""
    prompt = (
        f"cinematic dark tech background for {niche}, "
        f"futuristic AI atmosphere, neon lights, abstract digital, "
        f"high quality, vertical 9:16, moody lighting, no text, no people"
    )
    # Pollinations free endpoint
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1080&height=1920&nologo=true&seed={random.randint(1,99999)}"
    
    try:
        print(f"[INFO] Downloading AI background for: {niche}")
        urllib.request.urlretrieve(url, "bg_ai.jpg")
        img = Image.open("bg_ai.jpg").convert("RGB")
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        # Darken a bit so text stays readable
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.65)
        return img
    except Exception as e:
        print(f"[WARN] AI background failed ({e}), using fallback gradient")
        return make_fallback_bg(theme_name)

def make_fallback_bg(theme_name):
    theme = COLOR_THEMES.get(theme_name, COLOR_THEMES["electric_blue"])
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    accent = theme["accent"]
    for y in range(HEIGHT):
        factor = y / HEIGHT
        r = int(theme["bg"][0] + (accent[0] - theme["bg"][0]) * factor * 0.4)
        g = int(theme["bg"][1] + (accent[1] - theme["bg"][1]) * factor * 0.4)
        b = int(theme["bg"][2] + (accent[2] - theme["bg"][2]) * factor * 0.4)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return img

def apply_ken_burns(base_img, progress, zoom_strength=0.18):
    """Slow zoom + slight pan (Ken Burns effect)."""
    # progress: 0.0 → 1.0
    scale = 1.0 + (zoom_strength * progress)
    new_w = int(WIDTH * scale)
    new_h = int(HEIGHT * scale)
    resized = base_img.resize((new_w, new_h), Image.LANCZOS)

    # Slight drift
    max_dx = new_w - WIDTH
    max_dy = new_h - HEIGHT
    dx = int(max_dx * progress * 0.7)
    dy = int(max_dy * progress * 0.5)

    cropped = resized.crop((dx, dy, dx + WIDTH, dy + HEIGHT))
    return cropped

def add_particles(img, frame_idx, accent):
    """Subtle floating particles on top."""
    overlay = img.copy()
    draw = ImageDraw.Draw(overlay)
    t = frame_idx / FPS
    rng = random.Random(42)

    for i in range(25):
        speed = 15 + (i % 10) * 4
        px = (rng.randint(0, WIDTH) + int(t * speed * 0.3)) % WIDTH
        py = (rng.randint(0, HEIGHT) + int(t * speed)) % HEIGHT
        size = 2 + (i % 4)
        pulse = (math.sin(t * 2.5 + i) + 1) / 2
        alpha_color = tuple(int(c * (0.3 + 0.4 * pulse)) for c in accent)
        draw.ellipse([px - size, py - size, px + size, py + size], fill=alpha_color)

    return Image.blend(img, overlay, 0.35)

def get_current_word(timestamps, t):
    for item in timestamps:
        if item["start"] <= t <= item["end"]:
            return item["word"]
    return None

def render_frame(frame_idx, base_bg, script, theme, timestamps, total_frames, font_word, font_hook):
    progress = frame_idx / max(total_frames - 1, 1)
    img = apply_ken_burns(base_bg, progress)
    img = add_particles(img, frame_idx, theme["accent"])

    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    current_word = get_current_word(timestamps, t)
    is_first_word = t < (timestamps[2]["end"] if len(timestamps) > 2 else 3)

    if current_word:
        font = font_hook if is_first_word else font_word
        w = draw.textlength(current_word.upper(), font=font)
        x = (WIDTH - w) // 2
        y = HEIGHT // 2 - font.size // 2
        pad = 28
        draw.rounded_rectangle(
            [x - pad, y - pad, x + w + pad, y + font.size + pad],
            radius=18, fill=(0, 0, 0)
        )
        draw_glow_text(draw, current_word.upper(), font, x, y, theme["text"], theme["glow"])

    # Progress bar
    bar_h = 8
    draw.rectangle([0, HEIGHT - bar_h, WIDTH, HEIGHT], fill=(15, 15, 25))
    draw.rectangle([0, HEIGHT - bar_h, int(WIDTH * progress), HEIGHT], fill=theme["accent"])

    return img

def generate_video(script_path="script.json", audio_path="narration.mp3", timestamps_path="timestamps.json", output_path="short.mp4"):
    import urllib.parse

    with open(script_path) as f:
        script = json.load(f)
    with open(timestamps_path) as f:
        timestamps = json.load(f)

    theme_name = script.get("color_theme", "electric_blue")
    theme = COLOR_THEMES.get(theme_name, COLOR_THEMES["electric_blue"])
    niche = script.get("niche", "AI tools")

    font_word = get_font(92)
    font_hook = get_font(108)

    # Get AI background once
    base_bg = download_ai_background(niche, theme_name)

    audio_duration = get_audio_duration(audio_path)
    print("[INFO] Audio duration: " + str(round(audio_duration, 2)) + "s")
    total_frames = int(audio_duration * FPS) + FPS

    frames_dir = tempfile.mkdtemp()
    print("[INFO] Rendering " + str(total_frames) + " frames with AI background + Ken Burns...")

    for i in range(total_frames):
        if i % (FPS * 5) == 0:
            print("  Frame " + str(i) + "/" + str(total_frames))
        frame = render_frame(i, base_bg, script, theme, timestamps, total_frames, font_word, font_hook)
        frame.save(os.path.join(frames_dir, "frame_{:05d}.png".format(i)))

    video_no_audio = output_path.replace(".mp4", "_noaudio.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "frame_%05d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
        video_no_audio
    ], check=True)

    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_no_audio,
        "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac",
        "-shortest", output_path
    ], check=True)

    if os.path.exists(video_no_audio):
        os.remove(video_no_audio)
    if os.path.exists("bg_ai.jpg"):
        os.remove("bg_ai.jpg")

    print("[OK] Video saved: " + output_path)
    return output_path

if __name__ == "__main__":
    generate_video()
