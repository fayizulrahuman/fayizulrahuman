"""Animated contribution graph -> assets/contrib.svg
Run with GITHUB_TOKEN set to pull live data; run with --demo for sample data."""
import os, sys, json, html, datetime as dt, urllib.request

USER = "fayizulrahuman"
SERIF = "Georgia, 'Times New Roman', serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
TEAL, VIOLET, PINK, MUTED = "#5eead4", "#a78bfa", "#f0abfc", "#8b93b0"

def render(days, total):
    """days: list of (day_label, count)"""
    W, H = 1200, 360
    L, R, T, B = 64, 1150, 96, 292
    n = len(days)
    ymax = max(5, max(c for _, c in days))
    xs = [L + i * (R - L) / (n - 1) for i in range(n)]
    ys = [B - c / ymax * (B - T) for _, c in days]
    d = f"M{xs[0]:.1f},{ys[0]:.1f}"
    for i in range(n - 1):
        mx = (xs[i] + xs[i + 1]) / 2
        d += f" C{mx:.1f},{ys[i]:.1f} {mx:.1f},{ys[i+1]:.1f} {xs[i+1]:.1f},{ys[i+1]:.1f}"
    area = d + f" L{xs[-1]:.1f},{B} L{xs[0]:.1f},{B} Z"
    CYC, DRAW = 10.0, 0.45
    css = f"""
.line{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw {CYC}s linear infinite}}
@keyframes draw{{0%{{stroke-dashoffset:1;opacity:1}}{DRAW*100:.0f}%{{stroke-dashoffset:0}}92%{{stroke-dashoffset:0;opacity:1}}97%,100%{{opacity:0}}}}
.glow{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw {CYC}s linear infinite;filter:blur(5px)}}
.area{{opacity:0;animation:area {CYC}s ease-out infinite}}
@keyframes area{{0%,{DRAW*100-6:.0f}%{{opacity:0}}{DRAW*100+10:.0f}%,92%{{opacity:1}}97%,100%{{opacity:0}}}}
.grid{{animation:gin 1.4s ease-out both}}@keyframes gin{{from{{opacity:0}}to{{opacity:1}}}}
"""
    pts = ""
    for i, ((lab, c), x, y) in enumerate(zip(days, xs, ys)):
        st = (i / (n - 1)) * DRAW * 100
        css += f"@keyframes p{i}{{0%,{st:.2f}%{{opacity:0;transform:scale(.2)}}{st+1.2:.2f}%{{opacity:1;transform:scale(1.35)}}{st+2.6:.2f}%,92%{{opacity:1;transform:scale(1)}}97%,100%{{opacity:0}}}}.p{i}{{transform-box:fill-box;transform-origin:center;opacity:0;animation:p{i} {CYC}s linear infinite}}\n"
        if c > 0:
            pts += f'<g class="p{i}"><circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{PINK}" fill-opacity=".18"/><circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{PINK}" stroke="#0b1020" stroke-width="2"/>'
            pts += f'<text x="{x:.1f}" y="{y-16:.1f}" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700" fill="#f4f5ff">{c}</text></g>'
        else:
            pts += f'<circle class="p{i}" cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{VIOLET}"/>'
    b = f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070b16"/><stop offset="1" stop-color="#160f2e"/></linearGradient>
<linearGradient id="ln" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{TEAL}"/><stop offset=".55" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".42"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>
<radialGradient id="g1" cx=".85" cy=".1" r=".7"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".25"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{W}" height="{H}" rx="24" fill="url(#bg)"/><rect width="{W}" height="{H}" rx="24" fill="url(#g1)"/>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="23" fill="none" stroke="{VIOLET}" stroke-opacity=".22"/>
<text x="40" y="52" font-family="{SERIF}" font-size="30" fill="#f4f5ff">Contribution <tspan font-style="italic" fill="url(#ln)">graph</tspan></text>
<text x="{W-40}" y="50" text-anchor="end" font-family="{MONO}" font-size="12.5" fill="{MUTED}" letter-spacing="1.5">{total} contributions · last {n} days</text>
<g class="grid">"""
    for k in range(0, 8 if ymax <= 7 else 6):
        v = k if ymax <= 7 else round(k * ymax / 5)
        y = B - v / ymax * (B - T)
        b += f'<line x1="{L}" y1="{y:.1f}" x2="{R}" y2="{y:.1f}" stroke="#fff" stroke-opacity=".06" stroke-dasharray="3 6"/><text x="{L-14}" y="{y+4:.1f}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">{v}</text>'
    for (lab, _), x in zip(days, xs):
        b += f'<text x="{x:.1f}" y="{B+22}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{TEAL}" fill-opacity=".8">{lab}</text>'
    b += f'<text x="{(L+R)/2}" y="{B+46}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}" letter-spacing="3">DAYS</text></g>'
    b += f'<path class="area" d="{area}" fill="url(#ar)"/>'
    b += f'<path class="glow" pathLength="1" d="{d}" fill="none" stroke="url(#ln)" stroke-width="7" stroke-linecap="round" stroke-opacity=".6"/>'
    b += f'<path class="line" pathLength="1" d="{d}" fill="none" stroke="url(#ln)" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
    b += pts
    b += f'<circle r="7" fill="#fff"><animateMotion dur="{CYC}s" repeatCount="indefinite" calcMode="linear" keyPoints="0;1;1" keyTimes="0;{DRAW};1" path="{d}"/><animate attributeName="opacity" dur="{CYC}s" repeatCount="indefinite" values="1;1;0;0" keyTimes="0;{DRAW};{DRAW+.04};1"/></circle>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Animated contribution graph"><style>{css}@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}.line,.glow{{stroke-dashoffset:0}}.area,[class^=p]{{opacity:1}}}}</style>{b}</svg>'

def fetch(token, ndays=31):
    end = dt.datetime.now(dt.timezone.utc)
    start = end - dt.timedelta(days=ndays + 1)
    q = """query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""
    body = json.dumps({"query": q, "variables": {"login": USER, "from": start.isoformat(), "to": end.isoformat()}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", body, {"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "contrib-graph"})
    data = json.load(urllib.request.urlopen(req))
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    alld = {d["date"]: d["contributionCount"] for w in cal for d in w["contributionDays"]}
    out = []
    for i in range(ndays - 1, -1, -1):
        day = (end - dt.timedelta(days=i)).date()
        out.append((str(day.day), alld.get(day.isoformat(), 0)))
    return out

# snapshot of the profile graph (Oct 19 -> Nov 18, 2026)
DEMO = [0]*18 + [1, 2, 0, 0, 0, 0, 0, 2, 6, 0, 0, 7, 3]
DEMO_LABELS = [str(x) for x in list(range(19, 32)) + list(range(1, 19))]

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "assets", "contrib.svg")
    if "--demo" in sys.argv or not os.environ.get("GITHUB_TOKEN"):
        days = list(zip(DEMO_LABELS, DEMO))
    else:
        days = fetch(os.environ["GITHUB_TOKEN"])
    open(out, "w").write(render(days, sum(c for _, c in days)))
    print("wrote", out)
