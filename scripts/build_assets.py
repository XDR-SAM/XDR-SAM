"""Build the profile's self-contained SVG artwork; Python standard library only."""
from pathlib import Path
from math import sin, cos, pi
from html import escape

OUT = Path(__file__).resolve().parents[1] / "assets"
OUT.mkdir(exist_ok=True)

def text(x, y, value, size=16, color="var(--ink)", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(value)}</text>'

def shell(w, h, theme, title, body):
    colors = ("#10130F", "#F1F2E9", "#A9B1A2", "#C1F76D", "#30392B") if theme == "dark" else ("#F4F5ED", "#192313", "#57634E", "#44721A", "#D6DDCD")
    bg, ink, muted, accent, line = colors
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">Custom orbital network artwork for Abdullah Al Sami. AI, machine learning research, and software engineering.</desc>
<style>
:root{{--bg:{bg};--ink:{ink};--muted:{muted};--accent:{accent};--line:{line}}}
text{{font-family:Arial,Helvetica,sans-serif}} .mono{{font-family:Consolas,'Liberation Mono',monospace;letter-spacing:2px}}
.orbit{{transform-origin:0px 0px;animation:orbit 36s linear infinite}}
.signal{{animation:signal 6s ease-in-out infinite}}
.flow{{stroke-dasharray:5 12;animation:flow 12s linear infinite}}
@keyframes orbit{{to{{transform:rotate(360deg)}}}}
@keyframes signal{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
@keyframes flow{{to{{stroke-dashoffset:-170}}}}
@media(prefers-reduced-motion:reduce){{.orbit,.signal,.flow{{animation:none}}}}
</style>
<defs><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="var(--line)"/></pattern>
<radialGradient id="glow"><stop stop-color="var(--accent)" stop-opacity=".12"/><stop offset="1" stop-color="var(--accent)" stop-opacity="0"/></radialGradient></defs>
<rect width="{w}" height="{h}" rx="22" fill="var(--bg)"/><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="21" fill="url(#grid)" stroke="var(--line)"/>
{body}
</svg>'''

def network(cx, cy, r):
    s = [f'<g transform="translate({cx} {cy})"><circle r="{r*1.5}" fill="url(#glow)"/>']
    s.append(f'<circle r="{r}" fill="none" stroke="var(--line)"/>')
    s.append('<g class="orbit" fill="none" stroke="var(--accent)" stroke-width=".8">')
    for angle in range(0, 180, 20):
        s.append(f'<ellipse rx="{r}" ry="{r*.36}" transform="rotate({angle})" opacity=".48"/>')
    for rr in [.32, .64, .86]:
        s.append(f'<circle r="{r*rr}" opacity=".24"/>')
    for i in range(24):
        a = i*pi/12
        x,y = r*cos(a),r*sin(a)
        xx,yy = r*.64*cos(a+pi*.6),r*.64*sin(a+pi*.6)
        s.append(f'<path d="M{x:.2f},{y:.2f} L{xx:.2f},{yy:.2f}" opacity=".2"/>')
        s.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{2.8 if i%3 else 4}" fill="var(--accent)" stroke="none"/>')
    s.append('</g>')
    s.append(f'<circle r="{r+24}" fill="none" stroke="var(--line)" stroke-dasharray="2 10"/>')
    s.append('<circle r="9" fill="var(--accent)"/><circle r="22" class="signal" fill="none" stroke="var(--accent)"/>')
    s.append('</g>')
    return ''.join(s)

def hero(theme, mobile=False):
    w,h = (640,760) if mobile else (1200,590)
    p = 40 if mobile else 60
    s = [text(p,55 if mobile else 64,"S /",24,extra='font-weight="700"'),text(p+63,55 if mobile else 64,"XDR-SAM",14,extra='class="mono"')]
    s.append(text(w-p,55 if mobile else 64,"RESEARCH × ENGINEERING",11,"var(--muted)",'class="mono" text-anchor="end"'))
    s.append(f'<path d="M{p} 87 H{w-p}" stroke="var(--line)"/>')
    if mobile:
        s.append(network(479,290,104))
        s += [text(p,144,"ABDULLAH AL SAMI",14,"var(--muted)",'class="mono"'),text(p-5,258,"Sami.",112,extra='font-weight="700" letter-spacing="-7"'),text(p,371,"Curiosity into",46,extra='font-weight="700" letter-spacing="-2"'),text(p,426,"intelligence.",46,"var(--accent)",'font-weight="700" letter-spacing="-2"')]
        s += [text(p,486,"Exploring AI. Researching ML.",22,"var(--muted)"),text(p,519,"Building the systems around them.",22,"var(--muted)")]
        y=583
    else:
        s.append(network(935,291,166))
        s += [text(p,141,"ABDULLAH AL SAMI",14,"var(--muted)",'class="mono"'),text(p-7,263,"Sami.",136,extra='font-weight="700" letter-spacing="-8"'),text(p,333,"Curiosity into intelligence.",41,extra='font-weight="700" letter-spacing="-1.5"'),text(p,387,"Exploring AI. Researching ML.",22,"var(--muted)"),text(p,419,"Building the systems around them.",22,"var(--muted)")]
        y=472
    s.append(f'<rect x="{p}" y="{y}" width="190" height="34" rx="17" fill="var(--accent)"/>')
    s.append(text(p+95,y+22,"AI / ML FOCUSED",12,"var(--bg)",'class="mono" text-anchor="middle" font-weight="700"'))
    s.append(f'<path d="M{p} {h-57} H{w-p}" stroke="var(--line)"/>')
    s.append(text(p,h-27,"MODELS · PRODUCTS · INFRASTRUCTURE",11,"var(--muted)",'class="mono"'))
    s.append(text(w-p,h-27,"01 / PROFILE",11,"var(--muted)",'class="mono" text-anchor="end"'))
    return shell(w,h,theme,"Sami — Curiosity into intelligence.",''.join(s))

def process(theme, mobile=False):
    stages=[("Question","Define the problem"),("Experiment","Test the assumptions"),("Evaluate","Measure what matters"),("Build","Make it useful"),("Operate","Keep it reliable")]
    if mobile:
        s=[text(36,43,"FROM QUESTION TO SYSTEM",15,"var(--muted)",'class="mono"'),'<path d="M48 91 V351" stroke="var(--line)" stroke-width="2"/><path d="M48 91 V351" class="flow" stroke="var(--accent)" stroke-width="2"/>']
        for i,(name,caption) in enumerate(stages):
            y=91+i*65
            s.append(f'<circle cx="48" cy="{y}" r="6" fill="var(--bg)" stroke="var(--accent)" stroke-width="2"/>')
            s.append(text(76,y+7,name,23,extra='font-weight="700"'))
            s.append(text(255,y+7,caption,21,"var(--muted)"))
        return shell(640,400,theme,"Question. Experiment. Evaluate. Build. Operate.",''.join(s))
    s=[text(42,46,"FROM QUESTION TO SYSTEM",13,"var(--muted)",'class="mono"')]
    s.append('<path d="M65 103 H1090" stroke="var(--line)" stroke-width="2"/><path d="M65 103 H1090" class="flow" stroke="var(--accent)" stroke-width="2"/>')
    for i,(name,caption) in enumerate(stages):
        x=65+i*255
        s.append(f'<circle cx="{x}" cy="103" r="7" fill="var(--bg)" stroke="var(--accent)" stroke-width="2"/>')
        s.append(text(x-16,148,name,22,extra='font-weight="700"'))
        s.append(text(x-16,174,caption,13,"var(--muted)"))
    return shell(1200,205,theme,"Question. Experiment. Evaluate. Build. Operate.",''.join(s))

for theme in ("dark","light"):
    for mobile in (False,True):
        (OUT/f'hero-{theme}{"-mobile" if mobile else ""}.svg').write_text(hero(theme,mobile),encoding="utf-8")
    for mobile in (False,True):
        (OUT/f'process-{theme}{"-mobile" if mobile else ""}.svg').write_text(process(theme,mobile),encoding="utf-8")
print("Built eight self-contained, reduced-motion-aware SVG assets.")
