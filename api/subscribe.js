const NAME='AI without BS',API='https://api.resend.com';
const ADMIN='Admin@anchorsenterprisemanagement.com';
const PASSIVE='passive-stack';
const GUIDE='https://aiwithoutbs.net/passive-stack-guide';
const DISCLOSURE='Straight talk: the guide includes one clearly labeled referral link (SurveySavvy). Everything else is plain, direct, and tested on real devices.';
const h=()=>({Authorization:`Bearer ${process.env.RESEND_API_KEY}`,'Content-Type':'application/json'});
function isDup(status,text){return status===409||/already exists/i.test(text||'');}
async function alertAdmin(smtp,from,subject,text,to=ADMIN){
  if(smtp){try{await smtp.sendMail({from,to,subject,text});console.error('ALERT sent to admin via Brevo');return 'brevo'}catch(e){console.error('ALERT via Brevo failed -',e&&e.message)}}
  try{const r=await fetch(`${API}/emails`,{method:'POST',headers:h(),body:JSON.stringify({from:'AI without BS Alerts <alerts@send.bowandarrowconsultingco.com>',to:[to],subject,text})});
    if(r.ok){console.error('ALERT sent to admin via Resend');return 'resend'}console.error('ALERT via Resend failed -',await r.text())}catch(e){console.error('ALERT via Resend failed -',e&&e.message)}
  return null;
}
async function ensureAudience(name){
  const l=await (await fetch(`${API}/audiences`,{headers:h()})).json();
  let a=(l.data||[]).find(x=>x.name===name);
  if(!a){a=await (await fetch(`${API}/audiences`,{method:'POST',headers:h(),body:JSON.stringify({name})})).json();if(!a.id)throw new Error('audience')}
  return a;
}
async function addContact(audienceId,email){
  const r=await fetch(`${API}/audiences/${audienceId}/contacts`,{method:'POST',headers:h(),body:JSON.stringify({email,unsubscribed:false})});
  if(r.ok)return {ok:true,dup:false,text:''};
  const text=await r.text();
  return {ok:false,dup:isDup(r.status,text),text};
}
function weeklyHtml(){
  return `<div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;color:#111"><h2>You're in. Welcome to AI without BS.</h2><p>You've already done harder things than learning AI. Once a week you'll get one plain-English AI play you can actually use in your business. No jargon, no hype, no bro-speak.</p><p><b>Your first play:</b> Open Grok and paste this: <i>"Here's what my business does: [one sentence]. List the 3 most boring, repetitive tasks I probably do every week, and for each, give me a prompt I can use to hand it off to you."</i></p><p>Then try one. That's it.</p><p>Browse the plays anytime: <a href="https://aiwithoutbs.vercel.app">aiwithoutbs.vercel.app</a></p><p>David<br>AI without BS</p></div>`;
}
function passiveHtml(){
  return `<div style="font-family:Georgia,serif;max-width:560px;margin:auto;color:#111"><h2>Your 2026 passive income stack is ready.</h2><p>The Real-World 2026 Passive Income App Stack is below. Open the guide and set it up on the devices you already have.</p><p><a href="${GUIDE}" style="color:#d62828;font-weight:bold">Open the interactive audit and setup guide</a></p><p>${GUIDE}</p><p><b>Safe core:</b> ~$15/month (~$180/year). Phone and computer: Nielsen Pulse and SavvyConnect.</p><p><b>Clean ceiling:</b> ~$34–$37/month (~$408–$444/year). Add TVision, Nielsen on supported TVs, and Google Screenwise Meter (invite-only).</p><p><b>Cut immediately:</b> no Honeygain, EarnApp, Pawns, or other bandwidth-sharing apps (FBI IC3 March 2026 warning). Proxy risk in this stack: 0%.</p><p>${DISCLOSURE}</p><p>David<br>AI without BS</p></div>`;
}
module.exports=async(req,res)=>{
  if(req.method!=='POST')return res.status(405).json({ok:false,error:'Use POST.'});
  let b=req.body;if(typeof b==='string'){try{b=JSON.parse(b)}catch{b={}}}
  const email=String((b&&b.email)||'').trim().toLowerCase();
  const source=String((b&&b.source)||'').trim().toLowerCase();
  const guideSource=source===PASSIVE;
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)||email.length>254)return res.status(400).json({ok:false,error:'That email doesn\'t look right.'});
  try{
    const a=await ensureAudience(NAME);
    const added=await addContact(a.id,email);
    if(!added.ok){
      console.error(added.text);
      if(!(guideSource&&added.dup))throw new Error('contact');
    }
    if(guideSource){
      try{
        const tag=await ensureAudience(PASSIVE);
        const tagged=await addContact(tag.id,email);
        if(!tagged.ok&&!tagged.dup)console.error('passive-stack tag',tagged.text);
      }catch(e){console.error('passive-stack tag',e&&e.message)}
    }
    const html=guideSource?passiveHtml():weeklyHtml();
    const subject=guideSource?'Your 2026 passive income app stack guide':"You're in: your first AI play (no BS)";
    const from=`"AI without BS" <${process.env.SENDER_EMAIL||'info@bowandarrowconsultingco.com'}>`;
    const okBody=guideSource?{ok:true,source:PASSIVE,guide:GUIDE}:{ok:true};
    let emailed=false;
    try{
      const smtp=process.env.BREVO_SMTP_KEY&&process.env.BREVO_SMTP_LOGIN?require('nodemailer').createTransport({host:'smtp-relay.brevo.com',port:587,secure:false,connectionTimeout:8000,greetingTimeout:8000,socketTimeout:10000,auth:{user:process.env.BREVO_SMTP_LOGIN,pass:process.env.BREVO_SMTP_KEY}}):null;
      try{
        if(!smtp&&process.env.BREVO_API_KEY){
          const w=await fetch('https://api.brevo.com/v3/smtp/email',{method:'POST',headers:{'api-key':process.env.BREVO_API_KEY,'Content-Type':'application/json',accept:'application/json'},body:JSON.stringify({sender:{name:'AI without BS',email:process.env.SENDER_EMAIL||'info@bowandarrowconsultingco.com'},to:[{email}],replyTo:{email:ADMIN},subject,htmlContent:html})});
          if(!w.ok)throw new Error('Brevo API '+w.status+' '+await w.text());
          emailed=true;
        }else{
          if(!smtp)throw new Error('Brevo env vars missing');
          await smtp.sendMail({from,to:email,replyTo:ADMIN,subject,html});
          emailed=true;
        }
      }catch(e){
        console.error('WELCOME EMAIL FAILED for',email,'-',e&&e.message);
        await alertAdmin(smtp,from,`Welcome email FAILED for ${email}`,`A new subscriber (${email}) was added to the list, but their welcome email did not send.\n\nSource: ${guideSource?PASSIVE:'newsletter'}\nError: ${e&&e.message}\nTime: ${new Date().toISOString()}\n\nCheck the Brevo SMTP key in Vercel env (BREVO_SMTP_KEY / BREVO_SMTP_LOGIN).`);
      }
    }catch(e){console.error('welcome',e)}
    return res.status(200).json(guideSource?{...okBody,emailed}:{ok:true});
  }catch(e){console.error(e);return res.status(500).json({ok:false,error:'Something went wrong. Try again.'})}
};

module.exports.alertAdmin=alertAdmin;
module.exports.GUIDE=GUIDE;
module.exports.PASSIVE=PASSIVE;
module.exports.DISCLOSURE=DISCLOSURE;
