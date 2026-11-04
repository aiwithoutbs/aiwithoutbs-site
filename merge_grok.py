"""Merge Grok's descriptions. Usage: python3 merge_grok.py grok.txt   (lines: Tool name | one-liner | tag1, tag2)"""
import json,sys
P="reviews_src/directory.json"; d=json.load(open(P)); by={t["name"].lower():t for t in d}
OK={"writing","meetings/notes","marketing/social","images/design","video","voice","research","automation","customer service","sales/CRM","bookkeeping/finance","productivity","coding/website"}
okl={x.lower():x for x in OK}; n=0
for i,l in enumerate(open(sys.argv[1],encoding="utf-8"),1):
    l=l.strip().lstrip("-*0123456789. ").strip()
    if l.count("|")<2: continue
    name,desc,tags=[x.strip() for x in l.split("|",2)]
    if "[CHECK]" in l: print(f"FLAG line {i} has [CHECK]: {name}")
    t=by.get(name.lower())
    if not t: print(f"FLAG line {i} unknown tool: {name}"); continue
    tl=[x.strip() for x in tags.replace(";",",").split(",") if x.strip()]
    bad=[x for x in tl if x.lower() not in okl]
    if bad: print(f"FLAG line {i} unknown tags for {name}: {bad} (kept the rest)")
    good=[okl[x.lower()] for x in tl if x.lower() in okl]
    t["what_its_for"]=desc.replace("[CHECK]","").strip()
    if good: t["tags"]=good
    n+=1
json.dump(d,open(P,"w"),indent=1); print(f"merged {n}/{len(d)}; missing:",[t["name"] for t in d if not t["what_its_for"]])
