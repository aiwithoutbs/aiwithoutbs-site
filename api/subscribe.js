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
    return res.status(200).json({ok:true});
  }catch(e){console.error(e);return res.status(500).json({ok:false,error:'Something went wrong. Try again.'})}
};
