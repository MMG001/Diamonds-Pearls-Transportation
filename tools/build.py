# -*- coding: utf-8 -*-
"""Static site generator for Diamond & Pearls. Run from repo root: python3 tools/build.py"""
import json, os, sys, html, datetime
sys.path.insert(0, os.path.dirname(__file__))
from content import *  # noqa
import schema as S
import hashlib

def vhash(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:10]

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TODAY = datetime.date.today().isoformat()
PAGES = []  # for sitemap
e = html.escape

SVC = {s["slug"]: s for s in SERVICES}

def img(name, alt, cls="", eager=False, sizes="(max-width: 800px) 100vw, 50vw"):
    return (f'<img class="{cls}" src="/assets/img/{name}-960.webp" '
            f'srcset="/assets/img/{name}-960.webp 960w, /assets/img/{name}-1920.webp 1920w" sizes="{sizes}" '
            f'alt="{e(alt)}" width="960" height="640" {"fetchpriority=\"high\"" if eager else "loading=\"lazy\""} decoding="async">')

def phone_btn(cls="btn btn-ghost"):
    if PHONE:
        return f'<a class="{cls}" href="tel:{PHONE}">Call {e(PHONE_DISPLAY)}</a>'
    return ""

ADDR_LINE = f'{ADDRESS["street"]}, {ADDRESS["city"]}, {ADDRESS["region"]} {ADDRESS["zip"]}'
MAPS = "https://www.google.com/maps/search/?api=1&query=" + ADDR_LINE.replace(" ", "+").replace(",", "%2C")

def social_links(sep=" &middot; "):
    return sep.join(f'<a href="{u}" target="_blank" rel="noopener">{e(n)}</a>' for n, u in SOCIAL)

def nav():
    svc = "".join(f'<li><a href="/{s["slug"]}/">{e(s["name"])}</a></li>' for s in SERVICES)
    return f'''<header class="site-header" id="top">
  <div class="bar wrap">
    <a class="brand" href="/" aria-label="{e(BRAND)} home"><img src="/assets/img/logo-520.png" alt="{e(BRAND)}" width="520" height="175"></a>
    <button class="menu-toggle" aria-expanded="false" aria-controls="site-nav"><span></span><span></span><span></span><span class="sr">Menu</span></button>
    <nav id="site-nav" class="site-nav" aria-label="Main">
      <ul>
        <li class="has-sub"><a href="/services/">Services</a><ul class="sub">{svc}</ul></li>
        <li><a href="/special-events/">Events</a></li>
        <li><a href="/tours/">Tours</a></li>
        <li><a href="/service-areas/">Service Areas</a></li>
        <li><a href="/airports/">Airports</a></li>
        <li><a href="/rates/">Rates</a></li>
        <li><a href="/about/">About</a></li>
        <li><a href="/faq/">FAQ</a></li>
      </ul>
      <a class="btn btn-gold nav-cta" href="/contact/">Get a Quote</a>
    </nav>
  </div>
</header>'''

def footer():
    col = lambda title, items: f'<div><h3>{title}</h3><ul>' + "".join(f'<li><a href="{u}">{e(n)}</a></li>' for u, n in items) + '</ul></div>'
    services = [(f'/{s["slug"]}/', s["name"]) for s in SERVICES]
    areas = [(f'/service-areas/{a["slug"]}/', a["name"]) for a in AREAS[:8]] + [("/service-areas/", "All Service Areas")]
    more = [(f'/airports/{a["slug"]}/', f'{a["code"]} Airport') for a in AIRPORTS] + [("/rates/", "Rates"), ("/about/", "About Us"), ("/faq/", "FAQ"), ("/contact/", "Get a Quote"), ("/privacy/", "Privacy Policy")]
    contact_phone = f'<a href="tel:{PHONE}">{e(PHONE_DISPLAY)}</a>' if PHONE else 'Phone: <em>Coming Soon</em>'
    contact_email = f'<a href="mailto:{EMAIL}">{e(EMAIL)}</a>' if EMAIL else 'Email: <em>Coming Soon</em>'
    return f'''<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <img src="/assets/img/logo-520.png" alt="{e(BRAND)}" width="260" height="88" loading="lazy">
      <p>Luxury chauffeured transportation for Minneapolis, St. Paul and the Twin Cities.</p>
      <p class="foot-contact">{contact_phone}<br>{contact_email}<br><a href="{MAPS}" target="_blank" rel="noopener">{e(ADDRESS["street"])}<br>{e(ADDRESS["city"])}, {e(ADDRESS["region"])} {e(ADDRESS["zip"])}</a><br>{social_links()}</p>
      <p class="foot-license">USDOT #{e(USDOT)} &middot; MnDOT #{e(MNDOT)}</p>
      <a class="btn btn-gold" href="/contact/">Request a Quote</a>
    </div>
    {col("Services", services)}
    {col("Service Areas", areas)}
    {col("More", more)}
  </div>
  <div class="wrap foot-base"><p>&copy; {datetime.date.today().year} {e(BRAND)}. All rights reserved.</p><p>Serving Minneapolis &middot; St. Paul &middot; the Twin Cities Metro</p></div>
</footer>'''

def page(path, title, desc, body, crumbs=None, schema=None, og_img="hero-executive", wp_type="WebPage", main=None, spatial=None):
    url = SITE_URL + path
    extra = []
    for n in schema or []:
        if n.get("@type") == "FAQPage" and "@id" not in n:
            n = {"@type": "FAQPage", "@id": f"{url}#faq", "isPartOf": {"@id": f"{url}#webpage"}, "mainEntity": n["mainEntity"]}
        extra.append(n)
    ld = S.graph(path if path != "/404.html" else path, title, desc, crumbs, extra, wp_type=wp_type, main=main, spatial=spatial, og_img=og_img)
    crumb_html = ""
    if crumbs:
        items = [("Home", "/")] + crumbs
        crumb_html = f'<nav class="crumbs wrap{" on-hero" if body.lstrip().startswith('<section class="hero') else ""}" aria-label="Breadcrumb"><ol>' + "".join(
            (f'<li><a href="{u}">{e(n)}</a></li>' if i < len(items) - 1 else f'<li aria-current="page">{e(n)}</li>') for i, (n, u) in enumerate(items)) + '</ol></nav>'
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{e(BRAND)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE_URL}/assets/img/{og_img}-1920.webp">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0c0b0a">
<link rel="icon" href="/favicon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css?v={vhash("assets/css/site.css")}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{nav()}
<main id="main">
{crumb_html}
{body}
</main>
{footer()}
<script src="/assets/js/site.js?v={vhash("assets/js/site.js")}" defer></script>
</body>
</html>'''
    out = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" else os.path.join(ROOT, "index.html")
    if path == "/404.html":
        out = os.path.join(ROOT, "404.html")
    if path != "/404.html":
        S.check(path, doc, title, desc, url)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    if path != "/404.html":
        PAGES.append(path)

# ------------------------------------------------------------ components
def hero(h1, lead, image, eyebrow, alt, home=False):
    return f'''<section class="hero{' hero-home' if home else ''}">
  {img(image, alt, "hero-img", eager=True, sizes="100vw")}
  <div class="hero-shade"></div>
  <div class="wrap hero-inner">
    <p class="eyebrow">{e(eyebrow)}</p>
    <h1>{e(h1)}</h1>
    <p class="lead">{e(lead)}</p>
    <div class="actions"><a class="btn btn-gold" href="/contact/">Get a Free Quote</a>{phone_btn()}<a class="btn btn-ghost" href="/services/">Explore Services</a></div>
  </div>
</section>'''

def cards(items, cls="cards"):
    out = []
    for href, name, text, im in items:
        out.append(f'<a class="card" href="{href}">{img(im, name, "card-img", sizes="(max-width: 700px) 100vw, 33vw") if im else ""}<div class="card-body"><h3>{e(name)}</h3><p>{e(text)}</p><span class="more">Learn more</span></div></a>')
    return f'<div class="{cls}">' + "".join(out) + '</div>'

def chips(items):
    return '<ul class="chips">' + "".join(f'<li><a href="{u}">{e(n)}</a></li>' for u, n in items) + '</ul>'

def checklist(points):
    return '<ul class="checks">' + "".join(f'<li>{e(p)}</li>' for p in points) + '</ul>'

def faq_block(faqs, title="Frequently Asked Questions"):
    items = "".join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in faqs)
    schema = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    return f'<section class="section"><div class="wrap narrow"><h2 class="center">{e(title)}</h2><div class="faq">{items}</div></div></section>', schema

def cta(title="Ready to ride in luxury?", text="Tell us about your trip and we will send a personalized quote."):
    return f'''<section class="cta-band"><div class="wrap"><h2>{e(title)}</h2><p>{e(text)}</p><div class="actions center"><a class="btn btn-gold" href="/contact/">Request a Quote</a>{phone_btn()}</div></div></section>'''

def split(title, paras, image, alt, points=None, flip=False, eyebrow=""):
    ps = "".join(f"<p>{e(p)}</p>" for p in paras)
    return f'''<section class="section"><div class="wrap split{' flip' if flip else ''}">
  <div class="split-media">{img(image, alt, "rounded")}</div>
  <div class="split-text">{f'<p class="eyebrow">{e(eyebrow)}</p>' if eyebrow else ''}<h2>{e(title)}</h2>{ps}{checklist(points) if points else ''}</div>
</div></section>'''

STANDARD = [
    ("Professional Chauffeurs", "Courteous, discreet and professionally attired drivers who know the Twin Cities."),
    ("Always On Time", "Routes planned around traffic, weather and events, with flight tracking on every airport pickup."),
    ("Immaculate Vehicles", "Late-model luxury vehicles, detailed before every ride."),
    ("Transparent Quotes", "Clear pricing up front, with no surprises when your trip is over."),
]
def standard_block(dark=True):
    items = "".join(f'<div class="std"><span class="gem" aria-hidden="true"></span><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in STANDARD)
    return f'<section class="section {"dark" if dark else ""}"><div class="wrap"><p class="eyebrow center">The Diamond &amp; Pearls Standard</p><h2 class="center">Luxury Is in the Details</h2><div class="std-grid">{items}</div></div></section>'

# ------------------------------------------------------------ pages
def build_home():
    svc_cards = cards([(f'/{s["slug"]}/', s["name"], s["lead"], s["img"]) for s in SERVICES])
    ev = chips([(f'/special-events/{x["slug"]}/', x["name"]) for x in EVENTS])
    tr = chips([(f'/tours/{x["slug"]}/', x["name"]) for x in TOURS])
    ar = chips([(f'/service-areas/{a["slug"]}/', a["name"]) for a in AREAS])
    ap = chips([(f'/airports/{a["slug"]}/', f'{a["code"]} · {a["name"]}') for a in AIRPORTS])
    faq_html, faq_schema = faq_block(GENERAL_FAQS[:5])
    body = hero("Luxury Limo & Car Service in Minneapolis–St. Paul",
                "Chauffeured transportation for airport transfers, corporate travel, weddings and life's biggest celebrations across the Twin Cities.",
                "hero-executive", "Minneapolis · St. Paul · Twin Cities", "Executive passenger relaxing in the back seat of a luxury car", home=True)
    body += f'''<section class="section intro"><div class="wrap narrow center">
  <p class="eyebrow">Twin Cities Limousine &amp; Black Car Service</p>
  <h2>Arrive Polished. Travel Relaxed.</h2>
  <p>{e(BRAND)} provides premium ground transportation in Minneapolis, St. Paul and throughout the Twin Cities metro. Whether you need a ride to MSP, an executive car for a day of meetings, or an elegant arrival on your wedding day, our professional chauffeurs make every mile effortless.</p>
</div></section>
<section class="section tint"><div class="wrap"><p class="eyebrow center">What We Do</p><h2 class="center">Chauffeured Transportation Services</h2>{svc_cards}</div></section>'''
    body += standard_block()
    body += split("Every Occasion, Perfectly Timed", ["From prom night to a 50th anniversary, from a bachelorette weekend to a game at U.S. Bank Stadium, we plan the route around your celebration so you can enjoy every moment."],
                  "door-sunset", "Chauffeur opening a luxury car door at sunset", eyebrow="Special Events") .replace("</div>\n</div></section>", ev + "</div>\n</div></section>")
    body += split("Tours Worth Savoring", ["Wine, brewery and distillery tours, Irish pub crawls, holiday light tours and fall color drives. Your chauffeur drives; your group enjoys."],
                  "night-drive", "Black luxury sedan driving through the city at night", flip=True, eyebrow="Tours").replace("</div>\n</div></section>", tr + "</div>\n</div></section>")
    body += f'''<section class="section tint"><div class="wrap two-col">
  <div><p class="eyebrow">Airports</p><h2>Airport Car Service</h2><p>Flight-tracked pickups at Minneapolis-St. Paul International and the metro's private aviation airports.</p>{ap}</div>
  <div><p class="eyebrow">Service Areas</p><h2>Serving the Twin Cities &amp; Beyond</h2><p>Minneapolis, St. Paul, the suburbs and long-distance trips across Minnesota.</p>{ar}</div>
</div></section>'''
    body += faq_html + cta()
    page("/", "Limo Service Minneapolis MN | Luxury Car Service Twin Cities | Diamond & Pearls",
         "Luxury limo and chauffeured car service in Minneapolis and St. Paul. Airport transportation, corporate travel, weddings, special events and tours across the Twin Cities.",
         body, schema=[faq_schema] + [S.card_service(f'/{x["slug"]}/', x["name"], x["lead"], x["slug"]) for x in SERVICES])

def build_services_hub():
    body = hero("Our Chauffeured Transportation Services", "Luxury ground transportation for every reason to travel in Minneapolis, St. Paul and the Twin Cities.", "chauffeur-team", "Services", "Chauffeurs standing beside a luxury sedan")
    body += f'<section class="section"><div class="wrap">{cards([(f"/{s["slug"]}/", s["name"], s["lead"], s["img"]) for s in SERVICES])}</div></section>'
    body += standard_block() + cta()
    page("/services/", "Limo & Car Services Minneapolis | Chauffeured Transportation Services",
         "Explore our Minneapolis limo and car services: airport transportation, corporate travel, weddings, special events, tours and group charters.",
         body, crumbs=[("Services", "/services/")], wp_type="CollectionPage", main={"@id": SITE_URL + "/services/#list"},
         schema=[S.item_list("/services/", [(x["name"], f'/{x["slug"]}/') for x in SERVICES])] + [S.card_service(f'/{x["slug"]}/', x["name"], x["lead"], x["slug"]) for x in SERVICES])

def build_service(s):
    path = f'/{s["slug"]}/'
    body = hero(s["h1"], s["lead"], s["img"], "Minneapolis · St. Paul", s["name"])
    for i, (t, p) in enumerate(s["sections"]):
        pass
    secs = "".join(f'<div class="feature"><h3>{e(t)}</h3><p>{e(p)}</p></div>' for t, p in s["sections"])
    body += f'<section class="section"><div class="wrap"><div class="features">{secs}</div></div></section>'
    body += split(f'What to Expect', ["Every booking includes a professional chauffeur, a clean late-model luxury vehicle and a confirmed itinerary. Here is what is included:"], "door-hand", "Chauffeur opening a car door", points=s["points"], eyebrow=s["name"])
    sub = ""
    if s["slug"] == "special-events":
        sub = cards([(f'/special-events/{x["slug"]}/', x["name"], x["lead"], x["img"]) for x in EVENTS])
    elif s["slug"] == "tours":
        sub = cards([(f'/tours/{x["slug"]}/', x["name"], x["lead"], x["img"]) for x in TOURS])
    elif s["slug"] == "airport-transportation":
        sub = cards([(f'/airports/{a["slug"]}/', f'{a["name"]} ({a["code"]})', a["lead"], None) for a in AIRPORTS], "cards text-cards")
    if sub:
        body += f'<section class="section tint"><div class="wrap"><h2 class="center">Explore {e(s["name"])}</h2>{sub}</div></section>'
    body += f'<section class="section"><div class="wrap center"><h2>Where We Provide {e(s["name"])}</h2>{chips([(f"/service-areas/{a["slug"]}/", a["name"]) for a in AREAS])}</div></section>'
    fh, fs = faq_block(s["faqs"])
    body += fh + cta()
    kids = []
    if s["slug"] == "special-events":
        kids = [(f'/special-events/{x["slug"]}/', x["name"], x["lead"], x["slug"]) for x in EVENTS]
    elif s["slug"] == "tours":
        kids = [(f'/tours/{x["slug"]}/', x["name"], x["lead"], x["slug"]) for x in TOURS]
    elif s["slug"] == "airport-transportation":
        kids = [(f'/airports/{a["slug"]}/', f'{a["name"]} ({a["code"]})', a["lead"], "airport") for a in AIRPORTS]
    nodes = [fs, S.full_service(path, s["name"], s["lead"], s["slug"], sub_paths=[k[0] for k in kids])] + [S.card_service(*k) for k in kids]
    page(path, s["title"], s["desc"], body, crumbs=[("Services", "/services/"), (s["name"], path)], schema=nodes, og_img=s["img"], main=S.sid(path))

def build_child(x, parent_slug, parent_name):
    path = f'/{parent_slug}/{x["slug"]}/'
    body = hero(x["h1"], x["lead"], x["img"], parent_name, x["name"])
    body += split(f'{x["name"]} in Minneapolis & St. Paul', x["body"], x["img"], x["name"], points=x["points"], eyebrow=parent_name)
    siblings = EVENTS if parent_slug == "special-events" else TOURS
    body += f'<section class="section tint"><div class="wrap center"><h2>More {e(parent_name)}</h2>{chips([(f"/{parent_slug}/{y["slug"]}/", y["name"]) for y in siblings if y is not x])}</div></section>'
    fh, fs = faq_block(x["faqs"])
    body += fh + cta()
    sib = [(f"/{parent_slug}/{y['slug']}/", y["name"]) for y in siblings if y is not x]
    nodes = [fs, S.full_service(path, x["name"], x["lead"], x["slug"], related_paths=[f"/{parent_slug}/"] + [u for u, _ in sib])]
    nodes += [{"@type": "Service", "@id": SITE_URL + u + "#service", "name": n, "url": SITE_URL + u, "provider": S.BIZ} for u, n in sib]
    page(path, x["title"], x["desc"], body, crumbs=[(parent_name, f"/{parent_slug}/"), (x["name"], path)], schema=nodes, og_img=x["img"], main=S.sid(path))

def build_airports():
    body = hero("Airport Car Service Across the Twin Cities", "Commercial and private aviation transfers with flight tracking and professional chauffeurs.", "private-jet", "Airports", "Luxury car parked beside a private jet")
    body += f'<section class="section"><div class="wrap">{cards([(f"/airports/{a["slug"]}/", f"{a["name"]} ({a["code"]})", a["lead"], None) for a in AIRPORTS], "cards text-cards")}</div></section>' + cta()
    page("/airports/", "Airport Car Service Minneapolis | MSP, STP, FCM & ANE Transportation",
         "Chauffeured airport transportation at MSP, St. Paul Downtown (STP), Flying Cloud (FCM) and Anoka County-Blaine (ANE) airports.",
         body, crumbs=[("Airports", "/airports/")], og_img="private-jet", wp_type="CollectionPage", main={"@id": SITE_URL + "/airports/#list"},
         schema=[S.item_list("/airports/", [(f'{a["name"]} ({a["code"]})', f'/airports/{a["slug"]}/') for a in AIRPORTS])] + [S.card_service(f'/airports/{a["slug"]}/', f'{a["name"]} ({a["code"]})', a["lead"], "airport") for a in AIRPORTS])
    for a in AIRPORTS:
        path = f'/airports/{a["slug"]}/'
        body = hero(a["h1"], a["lead"], a["img"], f'{a["code"]} Airport', a["name"])
        body += split(f'Transportation at {a["name"]}', a["body"], "chauffeur-waiting" if a["code"] != "MSP" else "door-for-guest", "Chauffeur waiting beside a luxury car", points=a["points"], eyebrow=a["code"])
        body += f'<section class="section tint"><div class="wrap center"><h2>Other Airports We Serve</h2>{chips([(f"/airports/{b["slug"]}/", f"{b["code"]} · {b["name"]}") for b in AIRPORTS if b is not a])}<p class="mt">See also: <a href="/airport-transportation/">Airport Transportation</a> · <a href="/corporate-transportation/">Corporate Transportation</a></p></div></section>'
        faqs = [(f"Do you track flights at {a['code']}?", "Yes. Every airport pickup includes flight tracking so your chauffeur adjusts to your actual arrival time."),
                (f"How do I book a ride to or from {a['code']}?", "Request a quote online with your flight details, pickup address and number of passengers. We will confirm your ride and send your chauffeur's details before pickup.")]
        fh, fs = faq_block(faqs)
        body += fh + cta()
        oth = [b for b in AIRPORTS if b is not a]
        nodes = [fs, S.full_service(path, a["h1"], a["lead"], "airport", related_paths=["/airport-transportation/"] + [f'/airports/{b["slug"]}/' for b in oth])]
        nodes += [{"@type": "Service", "@id": f'{SITE_URL}/airports/{b["slug"]}/#service', "name": f'{b["name"]} ({b["code"]})', "url": f'{SITE_URL}/airports/{b["slug"]}/', "provider": S.BIZ} for b in oth]
        page(path, a["title"], a["desc"], body, crumbs=[("Airports", "/airports/"), (a["code"], path)], schema=nodes, og_img=a["img"], main=S.sid(path))

def build_areas():
    body = hero("Service Areas", "Luxury chauffeured transportation throughout Minneapolis, St. Paul, the Twin Cities suburbs and greater Minnesota.", "hotel-arrival", "Where We Drive", "Chauffeur waiting at a hotel entrance")
    groups = [("Minneapolis & St. Paul", AREAS[:2]), ("Twin Cities Suburbs", AREAS[2:13]), ("Greater Minnesota", AREAS[13:])]
    for t, g in groups:
        body += f'<section class="section"><div class="wrap"><h2>{e(t)}</h2>{cards([(f"/service-areas/{a["slug"]}/", a["name"] + ", MN", a["intro"], None) for a in g], "cards text-cards")}</div></section>'
    body += cta()
    page("/service-areas/", "Service Areas | Limo & Car Service Across the Twin Cities, MN",
         "Diamond & Pearls serves Minneapolis, St. Paul, Bloomington, Edina, Eagan, Eden Prairie, Maple Grove, Plymouth, Minnetonka, Woodbury and more.",
         body, crumbs=[("Service Areas", "/service-areas/")], og_img="hotel-arrival", wp_type="CollectionPage", main={"@id": SITE_URL + "/service-areas/#list"},
         schema=[S.item_list("/service-areas/", [(a["name"] + ", MN", f'/service-areas/{a["slug"]}/') for a in AREAS])])
    for a in AREAS:
        n = a["name"]; path = f'/service-areas/{a["slug"]}/'
        title = f"Limo Service {n} MN | Car Service & Airport Transportation in {n}"
        desc = f"Luxury limo and chauffeured car service in {n}, MN. Airport transfers to {a['airport']}, corporate travel, weddings, events and tours."
        body = hero(f"Limo & Car Service in {n}, MN", a["intro"], a["img"], f"{n}, Minnesota", f"Luxury car service in {n}")
        svc_list = cards([(f'/{s["slug"]}/', s["name"], s["lead"], None) for s in SERVICES], "cards text-cards")
        body += f'<section class="section"><div class="wrap"><p class="eyebrow center">Services in {e(n)}</p><h2 class="center">Chauffeured Transportation in {e(n)}</h2>{svc_list}</div></section>'
        places = "".join(f"<li>{e(p)}</li>" for p in a["places"])
        body += f'''<section class="section tint"><div class="wrap two-col">
  <div><p class="eyebrow">Local Knowledge</p><h2>Popular Destinations in {e(n)}</h2><ul class="checks">{places}</ul></div>
  <div><p class="eyebrow">Getting Around</p><h2>Neighborhoods &amp; Airports</h2><p>We serve {e(a["neigh"])}.</p><p>Nearest airports: <strong>{e(a["airport"])}</strong>. {e(a["note"])}</p><p><a href="/airport-transportation/">Airport transportation details &rarr;</a></p></div>
</div></section>'''
        others = [x for x in AREAS if x is not a]
        body += f'<section class="section"><div class="wrap center"><h2>Nearby Service Areas</h2>{chips([(f"/service-areas/{x["slug"]}/", x["name"]) for x in others])}</div></section>'
        faqs = [(f"Do you provide airport transportation from {n}?", f"Yes. We provide flight-tracked airport transfers between {n} and {a['airport']}, as well as the other Twin Cities airports."),
                (f"What services do you offer in {n}?", f"In {n} we offer airport transportation, corporate car service, wedding transportation, special event transportation, tours and group shuttles."),
                (f"How do I book a car in {n}?", "Request a quote online with your date, pickup location and destination. We will confirm availability and send your quote.")]
        fh, fs = faq_block(faqs)
        body += fh + cta(f"Book Your Ride in {n}")
        nodes = [fs, S.city_node(a)] + [S.card_service(f'/{x["slug"]}/', x["name"], x["lead"], x["slug"]) for x in SERVICES]
        page(path, title, desc, body, crumbs=[("Service Areas", "/service-areas/"), (n, path)], schema=nodes, og_img=a["img"], spatial={"@id": f"{SITE_URL}/service-areas/{a['slug']}/#city"})

def build_about():
    body = hero("About Diamond & Pearls", "A new standard for luxury transportation in the Twin Cities.", "chauffeur-smile", "About Us", "Smiling professional chauffeur")
    body += split("Built on Polish and Reliability", [
        f"{BRAND} was founded with a simple idea: every ride should feel as refined as the occasion it serves. Like a diamond and a pearl, we believe great service combines strength with grace.",
        "We serve executives, families, couples and groups across Minneapolis, St. Paul and the Twin Cities metro, with a focus on punctuality, discretion and genuine hospitality."],
        "chauffeur-smile", "Professional chauffeur in the driver's seat", eyebrow="Our Story")
    body += standard_block()
    body += split("Our Promise to You", ["We confirm every detail before your ride, track every flight, and treat every passenger like a VIP. If something matters to you, it matters to us."],
                  "door-for-guest", "Chauffeur opening a door for a passenger", points=["Clear communication from booking to drop-off", "Chauffeurs who know the Twin Cities", "Clean, comfortable, late-model vehicles", "Respect for your privacy and your schedule"], flip=True, eyebrow="Our Promise")
    body += cta()
    page("/about/", "About Diamond & Pearls | Luxury Transportation Minneapolis",
         "Learn about Diamond & Pearls Luxury Transportation, a Minneapolis limo and chauffeured car service built on punctuality, discretion and hospitality.",
         body, crumbs=[("About", "/about/")], og_img="chauffeur-smile", wp_type="AboutPage")

def build_faq():
    body = hero("Frequently Asked Questions", "Everything you need to know about booking luxury transportation with Diamond & Pearls.", "backseat-laptop", "FAQ", "Passenger working in the back seat of a luxury car")
    fh, fs = faq_block(GENERAL_FAQS, "Booking & Service Questions")
    body += fh + cta()
    page("/faq/", "Limo Service FAQ | Diamond & Pearls Minneapolis", "Answers to common questions about booking limo and chauffeured car service in Minneapolis and St. Paul.", body, crumbs=[("FAQ", "/faq/")], schema=[fs], og_img="backseat-laptop")

def build_contact():
    opts = "".join(f"<option>{e(s['name'])}</option>" for s in SERVICES) + "".join(f"<option>{e(x['name'])}</option>" for x in EVENTS + TOURS)
    body = f'''<section class="section quote-wrap"><div class="wrap quote-grid">
  <div class="quote-info">
    <p class="eyebrow">Get a Quote</p>
    <h1>Request Your Luxury Ride</h1>
    <p>Tell us about your trip and we will send a personalized quote. The more details you share, the more accurate your quote will be.</p>
    <ul class="contact-list">
      <li><strong>Phone</strong>{f'<a href="tel:{PHONE}">{e(PHONE_DISPLAY)}</a>' if PHONE else '<span>Coming Soon</span>'}</li>
      <li><strong>Email</strong>{f'<a href="mailto:{EMAIL}">{e(EMAIL)}</a>' if EMAIL else '<span>Coming Soon</span>'}</li>
      <li><strong>Office</strong><span><a href="{MAPS}" target="_blank" rel="noopener">{e(ADDRESS["street"])}<br>{e(ADDRESS["city"])}, {e(ADDRESS["region"])} {e(ADDRESS["zip"])}</a></span></li>
      <li><strong>Follow</strong><span>{social_links()}</span></li>
      <li><strong>Licensed</strong><span>USDOT #{e(USDOT)}<br>MnDOT #{e(MNDOT)}</span></li>
      <li><strong>Service Area</strong><span>Minneapolis, St. Paul &amp; the Twin Cities Metro</span></li>
    </ul>
    {img("door-for-guest", "Chauffeur opening the door for a guest", "rounded")}
  </div>
  <form id="quote" class="quote-form" data-endpoint="{e(FORM_ENDPOINT)}" novalidate>
    <div class="row"><label>Full name<input name="name" autocomplete="name" required></label><label>Phone<input name="phone" type="tel" autocomplete="tel" required></label></div>
    <label>Email<input name="email" type="email" autocomplete="email" required></label>
    <div class="row"><label>Service<select name="service" required><option value="">Select a service</option>{opts}</select></label><label>Passengers<input name="passengers" type="number" min="1" max="60" inputmode="numeric"></label></div>
    <div class="row"><label>Date<input name="date" type="date" required></label><label>Pickup time<input name="time" type="time"></label></div>
    <label>Pickup location<input name="pickup" placeholder="Address, hotel or airport"></label>
    <label>Drop-off / destination<input name="dropoff" placeholder="Address, venue or airport"></label>
    <label>Trip details<textarea name="details" rows="4" placeholder="Flight number, stops, hours needed, special requests"></textarea></label>
    <input type="text" name="company_website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
    <button class="btn btn-gold btn-block" type="submit">Request My Quote</button>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form>
</div></section>'''
    page("/contact/", "Get a Quote | Limo & Car Service Minneapolis | Diamond & Pearls",
         "Request a quote for luxury limo and chauffeured car service in Minneapolis, St. Paul and the Twin Cities.", body, crumbs=[("Get a Quote", "/contact/")], og_img="door-for-guest", wp_type="ContactPage")

def build_rates():
    body = hero("Rates", "Simple hourly pricing for chauffeured transportation across Minneapolis, St. Paul and the Twin Cities.", "executive-relax", "Pricing", "Executive passenger relaxing in a luxury car")
    tiles = "".join(f'<div class="rate"><h3>{e(n)}</h3><p class="rate-price">{e(pr)}<span>{e(u)}</span></p><p>{e(inc)}</p></div>' for n, pr, u, inc in RATES)
    call = f'<a class="btn btn-gold" href="tel:{PHONE}">Call {e(PHONE_DISPLAY)}</a>' if PHONE else ""
    body += f'''<section class="section"><div class="wrap"><p class="eyebrow center">Hourly Rates</p><h2 class="center">Our Rates</h2><div class="rates">{tiles}</div>
<p class="rate-min center">{e(RATE_MINIMUM)}</p>
<div class="actions center mt">{call}<a class="btn btn-ghost dark-text" href="/contact/">Request a Quote</a></div></div></section>'''
    body += cta()
    page("/rates/", "Limo Rates Minneapolis | Hourly Car Service Pricing | Diamond & Pearls",
         "Diamond & Pearls rates: $90 per hour standard service including airport, $120 per hour corporate service including private jet. Two-hour minimum. Call for group and weekly rates.",
         body, crumbs=[("Rates", "/rates/")], og_img="executive-relax")

def build_privacy():
    body = f'''<section class="section"><div class="wrap narrow prose"><h1>Privacy Policy</h1><p>Last updated {TODAY}.</p>
<p>{e(BRAND)} respects your privacy. When you request a quote or book a ride, we collect the information you provide, such as your name, phone number, email address and trip details, and use it only to respond to your request and provide our services.</p>
<h2>How we use your information</h2><p>We use your information to prepare quotes, confirm reservations, communicate about your trip and improve our service. We do not sell your personal information.</p>
<h2>Sharing</h2><p>We share information only with service providers who help us operate our business, or when required by law.</p>
<h2>Contact</h2><p>Questions about this policy can be sent through our <a href="/contact/">contact page</a>.</p></div></section>'''
    page("/privacy/", "Privacy Policy | Diamond & Pearls Luxury Transportation", "Privacy policy for Diamond & Pearls Luxury Transportation.", body, crumbs=[("Privacy Policy", "/privacy/")])

def build_404():
    body = '<section class="section"><div class="wrap narrow center"><p class="eyebrow">404</p><h1>Page Not Found</h1><p>The page you are looking for has moved or no longer exists.</p><div class="actions center"><a class="btn btn-gold" href="/">Back to Home</a><a class="btn btn-ghost dark-text" href="/contact/">Get a Quote</a></div></div></section>'
    page("/404.html", "Page Not Found | Diamond & Pearls", "Page not found.", body)

def build_meta():
    urls = "".join(f"<url><loc>{SITE_URL}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in PAGES)
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nDisallow: /tools/\nSitemap: {SITE_URL}/sitemap.xml\n")

if __name__ == "__main__":
    build_home(); build_services_hub()
    for s in SERVICES: build_service(s)
    for x in EVENTS: build_child(x, "special-events", "Special Events")
    for x in TOURS: build_child(x, "tours", "Tours")
    build_airports(); build_areas(); build_about(); build_faq(); build_rates(); build_contact(); build_privacy(); build_404(); build_meta()
    print(f"Built {len(PAGES)} pages")
