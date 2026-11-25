"""Build /reviews from reviews_src/. Run: python3 build_reviews.py
A tool gets a page ONLY if reviews_src/content/<slug>.json exists and passes validation."""
import json,html,os,glob,sys,re
from ranks import RANKS,TIERS,MEANING,rank_no,rank_cls
SITE="https://aiwithoutbs.vercel.app"
REQ={"title":(20,65),"meta_description":(70,160),"summary":(40,600),"good_for":None,"how_to_use":(20,2500),
     "what_youll_get":(40,2000),"missing":None,"verdict_tier":None,"verdict":(20,1500),"one_liner":(20,600),"why_care":(20,2000),"when_to_use":(20,2000),"when_to_skip":(20,1500),"privacy":(20,1500),"alternatives":(20,1000),"missing_text":(20,3000),"price_free":(5,300),
     "price_paid":(5,400),"last_checked":(6,20)}
H=lambda s:html.escape(str(s))
def price_txt(s,prefixes):
    t=str(s).strip()
    for p in prefixes:
        if t.lower().startswith(p.lower()):
            t=t[len(p):].lstrip(" :")
            break
    return H(t)

def rich(txt):
    """Plain text -> HTML: bullet lines -> ul, tab rows -> table, 'Ready-to-paste prompt:' block -> pre, rest -> p."""
    out=[];ul=[];tb=[];lines=txt.split("\n");i=0
    def flush():
        if ul: out.append("<ul>"+"".join(f"<li>{H(x)}</li>" for x in ul)+"</ul>"); ul.clear()
        if tb: out.append('<table class="plans">'+"".join("<tr>"+"".join(f"<{'th' if j==0 else 'td'}>{H(x)}</{'th' if j==0 else 'td'}>" for x in r)+"</tr>" for j,r in enumerate(tb))+"</table>"); tb.clear()
    while i<len(lines):
        l=lines[i].strip();i+=1
        if not l: flush(); continue
        if l[:2] in("* ","- ","• ") or l[0]=="•": flush() if tb else None; ul.append(l.lstrip("*-• ").strip()); continue
        if "\t" in lines[i-1]: flush() if ul else None; tb.append([x.strip() for x in lines[i-1].split("\t") if x.strip()]); continue
        flush()
        if l.lower().startswith("ready-to-paste prompt"):
            out.append(f"<p><b>{H(l)}</b></p>"); p=[]
            while i<len(lines) and lines[i].strip()=="": i+=1
            while i<len(lines) and lines[i].strip(): p.append(lines[i].strip()); i+=1
            out.append(f'<pre class="prompt">{H(chr(10).join(p))}</pre>'); continue
        out.append(f"<p>{H(l)}</p>")
    flush(); return "".join(out)
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
FONTS='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700;1,900&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Inter:wght@500;600;700;800;900&display=swap" rel="stylesheet">'
NAV=[("/reviews","Reviews"),("/directory","Directory"),("/glossary","The What-the-Hell-Did-He-Just-Say? Vocabulary List")]
def masthead(path,home=False):
    nav="".join(f'<a href="{u}"'+(' aria-current="page"' if path==u or path.startswith(u+"/") else "")+f'>{H(t)}</a>' for u,t in NAV)
    return f'''<a class="skip" href="#content">Skip to the story</a><header class="wrap"><div class="topbar"><span>Plain talk for people who've already done harder things</span><a href="#newsletter">Get the weekly play →</a></div><div class="mast{"" if home else " sm"}"><a class="logo" href="/" aria-label="AI without BS home">AI <s>without</s> BS</a><div class="tagline">The trade paper for operators who've made payroll.</div></div><nav class="main" aria-label="Main">{nav}</nav></header>'''
# Newsletter form: same /api/subscribe POST and messages as before the redesign. Don't change it without testing api/subscribe.js.
SIGNUP=r"""<section class="signup" id="newsletter" aria-label="Newsletter and sponsorship"><div class="nl"><span class="label">The weekly play</span><h2>Get one plain-English AI play a week. No BS.</h2><p class="pitch">One email. One thing you can use. Unsubscribe anytime.</p><form onsubmit="event.preventDefault();var f=this,m=f.parentNode.querySelector('.msg');m.textContent='Sending...';fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:f.email.value})}).then(r=>r.json()).then(d=>{m.textContent=d.ok?'You\'re in. Watch your inbox.':(d.error||'Something went wrong. Try again.');if(d.ok)f.reset()}).catch(()=>m.textContent='Something went wrong. Try again.')"><input type="email" name="email" required placeholder="you@yourbusiness.com" aria-label="Email address" autocomplete="email"><button type="submit">Send me the plays</button></form><p class="msg" aria-live="polite"></p></div><div class="sp"><span class="label red">Sponsor this site</span><div class="price">$49<small>/month</small></div><p>Reach business owners who've already done the hard stuff. <b>Sponsorship never buys a recommendation</b> or a better review. Sponsored spots are labeled.</p><a class="btn k" href="https://www.paypal.com/webapps/billing/plans/subscribe?plan_id=P-4J015748U73961353NLUAQFY" target="_blank" rel="noopener">Become a sponsor</a></div></section>"""
FOOTER='<footer class="site"><div class="wrap row"><div><a class="logo" href="/">AI <s>without</s> BS</a><p style="margin-top:8px"><a class="m" href="/reviews#how-we-review">How we review</a> · Spot a wrong price or fact? Email <a class="m" href="mailto:info@bowandarrowconsultingco.com">info@bowandarrowconsultingco.com</a> and we\'ll fix it.</p></div><p class="credit">AIwithoutBS.com · Inspired by Alex Finn, Frey Chu and Chris Koerner. Respect.</p></div></footer>'
def chrome_bottom(): return f'<div class="wrap">{SIGNUP}</div>{FOOTER}'
def page(path,title,desc,body,jsonld,home=False):
    url=SITE+path
    main=f'<main id="content" class="home">{body}</main>' if home else f'<main id="content" class="wrap page">{body}</main>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{H(title)}</title><meta name="description" content="{H(desc)}"><link rel="canonical" href="{url}"><meta property="og:type" content="{"website" if home else "article"}"><meta property="og:title" content="{H(title)}"><meta property="og:description" content="{H(desc)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="AI without BS"><meta name="twitter:card" content="summary"><meta name="theme-color" content="#fffdf7">{FONTS}<link rel="stylesheet" href="/style.css"><script type="application/ld+json">{json.dumps(jsonld)}</script></head><body>{masthead(path,home)}{main}{chrome_bottom()}</body></html>'''
def badge(tier,href=None):
    return f'<a class="{rank_cls(tier)}" href="{href}">{H(tier)}</a>' if href else f'<span class="{rank_cls(tier)}">{H(tier)}</span>'
def scale_key():
    return '<div class="scale" id="ranks">'+"".join(f'<div><span class="num">{i}</span>{badge(r)}<p>{H(m)}</p></div>' for i,(r,m) in enumerate(RANKS,1))+'</div>'
# Card headline per review: homepage, reviews index, and the top of each review.
CARD={'mailchimp-ai': 'Gets your newsletter past the blank page.', 'zoom-ai-companion': 'Writes the meeting recap so you don\'t have to.', 'capcut': 'Captions your videos so you don\'t have to type them.', 'loom': 'Show it once on video instead of typing it out.', 'calendly': 'Ends the "does Tuesday work?" email chain.', 'intercom': 'Pays for itself only when it solves the problem.', 'tidio': 'Answers the same customer questions so you don\'t have to.', 'quickbooks': 'Your bookkeeper gets a sidekick, not a replacement.', 'deepl': 'Translations that read like a person wrote them.', 'adobe-firefly': 'AI pictures you can use without a lawyer.', 'midjourney': 'Pictures that look like you hired a designer.', 'canva-ai': 'Flyers that look like you paid somebody.', 'chatgpt': 'Kills the blank page in 30 seconds.', 'claude': 'Actually reads the whole damn contract.', 'gemini': 'Your AI if you live in Gmail.', 'grok': 'Knows what happened this morning.', 'meta-muse': 'The AI that gets off the couch.', 'microsoft-copilot': 'Your AI if you live in Word and Outlook.', 'notion-ai': 'Finds the stuff you swore you saved.', 'otter-ai': "Takes the call notes so you don't.", 'perplexity': 'Answers with receipts, links included.', 'zapier-ai': "Quit copy-pasting like it's 1997.", 'make': 'Cheaper automation, if you put in the time.'}
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
<div class="vbox"><span class="no">#{rank_no(c["verdict_tier"])}</span><span class="label">Our rank · <a href="/reviews#ranks">see the six-rank key</a></span>{badge(c["verdict_tier"])}<p><b>“{H(CARD.get(slug,t["name"]))}”</b> {H(MEANING[c["verdict_tier"]])} <span class="tag">Researched</span></p></div>
<section><h2>WHY YOU SHOULD CARE</h2>{rich(c["why_care"])}</section>
<section><h2>WHEN TO USE IT</h2>{rich(c["when_to_use"])}</section>
<section><h2>WHEN TO SKIP IT</h2>{rich(c["when_to_skip"])}</section>
<section><h2>HOW TO USE IT</h2>{rich(c["how_to_use"])}</section>
<section><h2>WHAT YOU'LL GET</h2>{rich(c["what_youll_get"])}{exh}</section>
<section><h2>WHAT YOU'RE MISSING</h2>{rich(c["missing_text"])}</section>
<section><h2>PRIVACY</h2>{rich(c["privacy"])}</section>
<section><h2>ALTERNATIVES</h2>{rich(c["alternatives"])}</section>
<section><h2>Price</h2><p><b>Free:</b> {price_txt(c["price_free"],("Free",))}</p><p><b>Paid:</b> {price_txt(c["price_paid"],("Paid",))}</p><p>Sources (official, checked {H(c["last_checked"])}):</p><ul>{src}</ul><p>Official site: <a href="{H(t["official_url"])}" rel="nofollow noopener" target="_blank">{H(t["official_url"])}</a></p></section>
<section><h2>VERDICT</h2><p class="verdict">{badge(c["verdict_tier"])} <span>Rank {rank_no(c["verdict_tier"])} of 6: {H(MEANING[c["verdict_tier"]])}</span></p>{rich(c["verdict"])}</section>
<p>Spot a wrong price or fact? Email <a href="mailto:info@bowandarrowconsultingco.com">info@bowandarrowconsultingco.com</a> and we'll fix it. <a href="/reviews#how-we-review">How we review</a>.</p>
<p>See every AI tool we track in the <a href="/directory">AI tool directory</a>{cat_link}.</p>
<nav class="pn"><a href="/reviews">← All reviews</a><a href="/directory">Directory</a><a href="/">Home →</a></nav>'''
    ld={"@context":"https://schema.org","@type":"Article","headline":c["title"],"description":c["meta_description"],"dateModified":c.get("date_iso","2026-11-04"),"author":{"@type":"Organization","name":"AI without BS"},"about":{"@type":"SoftwareApplication","name":t["name"],"url":t["official_url"],"applicationCategory":"BusinessApplication"}}
    open(f"reviews/{slug}.html","w").write(page(f"/reviews/{slug}",c["title"],c["meta_description"],body,ld))
    pub.append((slug,t["name"],c))
# Short dek line per card (homepage, reviews index). Each one condenses that review's own verdict; no new claims.
DEK={'mailchimp-ai':'Free extra on Standard and Premium. Not a reason to upgrade.','zoom-ai-companion':'Free with Zoom Pro: unlimited meeting summaries. The $20 ZoomMate add-on is optional.','capcut':'Free captions and quick edits. Check the license before using templates in ads.','loom':'Free screen videos that work. The AI costs $24 a user a month.','calendly':'Free booking link that works. The AI notetaker costs extra.','intercom':'Strong AI support agent at $0.99 per solved chat. Seats and add-ons add up.','tidio':'Handy if customers ask the same things. Watch the monthly chat cap.','quickbooks':'Handy if you already use QuickBooks. The best AI costs $140 a month.','deepl':'Does translation really well. Free to start; paid keeps your text private.','adobe-firefly':'Free to try, safe for ads. Video eats credits fast.','midjourney':'Top-shelf images, no free plan. Public unless you pay for Pro.','chatgpt':'Free, and it actually gets you a draft. Still check the facts.','perplexity':'Answers you can check before you bet on them.','canva-ai':'Wins at posts and flyers. Free AI uses run out fast.','grok':"Free, live info, usable draft. Don't treat it as an expert.",'zapier-ai':'Kills repetitive work. Start with one task.','otter-ai':'Great for notes. The free plan dies after about 30 minutes.','gemini':"Useful if you're already in Google. Free is limited.",'microsoft-copilot':'Only really useful inside the apps, and that takes paid.','meta-muse':'Promising, limited availability. Make it prove it.','notion-ai':"Only if you already live in Notion. Don't start a $100/month system for the AI.",'make':'More automation per dollar than Zapier. Expect a learning curve.','claude':'Best when the wording has to hold up. When a proposal, an agreement, or a hard email has to say exactly what you mean, this is the one we point at it.'}
ORDER=['claude','chatgpt','perplexity','canva-ai','grok','zapier-ai','otter-ai','gemini','microsoft-copilot','meta-muse','notion-ai','make','midjourney','adobe-firefly','deepl','quickbooks','tidio','intercom','calendly','loom','capcut','zoom-ai-companion','mailchimp-ai']  # tie-break within a rank
ranked=sorted(pub,key=lambda p:(rank_no(p[2]["verdict_tier"]),ORDER.index(p[0]) if p[0] in ORDER else 99,p[1]))
SHORT={'mailchimp-ai':'Mailchimp AI','zoom-ai-companion':'Zoom AI Companion','quickbooks':'QuickBooks AI','canva-ai':'Canva AI','meta-muse':'Muse (Meta)'}
def ritem(s,n,c,top=False):
    return f'<a class="ritem{" top" if top else ""}" href="/reviews/{s}"><span class="label tl">{H(SHORT.get(s,n))}</span>{badge(c["verdict_tier"])}<h3>{H(CARD.get(s,n))}</h3><p>{H(DEK.get(s,c["one_liner"]))}</p></a>'
cards="".join(ritem(s,n,c,i==0) for i,(s,n,c) in enumerate(ranked))
cards=f'<div class="rlist">{cards}</div>' if cards else '<p><b>Reviews coming soon.</b> We are checking each tool against its official pages first. Sign up below and you will hear when they land.</p>'
idx=f'''<p class="kicker">AI tool reviews</p><h1>Honest AI tool reviews for small business</h1><p class="sub">What each tool actually does for your business, what it costs, and what you are missing. If it won't move your business forward, we say skip it.</p>
<section><h2>The six ranks, best to worst</h2><p>Every review gets exactly one rank. No participation trophies. The bottom rank is on the board even though nothing has earned it yet.</p>{scale_key()}</section>
<section><h2>The verdicts, ranked straight</h2>{cards}</section>
<section id="how-we-review"><h2>How we review</h2><p>Every review is researched from the tool's official pages and dated. Reviews marked <b>Researched</b> are built from those official sources. Once we've used a tool hands-on and documented it, the review gets marked <b>Tested</b>. No star ratings, no made-up quotes.</p><p class="note">Companies may sponsor the site or newsletter, but sponsorship never buys a recommendation, a better review, or a directory ranking. Sponsored spots are labeled.</p><p>Spot a wrong price or fact? Email <a href="mailto:info@bowandarrowconsultingco.com">info@bowandarrowconsultingco.com</a> and we'll fix it.</p></section>
<p>Looking for a tool we have not reviewed yet? Check the <a href="/directory">AI tool directory</a>.</p>
<section><h2>How we check</h2><p>Prices, limits and features come from each tool's official pages, linked on every review with the date we checked. Hands-on testing is being added; any example marked "illustrative" was not a real test run. No star ratings, no made-up quotes, no paid placements.</p></section>'''
open("reviews/index.html","w").write(page("/reviews","AI Tool Reviews for Small Business | AI without BS","Plain-English reviews of AI tools for small business owners: what each one does, what it costs, and when to skip it. Checked against official sources.",idx,{"@context":"https://schema.org","@type":"CollectionPage","name":"AI Tool Reviews","url":SITE+"/reviews"}))
exec(open("build_directory.py").read())
exec(open("build_home.py").read())
g=open("notes/v2/glossary.txt").read().replace("\u2019","'").splitlines()
gt=next(l[6:] for l in g if l.startswith("TITLE ")); gs=next(l[9:] for l in g if l.startswith("SUBTITLE "))
terms=[l.split("|",1) for l in g if "|" in l]
gb=f'<p class="kicker">AI jargon, translated</p><h1>The What-the-Hell-Did-He-Just-Say? Vocabulary List</h1><p class="sub">Translate the nonsense. Make it make sense. Your jargon code key: {len(terms)} AI terms you keep hearing, explained in plain English.</p><section class="why"><h2>Why you should care</h2><p>Half the reason AI feels like a club you are not in is the vocabulary. Salespeople and the kids toss these words around to sound smart and make you feel slow. Learn these and you stop nodding along, start asking the right questions, and nobody sells you a "revolutionary AI agent" that is really a chatbot with a nice haircut.</p></section><section><dl class="glossary">'+"".join(f'<dt id="{H(re.sub(r"[^a-z0-9]+","-",k.strip().lower()).strip("-"))}"><b>{i}. {H(k.strip())}</b></dt><dd>{H(v.strip())}</dd>' for i,(k,v) in enumerate(terms,1))+'</dl></section><p>Ready to use it? Read our <a href="/reviews">AI tool reviews</a> or browse the <a href="/directory">AI tool directory</a>.</p>'
gld={"@context":"https://schema.org","@type":"DefinedTermSet","name":gt,"url":SITE+"/glossary","hasDefinedTerm":[{"@type":"DefinedTerm","name":k.strip(),"description":v.strip()} for k,v in terms]}
open("glossary.html","w").write(page("/glossary","The What-the-Hell-Did-He-Just-Say? Vocabulary List | AI without BS","Plain-English AI glossary for small business owners: LLM, tokens, hallucination, RAG, agents and 20 more AI terms explained without the BS.",gb,gld))
urls=["/","/reviews","/directory","/glossary"]+[f"/pages/{os.path.basename(p)[:-5]}" for p in sorted(glob.glob("pages/*.html"))]+[f"/reviews/{s}" for s,_,_ in pub]
open("sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{SITE}{u}</loc></url>\n" for u in urls)+"</urlset>\n")
open("robots.txt","w").write(f"User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: {SITE}/sitemap.xml\n")
print(f"published {len(pub)} reviews:",[s for s,_,_ in pub]); sys.exit(bad)
