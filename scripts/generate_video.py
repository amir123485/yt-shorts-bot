import json
import math
import os
import random
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1920
FPS = 30

COLOR_THEMES = {
    "electric_blue":   {"bg": (5, 10, 25),   "accent": (0, 180, 255),  "text": (255, 255, 255), "sub": (150, 220, 255), "glow": (0, 140, 255)},
    "cyber_purple":    {"bg": (15, 5, 30),   "accent": (180, 50, 255), "text": (255, 255, 255), "sub": (220, 150, 255), "glow": (160, 40, 255)},
    "neon_cyan":       {"bg": (0, 15, 20),   "accent": (0, 255, 220),  "text": (255, 255, 255), "sub": (100, 255, 230), "glow": (0, 220, 200)},
    "deep_navy":       {"bg": (5, 8, 25),    "accent": (50, 120, 255), "text": (255, 255, 255), "sub": (140, 180, 255), "glow": (40, 100, 255)},
    "tech_green":      {"bg": (0, 15, 10),   "accent": (0, 255, 120),  "text": (255, 255, 255), "sub": (100, 255, 180), "glow": (0, 220, 100)},
}

def get_font(size, bold=True):
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

def make_digital_circuit(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    accent = theme["accent"]

    # Moving horizontal and vertical circuit lines
    for i in range(0, HEIGHT, 90):
        y = (i + int(t * 40)) % HEIGHT
        alpha = 40 + int(30 * math.sin(t * 2 + i * 0.01))
        color = tuple(min(255, c * alpha // 100) for c in accent)
        draw.line([(0, y), (WIDTH, y)], fill=color, width=2)

    for i in range(0, WIDTH, 110):
        x = (i + int(t * 25)) % WIDTH
        alpha = 30 + int(25 * math.sin(t * 1.5 + i * 0.01))
        color = tuple(min(255, c * alpha // 100) for c in accent)
        draw.line([(x, 0), (x, HEIGHT)], fill=color, width=2)

    # Glowing nodes
    rng = random.Random(42)
    for _ in range(35):
        nx = rng.randint(50, WIDTH - 50)
        ny = rng.randint(50, HEIGHT - 50)
        pulse = (math.sin(t * 3 + nx * 0.01) + 1) / 2
        r = int(6 + 10 * pulse)
        color = tuple(int(c * (0.5 + 0.5 * pulse)) for c in accent)
        draw.ellipse([nx - r, ny - r, nx + r, ny + r], fill=color)

    return img

def make_futuristic_hud(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    accent = theme["accent"]

    # Rotating rings
    cx, cy = WIDTH // 2, HEIGHT // 2
    for i, radius in enumerate([180, 280, 400, 520]):
        angle_offset = t * (0.4 + i * 0.15) * (1 if i % 2 == 0 else -1)
        for a in range(0, 360, 8):
            rad = math.radians(a + angle_offset * 60)
            x1 = cx + int(radius * math.cos(rad))
            y1 = cy + int(radius * math.sin(rad))
            x2 = cx + int((radius + 12) * math.cos(rad))
            y2 = cy + int((radius + 12) * math.sin(rad))
            alpha = 80 + int(60 * math.sin(t * 2 + a * 0.05))
            color = tuple(min(255, c * alpha // 120) for c in accent)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=3)

    # Corner brackets
    bracket = 80
    for x, y in [(60, 120), (WIDTH - 60, 120), (60, HEIGHT - 120), (WIDTH - 60, HEIGHT - 120)]:
        draw.line([(x - bracket, y), (x, y), (x, y + (bracket if y < HEIGHT // 2 else -bracket))], fill=accent, width=4)

    return img

def make_neon_grid(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    accent = theme["accent"]

    spacing = 70
    offset = int(t * 50) % spacing

    for x in range(-spacing, WIDTH + spacing, spacing):
        draw.line([(x + offset, 0), (x + offset, HEIGHT)], fill=tuple(c // 3 for c in accent), width=1)
    for y in range(-spacing, HEIGHT + spacing, spacing):
        draw.line([(0, y + offset), (WIDTH, y + offset)], fill=tuple(c // 3 for c in accent), width=1)

    # Moving bright dots on grid
    rng = random.Random(99)
    for _ in range(40):
        gx = (rng.randint(0, 20) * spacing + offset) % WIDTH
        gy = (rng.randint(0, 30) * spacing + int(t * 30)) % HEIGHT
        pulse = (math.sin(t * 4 + gx) + 1) / 2
        r = int(4 + 8 * pulse)
        color = tuple(int(c * (0.6 + 0.4 * pulse)) for c in accent)
        draw.ellipse([gx - r, gy - r, gx + r, gy + r], fill=color)

    return img

def make_abstract_tech(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    accent = theme["accent"]

    for i in range(8):
        angle = t * 0.5 + i * math.pi / 4
        radius = 200 + 80 * math.sin(t * 1.2 + i)
        x = WIDTH // 2 + int(radius * math.cos(angle))
        y = HEIGHT // 2 + int(radius * math.sin(angle) * 0.7)
        size = 40 + int(20 * math.sin(t * 2 + i))
        color = tuple(int(c * (0.4 + 0.3 * math.sin(t + i))) for c in accent)
        draw.ellipse([x - size, y - size, x + size, y + size], outline=color, width=3)

    # Center pulse
    pulse = int(60 + 40 * math.sin(t * 3))
    for r in range(pulse, 0, -15):
        alpha = int(50 * r / pulse)
        color = tuple(min(255, c * alpha // 80) for c in accent)
        draw.ellipse([WIDTH//2 - r, HEIGHT//2 - r, WIDTH//2 + r, HEIGHT//2 + r], outline=color, width=2)

    return img

def make_glowing_particles(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    accent = theme["accent"]
    rng = random.Random(123)

    for i in range(80):
        speed = rng.uniform(20, 90)
        px = (rng.randint(0, WIDTH) + t * speed * 0.3) % WIDTH
        py = (rng.randint(0, HEIGHT) + t * speed) % HEIGHT
        size = rng.uniform(3, 12)
        pulse = (math.sin(t * 3 + i) + 1) / 2
        brightness = 0.4 + 0.6 * pulse
        color = tuple(int(c * brightness) for c in accent)
        r = int(size * (0.7 + 0.3 * pulse))
        draw.ellipse([px - r, py - r, px + r, py + r], fill=color)

    return img

def make_minimal_dark(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    accent = theme["accent"]

    # Soft moving gradient waves
    for y in range(0, HEIGHT, 4):
        wave = math.sin(y * 0.008 + t * 1.5) * 0.5 + 0.5
        color = tuple(int(c * (0.15 + 0.25 * wave)) for c in accent)
        draw.line([(0, y), (WIDTH, y)], fill=color, width=4)

    # Floating soft orbs
    for i in range(6):
        ox = WIDTH // 2 + int(300 * math.sin(t * 0.4 + i * 1.2))
        oy = HEIGHT // 2 + int(400 * math.cos(t * 0.3 + i * 0.9))
        radius = 120 + int(40 * math.sin(t + i))
        for r in range(radius, 0, -20):
            alpha = int(25 * r / radius)
            color = tuple(min(255, c * alpha // 60) for c in accent)
            draw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=color)

    return img

def make_cyber_wave(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    accent = theme["accent"]

    for i in range(12):
        phase = t * 1.5 + i * 0.4
        points = []
        for x in range(0, WIDTH, 8):
            y = int(HEIGHT * 0.3 + i * 90 + 60 * math.sin(x * 0.01 + phase))
            points.append((x, y))
        if len(points) > 1:
            alpha = 60 + int(40 * math.sin(phase))
            color = tuple(min(255, c * alpha // 100) for c in accent)
            draw.line(points, fill=color, width=3)

    return img

def make_soft_gradient_tech(frame_idx, theme):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)
    t = frame_idx / FPS
    accent = theme["accent"]

    for y in range(HEIGHT):
        factor = (math.sin(y * 0.004 + t * 0.8) + 1) / 2
        r = int(theme["bg"][0] + (accent[0] - theme["bg"][0]) * factor * 0.35)
        g = int(theme["bg"][1] + (accent[1] - theme["bg"][1]) * factor * 0.35)
        b = int(theme["bg"][2] + (accent[2] - theme["bg"][2]) * factor * 0.35)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Soft moving circles
    for i in range(5):
        cx = int(WIDTH * (0.2 + 0.15 * i) + 80 * math.sin(t * 0.6 + i))
        cy = int(HEIGHT * 0.5 + 200 * math.cos(t * 0.4 + i * 1.1))
        radius = 100 + int(50 * math.sin(t + i))
        for r in range(radius, 0, -25):
            alpha = int(20 * r / radius)
            color = tuple(min(255, c * alpha // 50) for c in accent)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    return img

BG_MAKERS = {
    "digital_circuit": make_digital_circuit,
    "futuristic_hud": make_futuristic_hud,
    "neon_grid": make_neon_grid,
    "abstract_tech": make_abstract_tech,
    "glowing_particles": make_glowing_particles,
    "minimal_dark": make_minimal_dark,
    "cyber_wave": make_cyber_wave,
    "soft_gradient_tech": make_soft_gradient_tech,
}

def get_current_word(timestamps, t):
    for item in timestamps:
        if item["start"] <= t <= item["end"]:
            return item["word"]
    return None

def render_frame(frame_idx, script, theme, timestamps, total_frames, font_word, font_hook, font_small):
    bg_style = script.get("background_style", "digital_circuit")
    maker = BG_MAKERS.get(bg_style, make_digital_circuit)
    img = maker(frame_idx, theme)
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
    progress = min(t / (total_frames / FPS), 1.0)
    bar_h = 8
    draw.rectangle([0, HEIGHT - bar_h, WIDTH, HEIGHT], fill=(20, 20, 30))
    draw.rectangle([0, HEIGHT - bar_h, int(WIDTH * progress), HEIGHT], fill=theme["accent"])

    return img

def generate_video(script_path="script.json", audio_path="narration.mp3", timestamps_path="timestamps.json", output_path="short.mp4"):
    with open(script_path) as f:
        script = json.load(f)
    with open(timestamps_path) as f:
        timestamps = json.load(f)

    theme = COLOR_THEMES.get(script.get("color_theme", "electric_blue"), COLOR_THEMES["electric_blue"])
    font_word = get_font(92)
    font_hook = get_font(108)
    font_small = get_font(40)

    audio_duration = get_audio_duration(audio_path)
    print("[INFO] Audio duration: " + str(round(audio_duration, 2)) + "s")
    total_frames = int(audio_duration * FPS) + FPS

    frames_dir = tempfile.mkdtemp()
    print("[INFO] Rendering " + str(total_frames) + " frames...")

    for i in range(total_frames):
        if i % (FPS * 5) == 0:
            print("  Frame " + str(i) + "/" + str(total_frames))
        frame = render_frame(i, script, theme, timestamps, total_frames, font_word, font_hook, font_small)
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

    os.remove(video_no_audio)
    print("[OK] Video saved: " + output_path)
    return output_path

if __name__ == "__main__":
    generate_video()
