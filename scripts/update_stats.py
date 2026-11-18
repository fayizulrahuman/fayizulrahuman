"""Builds assets/stats.svg from the GitHub GraphQL API (no third-party cache).
Runs in GitHub Actions with GITHUB_TOKEN; use --demo for sample numbers."""
import os, sys, json, html, urllib.request

USER = "fayizulrahuman"
SERIF = "Georgia, 'Times New Roman', serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
TEAL, VIOLET, PINK, AMBER, BLUE, ROSE, MUTED = "#5eead4", "#a78bfa", "#f0abfc", "#fbbf24", "#60a5fa", "#fb7185", "#8b93b0"
E = html.escape

QUERY = """query($login:String!){user(login:$login){
 repositories(ownerAffiliations:OWNER,isFork:false,first:100){totalCount nodes{stargazerCount}}
 starredRepositories{totalCount}
 contributionsCollection{totalCommitContributions totalPullRequestContributions totalIssueContributions
   totalRepositoriesWithContributedCommits contributionCalendar{totalContributions}}}}"""

def fetch(token):
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", body, {"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-stats"})
    u = json.load(urllib.request.urlopen(req))["data"]["user"]
    cc = u["contributionsCollection"]
    return {
        "stars_earned": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "starred": u["starredRepositories"]["totalCount"],
        "repos": u["repositories"]["totalCount"],
        "contribs": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "contrib_repos": cc["totalRepositoriesWithContributedCommits"],
    }

DEMO = {"stars_earned": 8, "starred": 13, "repos": 9, "contribs": 41, "commits": 26, "contrib_repos": 8}

def render(d):
    W, H = 1200, 330
    tiles = [
        ("Stars earned", d["stars_earned"], "stars others gave your repos", TEAL),
        ("Repos you starred", d["starred"], "the count on your Stars tab", VIOLET),
        ("Public repos", d["repos"], "owned by you, forks excluded", PINK),
        ("Contributions", d["contribs"], "in the last year", AMBER),
        ("Commits", d["commits"], "in the last year", BLUE),
        ("Repos worked on", d["contrib_repos"], "with commits, last year", ROSE),
    ]
    b = f'''<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070b16"/><stop offset="1" stop-color="#160f2e"/></linearGradient>
<radialGradient id="g1" cx=".85" cy=".1" r=".7"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".25"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient></defs>
<rect width="{W}" height="{H}" rx="24" fill="url(#bg)"/><rect width="{W}" height="{H}" rx="24" fill="url(#g1)"/>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="23" fill="none" stroke="{VIOLET}" stroke-opacity=".22"/>
<text x="40" y="52" font-family="{SERIF}" font-size="30" fill="#f4f5ff">GitHub <tspan font-style="italic" fill="{TEAL}">at a glance</tspan></text>
<text x="{W-40}" y="50" text-anchor="end" font-family="{MONO}" font-size="12.5" fill="{MUTED}" letter-spacing="1.5">live from the GitHub API</text>'''
    cw, ch, gap = 352, 112, 22
    for i, (lab, val, sub, c) in enumerate(tiles):
        x = 40 + (i % 3) * (cw + gap); y = 84 + (i // 3) * (ch + 16)
        t = 0.15 * i
        b += f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.7s" begin="{t:.2f}s" fill="freeze"/>'
        b += f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="16" fill="#0b1226" stroke="{c}" stroke-opacity=".45"/><rect x="{x}" y="{y+20}" width="4" height="{ch-40}" rx="2" fill="{c}"/>'
        b += f'<text x="{x+26}" y="{y+34}" font-family="{MONO}" font-size="12" fill="{c}" letter-spacing="1.5">{E(lab)}</text>'
        b += f'<text x="{x+26}" y="{y+82}" font-family="{SERIF}" font-size="50" fill="#f4f5ff">{val}</text>'
        b += f'<text x="{x+cw-22}" y="{y+82}" text-anchor="end" font-family="{SANS}" font-size="12.5" fill="{MUTED}">{E(sub)}</text>'
        b += f'<circle cx="{x+cw-24}" cy="{y+28}" r="4" fill="{c}"><animate attributeName="opacity" values="1;.2;1" dur="2.8s" begin="{t:.2f}s" repeatCount="indefinite"/></circle></g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub stats">{b}</svg>'

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "assets", "stats.svg")
    tok = os.environ.get("GITHUB_TOKEN")
    data = DEMO if ("--demo" in sys.argv or not tok) else fetch(tok)
    open(out, "w").write(render(data)); print("wrote stats.svg", data)
