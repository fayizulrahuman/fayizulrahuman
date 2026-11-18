"""Animated contribution graph -> assets/contrib.svg
Run with GITHUB_TOKEN set to pull live data; run with --demo for sample data."""
import os, sys, json, html, datetime as dt, urllib.request

USER = "fayizulrahuman"
SERIF = "Georgia, 'Times New Roman', serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
TEAL, VIOLET, PINK, MUTED = "#5eead4", "#a78bfa", "#f0abfc", "#8b93b0"

def render(days, total):
    """days: list of (day_label, count). Everything animates with SMIL on one timeline."""
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
    CYC, D = 10, 0.45
    def anim(attr, vals, kts):
        return f'<animate attributeName="{attr}" dur="{CYC}s" repeatCount="indefinite" values="{vals}" keyTimes="{kts}"/>'
    # cumulative path length ratio for each point, so points appear exactly when the line reaches them
    import math
    seglen = []
    for i in range(n - 1):
        mx = (xs[i] + xs[i+1]) / 2
        P = [(xs[i], ys[i]), (mx, ys[i]), (mx, ys[i+1]), (xs[i+1], ys[i+1])]
        prev, ln = P[0], 0.0
        for k in range(1, 41):
            t = k / 40; u = 1 - t
            x = u**3*P[0][0] + 3*u*u*t*P[1][0] + 3*u*t*t*P[2][0] + t**3*P[3][0]
            y = u**3*P[0][1] + 3*u*u*t*P[1][1] + 3*u*t*t*P[2][1] + t**3*P[3][1]
            ln += math.hypot(x - prev[0], y - prev[1]); prev = (x, y)
        seglen.append(ln)
    tot = sum(seglen) or 1
    cum = [0.0]
    for sl in seglen: cum.append(cum[-1] + sl / tot)
    pts = ""
    for i, ((lab, c), x, y) in enumerate(zip(days, xs, ys)):
        st = cum[i] * D
        kt = f"0;{st:.4f};{min(st+0.012, 0.9):.4f};0.92;0.97;1"
        fade = anim("opacity", "0;0;1;1;0;0", kt)
        if c > 0:
            pts += f'<g opacity="0">{fade}<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{PINK}" fill-opacity=".18"/><circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{PINK}" stroke="#0b1020" stroke-width="2"/>'
            pts += f'<text x="{x:.1f}" y="{y-16:.1f}" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700" fill="#f4f5ff">{c}</text></g>'
        else:
            pts += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{VIOLET}" opacity="0">{fade}</circle>'
    defs = f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070b16"/><stop offset="1" stop-color="#160f2e"/></linearGradient>
<linearGradient id="ln" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{TEAL}"/><stop offset=".55" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".42"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>
<radialGradient id="g1" cx=".85" cy=".1" r=".7"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".25"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<filter id="blur"><feGaussianBlur stdDeviation="5"/></filter>
</defs>"""
    b = defs + f"""
<rect width="{W}" height="{H}" rx="24" fill="url(#bg)"/><rect width="{W}" height="{H}" rx="24" fill="url(#g1)"/>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="23" fill="none" stroke="{VIOLET}" stroke-opacity=".22"/>
<text x="40" y="52" font-family="{SERIF}" font-size="30" fill="#f4f5ff">Contribution <tspan font-style="italic" fill="url(#ln)">graph</tspan></text>
<text x="{W-40}" y="50" text-anchor="end" font-family="{MONO}" font-size="12.5" fill="{MUTED}" letter-spacing="1.5">{total} contributions · last {n} days</text>"""
    for k in range(0, 8 if ymax <= 7 else 6):
        v = k if ymax <= 7 else round(k * ymax / 5)
        y = B - v / ymax * (B - T)
        b += f'<line x1="{L}" y1="{y:.1f}" x2="{R}" y2="{y:.1f}" stroke="#fff" stroke-opacity=".06" stroke-dasharray="3 6"/><text x="{L-14}" y="{y+4:.1f}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">{v}</text>'
    for (lab, _), x in zip(days, xs):
        b += f'<text x="{x:.1f}" y="{B+22}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{TEAL}" fill-opacity=".8">{lab}</text>'
    b += f'<text x="{(L+R)/2}" y="{B+46}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}" letter-spacing="3">DAYS</text>'
    b += f'<path d="{area}" fill="url(#ar)" opacity="0">{anim("opacity","0;0;1;1;0;0",f"0;{D-.04:.3f};{D+.1:.3f};0.92;0.97;1")}</path>'
    for sw, op, extra in ((7, ".6", ' filter="url(#blur)"'), (3.2, "1", "")):
        b += (f'<path pathLength="1" d="{d}" fill="none" stroke="url(#ln)" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" stroke-opacity="{op}" stroke-dasharray="1" stroke-dashoffset="1"{extra}>'
              + anim("stroke-dashoffset", "1;0;0", f"0;{D};1") + anim("opacity", "1;1;0;0", "0;0.92;0.97;1") + '</path>')
    b += pts
    b += (f'<circle r="7" fill="#fff" opacity="0"><animateMotion dur="{CYC}s" repeatCount="indefinite" calcMode="linear" keyPoints="0;1;1" keyTimes="0;{D};1" path="{d}"/>'
          + anim("opacity", "1;1;0;0", f"0;{D};{D+.04};1") + '</circle>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Animated contribution graph">{b}</svg>'

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
