# exec'd by build_reviews.py (shares pub, ranked, CARD, DEK, SHORT, ritem, badge, scale_key, page, H, SITE).
# Builds index.html (the homepage) and puts the shared masthead/footer on the ten job pages in pages/.
import re as _re
_feat=ranked[0] if ranked else None   # top-ranked review is the cover feature
_rest=ranked[1:]
_JOBS=[(os.path.basename(p)[:-5],_re.search(r"<h1>(.*?)</h1>",open(p).read()).group(1)) for p in sorted(glob.glob("pages/*.html"))]
_ORDERJ=["client-emails","research-prep","proposals-estimates","summarize-documents","track-competitors","notes-to-actions","client-check-ins","market-pricing","social-posts","meeting-prep"]
_JOBS.sort(key=lambda x:_ORDERJ.index(x[0]) if x[0] in _ORDERJ else 99)
_CATS=[("writing","Writing","Write emails, posts &amp; proposals"),("meetings/notes","Meetings / notes","Get notes from calls"),("marketing/social","Marketing / social","Market your business"),("images/design","Images / design","Make graphics &amp; flyers"),("customer service","Customer service","Answer customers"),("automation","Automation","Stop copy-pasting between apps"),("research","Research","Research prices &amp; competitors"),("coding/website","Coding / website","Build a website")]
_feath=""
if _feat:
    fs,fn,fc=_feat
    _feath=f'''<div class="feature" id="featured"><div class="wrap grid"><div class="big">#{rank_no(fc["verdict_tier"])}<small>Top-ranked review</small></div><div><span class="label">Featured review · {H(fn)}</span><h2>{H(CARD.get(fs,fn))}</h2><p>{H(DEK.get(fs,fc["one_liner"]))}</p><div class="ctas">{badge(fc["verdict_tier"])}<a class="btn inv" href="/reviews/{fs}">Read the full review →</a></div></div></div></div>'''
_home=f'''<aside class="stack-promo" aria-label="Passive income audit"><div class="wrap"><p><a href="/passive-stack">Earn $180–$444/year ($0 out of pocket)</a></p></div></aside><div class="wrap"><div class="cover"><div class="lead"><span class="label red">The cover story</span>
<h1>You've already done harder things. <i>Now make AI work for you.</i></h1>
<p class="dek">Stop letting the jargon and the kids make you feel behind. You've got the judgment and the scars. We make the tools make sense and show you exactly how to point them so they do the work.</p>
<div class="ctas"><a class="btn k" href="/directory">Browse the directory</a><a class="btn o" href="/reviews">Read the reviews</a><a class="btn o" href="/glossary">AI jargon, translated</a></div></div>
<aside class="side"><span class="label">Our three promises</span><h2>Every page answers three questions.</h2>
<div class="prom"><span class="n">1</span><div><b>What it actually means</b><p>Spelled out, no leftover nonsense.</p></div></div>
<div class="prom"><span class="n">2</span><div><b>Why it matters to your results</b><p>Not some tech fantasy.</p></div></div>
<div class="prom"><span class="n">3</span><div><b>What we're going to do with it</b><p>So the computer works for you. You stay the one in charge.</p></div></div>
</aside></div></div>
{_feath}
<div class="wrap">
<section id="reviews"><div class="sh"><div><span class="label red">Recently reviewed</span><h2>The verdicts, ranked straight.</h2></div><p>Six ranks, best to worst. We check each tool against its official pages and don't hand out participation trophies.</p></div>
{scale_key()}
<div class="rlist">{"".join(ritem(s,n,c) for s,n,c in _rest)}</div>
<p style="margin-top:28px"><a class="btn k" href="/reviews">All reviews and how we rank →</a></p></section>
<section id="directory"><div class="sh"><div><span class="label red">The directory</span><h2>Find a tool by job.</h2></div><p>Start with the work, not the tool everybody's yelling about.</p></div>
<div class="dir">{"".join(f'<a href="/directory?cat={_c.replace(" ","%20")}#list"><span class="label red">{_l}</span><strong>{_t}</strong><span class="go">See tools →</span></a>' for _c,_l,_t in _CATS)}</div></section>
<section id="jobs"><div class="sh"><div><span class="label red">Ten jobs</span><h2>Pick a job. Point the computer at it.</h2></div></div>
<div class="jobs">{"".join(f'<a class="job" href="/pages/{_s}"><span class="n">{_i:02d}</span><span class="t">{_t}</span></a>' for _i,(_s,_t) in enumerate(_JOBS,1))}</div></section>
<section id="about" style="border-bottom:0"><div class="about"><div class="pull">Most AI talk is written by people who've never had to make payroll or lose and rebuild something. This is for the rest of us.</div>
<div><span class="label red">About</span><p style="margin-top:12px">We check each tool against its official pages, tell you what it's good for, and say skip it when it won't move your business forward. <a href="/reviews#how-we-review" style="color:var(--red);font-weight:700">How we review</a>.</p><p>You already know how to get results. We just make the new tools make sense so they work for you instead of the other way around.</p><p class="note">Companies may sponsor the site or newsletter, but sponsorship never buys a recommendation, a better review, or a directory ranking. Sponsored spots are labeled.</p></div></div></section>
</div>'''
open("index.html","w").write(page("/","AI without BS | Plain-English AI for small business owners","Plain-English AI for small business owners who've already done harder things: honest, ranked AI tool reviews, a no-BS tools directory, and one AI play a week.",_home,{"@context":"https://schema.org","@type":"WebSite","name":"AI without BS","url":SITE+"/"},home=True))
# Job pages: hand-written bodies, shared chrome. Idempotent: swaps whatever header/footer is there.
for _p in sorted(glob.glob("pages/*.html")):
    _h=open(_p).read()
    _title=_re.search(r"<title>(.*?)</title>",_h).group(1)
    _body=_re.search(r"<main[^>]*>(.*?)</main>",_h,_re.S).group(1)
    _body=_body.replace('href="../index.html"','href="/"')
    _body=_re.sub(r'href="([a-z0-9-]+)\.html"',r'href="/pages/\1"',_body)
    _slug=os.path.basename(_p)[:-5]
    _desc=_re.sub(r"<[^>]+>","",_re.search(r"<h2>What this actually means</h2><p>(.*?)</p>",_body,_re.S).group(1)) if "What this actually means" in _body else _title
    _desc=html.unescape(_desc)[:155]
    open(_p,"w").write(page(f"/pages/{_slug}",html.unescape(_title),_desc,_body,{"@context":"https://schema.org","@type":"HowTo","name":html.unescape(_title).split(" | ")[0],"url":SITE+f"/pages/{_slug}"}))
