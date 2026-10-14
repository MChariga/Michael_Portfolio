const $=(s,r=document)=>[...r.querySelectorAll(s)];
const bg=$('.burger')[0];if(bg)bg.onclick=()=>$('nav')[0].classList.toggle('open');
$('.tabs button').forEach(b=>b.onclick=()=>{$('.tabs button').forEach(x=>x.classList.toggle('on',x===b));
 $('[data-t]').forEach(c=>c.classList.toggle('hide',b.dataset.f!=='all'&&c.dataset.t!==b.dataset.f))});

/* Email dialog: works with or without a mail app installed (Gmail, mail app or copy). */
function mailDialog(o){
 const to=EMAIL,su=o.subject||'',bd=o.body||'',q=encodeURIComponent;
 const gm='https://mail.google.com/mail/?view=cm&fs=1&to='+q(to)+'&su='+q(su)+'&body='+q(bd);
 const mt='mailto:'+to+'?subject='+q(su)+'&body='+q(bd);
 const esc=t=>t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
 const d=document.createElement('div');d.className='mm';
 d.innerHTML=`<div class="mmc" role="dialog" aria-modal="true"><button class="mmx" aria-label="Close">&times;</button><h3>${o.title||'Email me'}</h3><p>${o.lead||'Choose how you would like to write to me.'}</p>
 <div class="mmto"><span>To</span><b>${to}</b></div>${bd?`<pre>${esc(bd)}</pre>`:''}
 <div class="btns"><a class="btn" target="_blank" rel="noopener" href="${gm}">Open in Gmail</a><a class="btn o" href="${mt}">Open email app</a><button type="button" class="btn o" data-copy>${bd?'Copy message':'Copy address'}</button></div>${o.note?`<p class="mmnote">${o.note}</p>`:''}<p class="small mmok" hidden>Copied to clipboard</p></div>`;
 const close=()=>d.remove();d.onclick=e=>{if(e.target===d)close()};$('.mmx',d)[0].onclick=close;
 $('[data-copy]',d)[0].onclick=async()=>{const t=bd?`To: ${to}\nSubject: ${su}\n\n${bd}`:to;
  try{await navigator.clipboard.writeText(t)}catch(_){const a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove()}
  $('.mmok',d)[0].hidden=false};
 document.body.appendChild(d);$('.btn',d)[0].focus();
}
$('[data-mail]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();mailDialog({})}));
const cf=document.getElementById('cf');if(cf)cf.onsubmit=e=>{e.preventDefault();const f=e.target;
 mailDialog({title:'Your message is ready',lead:'Choose how you would like to send it. The message is already written.',subject:'Portfolio enquiry from '+f.n.value,body:f.b.value+'\n\nFrom: '+f.n.value+' ('+f.m.value+')'})};

document.addEventListener('keydown',e=>{if(e.key==='Escape')$('.mm').forEach(x=>x.remove())});


const tf=document.getElementById('tf');if(tf)tf.onsubmit=e=>{e.preventDefault();const f=e.target;
 mailDialog({title:'Your application email is ready',lead:'Choose how to send it, then attach your CV.',note:'<b>Before you send:</b> attach your CV (required) and, if you like, a work sample. Email links cannot attach files for you.',
  subject:'Consultancy team: '+f.a.value+' ('+f.n.value+')',body:'Hello,\n\nI would like to be considered for your consultancy team.\n\nName: '+f.n.value+'\nEmail: '+f.m.value+'\nMain area: '+f.a.value+'\nWork sample link (optional): '+(f.w.value||'attached or not provided')+'\n\n'+f.b.value+'\n\nCV attached: yes'})};
