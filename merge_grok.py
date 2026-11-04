"""Merge Grok's text. Usage: python3 merge_grok.py grok.txt
Lines: 'Tool name | what it is | why you'd care | tags'  (or old 3-col 'Tool name | what it is | tags').
Works even if everything is pasted on one line run together."""
import json,sys,re
P="reviews_src/directory.json"; d=json.load(open(P)); by={t["name"].lower():t for t in d}
OK={"writing","meetings/notes","marketing/social","images/design","video","voice","research","automation","customer service","sales/CRM","bookkeeping/finance","productivity","coding/website"}
okl={x.lower():x for x in OK}; n=0
raw=open(sys.argv[1],encoding="utf-8").read()
names=sorted((t["name"] for t in d),key=len,reverse=True)
parts=re.split(r'(?:^|(?<=\s)|(?<=\d\.))(' + '|'.join(map(re.escape,names)) + r')\s*\|\s*', raw, flags=re.I)
for i in range(1,len(parts)-1,2):
    name,rest=parts[i].strip(),parts[i+1].strip().rstrip("-*0123456789. \n")
    rest=re.sub(r'\s*\n.*$','',rest,flags=re.S) if rest.count("\n") and rest.split("\n")[0].count("|")>=1 else rest
    f=[x.strip() for x in rest.split("|")]
    if len(f)>=3: desc,why,tags=f[0],f[1],f[2]
    elif len(f)==2: desc,why,tags=f[0],"",f[1]
    else: print("FLAG bad line:",name); continue
    if "[CHECK]" in rest: print("FLAG [CHECK]:",name)
    t=by[name.lower()]
    tl=[x.strip() for x in tags.replace(";",",").split(",") if x.strip()]
    bad=[x for x in tl if x.lower() not in okl]
    if bad: print(f"FLAG unknown tags for {name}: {bad} (kept the rest)")
    good=[okl[x.lower()] for x in tl if x.lower() in okl]
    t["what_its_for"]=desc.replace("[CHECK]","").strip()
    if why: t["why"]=why.replace("[CHECK]","").strip()
    if good: t["tags"]=good
    n+=1
json.dump(d,open(P,"w"),indent=1); print(f"merged {n}/{len(d)}; missing desc:",[t["name"] for t in d if not t["what_its_for"]],"; missing why:",len([t for t in d if not t.get("why")]))
