import json,re,glob
from ranks import TIERS
SECS=["ONE-LINER","WHY YOU SHOULD CARE","WHEN TO USE IT","WHEN TO SKIP IT","HOW TO USE IT","WHAT YOU'LL GET","WHAT YOU'RE MISSING","PRIVACY","ALTERNATIVES","VERDICT"]
KEY=dict(zip(SECS,["one_liner","why_care","when_to_use","when_to_skip","how_to_use","what_youll_get","missing_text","privacy","alternatives","verdict"]))
rx=re.compile(r"^("+"|".join(re.escape(s) for s in SECS)+r")\b[:\s]*(.*)$")
for slug in [p.split('/')[-1][:-5] for p in sorted(glob.glob("reviews_src/content/*.json"))]:
    t=open(f"notes/v2/{slug}.txt").read().replace("\u2019","'").replace("\u2060","").replace("\ufffc","")
    t=re.sub(r"(?m)^\s*Copy prompt\s*$","",t)
    cur=None;d={}
    for line in t.splitlines():
        m=rx.match(line.strip())
        if m: cur=m.group(1); d[cur]=[m.group(2)] if m.group(2) else []; continue
        if cur: d[cur].append(line.rstrip())
    c=json.load(open(f"reviews_src/content/{slug}.json"))
    for s in SECS:
        v="\n".join(d.get(s,[])).strip(); v=re.sub(r"\n{3,}","\n\n",v)
        if not v: print("MISSING",slug,s); continue
        c[KEY[s]]=v
    v=c["verdict"]; first,_,rest=v.partition("\n")
    # The rank is set by hand in the JSON ("verdict_tier", one of ranks.TIERS) and never overwritten from notes.
    # Drop any rank/tier word the notes open the verdict with (old scale words too, e.g. "NICHE TOOL").
    m=re.match(r"\s*("+"|".join(re.escape(x) for x in TIERS+["Worth a try","Use it","Niche","Skip"])+r")(\s+tool)?\b[.:]?\s*",first,re.I)
    if m: v=(first[m.end():]+"\n"+rest).strip()
    if c.get("verdict_tier") not in TIERS: print("NORANK",slug,"- set verdict_tier to one of",TIERS)
    c["verdict"]=re.sub(r"(?m)^Closing line:\s*","",v)
    c["summary"]=c["one_liner"]
    json.dump(c,open(f"reviews_src/content/{slug}.json","w"),indent=1,ensure_ascii=False)
    # conflict check: $ amounts in v2 not in verified prices
    known=c["price_free"]+c["price_paid"]+" ".join(c.get("missing",[]))
    bad=sorted({x for x in re.findall(r"\$[\d,.]+\d",t) if x not in known})
    print(slug,c["verdict_tier"],"| unmatched $:",bad)
