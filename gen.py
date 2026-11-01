import html
P=[
("client-emails","Client Emails & Follow-ups",
"You tell Grok the situation. It writes the draft. You fix what doesn't sound like you and hit send. That's it. The computer is doing the typing so you don't have to.",
"You already know what the client needs to hear. You've written a thousand of these. The only reason it takes 15 minutes is because you're staring at a blank page. That's a waste of someone who's already done harder things.",
"Write a professional but direct email to a client about [situation]. Keep it under 120 words. Sound like a 50-year-old who's been doing this for 20 years, not a marketing team. Facts: [paste facts].",
["Open Grok and paste the prompt.","Read it. Change anything that doesn't sound like you.","Send it."],
"I had Grok write the draft so I wasn't staring at a blank page. I still decided what to say."),
("research-prep","Research & Prep Assistant (Grok Bot)",
"A Grok Bot is like a sharp assistant you hand a folder to: \"Go dig on this, come back with the short version.\" You give the assignment. It does the legwork. You read the brief.",
"You used to burn an evening googling a new client or vendor before the meeting. That evening belongs to you, your family, or your next deal. The kids aren't smarter than you. They just stopped doing the digging by hand.",
"Research [company or person] before my meeting on [date]. Give me: what they do, recent news, who the key people are, and 3 smart questions I should ask. Keep it to one page. Link your sources so I can check them.",
["Paste the instruction to your Grok Bot.","Skim the brief. Click a source or two to check anything important.","Walk in prepared."],
"I had my assistant do the homework. I still run the meeting."),
("proposals-estimates","Writing Proposals or Estimates",
"You know the job, the price, and the scope. Grok turns your notes into a clean proposal. Think of it as the guy who types up what you scribbled on the back of a napkin.",
"Proposals that sit unsent don't close. You've priced a hundred jobs in your head. The bottleneck was never knowing the work. It was the formatting. Kill the bottleneck, get paid faster.",
"Turn these notes into a clear, professional proposal for [client]. Include: the problem, what we'll do, timeline, price, and next step. Plain language, no fluff, under one page. Notes: [paste your notes and numbers].",
["Paste your notes and numbers into the prompt.","Check every number and promise yourself. That part is on you.","Send it."],
"Grok formatted it. The price and the promises are mine."),
("summarize-documents","Summarizing Long Documents or Contracts",
"You hand Grok the 40-page monster. It hands back the short version: what it says, what you owe, what to watch out for. Like having someone read the fine print and point at the scary parts.",
"You've signed things you skimmed. We all have. Some of us paid for it. Getting the short version first means you know which pages to read slowly. This does not replace your lawyer on the big stuff.",
"Summarize this document in plain English. Tell me: what it's about, what I'm agreeing to, deadlines and dollar amounts, and anything unusual or risky I should read closely. Quote the section for each point. Document: [paste text].",
["Paste the document text into Grok.","Read the summary, then read the flagged sections yourself.","Big money or legal risk? Take it to your lawyer with your questions ready."],
"Grok gave me the map. I still read the parts that matter."),
("track-competitors","Tracking Competitors or Industry News (Grok Bot)",
"Instead of you checking ten websites every week, a Grok Bot checks and sends you the short list of what changed. Picture a scout who reports back so you don't have to stand watch.",
"Getting blindsided by a competitor's new price or a rule change costs real money. You used to hear it at the trade show months later. Now you hear it while it still matters.",
"Every Monday morning, check for news about [competitor names] and [your industry]. Send me the 5 most important things in plain English, one line each, with a link to the source. Skip anything that doesn't affect my business.",
["Give your Grok Bot the instruction.","Read the Monday list over coffee.","Click the source before you act on anything."],
"I have a scout watching the market. I make the moves."),
("notes-to-actions","Rough Notes into Clean Summaries & Action Lists",
"Your notes look like a crime scene. Grok turns them into who does what by when. Same info, just cleaned up and organized.",
"Great meetings die when nobody remembers who promised what. You've lost deals over a dropped follow-up. A clean action list sent the same day makes you the most organized person in the room.",
"Turn these rough notes into a short summary and an action list. For each action: what, who, and by when. If something's unclear, list it as a question instead of guessing. Notes: [paste notes].",
["Paste your notes, typos and all.","Fix anything Grok got wrong or marked as a question.","Send the list to everyone the same day."],
"Grok cleaned up my notes. I made sure nothing got dropped."),
("client-check-ins","Routine Client Updates & Check-ins (Grok Bot)",
"The \"just checking in\" emails you mean to send and never do? A Grok Bot drafts them on a schedule so you can review them. You stay in touch without it living in your head.",
"Clients leave when they feel forgotten, not when you mess up. You know that. Regular check-ins are how you take care of people, and now it doesn't depend on you remembering on a busy Tuesday.",
"Every other Friday, draft a short check-in email for each client on this list: [names and one line about each]. Keep it warm, specific, and under 80 words. Don't send anything. Show me the drafts first.",
["Give your Grok Bot the list and the instruction.","Review the drafts. Add a personal line where it counts.","You hit send."],
"My bot reminds me and drafts it. The relationship is still mine."),
("market-pricing","Quick Market or Pricing Research",
"You ask Grok what others charge or what the market looks like, and it gives you a quick lay of the land. Think of it as calling around to five shops without making five calls.",
"Underpricing is the silent killer. You've done it. You've watched others do it. A 10-minute check before you quote beats guessing and leaving money on the table.",
"What do businesses like mine typically charge for [service] in [city or region]? Give me a low, typical, and high range, what drives the difference, and link your sources. If you're not sure, say so.",
["Ask the question with your service and area.","Check the sources. Numbers online can be old or wrong.","Set your price with your own judgment."],
"Grok did the calling around. I set the price."),
("social-posts","Drafting Simple Social or Marketing Posts",
"You tell Grok what you want to say and who you're talking to. It gives you a few versions. You pick one, make it sound like you, and post it. Like having a copywriter who never gets tired.",
"You've got 20 years of stories that would help people. They're stuck in your head because writing posts feels like homework. Your experience is the product. Grok just helps you get it out.",
"Write 3 short social posts about [topic or story] for [your audience]. Sound like a straight-talking business owner, not a marketer. No hashtag soup, no hype. Under 60 words each. My story: [a few sentences].",
["Paste the prompt with your story.","Pick the best one and rewrite any line that doesn't sound like you.","Post it yourself."],
"Grok helped with the words. The story is mine."),
("meeting-prep","Preparing for Meetings or Calls",
"Before a big call, you tell Grok what's going on and it helps you plan: what to cover, what they might push back on, what you want out of it. Like a quick huddle with a coach before the game.",
"You've walked into meetings cold and winged it. Sometimes it worked. The big ones deserve better. Ten minutes of prep is how you walk out with what you came for.",
"I have a [type of meeting] with [who] about [topic]. My goal is [goal]. Give me: a short agenda, 3 objections they might raise with how to answer each, and the one question I must ask before we hang up.",
["Fill in the blanks and paste it.","Cross out anything that doesn't fit and add what Grok missed.","Bring the one-pager to the call."],
"I prepped with Grok so I could focus on the person, not my notes."),
]
H=lambda s:html.escape(s,quote=False)
def page(title,body,css):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{H(title)} | AI without BS</title><link rel="stylesheet" href="{css}"></head><body><header class="top"><a class="logo" href="{'../' if css.startswith('..') else ''}index.html">AI <span>without</span> BS</a></header><main>{body}</main><footer><form class="signup" onsubmit="event.preventDefault();var f=this,m=f.querySelector('.msg');m.textContent='Sending...';fetch('/api/subscribe',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:f.email.value}})}}).then(r=>r.json()).then(d=>{{m.textContent=d.ok?'You\'re in. Watch your inbox.':(d.error||'Something went wrong. Try again.');if(d.ok)f.reset()}}).catch(()=>m.textContent='Something went wrong. Try again.')"><p class="pitch"><b>Get one plain-English AI play a week. No BS.</b> One email. One thing you can use. Unsubscribe anytime.</p><input type="email" name="email" required placeholder="you@yourbusiness.com" aria-label="Email address"><button type="submit">Send me the plays</button><p class="msg" aria-live="polite"></p></form><div class="sponsor"><p><b>Sponsor this site.</b> Reach business owners who\'ve already done the hard stuff. Sponsor spot: $49/month.</p><a class="btn" href="https://www.paypal.com/ncp/payment/YK9DCZUG7DSG6" target="_blank" rel="noopener">Become a sponsor</a></div><p>AIwithoutBS.com · Plain talk for people who've already done harder things.</p><p class="credit">Inspired by the directory builds of Alex Finn, Frey Chu and Chris Koerner. Respect.</p></footer></body></html>'''
import os;os.makedirs("site/pages",exist_ok=True)
cards=""
for i,(s,t,m,w,pr,st,ex) in enumerate(P,1):
    cards+=f'<a class="card" href="pages/{s}.html"><b>{i:02d}</b><span>{H(t)}</span></a>'
    steps="".join(f"<li>{H(x)}</li>" for x in st)
    nav=f'<nav class="pn">'+(f'<a href="{P[i-2][0]}.html">← Prev</a>' if i>1 else '<a href="../index.html">← Home</a>')+(f'<a href="{P[i][0]}.html">Next →</a>' if i<10 else '<a href="../index.html">Home →</a>')+'</nav>'
    b=f'''<p class="kicker">Use case {i:02d}</p><h1>{H(t)}</h1>
<section><h2>What this actually means</h2><p>{H(m)}</p></section>
<section><h2>Why it matters to you</h2><p>{H(w)}</p></section>
<section><h2>What we're going to do with it</h2><p>Open Grok and paste this:</p><pre class="prompt">{H(pr)}</pre><ol>{steps}</ol></section>
<section class="say"><h2>How you'll explain it</h2><blockquote>“{H(ex)}”</blockquote></section>{nav}'''
    open(f"site/pages/{s}.html","w").write(page(t,b,"../style.css"))
home=f'''<section class="hero"><h1>You've already done harder things.<br><em>Grok and Grok Bots work for you.</em></h1><p class="sub">Stop letting the jargon and the kids make you feel behind. You've got the judgment and the scars. We make the tools make sense and show you exactly how to point them so they do the work.</p>
<ul class="three"><li><b>What it actually means</b> — spelled out, no leftover nonsense.</li><li><b>Why it matters</b> to your results, not some tech fantasy.</li><li><b>What we're going to do with it</b> so the computer works for you. You stay the one in charge.</li></ul></section>
<section><h2>Pick a job. Point the computer at it.</h2><div class="grid">{cards}</div></section>
<section id="about" class="about"><h2>About</h2><p>Most AI talk is written by people who've never had to make payroll or lose and rebuild something. This is for the rest of us.</p><p>We can tell you what the other tools are. When it's time to actually get something done, we start with Grok and Grok Bots.</p><p>You already know how to get results. We just make the new tools make sense so they work for you instead of the other way around.</p></section>'''
open("site/index.html","w").write(page("Home",home,"style.css"))
