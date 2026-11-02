const NAME='AI without BS',API='https://api.resend.com';
const h=()=>({Authorization:`Bearer ${process.env.RESEND_API_KEY}`,'Content-Type':'application/json'});
module.exports=async(req,res)=>{
  if(req.method!=='POST')return res.status(405).json({ok:false,error:'Use POST.'});
  let b=req.body;if(typeof b==='string'){try{b=JSON.parse(b)}catch{b={}}}
  const email=String((b&&b.email)||'').trim().toLowerCase();
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)||email.length>254)return res.status(400).json({ok:false,error:'That email doesn\'t look right.'});
  try{
    const l=await (await fetch(`${API}/audiences`,{headers:h()})).json();
    let a=(l.data||[]).find(x=>x.name===NAME);
    if(!a){a=await (await fetch(`${API}/audiences`,{method:'POST',headers:h(),body:JSON.stringify({name:NAME})})).json();if(!a.id)throw new Error('audience')}
    const r=await fetch(`${API}/audiences/${a.id}/contacts`,{method:'POST',headers:h(),body:JSON.stringify({email,unsubscribed:false})});
    if(!r.ok){console.error(await r.text());throw new Error('contact')}
    try{
      const html=`<div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;color:#111"><h2>You're in. Welcome to AI without BS.</h2><p>You've already done harder things than learning AI. Once a week you'll get one plain-English AI play you can actually use in your business. No jargon, no hype, no bro-speak.</p><p><b>Your first play:</b> Open Grok and paste this: <i>"Here's what my business does: [one sentence]. List the 3 most boring, repetitive tasks I probably do every week, and for each, give me a prompt I can use to hand it off to you."</i></p><p>Then try one. That's it.</p><p>Browse the plays anytime: <a href="https://aiwithoutbs.vercel.app">aiwithoutbs.vercel.app</a></p><p>David<br>AI without BS</p></div>`;
      const subject="You're in: your first AI play (no BS)";
      if(process.env.BREVO_SMTP_KEY&&process.env.BREVO_SMTP_LOGIN){
        const t=require('nodemailer').createTransport({host:'smtp-relay.brevo.com',port:587,secure:false,auth:{user:process.env.BREVO_SMTP_LOGIN,pass:process.env.BREVO_SMTP_KEY}});
        await t.sendMail({from:`"AI without BS" <${process.env.SENDER_EMAIL||'info@bowandarrowconsultingco.com'}>`,to:email,subject,html});
        return res.status(200).json({ok:true});
      }
      const w=process.env.BREVO_API_KEY
        ?await fetch('https://api.brevo.com/v3/smtp/email',{method:'POST',headers:{'api-key':process.env.BREVO_API_KEY,'Content-Type':'application/json',accept:'application/json'},body:JSON.stringify({sender:{name:'AI without BS',email:process.env.SENDER_EMAIL||'info@bowandarrowconsultingco.com'},to:[{email}],subject,htmlContent:html})})
        :await fetch(`${API}/emails`,{method:'POST',headers:h(),body:JSON.stringify({from:'AI without BS <onboarding@resend.dev>',to:[email],subject,html})});
      if(!w.ok)console.error('welcome',await w.text());
    }catch(e){console.error('welcome',e)}
    return res.status(200).json({ok:true});
  }catch(e){console.error(e);return res.status(500).json({ok:false,error:'Something went wrong. Try again.'})}
};
