# -*- coding: utf-8 -*-
"""JSON-LD entity graph builder + build-time QA (Universal Schema Prompt v3.2).

Facts come only from content.py. Missing facts are omitted, never invented:
- No telephone / email / address / geo / hours / sameAs / foundingDate yet (client: "coming soon").
- No GeoCircle: it needs real office coordinates and a radius. areaServed = State + anchor City only.
- No AskAction: the quote form has no backend yet (FORM_ENDPOINT empty). Add it when the form is wired.
- No Review / AggregateRating: no first-party reviews exist. Google/Yelp reviews must never be marked up.
"""
import json, re
from content import *  # noqa

D = SITE_URL
BIZ = {"@id": f"{D}/#business"}
WIKI = "https://en.wikipedia.org/wiki/"

def thing(name, title):
    return {"@type": "Thing", "name": name, "sameAs": WIKI + title}

# Wikipedia concept per service slug (category on Service nodes, mirrored in knowsAbout)
CATEGORY = {
    "airport-transportation": thing("Vehicle for hire", "Vehicle_for_hire"),
    "corporate-transportation": thing("Business tourism", "Business_tourism"),
    "wedding-transportation": thing("Wedding", "Wedding"),
    "special-events": thing("Limousine", "Limousine"),
    "tours": thing("Tourism", "Tourism"),
    "group-charter": thing("Vehicle for hire", "Vehicle_for_hire"),
    "prom-homecoming": thing("Prom", "Prom"),
    "bachelor-party": thing("Bachelor party", "Bachelor_party"),
    "bachelorette-party": thing("Bachelorette party", "Bachelorette_Party"),
    "birthday": thing("Birthday", "Birthday"),
    "anniversary": thing("Wedding anniversary", "Wedding_anniversary"),
    "graduation": thing("Graduation", "Graduation"),
    "quinceanera": thing("Quinceañera", "Quinceañera"),
    "night-out": thing("Nightlife", "Nightlife"),
    "concerts-sporting-events": thing("Concert", "Concert"),
    "funeral": thing("Funeral", "Funeral"),
    "wine-tours": thing("Wine tasting", "Wine_tasting"),
    "brewery-tours": thing("Brewery", "Brewery"),
    "distillery-tours": thing("Distillery", "Distillery"),
    "pub-crawl": thing("Pub crawl", "Pub_crawl"),
    "holiday-light-tours": thing("Christmas lights", "Christmas_lights"),
    "city-tours": thing("Tour bus service", "Tour_bus_service"),
    "fall-color-tours": thing("Autumn leaf color", "Autumn_leaf_color"),
    "airport": thing("Airport", "Airport"),
}

CITY_WIKI = {
    "minneapolis": "Minneapolis", "st-paul": "Saint_Paul,_Minnesota", "bloomington": "Bloomington,_Minnesota",
    "edina": "Edina,_Minnesota", "eagan": "Eagan,_Minnesota", "eden-prairie": "Eden_Prairie,_Minnesota",
    "maple-grove": "Maple_Grove,_Minnesota", "plymouth": "Plymouth,_Minnesota", "minnetonka": "Minnetonka,_Minnesota",
    "woodbury": "Woodbury,_Minnesota", "white-bear-lake": "White_Bear_Lake,_Minnesota", "lakeville": "Lakeville,_Minnesota",
    "stillwater": "Stillwater,_Minnesota", "rochester": "Rochester,_Minnesota", "duluth": "Duluth,_Minnesota",
    "st-cloud": "St._Cloud,_Minnesota",
}
STATE = {"@type": "State", "name": "Minnesota", "sameAs": WIKI + "Minnesota"}

def sid(path):  # Service @id for a page path
    return {"@id": f"{D}{path}#service"}

# ---------------------------------------------------------------- core nodes
def business():
    n = {
        "@type": "LocalBusiness", "@id": BIZ["@id"],
        "additionalType": WIKI + "Limousine",
        "name": BRAND, "alternateName": SHORT,
        "url": D + "/", "logo": D + "/assets/img/logo-520.png", "image": D + "/assets/img/hero-executive-1920.webp",
        "description": "Luxury limousine and chauffeured car service in Minneapolis, St. Paul and the Twin Cities metro.",
        "areaServed": [STATE, {"@type": "City", "name": "Minneapolis", "sameAs": WIKI + "Minneapolis"}],
        "knowsAbout": [thing("Limousine", "Limousine"), thing("Chauffeur", "Chauffeur"), thing("Vehicle for hire", "Vehicle_for_hire")],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Chauffeured transportation services",
                            "itemListElement": [sid(f'/{s["slug"]}/') for s in SERVICES]},
    }
    if PHONE:
        n["telephone"] = PHONE
        n["potentialAction"] = [{"@type": "CommunicateAction", "target": {"@type": "EntryPoint", "urlTemplate": f"tel:{PHONE}", "actionPlatform": ["http://schema.org/DesktopWebPlatform", "http://schema.org/MobileWebPlatform"]}}]
    if EMAIL:
        n["email"] = EMAIL
    if FORM_ENDPOINT:
        n.setdefault("potentialAction", []).append({"@type": "AskAction", "name": "Request a quote",
            "target": {"@type": "EntryPoint", "urlTemplate": D + "/contact/#quote", "actionPlatform": ["http://schema.org/DesktopWebPlatform", "http://schema.org/MobileWebPlatform"]}})
    return n

def website():
    return {"@type": "WebSite", "@id": f"{D}/#website", "url": D + "/", "name": BRAND, "publisher": BIZ, "inLanguage": "en-US"}

def nav_services():
    """Nav-level nodes: the 6 hub services are linked in the menu on every page."""
    return [{"@type": "Service", "@id": sid(f'/{s["slug"]}/')["@id"], "name": s["name"], "url": f'{D}/{s["slug"]}/', "provider": BIZ} for s in SERVICES]

def card_service(path, name, blurb, cat_key):
    return {"@type": "Service", "@id": sid(path)["@id"], "name": name, "serviceType": name, "description": blurb,
            "provider": BIZ, "url": D + path, "areaServed": STATE, "category": CATEGORY[cat_key]}

def full_service(path, name, desc, cat_key, related_paths=(), sub_paths=(), area=None):
    n = card_service(path, name, desc, cat_key)
    n["mainEntityOfPage"] = {"@id": f"{D}{path}#webpage"}
    if area:
        n["areaServed"] = area
    if related_paths:
        n["isRelatedTo"] = [sid(p) for p in related_paths]
    if sub_paths:
        n["hasOfferCatalog"] = {"@type": "OfferCatalog", "name": name, "itemListElement": [sid(p) for p in sub_paths]}
    return n

def item_list(path, items):
    return {"@type": "ItemList", "@id": f"{D}{path}#list",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "url": D + u} for i, (n, u) in enumerate(items)]}

def city_node(a):
    return {"@type": "City", "@id": f'{D}/service-areas/{a["slug"]}/#city', "name": a["name"],
            "sameAs": WIKI + CITY_WIKI[a["slug"]], "containedInPlace": STATE}

def faq_node(path, faqs):
    return {"@type": "FAQPage", "@id": f"{D}{path}#faq", "isPartOf": {"@id": f"{D}{path}#webpage"},
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

def graph(path, title, desc, crumbs, extra, wp_type="WebPage", main=None, spatial=None, og_img=None):
    url = D + path
    wp = {"@type": wp_type, "@id": f"{url}#webpage", "url": url, "name": title, "description": desc,
          "isPartOf": {"@id": f"{D}/#website"}, "about": BIZ, "inLanguage": "en-US"}
    if og_img:
        wp["primaryImageOfPage"] = {"@type": "ImageObject", "url": f"{D}/assets/img/{og_img}-1920.webp"}
    nodes = [website(), business(), wp]
    if crumbs:
        items = [("Home", "/")] + crumbs
        wp["breadcrumb"] = {"@id": f"{url}#breadcrumb"}
        nodes.append({"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb",
                      "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": D + u} for i, (n, u) in enumerate(items)]})
    if main:
        wp["mainEntity"] = main
    if spatial:
        wp["spatialCoverage"] = spatial
    # nav-level services first; richer nodes passed in `extra` replace them by @id
    by_id = {}
    for n in nav_services() + (extra or []):
        k = n.get("@id")
        if k and k in by_id:
            nodes[by_id[k]] = n
        else:
            if k: by_id[k] = len(nodes)
            nodes.append(n)
    return {"@context": "https://schema.org", "@graph": nodes}

# ---------------------------------------------------------------- QA (build fails on any error)
BANNED_SAMEAS = re.compile(r"^https?://(www\.)?(twitter|x|instagram|facebook|linkedin|tiktok|youtube)\.com/?$|google\.[a-z.]+/search|#$")

def _walk(o, fn, parent_type=None):
    if isinstance(o, dict):
        fn(o)
        for k, v in o.items():
            _walk(v, fn, o.get("@type"))
    elif isinstance(o, list):
        for v in o: _walk(v, fn, parent_type)

def check(path, html_doc, title, desc, canonical):
    errs = []
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html_doc, re.S)
    if len(blocks) != 1: errs.append("expected exactly one JSON-LD block")
    data = json.loads(blocks[0])
    defined, referenced = set(), set()
    biz_count = 0
    def fn(n):
        nonlocal biz_count
        t = n.get("@type"); ts = t if isinstance(t, list) else [t]
        if "@id" in n and len(n) == 1: referenced.add(n["@id"])
        elif "@id" in n: defined.add(n["@id"])
        if "Organization" in ts: errs.append("stray Organization node")
        if n.get("@id") == BIZ["@id"] and len(n) > 1:
            biz_count += 1
            if "audience" in n: errs.append("audience on business node")
            if "inLanguage" in n: errs.append("inLanguage on business node")
        if "Service" in ts and ("about" in n or "inLanguage" in n): errs.append("about/inLanguage on Service")
        if t == "EntryPoint" and set(n) - {"@type", "urlTemplate", "actionPlatform"}: errs.append("extra keys on EntryPoint")
        if t and t.endswith("Action") and t != "SearchAction" and any(k.endswith("-input") for k in n): errs.append("-input on action")
        if t == "ContactAction": errs.append("ContactAction does not exist")
        for k in ("Review", "AggregateRating"):
            if k in ts: errs.append(f"{k} markup not allowed")
        sa = n.get("sameAs")
        for u in ([sa] if isinstance(sa, str) else sa or []):
            if BANNED_SAMEAS.search(u): errs.append(f"placeholder sameAs {u}")
    _walk(data, fn)
    if biz_count != 1: errs.append(f"business node defined {biz_count} times")
    dangling = referenced - defined
    if dangling: errs.append(f"dangling @id {sorted(dangling)}")
    wp = [n for n in data["@graph"] if str(n.get("@id", "")).endswith("#webpage")][0]
    if wp["name"] != title or wp["description"] != desc or wp["url"] != canonical:
        errs.append("WebPage name/description/url != title/meta/canonical")
    # FAQ markup must be visible on the page
    for n in data["@graph"]:
        if n.get("@type") == "FAQPage":
            for q in n["mainEntity"]:
                if f"<summary>{_esc(q['name'])}</summary>" not in html_doc: errs.append(f"FAQ not visible: {q['name']}")
    if errs:
        raise SystemExit(f"SCHEMA QA FAILED on {path}:\n  " + "\n  ".join(errs))

def _esc(s):
    import html
    return html.escape(s)
