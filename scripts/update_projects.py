"""Builds one animated card per public repo and rewrites the project grid in README.md.
Runs in GitHub Actions (GITHUB_TOKEN) so new repos and star counts appear automatically.
Use --demo to build from the bundled sample data without network access."""
import os, sys, json, glob, html, textwrap, urllib.request

USER = "fayizulrahuman"
MAX_REPOS = 6                      # cards shown (keep it even for a tidy 2-column grid)
EXCLUDE = {USER, USER + ".github.io"}   # repos never shown (the profile repo itself, etc.)
ROOT = os.path.join(os.path.dirname(__file__), "..")
E = html.escape
SERIF = "Georgia, 'Times New Roman', serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
COLORS = ["#5eead4", "#a78bfa", "#f0abfc", "#fbbf24", "#60a5fa", "#fb7185"]

def card(repo, desc, chips, stars, c):
    W, H = 580, 240
    b = f'''<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070b16"/><stop offset="1" stop-color="#160f2e"/></linearGradient>
<radialGradient id="g1" cx=".8" cy=".4" r=".6"><stop offset="0" stop-color="#a78bfa" stop-opacity=".3"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></radialGradient></defs>
<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="20" fill="url(#bg)" stroke="{c}" stroke-opacity=".45"/><rect x="2" y="2" width="{W-4}" height="{H-4}" rx="20" fill="url(#g1)"/>
<circle cx="{W-34}" cy="46" r="5" fill="{c}"><animate attributeName="opacity" values="1;.2;1" dur="2.6s" repeatCount="indefinite"/></circle>'''
    if stars:
        b += f'<text x="{W-52}" y="51" text-anchor="end" font-family="{MONO}" font-size="13" fill="#e8eaf6">★ {stars}</text>'
    b += f'<text x="32" y="48" font-family="{MONO}" font-size="12" fill="{c}" letter-spacing="2">{E(chips[0].lower() if chips else "repository")}</text>'
    b += f'<text x="32" y="94" font-family="{SERIF}" font-size="36" fill="#f4f5ff" letter-spacing="-.5">{E(repo)}</text>'
    y = 126
    for ln in textwrap.wrap(desc, 62)[:3]:
        b += f'<text x="32" y="{y}" font-family="{SANS}" font-size="14.5" fill="#aab0cf">{E(ln)}</text>'; y += 22
    x = 32
    for ch in chips[:3]:
        w = len(ch) * 7.4 + 24
        b += f'<rect x="{x}" y="190" width="{w:.0f}" height="28" rx="14" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-opacity=".4"/>'
        b += f'<text x="{x+w/2:.0f}" y="209" text-anchor="middle" font-family="{MONO}" font-size="12" fill="#e8eaf6">{E(ch)}</text>'
        x += w + 10
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{E(repo)}">{b}</svg>'

def short(text, limit=165):
    text = " ".join((text or "No description yet.").split())
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0].rstrip(".,;:") + "…"

def fetch():
    hdr = {"User-Agent": "profile-readme", "Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"): hdr["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed", headers=hdr)
    return json.load(urllib.request.urlopen(req))

DEMO = [  # shape of the GitHub API response (name, description, language, stargazers_count, topics ...)
 {"name": "fallguard", "description": "AI-powered, privacy-first fall detection for the elderly.", "language": "Python", "stargazers_count": 1, "topics": []},
 {"name": "VitalSync", "description": "VitalSync is a unified mobile health platform.", "language": "JavaScript", "stargazers_count": 1, "topics": []},
 {"name": "hidden-gems", "description": "A full-stack travel app.", "language": "JavaScript", "stargazers_count": 1, "topics": ["nodejs", "mongodb", "maplibre"]},
 {"name": "fintrack", "description": "FinTrack - Smart Personal Expense Manager.", "language": "TypeScript", "stargazers_count": 2, "topics": []},
]

def main():
    repos = DEMO if "--demo" in sys.argv else fetch()
    repos = [r for r in repos if not r.get("fork") and not r.get("archived") and r["name"] not in EXCLUDE][:MAX_REPOS]
    over = {}
    p = os.path.join(ROOT, "scripts", "projects.override.json")
    if os.path.exists(p): over = json.load(open(p))
    os.makedirs(os.path.join(ROOT, "assets", "cards"), exist_ok=True)
    for f in glob.glob(os.path.join(ROOT, "assets", "cards", "*.svg")): os.remove(f)
    cells = []
    for i, r in enumerate(repos):
        o = over.get(r["name"], {})
        chips = o.get("chips") or (r.get("topics") or [])[:3] or ([r["language"]] if r.get("language") else [])
        svg = card(r["name"], o.get("desc") or short(r.get("description")), chips, r.get("stargazers_count", 0), COLORS[i % len(COLORS)])
        open(os.path.join(ROOT, "assets", "cards", r["name"] + ".svg"), "w").write(svg)
        cells.append(f'<td width="50%"><a href="https://github.com/{USER}/{r["name"]}"><img src="assets/cards/{r["name"]}.svg" alt="{E(r["name"])}"/></a></td>')
    rows = ["<tr>\n" + "\n".join(cells[i:i+2]) + ("\n<td width=\"50%\"></td>" if len(cells[i:i+2]) == 1 else "") + "\n</tr>" for i in range(0, len(cells), 2)]
    block = "<!--PROJECTS:START-->\n<table>\n" + "\n".join(rows) + "\n</table>\n<!--PROJECTS:END-->"
    rp = os.path.join(ROOT, "README.md"); md = open(rp).read()
    a, z = md.index("<!--PROJECTS:START-->"), md.index("<!--PROJECTS:END-->") + len("<!--PROJECTS:END-->")
    open(rp, "w").write(md[:a] + block + md[z:])
    print("cards:", [r["name"] for r in repos])

if __name__ == "__main__":
    main()
