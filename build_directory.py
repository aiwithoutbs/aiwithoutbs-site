# exec'd by build_reviews.py (shares pub, DIR, page, H, SITE). Builds directory.html.
import datetime
_FT={True:"Yes",False:"No"}
_today=datetime.date.today()
_pubs={s:c for s,_,c in pub}
_dl=sorted(DIR.values(),key=lambda t:t["name"].lower())
_cats=sorted({c for t in _dl for c in t["tags"]})
def _why(t):
    w=t.get("why","").strip()
    return f'<br><span class="why"><b>Why you\'d care:</b> {H(w)}</span>' if w else ""
def _row(t):
    s=t["slug"];d=t["what_its_for"] or ("AI tool for "+", ".join(t["tags"])+".")
    rv=f'<a href="/reviews/{s}">Read our review</a>' if s in _pubs else '<span class="soon">Review coming</span>'
    return f'<li class="tool" data-tags="{H(" ".join(t["tags"]))}" data-name="{H(t["name"].lower())}"><b><a href="{H(t["url"])}" rel="nofollow noopener" target="_blank">{H(t["name"])}</a></b> <span class="tags">{H(" · ".join(t["tags"]))}</span><br>{H(d)}{_why(t)}<br><small>Free tier: {_FT.get(t["free_tier"],"See site")} · Paid from: {H(t["paid_from"])} · Checked {H(t["last_checked"])}</small> · {rv}</li>'
_LAUNCH=49  # tools in the launch batch; anything after was added later
_new=list(reversed(list(DIR.values())[_LAUNCH:]))[:6]
_rec=sorted(pub,key=lambda p:p[2].get("date_iso",""),reverse=True)
_newh="<ul>"+"".join(f'<li><a href="#t-{t["slug"]}">{H(t["name"])}</a></li>' for t in _new)+"</ul>" if _new else ""
_rech="<ul>"+"".join(f'<li><a href="/reviews/{s}">{H(n)}</a>: {H(c["verdict_tier"])} ({H(c["last_checked"])})</li>' for s,n,c in _rec)+"</ul>" if _rec else "<p>First reviews land this week. Sign up below to hear when.</p>"
_groups="".join(f'<section class="cat" id="cat-{H(c.replace("/","-"))}"><h3>{H(c)}</h3><ul>'+"".join(_row(t).replace('<li class="tool"',f'<li id="t-{t["slug"]}" class="tool"',1) if c==t["tags"][0] else _row(t) for t in _dl if c in t["tags"])+'</ul></section>' for c in _cats)
_btns='<button type="button" data-cat="">All</button>'+"".join(f'<button type="button" data-cat="{H(c)}">{H(c)}</button>' for c in _cats)
_js='''<script>(function(){var q=document.getElementById("q"),cur="";function run(){var v=q.value.toLowerCase();document.querySelectorAll(".cat").forEach(function(s){var n=0;s.querySelectorAll(".tool").forEach(function(li){var ok=(!cur||li.dataset.tags.split(" ").indexOf(cur)>-1)&&(!v||li.textContent.toLowerCase().indexOf(v)>-1);li.hidden=!ok;if(ok)n++});s.hidden=!n||(cur&&s.querySelector("h3").textContent!==cur)});document.getElementById("cnt").textContent=document.querySelectorAll(".cat:not([hidden]) .tool:not([hidden])").length+" listings shown"}document.getElementById("f").hidden=false;document.querySelectorAll("#f button").forEach(function(b){b.onclick=function(){cur=b.dataset.cat;document.querySelectorAll("#f button").forEach(function(x){x.classList.toggle("on",x===b)});run()}});q.oninput=run;var m=location.search.match(/cat=([^&]+)/);if(m){cur=decodeURIComponent(m[1]);document.querySelectorAll("#f button").forEach(function(x){x.classList.toggle("on",x.dataset.cat===cur)})}run()})();</script>'''
_body=f'''<p class="kicker">AI tool directory · {len(_dl)} tools · Updated {_today.strftime("%b %-d, %Y")}</p><h1>The No-BS AI Tools Directory</h1><p class="sub"><strong>Straight talk: what it does and why you should care. No hype.</strong></p><p class="sub">AI tools for small business, in plain English: what each one is, why you'd care, whether there's a free tier, and the lowest paid price from the official pricing page. Reviewed tools link to our honest review.</p>
{("<section><h2>Just added</h2>"+_newh+"</section>") if _new else ""}
<section><h2>Recently reviewed</h2>{_rech}<p><a href="/reviews">All reviews →</a></p></section>
<section id="list"><h2>All tools by use case</h2><div id="f" hidden><input id="q" type="search" placeholder="Search tools" aria-label="Search tools"> <span id="cnt"></span><div class="fb">{_btns}</div></div>{_groups}</section>
<p><small>Prices are the lowest paid plan shown on each official site on the date checked; "Not confirmed" means the official page didn't show a price we could verify. Tool links are not affiliate links.</small></p>{_js}'''
_ld={"@context":"https://schema.org","@type":"ItemList","name":"AI tool directory for small business","url":SITE+"/directory","numberOfItems":len(_dl),"itemListElement":[{"@type":"ListItem","position":i+1,"name":t["name"],"url":(SITE+"/reviews/"+t["slug"]) if t["slug"] in _pubs else t["url"]} for i,t in enumerate(_dl)]}
open("directory.html","w").write(page("/directory","The No-BS AI Tools Directory for Small Business (2026) | AI without BS",f"A plain-English list of {len(_dl)} AI tools for small business owners: what each is for, free tier, and starting price from official pages.",_body,_ld))
