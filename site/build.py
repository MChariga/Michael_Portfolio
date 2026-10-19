"""Static site generator: content.json -> dist/*.html (+ sitemap.xml, robots.txt). Run: python3 build.py"""
import json, shutil, pathlib, re, hashlib, datetime
from PIL import Image
import rcssmin, rjsmin
from html import escape as e
C = json.load(open("content.json", encoding="utf-8")); S = C["site"]; B = C["booking"]; OUT = pathlib.Path("dist")
PAGES = [("Home", "index.html"), ("Work", "work.html"), ("Projects", "projects.html"), ("Publications", "publications.html"),
         ("Gallery", "gallery.html"), ("About", "about.html"), ("CV", "cv.html"), ("Services", "services.html")]
ALL = PAGES + [("Book", "book.html"), ("Conference", "conference.html")]
COL = {"Education": "edu", "Agriculture": "agri", "Parenting": "par", "Conferences": "conf"}

shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir()
ASSET = {}
for _sub, _min in (("css", rcssmin.cssmin), ("js", rjsmin.jsmin)):
    (OUT / _sub).mkdir()
    for _f in sorted(pathlib.Path(_sub).glob("*")):
        _code = _min(_f.read_text(encoding="utf-8")); _h = hashlib.md5(_code.encode()).hexdigest()[:8]
        _name = f"{_f.stem}.{_h}{_f.suffix}"; (OUT / _sub / _name).write_text(_code, encoding="utf-8"); ASSET[_f.name] = _name


def optimise():
    """Converts photos to WebP at the sizes the site actually shows them."""
    src, dst = pathlib.Path("assets"), OUT / "assets"
    (dst / "gallery" / "t").mkdir(parents=True, exist_ok=True)
    def save(im, path, w, q):
        if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save(path, "WEBP", quality=q, method=6)
    width = {"profile": 360, "about": 800, "conference": 1000, "aspire-cert": 700}
    for f in src.iterdir():
        if f.is_dir(): continue
        if f.name == "og.jpg": shutil.copy(f, dst / f.name)
        elif f.suffix.lower() in (".jpg", ".png"):
            im = Image.open(f).convert("RGB")
            if f.stem == "cover": save(im, dst / "cover.webp", 2000, 72); save(im, dst / "cover-1200.webp", 1200, 70)
            else: save(im, dst / (f.stem + ".webp"), width.get(f.stem, 720), 84 if f.stem == "profile" else 76)
        else: shutil.copy(f, dst / f.name)
    for f in (src / "gallery").glob("*.jpg"):
        im = Image.open(f).convert("RGB"); save(im, dst / "gallery" / (f.stem + ".webp"), 1200, 74); save(im, dst / "gallery" / "t" / (f.stem + ".webp"), 640, 70)


optimise()
ICON = {"edu": "&#127891;", "agri": "&#127807;", "par": "&#128106;"}


ICONS = {
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M3 13h18"/>',
    "clip": '<path d="M9 4h6l1 2h3v14H5V6h3z"/><path d="M9 12h6M9 16h4"/>',
    "network": '<circle cx="12" cy="5" r="2.6"/><circle cx="5" cy="18" r="2.6"/><circle cx="19" cy="18" r="2.6"/><path d="M12 7.6v4.2M12 11.8 6.4 16M12 11.8 17.6 16"/>',
    "bars": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "db": '<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>',
    "search": '<circle cx="11" cy="11" r="6"/><path d="M16 16l5 5"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
    "pin": '<path d="M12 21s7-6.2 7-11a7 7 0 0 0-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "trend": '<path d="M3 18l5-6 4 3 8-10"/><path d="M15 5h5v5"/>'}
svg = lambda k: f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[k]}</svg>'


def sh(eyebrow, title, link=None, href=None, lede=None):
    a = f'<a href="{href}">{link} &rarr;</a>' if link else ""
    return f'<div class="sh"><div><span class="eyebrow">{eyebrow}</span><h2>{title}</h2></div>{a}</div>' + (f'<p class="lede">{lede}</p>' if lede else "")


def card(p):
    tags = "".join(f"<span>{e(t)}</span>" for t in p["tags"])
    a = f'<a href="{p["link"]}">{e(p["label"])} &rarr;</a>' if p.get("link") else ""
    k = COL.get(p.get("area", ""), "agri")
    media = (f'<img src="assets/{p["img"]}" alt="{e(p["title"])}" loading="lazy">' if p.get("img") else
             f'<div class="tile {k}"><b>{e(p["tags"][0])}</b><span>{e(" · ".join(p["tags"][1:]))}</span></div>')
    note = f'<small class="note">{e(p["note"])}</small>' if p.get("note") else ""
    return (f'<article class="card" data-t="{p["type"]}">{media}'
            f'<div class="cb"><span class="area {k}">{e(p.get("area", ""))}</span><h3>{e(p["title"])}</h3><div class="tags">{tags}</div><p>{e(p["desc"])}</p>{note}{a}</div></article>')


def row(title, sub, year, icon, link=None):
    t = f'<a href="{link}">{e(title)}</a>' if link else e(title)
    return f'<li><i>{icon}</i><div><b>{t}</b><small>{e(sub)}</small></div><time>{e(year)}</time></li>'


def tabs(items):
    return '<div class="tabs">' + "".join(f'<button data-f="{k}"{" class=on" if k == "all" else ""}>{v}</button>' for k, v in items) + "</div>"


def page(fn, title, desc, body, og="og.jpg", scripts=(), extra_ld=None, preload=""):
    nav = "".join(f'<a href="{h}"{" aria-current=page" if h == fn else ""}>{t}</a>' for t, h in PAGES) + f'<a class="navbtn" href="book.html">Book a call</a>'
    person = {"@type": "Person", "@id": S["url"] + "/#me", "name": S["full"], "jobTitle": S["headline"], "url": S["url"], "image": f'{S["url"]}/assets/profile.webp',
              "email": S["email"], "sameAs": [S["github"], S["linkedin"]], "address": {"@type": "PostalAddress", "addressLocality": "Nairobi", "addressCountry": "KE"},
              "knowsAbout": ["Monitoring and evaluation", "Research methods", "Survey design", "Dashboards", "R Shiny", "KoboToolbox", "Agroecology", "Mathematics education"]}
    graph = [person, {"@type": "WebSite", "url": S["url"], "name": S["full"], "publisher": {"@id": S["url"] + "/#me"}}] + ([extra_ld] if extra_ld else [])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, separators=(",", ":"))
    fav = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230b2545'/%3E%3Ctext x='32' y='42' font-family='Georgia,serif' font-size='28' font-weight='700' fill='%23d6a43e' text-anchor='middle'%3EMC%3C/text%3E%3C/svg%3E"
    ttl = title if title.startswith(S["name"]) else f'{title} | {S["name"]}'
    js = "".join(f'<script src="js/{h}" defer></script>' for h in (ASSET["core.js"],) + tuple(ASSET[x] for x in scripts))
    bookvar = f",BOOK={json.dumps(B, separators=(',', ':'))}" if "book.js" in scripts else ""
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(ttl)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{S["url"]}/{"" if fn == "index.html" else fn}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#0b2545"><link rel="icon" href="{fav}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{S["full"]}"><meta property="og:title" content="{e(ttl)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{S["url"]}/{"" if fn == "index.html" else fn}"><meta property="og:image" content="{S["url"]}/assets/{og}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="fonts/newsreader-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>{preload}<script type="application/ld+json">{ld}</script><link rel="stylesheet" href="css/{ASSET["style.css"]}"></head><body>
<header><div class="wrap bar"><a class="logo" href="index.html"><b>{S["name"]}</b><span>{S["tagline"]}</span></a><button class="burger" aria-label="Menu">&#9776;</button><nav>{nav}</nav></div></header>
<main>{body}</main>
<footer id="contact"><div class="wrap ft"><div><h2>Get in touch</h2><p>For research collaborations, evaluations, dashboards and data quality support.</p>
<p><a href="mailto:{S["email"]}" data-mail>{S["email"]}</a><br><a href="{S["linkedin"]}">LinkedIn</a> &middot; <a href="{S["github"]}">GitHub</a><br>{S["location"]}</p>
<p><a class="btn gold" href="book.html">Book a call</a></p></div>
<form id="cf"><input name="n" placeholder="Name" required><input name="m" type="email" placeholder="Email" required><textarea name="b" rows="3" placeholder="Message" required></textarea><button class="btn gold">Send message</button></form></div>
<div class="wrap fb">&copy; 2026 {S["full"]}. Evidence today. Better tomorrow.</div></footer>
<script>const EMAIL="{S["email"]}"{bookvar}</script>{js}</body></html>'''


def profile():
    return f'''<section class="hero"><div class="pc"><div class="cover"><img class="cv-img" src="assets/cover.jpg" srcset="assets/cover-1200.jpg 1200w, assets/cover.jpg 2000w" sizes="100vw" width="2000" height="500" alt="" fetchpriority="high" decoding="async">
<div class="cover-in"><img class="avatar" src="assets/profile.jpg" width="360" height="360" alt="Portrait of {e(S["full"])}">
<div class="cover-text"><span class="eyebrow">Research &middot; Evaluation &middot; Data systems</span><b>Evidence that helps programmes learn.</b></div></div></div>
<div class="hbody"><div class="pmain"><h1>{S["full"]}</h1><p class="hl">{e(S["headline"])}</p><p class="sub">{e(S["sub"])}</p>
<p class="meta">{e(S["location"])} &middot; <a href="mailto:{S["email"]}" data-mail>Contact info</a> &middot; <a href="{S["github"]}">GitHub</a> &middot; <a href="{S["linkedin"]}">LinkedIn</a></p>
<p class="open"><span></span>{e(S["open_to"])}</p>
<div class="btns"><a class="btn" href="book.html">Book a call</a><a class="btn o" href="cv.html">View CV</a><a class="btn o" href="{S["cv"]}" download>Download CV</a></div></div>
<aside class="glance dk"><span class="eyebrow">At a glance</span><ul class="gl"><li>{svg("layers")}<p><b>Worked across</b>Education, agriculture, parenting</p></li><li>{svg("bars")}<p><b>Methods</b>MEL, RCTs, surveys, dashboards</p></li><li>{svg("pin")}<p><b>Based</b>{e(S["location"])}</p></li></ul></aside></div></div></section>'''


def areas_cards():
    out = ""
    for a in C["areas"]:
        img = f'<img src="assets/{a["img"]}" alt="{e(a["name"])}" loading="lazy">' if a["img"] else f'<div class="ph-icon {a["color"]}">{ICON[a["color"]]}</div>'
        pts = "".join(f"<li>{e(x)}</li>" for x in a["points"])
        out += f'<article class="acard {a["color"]}">{img}<div class="cb"><span class="area {a["color"]}">{e(a["tag"])}</span><h3>{e(a["name"])}</h3><p>{e(a["blurb"])}</p><ul class="dots">{pts}</ul><a href="work.html#{a["id"]}">See the detail &rarr;</a></div></article>'
    return out


def paths(here=False):
    team = "#team" if here else "services.html#team"
    second = f'<a class="btn o" href="mailto:{S["email"]}" data-mail>Email me</a>' if here else '<a class="btn o" href="services.html">How I can help</a>'
    return f'''<div class="paths three"><article class="path"><div class="ic">{svg("briefcase")}</div><span class="eyebrow">For employers</span><h3>Hiring?</h3><p>I am open to full-time and contract roles in monitoring, evaluation, research and data systems. My CV has the full detail.</p><div class="btns"><a class="btn" href="cv.html">View CV</a><a class="btn o" href="{S["cv"]}" download>Download CV</a></div></article>
<article class="path"><div class="ic">{svg("clip")}</div><span class="eyebrow">For clients</span><h3>Have a project?</h3><p>Evaluation design, data collection systems, dashboards, analysis and training. Reach out and we will talk it through.</p><div class="btns"><a class="btn" href="book.html">Book a call</a>{second}</div></article>
<article class="path"><div class="ic">{svg("network")}</div><span class="eyebrow">For specialists</span><h3>Join my consultancy team?</h3><p>I work with specialists on larger assignments. Send your CV (required) and a work sample (optional), then email me.</p><div class="btns"><a class="btn" href="{team}">Send your CV</a><a class="btn o" href="mailto:{S["email"]}" data-mail>Email me</a></div></article></div>'''


def home():
    feat = "".join(card(p) for t in C["featured"] for p in C["projects"] if p["title"] == t)
    st = "".join(f'<div><b>{v}</b><span>{l}</span></div>' for v, l in C["stats"])
    pubs = "".join(row(p["title"], p["venue"], p["year"], "&#128196;", p.get("link")) for p in C["pubs"])
    aw = "".join(row(a["title"], a["by"], a["year"], "&#127942;", a.get("link")) for a in C["awards"])
    g = [x for x in C["gallery"] if x["file"] in ("g41.jpg", "g00.jpg", "g16.jpg", "g30.jpg")]
    strip = "".join(f'<img src="assets/gallery/{x["file"]}" alt="{e(x["caption"])}" loading="lazy">' for x in g)
    return f'''{profile()}
<section class="wrap sec">{sh("What I have worked on", "Education, agriculture and parenting", "Full detail", "work.html", "The settings so far. The questions change, the approach does not: what is working, for whom, and why.")}<div class="agrid">{areas_cards()}</div></section>
<section class="band"><div class="wrap"><span class="eyebrow">Selected achievements</span><h2>What the work adds up to</h2><div class="stats">{st}</div></div></section>
<section class="wrap sec alt">{sh("Work with me", "Hiring, a project or a collaboration", "Services", "services.html")}{paths()}</section>
<section class="wrap sec">{sh("Selected work", "Dashboards, reports and code", "View all projects", "projects.html")}<div class="grid g3">{feat}</div></section>
<section class="wrap sec alt">{sh("From the field", "Fieldwork, camps and conferences", "View gallery", "gallery.html")}<div class="strip">{strip}</div></section>
<section class="wrap sec cols two"><div><span class="eyebrow">Publications</span><h3>Papers and reports</h3><ul class="rows">{pubs}</ul></div><div><span class="eyebrow">Recognition</span><h3>Awards and funding</h3><ul class="rows">{aw}</ul></div>
</section>'''


def work():
    camps = ""
    for n, w, t in C["camps"]:
        l = C["camps_link"].get(n)
        nm = f'<a href="{l}"{" target=_blank rel=noopener" if l.startswith("http") else ""}>{e(n)}</a>' if l else e(n)
        camps += f'<li><b>{nm}</b><small>{e(w)}</small>{f"<em>{t}</em>" if t else ""}</li>'
    frn = "".join(f'<li><b>{e(x[0])}</b>{f"<em>{x[1]}</em>" if x[1] else ""}<small>{e(x[2])}</small>{f"<a class=more href={x[3]}>{x[4] if len(x) > 4 else "Read the report"} &rarr;</a>" if len(x) > 3 else ""}</li>' for x in C["frns"])
    dl = lambda k: "".join(f'<li><a href="{u}"{" target=_blank rel=noopener" if u.startswith("http") else ""}>{e(t)}</a></li>' for t, u in C["docs"][k])
    fund = "".join(f"<span>{e(x)}</span>" for x in C["funders"])
    return f'''<section class="wrap sec"><h1 class="pt">Work so far</h1><p class="lede">Where I have worked, what I did, and what came out of it. These are the settings so far, not the limit of what the methods can do.</p>
<nav class="jump"><a class="edu" href="#education">Education</a><a class="agri" href="#agriculture">Agriculture</a><a class="par" href="#parenting">Parenting Initiative</a></nav></section>
<section class="wrap sec wsec edu" id="education"><div class="whead"><span class="area edu">Volunteer, Africa Maths Initiative</span><h2>Education</h2>
<p>I work mainly as a volunteer with the Africa Maths Initiative (AMI). At each camp I create hands-on, gamified maths lessons and facilitate them with learners. I also help measure what the camps achieve. The team has run 26 camps since 2022.</p></div>
<div class="wgrid"><div><h3>Camps I have taken part in</h3><ul class="chips">{camps}<li><b>And others</b><small>Across East Africa</small></li></ul></div>
<div><h3>My contribution</h3><ul class="dots"><li>Created and facilitated hands-on, gamified maths lessons</li><li>Designed data collection tools for baseline and endline studies</li><li>Analysed the data and contributed to camp reports</li><li>Presented the AMI camps at the AFRICME7 conference, Johannesburg</li></ul>
<h3>Documentation</h3><ul class="dots docs">{dl("education")}</ul><h3>Outputs</h3><ul class="dots"><li>Two co-authored papers on maths camps</li><li>AFRICME7 proceedings paper on 21 maths camps</li></ul><p><a class="more" href="publications.html">See publications &rarr;</a> &nbsp; <a class="more" href="conference.html">AFRICME7 page &rarr;</a></p></div></div></section>
<section class="wrap sec wsec agri" id="agriculture"><div class="whead"><span class="area agri">Kenya Agroecology Hub partnership</span><h2>Agriculture</h2>
<p>In collaboration with the Kenya Agroecology Hub, I support Farmer Research Networks (FRNs) and CRFS grantees in western Kenya. I have directly supported 10 partner organisations working in agroecology.</p></div>
<div class="wgrid"><div><h3>Where it started</h3><p>{e(C["pilot"])} <a class="more" href="{C["pilot_link"]}">Read the pilot report &rarr;</a></p><h3>Farmer-led research I have supported</h3><ul class="chips">{frn}</ul><h3>Funded by</h3><div class="tags big">{fund}</div></div>
<div><h3>My role in each study</h3><ul class="dots"><li>Designing data collection tools in KoboCollect</li><li>Training data collectors</li><li>Preparing field protocols</li><li>Data cleaning and analysis</li><li>Creating dashboards in Python, Excel and R Shiny</li></ul>
<h3>Documentation</h3><ul class="dots docs">{dl("agriculture")}</ul><h3>See the work</h3><p><a class="more" href="projects.html">Dashboards, reports and code &rarr;</a></p></div></div></section>
<section class="wrap sec wsec par" id="parenting"><div class="whead"><span class="area par">Global Parenting Initiative</span><h2>Parenting Initiative</h2>
<p>I supported the ParentApp for Teens randomised controlled trial in Mwanza, Tanzania, part of the Global Parenting Initiative, working in collaboration with the National Institute for Medical Research (NIMR), Mwanza Centre. My engagement lasted three months.</p></div>
<div class="wgrid"><div><h3>My contribution</h3><ul class="dots"><li>Supported the field team to obtain consent forms from caregivers</li><li>Followed up with participants and documented the challenges they had using the ParentApp on their phones</li><li>Resolved problems where possible so participants could keep taking part</li></ul></div>
<div><aside class="partner dk"><span class="eyebrow">Research partner</span><h3>National Institute for Medical Research</h3><p>Mwanza Centre, Tanzania</p><p class="pn">The ParentApp for Teens trial was carried out in collaboration with NIMR.</p></aside></div></div></section>'''


def projects():
    return f'''<section class="wrap sec"><h1 class="pt">Projects</h1><p class="lede">Each one is linked to the live version or the full document.</p>
{tabs([("all", "All"), ("dashboard", "Dashboards"), ("report", "Reports"), ("code", "Data &amp; Code")])}<div class="grid g3">{"".join(card(p) for p in C["projects"])}</div></section>'''


def pubs():
    r = "".join(row(p["title"], p["venue"], p["year"], "&#128196;", p.get("link")) for p in C["pubs"])
    return f'''<section class="wrap sec"><h1 class="pt">Publications</h1><p class="lede">Conference presentations, accepted papers and research reports.</p><ul class="rows big">{r}</ul>
<h2 style="margin-top:40px">Reports</h2><div class="grid g3">{"".join(card(p) for p in C["projects"] if p["type"] == "report")}</div></section>'''


def about():
    ed = "".join(f"<li><b>{e(a)}</b><small>{e(b)}</small></li>" for a, b in C["education"])
    sk = "".join(f"<li>{e(s)}</li>" for s in C["skills"]); it = "".join(f"<span>{e(s)}</span>" for s in C["interests"])
    return f'''<section class="wrap sec ab"><div><h1 class="pt">About me</h1><p>{e(S["about"])}</p><h3>Education</h3><ul class="rows">{ed}</ul>
<h3>Research interests</h3><div class="tags big">{it}</div><p style="margin-top:24px"><a class="btn" href="cv.html">View my CV</a> <a class="btn o" href="book.html">Book a session</a></p></div>
<aside><img src="assets/about.jpg" alt="{e(S["full"])} at work" loading="lazy"><h3>Skills</h3><ul class="dots">{sk}</ul>
<img src="assets/aspire-cert.jpg" alt="Aspire Leaders Program certificate, March 2025" loading="lazy"></aside></section>'''


def conference():
    k = C["conference"]
    img = f'<img class="cphoto" src="assets/{k["photo"]}" alt="Presenting at {k["name"]}, {e(k["host"])}">'
    meta = "".join(f"<li><b>{a}</b><small>{e(v)}</small></li>" for a, v in [("Conference", k["name"] + ": " + k["full"]), ("Venue", k["host"]), ("Year", k["year"]), ("Funding", k["funder"])] if v)
    out = "".join(f"<li>{e(o)}</li>" for o in k["outcomes"])
    return f'''<section class="wrap sec ab"><div><h1 class="pt">{k["name"]} in Johannesburg</h1><p class="lede">{e(k["host"])}, {k["year"]}</p>{img}
<h3>My role</h3><p>{e(k["role"])}</p><h3>Funding</h3><p>{e(k["funding"])}</p><h3>Outcomes</h3><ul class="dots">{out}</ul></div>
<aside><h3>Conference details</h3><ul class="rows">{meta}</ul><p><a class="btn" href="publications.html">See publications</a></p></aside></section>'''


def gallery():
    from PIL import Image
    sec = C["gallery_sections"]; out = ""
    counts = {k: sum(1 for g in C["gallery"] if g["category"] == k) for k in sec}
    for cat, (title, blurb) in sec.items():
        figs = ""
        for g in [x for x in C["gallery"] if x["category"] == cat]:
            w, h = Image.open("assets/gallery/" + g["file"]).size; ar = round(w / h, 3)
            figs += (f'<figure class="gi" style="--ar:{ar}" tabindex="0" data-full="assets/gallery/{g["file"]}"><img src="assets/gallery/t/{g["file"]}" alt="{e(g["caption"])}" width="{w}" height="{h}" loading="lazy" decoding="async">'
                     f'<figcaption>{e(g["caption"])}</figcaption></figure>')
        out += (f'<section class="gsec" data-t="{cat}"><header class="gh"><span class="area {COL[cat]}">{e(cat)}</span><h2>{e(title)}</h2><p>{e(blurb)}</p></header>'
                f'<div class="jr">{figs}</div></section>')
    total = len(C["gallery"])
    pills = tabs([("all", f"All <i>{total}</i>")] + [(k, f"{k} <i>{v}</i>") for k, v in counts.items()])
    return f'''<section class="wrap sec"><h1 class="pt">Gallery</h1><p class="lede">Moments from fieldwork, camps and conferences. Select a photo to view it full size.</p>{pills}{out}</section>'''


def cv():
    V = C["cv"]
    ex = ""
    for x in V["experience"]:
        b = "".join(f"<li>{e(t)}</li>" for t in x["bullets"])
        ex += f'<div class="job"><div class="jh"><div><h4>{e(x["role"])}</h4><p>{e(x["org"])} &middot; {e(x["place"])}</p></div><time>{e(x["period"])}</time></div><ul class="dots">{b}</ul></div>'
    ed = "".join(f"<li><div><b>{e(a)}</b><small>{e(b)}</small></div><time>{e(c)}</time></li>" for a, b, c in V["education"])
    pb = "".join(f'<li><div><b>{e(p["title"])}</b><small>{e(p["venue"])}{", " + p["year"] if p["year"] else ""}</small></div></li>' for p in C["pubs"])
    rp = "".join(f"<li><div><b>{e(a)}</b><small>{e(b)}</small></div></li>" for a, b in V["reports"])
    comp = "".join(f"<li>{e(x)}</li>" for x in V["competencies"]); aw = "".join(f"<li>{e(x)}</li>" for x in V["awards"])
    tl = "".join(f"<span>{e(x)}</span>" for x in V["tools"])
    return f'''<section class="wrap sec"><div class="cvbar"><div><h1 class="pt">Curriculum vitae</h1><p class="lede">Read it here, open the PDF, or download a copy.</p></div>
<div class="btns"><a class="btn" href="{S["cv"]}" target="_blank" rel="noopener">View PDF</a><a class="btn o" href="{S["cv"]}" download>Download PDF</a><button class="btn o" onclick="window.print()">Print</button></div></div>
<article class="cvdoc"><header class="cvh"><div><h2>{S["full"]}</h2><p class="hl">{e(S["headline"])}</p></div><p class="cvc">{e(S["location"])}<br><a href="mailto:{S["email"]}">{S["email"]}</a><br><a href="{S["github"]}">github.com/MChariga</a></p></header>
<h3>Profile</h3><p>{e(V["summary"])}</p><h3>Core competencies</h3><ul class="cols3">{comp}</ul><h3>Experience</h3>{ex}
<h3>Education</h3><ul class="rows plain">{ed}</ul><h3>Publications and presentations</h3><ul class="rows plain">{pb}</ul><h3>Reports</h3><ul class="rows plain">{rp}</ul><h3>Awards</h3><ul class="dots">{aw}</ul><h3>Tools</h3><div class="tags big">{tl}</div><p class="small">Referees available on request.</p></article></section>'''


def services():
    V = C["services"]
    li = lambda xs: "".join(f"<li>{e(x)}</li>" for x in xs)
    ic = ["bars", "db", "search"]
    pillars = "".join(f'<article class="pillar"><div class="ic">{svg(ic[i])}</div><h3>{e(p["name"])}</h3><ul class="dots">{li(p["items"])}</ul></article>' for i, p in enumerate(V["pillars"]))
    sc = V["scope"]; ico = ["bars", "network", "trend"]
    rows = "".join(f'<li>{svg(ico[i])}<div><b>{e(t)}</b><span>{e(d)}</span></div></li>' for i, (t, d) in enumerate(sc["items"]))
    scope = (f'<div class="scope dk"><div class="sc-l"><span class="eyebrow">{e(sc["kicker"])}</span><h3>{e(sc["title"])}</h3><p>{e(sc["text"])}</p></div><ul class="sc-r">{rows}</ul>'
             f'<div class="sc-foot"><span>{e(sc["foot"])}</span><a class="btn gold" href="book.html">Book a call to scope it</a></div></div>')
    opts = "".join(f"<option>{e(x)}</option>" for x in V["team_areas"])
    return f'''<section class="wrap sec"><h1 class="pt">Work with me</h1><p class="lede">Whether you are hiring, need project support or want to join the team, here is how I can help.</p>{paths(True)}
<div class="gapt">{sh("What I offer", "Three connected services", lede="Each project is scoped around your needs, your data, your timeline and how the evidence will be used.")}<div class="pillars">{pillars}</div></div>
{scope}
<div class="gapt">{sh("How it works", "Three simple steps")}<ol class="steps"><li><b>A short call</b><span>Book anything from 5 minutes, with no commitment. Tell me what you are trying to learn or build.</span></li><li><b>Scope and proposal</b><span>I send a clear scope, timeline and price based on the work itself.</span></li><li><b>Deliver and hand over</b><span>Tools, data and documentation your team can keep using after I step back.</span></li></ol></div>
<section class="team" id="team"><span class="eyebrow">Join the team</span><h2>Join my consultancy team</h2><div class="tgrid"><div><p>I bring in specialists for larger assignments in MEL, data systems, research and training. If you would like to be considered:</p><ol class="dots"><li><b>Your CV is required.</b> A PDF is best.</li><li>A work sample is optional but helps, for example a report, dashboard or tool you built.</li><li>Fill in the short form. It prepares an email to me, then you attach your files and send.</li></ol></div>
<form id="tf" class="tf"><input name="n" placeholder="Your name" required><input name="m" type="email" placeholder="Your email" required><select name="a" aria-label="Main area of expertise">{opts}</select><input name="w" type="url" placeholder="Link to a work sample (optional)"><textarea name="b" rows="3" placeholder="A few lines about your experience"></textarea>
<label class="chk"><input type="checkbox" required> I will attach my CV to the email (required)</label><button class="btn">Prepare my email</button></form></div></section></section>'''


def book():
    return f'''<section class="wrap sec"><h1 class="pt">Book a call</h1><p class="lede">Pick a time for a short conversation, from 5 minutes up. Use it to talk about a role, a consultancy, a collaboration or a quick question.</p>
<div class="bk"><div class="cal"><div class="calh"><button id="pm" aria-label="Previous month">&lsaquo;</button><b id="mt"></b><button id="nm" aria-label="Next month">&rsaquo;</button></div>
<div class="dow"><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span></div><div id="days" class="days"></div>
<p class="small">Times shown in <span id="tzl"></span>. Your local time is shown beside each slot.</p></div>
<div class="slots"><h3 id="sd">Choose a date</h3><div id="sl" class="sl"><p class="small">Pick a day on the calendar to see open times.</p></div></div>
<form id="bf" class="bform" hidden><h3>Your details</h3><label>Topic<select name="t" id="top"></select></label>
<input name="n" placeholder="Your name" required><input name="m" type="email" placeholder="Email" required><textarea name="b" rows="3" placeholder="What would you like to cover?"></textarea>
<div class="sum" id="sum"></div><button class="btn">Request this time</button><p class="small">This sends your request to {S["email"]}. A time is confirmed once I reply.</p></form></div>
<div id="cal-embed"></div></section>'''


ld_services = {"@type": "ProfessionalService", "name": S["full"] + ": research, evaluation and data systems consultancy", "url": S["url"] + "/services.html", "provider": {"@id": S["url"] + "/#me"},
               "serviceType": ["Monitoring and evaluation", "Survey and data collection systems", "Dashboards and data tools", "Data analysis and reporting", "Research support", "Training"]}
cover_pre = '<link rel="preload" as="image" href="assets/cover.jpg" imagesrcset="assets/cover-1200.jpg 1200w, assets/cover.jpg 2000w" imagesizes="(max-width:1200px) 100vw, 1120px" fetchpriority="high">'
pages = [("index.html", f'{S["name"]}: Research, Evaluation & Data Systems Specialist, Kenya', "Kenya-based research, evaluation and data systems specialist: MEL design, survey systems, dashboards and analysis. Work in education, agriculture and parenting.", home(), {"preload": cover_pre}),
         ("work.html", "Work so far: education, agriculture and parenting", "Maths camps, farmer research networks and a parenting trial: what I did, the methods used and what came out of each.", work(), {}),
         ("projects.html", "Projects: dashboards, reports and code", "R Shiny and Streamlit dashboards, evaluation reports and data pipelines for agroecology and education programmes.", projects(), {}),
         ("publications.html", "Publications and reports", "Conference papers, accepted articles and research reports on maths education and farmer-led research.", pubs(), {}),
         ("gallery.html", "Gallery: fieldwork, maths camps and conferences", "Photos from maths camps, farmer fieldwork and conferences across East Africa.", gallery(), {"scripts": ("gallery.js",)}),
         ("about.html", "About", "Research and evaluation specialist with five years across Kenya and Tanzania in MEL systems, participatory research and data-driven programme design.", about(), {}),
         ("services.html", "Work with me: services and consultancy", "MEL design, survey systems, dashboards, analysis and training. Hire me, start a project, or join the consultancy team.", services(), {"extra_ld": ld_services}),
         ("cv.html", "Curriculum vitae", "CV of " + S["full"] + ", research, evaluation and data systems specialist. Read online or download the PDF.", cv(), {}),
         ("book.html", "Book a call", "Book a short call, from 5 minutes, about a role, a consultancy or a collaboration.", book(), {"scripts": ("book.js",)}),
         ("conference.html", "AFRICME7 conference presentation, Johannesburg", "Presenting maths camp research at AFRICME7, Wits School of Education, with KENET funding.", conference(), {})]
for d_ in ("reports", "fonts"):
    if pathlib.Path(d_).exists(): shutil.copytree(d_, OUT / d_)
for f in pathlib.Path(".").glob("*.pdf"): shutil.copy(f, OUT / f.name)
WEBP = re.compile(r"(assets/(?!og\.)[\w\-/]+)\.(?:jpg|png)")
PHEAD = re.compile(r'(<section class="wrap sec">)<h1 class="pt">(.*?)</h1><p class="lede">(.*?)</p>', re.S)
HEAD = {"work.html": ("Work so far", "Evidence in education, agriculture and parenting"), "projects.html": ("Projects", "Dashboards, reports and code"),
        "publications.html": ("Publications", "Papers and reports"), "gallery.html": ("Gallery", "From the field"),
        "services.html": ("Work with me", "How I can help"), "book.html": ("Book a call", "Let's talk")}
def finish(html, fn=""):
    def ph(m):
        eb, h1 = HEAD.get(fn, ("", m.group(2)))
        return f'{m.group(1)}<div class="phead">{f"<span class=eyebrow>{eb}</span>" if eb else ""}<h1 class="pt">{h1}</h1><p class="lede">{m.group(3)}</p></div>'
    html = PHEAD.sub(ph, html)
    return re.sub(r"\s*\n\s*", "", WEBP.sub(r"\1.webp", html))
for fn, t, d, b, kw in pages:
    (OUT / fn).write_text(finish(page(fn, t, d, b, **kw), fn), encoding="utf-8")
nf = page("404.html", "Page not found", "Page not found.", '<section class="wrap sec"><h1 class="pt">Page not found</h1><p class="lede">That page does not exist. Try the <a href="index.html">home page</a> or the <a href="projects.html">projects</a>.</p></section>').replace('content="index,follow,max-image-preview:large"', 'content="noindex"')
(OUT / "404.html").write_text(finish(nf), encoding="utf-8")
today = datetime.date.today().isoformat()
(OUT / ".nojekyll").write_text("")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {S['url']}/sitemap.xml\n")
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{S['url']}/{'' if h == 'index.html' else h}</loc><lastmod>{today}</lastmod></url>" for _, h in ALL) + "</urlset>")
(OUT / "_headers").write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n/css/*\n  Cache-Control: public, max-age=31536000, immutable\n/js/*\n  Cache-Control: public, max-age=31536000, immutable\n/assets/*\n  Cache-Control: public, max-age=2592000\n/reports/*\n  Cache-Control: public, max-age=604800\n")
print("Built", len(pages), "pages into dist/")
