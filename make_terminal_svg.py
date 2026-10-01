"""
Generates an animated macOS-terminal-style SVG for a GitHub README.

Usage:
    python make_terminal_svg.py

Output:
    assets/terminal.svg
"""

from pathlib import Path

PROMPT = "zubair_hussain/info $ "
COMMAND = "whoami"

OUTPUT_LINES = [
    ("", ""),
    ("Now", "Full Stack Developer · AI Engineer"),
    ("Prev", "Freelancer @ Upwork · Fiverr · LinkedIn"),
    ("Also", "Co-founder @ Xovato Digital Agency"),
    ("Intern", "xis.ai — Software Development Dept"),
    ("Edu", "B.Tech / BS IT, In Progress"),
    ("", ""),
    ("", "── Stack ──────────────────────────"),
    ("Frontend", "React, Next.js, TypeScript, Tailwind"),
    ("Backend", "Node.js, Django, FastAPI"),
    ("AI / ML", "LangChain, OpenAI API, Scikit-learn"),
    ("DevOps", "Docker, Firebase, Git"),
    ("", ""),
    ("", "── Highlights ─────────────────────"),
    ("", "• 35+ public repos across web, AI & mobile"),
    ("", "• Kaggle top 10% — multiple competitions"),
    ("", "• Built full text-to-image AI pipeline"),
    ("", "• Shipped real client projects on Upwork & Fiverr"),
]

FONT = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"
FONT_SIZE = 14
LINE_HEIGHT = 22
CHAR_W = FONT_SIZE * 0.6
PADDING_X = 20
CONTENT_TOP = 55
TITLEBAR_H = 36
WINDOW_W = 640
BG_COLOR = "#151517"
TITLEBAR_COLOR = "#2b2b2d"
PROMPT_COLOR = "#5fd97a"
COMMAND_COLOR = "#f2f2f2"
LABEL_COLOR = "#8a7dfb"
TEXT_COLOR = "#c7c7c7"
DIM_COLOR = "#6a6a6a"
CURSOR_COLOR = "#f2f2f2"

CHAR_DUR = 0.055
TYPE_START = 0.6
TYPE_DUR = len(COMMAND) * CHAR_DUR
TYPE_END = TYPE_START + TYPE_DUR
LINE_STAGGER = 0.11
OUTPUT_START = TYPE_END + 0.35
OUTPUT_END = OUTPUT_START + len(OUTPUT_LINES) * LINE_STAGGER
HOLD = 2.6
FADE_START = OUTPUT_END + HOLD
FADE_DUR = 0.45
CYCLE = FADE_START + FADE_DUR + 0.6


def frac(t):
    return max(0.0, min(1.0, t / CYCLE))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def opacity_animate(el_id, show_at, hide_at=None):
    hide_at = hide_at or FADE_START
    key_times = [0, frac(show_at)]
    values = [0, 0]

    if frac(show_at) < frac(show_at + 0.15):
        key_times.append(frac(show_at + 0.15))
        values.append(1)

    key_times.extend([frac(hide_at), frac(hide_at + FADE_DUR), 1])
    values.extend([1, 0, 0])

    return (
        f'<animate xlink:href="#{el_id}" attributeName="opacity" '
        f'values="{";".join(str(v) for v in values)}" '
        f'keyTimes="{";".join(f"{k:.4f}" for k in key_times)}" '
        f'dur="{CYCLE:.3f}s" repeatCount="indefinite" />'
    )


def build_svg():
    total_lines = 1 + len(OUTPUT_LINES) + 1
    height = TITLEBAR_H + total_lines * LINE_HEIGHT + 30
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {WINDOW_W} {height}" width="{WINDOW_W}" height="{height}">',
        f'<rect x="0" y="0" width="{WINDOW_W}" height="{height}" rx="12" ry="12" '
        f'fill="{BG_COLOR}" stroke="#000" stroke-opacity="0.4" stroke-width="1"/>',
        f'<path d="M0,12 a12,12 0 0 1 12,-12 h{WINDOW_W - 24} a12,12 0 0 1 12,12 '
        f'v{TITLEBAR_H - 12} h-{WINDOW_W} z" fill="{TITLEBAR_COLOR}"/>',
    ]
    animates = []

    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{22 + i * 20}" cy="{TITLEBAR_H / 2}" r="6" fill="{color}"/>')

    parts.append(
        f'<text x="{WINDOW_W / 2}" y="{TITLEBAR_H / 2 + 4}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="12" fill="#9a9a9a">zubair_hussain — info — 80x24</text>'
    )

    y = CONTENT_TOP
    prompt_w = len(PROMPT) * CHAR_W
    command_w = len(COMMAND) * CHAR_W
    cursor_x_start = PADDING_X + prompt_w
    cursor_x_end = cursor_x_start + command_w

    parts.append(
        f'<clipPath id="cmdClip"><rect id="cmdClipRect" x="{cursor_x_start}" y="{y - FONT_SIZE}" '
        f'width="0" height="{FONT_SIZE + 8}"/></clipPath>'
    )
    parts.append(
        f'<text x="{PADDING_X}" y="{y}" font-family="{FONT}" font-size="{FONT_SIZE}">'
        f'<tspan fill="{PROMPT_COLOR}">{esc(PROMPT)}</tspan>'
        f'<tspan fill="{COMMAND_COLOR}" clip-path="url(#cmdClip)">{esc(COMMAND)}</tspan>'
        f'</text>'
    )
    parts.append(
        f'<rect id="typeCursor" x="{cursor_x_start}" y="{y - FONT_SIZE}" width="7" '
        f'height="{FONT_SIZE + 4}" fill="{CURSOR_COLOR}"/>'
    )

    animates.append(
        f'<animate xlink:href="#cmdClipRect" attributeName="width" '
        f'values="0;0;{command_w:.1f};{command_w:.1f};0;0" '
        f'keyTimes="0;{frac(TYPE_START):.4f};{frac(TYPE_END):.4f};{frac(FADE_START):.4f};'
        f'{frac(FADE_START + FADE_DUR):.4f};1" dur="{CYCLE:.3f}s" repeatCount="indefinite"/>'
    )
    animates.append(
        f'<animate xlink:href="#typeCursor" attributeName="x" '
        f'values="{cursor_x_start};{cursor_x_start};{cursor_x_end};{cursor_x_end}" '
        f'keyTimes="0;{frac(TYPE_START):.4f};{frac(TYPE_END):.4f};1" '
        f'dur="{CYCLE:.3f}s" repeatCount="indefinite"/>'
    )
    animates.append(
        f'<animate xlink:href="#typeCursor" attributeName="opacity" values="0;1;1;0;0" '
        f'keyTimes="0;{frac(TYPE_START):.4f};{frac(TYPE_END):.4f};{frac(TYPE_END + 0.15):.4f};1" '
        f'dur="{CYCLE:.3f}s" repeatCount="indefinite"/>'
    )

    y += LINE_HEIGHT * 1.4
    for i, (label, rest) in enumerate(OUTPUT_LINES):
        line_id = f"line{i}"
        show_at = OUTPUT_START + i * LINE_STAGGER

        if label:
            text = (
                f'<tspan fill="{LABEL_COLOR}">{esc(label)}</tspan>'
                f'<tspan fill="{TEXT_COLOR}">{"&#160;" * max(1, 11 - len(label))}{esc(rest)}</tspan>'
            )
        elif rest.startswith("──"):
            text = f'<tspan fill="{DIM_COLOR}">{esc(rest)}</tspan>'
        elif rest.startswith("•"):
            text = f'<tspan fill="{LABEL_COLOR}">•</tspan><tspan fill="{TEXT_COLOR}">{esc(rest[1:])}</tspan>'
        else:
            text = f'<tspan fill="{TEXT_COLOR}">{esc(rest)}</tspan>'

        parts.append(
            f'<g id="{line_id}" opacity="0"><text x="{PADDING_X}" y="{y}" '
            f'font-family="{FONT}" font-size="{FONT_SIZE}">{text}</text></g>'
        )
        animates.append(opacity_animate(line_id, show_at))
        y += LINE_HEIGHT

    y += LINE_HEIGHT * 0.4
    final_prompt_show = OUTPUT_END + 0.1
    parts.append(
        f'<g id="finalPrompt" opacity="0"><text x="{PADDING_X}" y="{y}" font-family="{FONT}" '
        f'font-size="{FONT_SIZE}" fill="{PROMPT_COLOR}">{esc(PROMPT)}</text>'
        f'<rect id="blinkCursor" x="{cursor_x_start}" y="{y - FONT_SIZE}" width="7" '
        f'height="{FONT_SIZE + 4}" fill="{CURSOR_COLOR}"/></g>'
    )
    animates.append(opacity_animate("finalPrompt", final_prompt_show))

    blink_key_times = [0]
    blink_values = [0]
    t = final_prompt_show + 0.2
    for _ in range(max(1, int(HOLD / 0.9)) * 2):
        blink_key_times.append(frac(t))
        blink_values.append(1 if len(blink_values) % 2 else 0)
        t += 0.45
    blink_key_times.extend([frac(FADE_START), 1])
    blink_values.extend([0, 0])

    fixed_key_times = []
    last = -1
    for key_time in blink_key_times:
        if key_time <= last:
            key_time = min(1.0, last + 0.0001)
        fixed_key_times.append(key_time)
        last = key_time

    animates.append(
        f'<animate xlink:href="#blinkCursor" attributeName="opacity" '
        f'values="{";".join(str(v) for v in blink_values)}" '
        f'keyTimes="{";".join(f"{k:.4f}" for k in fixed_key_times)}" '
        f'dur="{CYCLE:.3f}s" repeatCount="indefinite"/>'
    )

    parts.extend(animates)
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    output_path = Path("assets") / "terminal.svg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_svg(), encoding="utf-8")
    print(f"Saved {output_path} — cycle length {CYCLE:.2f}s")
