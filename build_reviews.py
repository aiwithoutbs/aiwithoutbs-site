"""Build /reviews from reviews_src/. Run: python3 build_reviews.py
A tool gets a page ONLY if reviews_src/content/<slug>.json exists and passes validation."""
import json,html,os,glob,sys
SITE="https://aiwithoutbs.vercel.app"
TIERS=["Use it","Worth a try","Niche","Skip"]
REQ={"title":(20,65),"meta_description":(70,160),"summary":(40,300),"good_for":None,"how_to_use":(20,1500),
     "what_youll_get":(40,1200),"missing":None,"verdict_tier":None,"verdict":(20,400),"price_free":(5,300),
     "price_paid":(5,400),"last_checked":(6,20)}
H=lambda s:html.escape(str(s))
DIR={t['slug']:t for t in json.load(open('reviews_src/directory.json'))}
tools={t["slug"]:t for t in json.load(open("reviews_src/tools.json"))}
def validate(slug,c):
    e=[]
    for k,lim in REQ.items():
        if k not in c or not c[k]: e.append(f"missing {k}"); continue
        if lim and not lim[0]<=len(c[k])<=lim[1]: e.append(f"{k} length {len(c[k])} not in {lim}")
    for k in("good_for","missing"):
        v=c.get(k)
        if not(isinstance(v,list) and 2<=len(v)<=8 and all(isinstance(x,str) and 5<=len(x)<=250 for x in v)): e.append(f"{k} must be list of 2-8 strings, 5-250 chars")
    if c.get("verdict_tier") not in TIERS: e.append(f"verdict_tier must be one of {TIERS}")
    ex=c.get("example_output")
    if ex is not None and not(isinstance(ex,dict) and ex.get("text") and ex.get("kind") in("illustrative","tested")):
        e.append("example_output needs text and kind illustrative|tested")
    if ex and ex.get("kind")=="tested" and not ex.get("tested_on"): e.append("tested example needs tested_on date")
    return e
SIGNUP=open("index.html").read().split("<footer>",1)[1].split("</footer>")[0]
def page(path,title,desc,body,jsonld):
    url=SITE+path
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{H(title)}</title><meta name="description" content="{H(desc)}"><link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:title" content="{H(title)}"><meta property="og:description" content="{H(desc)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="AI without BS"><meta name="twitter:card" content="summary"><link rel="stylesheet" href="/style.css"><script type="application/ld+json">{json.dumps(jsonld)}</script></head><body><header class="top"><a class="logo" href="/">AI <span>without</span> BS</a> <a class="navlink" href="/reviews">Reviews</a> <a class="navlink" href="/directory">Directory</a></header><main>{body}</main><footer>{SIGNUP}</footer></body></html>'''
os.makedirs("reviews",exist_ok=True)
for f in glob.glob("reviews/*.html"): os.remove(f)
pub=[];bad=0
for f in sorted(glob.glob("reviews_src/content/*.json")):
    slug=os.path.basename(f)[:-5]
    if slug not in tools: print("SKIP unknown slug",slug); bad=1; continue
    c=json.load(open(f)); e=validate(slug,c)
    if e: print("SKIP",slug,"; ".join(e)); bad=1; continue
    t=tools[slug]; li=lambda xs:"<ul>"+"".join(f"<li>{H(x)}</li>" for x in xs)+"</ul>"
    ex=c.get("example_output");exh=""
    if ex: exh=f'<p class="kicker">{"Illustrative example, not a real test run" if ex["kind"]=="illustrative" else "Real output, tested "+H(ex["tested_on"])}</p><pre class="prompt">{H(ex["text"])}</pre>'
    src="".join(f'<li><a href="{H(u)}" rel="nofollow noopener" target="_blank">{H(u)}</a></li>' for u in t["price_sources"])
    dt=DIR.get(slug); cat_link=f' (or just <a href="/directory?cat={dt["tags"][0]}#list">{H(dt["tags"][0])}</a> tools)' if dt else ''
    body=f'''<p class="kicker">AI tool review · Last checked: {H(c["last_checked"])}</p><h1>{H(t["name"])} review for small business</h1><p class="sub">{H(c["summary"])}</p>
<p class="verdict"><span class="tag">Researched</span> <b>Verdict: {H(c["verdict_tier"])}.</b> {H(c["verdict"])}</p>
<section><h2>What it's good for</h2>{li(c["good_for"])}</section>
<section><h2>How to use it</h2><pre class="prompt">{H(c["how_to_use"])}</pre></section>
<section><h2>What you'll get</h2><p>{H(c["what_youll_get"])}</p>{exh}</section>
<section><h2>What you're missing</h2>{li(c["missing"])}</section>
<section><h2>Price</h2><p><b>Free:</b> {H(c["price_free"])}</p><p><b>Paid:</b> {H(c["price_paid"])}</p><p>Sources (official, checked {H(c["last_checked"])}):</p><ul>{src}</ul><p>Official site: <a href="{H(t["official_url"])}" rel="nofollow noopener" target="_blank">{H(t["official_url"])}</a></p></section>
<p>See every AI tool we track in the <a href="/directory">AI tool directory</a>{cat_link}.</p>
<nav class="pn"><a href="/reviews">← All reviews</a><a href="/directory">Directory</a><a href="/">Home →</a></nav>'''
    ld={"@context":"https://schema.org","@type":"Article","headline":c["title"],"description":c["meta_description"],"dateModified":c.get("date_iso","2026-11-04"),"author":{"@type":"Organization","name":"AI without BS"},"about":{"@type":"SoftwareApplication","name":t["name"],"url":t["official_url"],"applicationCategory":"BusinessApplication"}}
    open(f"reviews/{slug}.html","w").write(page(f"/reviews/{slug}",c["title"],c["meta_description"],body,ld))
    pub.append((slug,t["name"],c))
cards="".join(f'<a class="card" href="/reviews/{s}"><b>{H(c["verdict_tier"])}</b><span>{H(n)}</span></a>' for s,n,c in pub) or '<p><b>Reviews coming soon.</b> We are checking each tool against its official pages first. Sign up below and you will hear when they land.</p>'
idx=f'''<p class="kicker">AI tool reviews</p><h1>Honest AI tool reviews for small business</h1><p class="sub">What each tool actually does for your business, what it costs, and what you are missing. If it won't move your business forward, we say skip it.</p>
<section id="how-we-review"><h2>How we review</h2><p>Every review is researched from the tool's official pages and dated. Reviews marked <b>Researched</b> are built from those official sources. Once we've used a tool hands-on and documented it, the review gets marked <b>Tested</b>. No star ratings, no made-up quotes.</p><p>Companies may sponsor the site or newsletter, but sponsorship never buys a recommendation, a better review, or a directory ranking. Sponsored spots are labeled.</p><p>Spot a wrong price or fact? Email info@bowandarrowconsultingco.com and we'll fix it.</p></section>
<section><h2>The reviews</h2><div class="grid">{cards}</div></section>
<p>Looking for a tool we have not reviewed yet? Check the <a href="/directory">AI tool directory</a>.</p>
<section><h2>How we check</h2><p>Prices, limits and features come from each tool's official pages, linked on every review with the date we checked. Hands-on testing is being added; any example marked "illustrative" was not a real test run. No star ratings, no made-up quotes, no paid placements.</p></section>'''
open("reviews/index.html","w").write(page("/reviews","AI Tool Reviews for Small Business | AI without BS","Plain-English reviews of AI tools for small business owners: what each one does, what it costs, and when to skip it. Checked against official sources.",idx,{"@context":"https://schema.org","@type":"CollectionPage","name":"AI Tool Reviews","url":SITE+"/reviews"}))
exec(open("build_directory.py").read())
urls=["/","/reviews","/directory"]+[f"/pages/{os.path.basename(p)[:-5]}" for p in sorted(glob.glob("pages/*.html"))]+[f"/reviews/{s}" for s,_,_ in pub]
open("sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{SITE}{u}</loc></url>\n" for u in urls)+"</urlset>\n")
open("robots.txt","w").write(f"User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: {SITE}/sitemap.xml\n")
print(f"published {len(pub)} reviews:",[s for s,_,_ in pub]); sys.exit(bad)
