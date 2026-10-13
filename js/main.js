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
 <div class="btns"><a class="btn" target="_blank" rel="noopener" href="${gm}">Open in Gmail</a><a class="btn o" href="${mt}">Open email app</a><button type="button" class="btn o" data-copy>${bd?'Copy message':'Copy address'}</button></div><p class="small mmok" hidden>Copied to clipboard</p></div>`;
 const close=()=>d.remove();d.onclick=e=>{if(e.target===d)close()};$('.mmx',d)[0].onclick=close;
 $('[data-copy]',d)[0].onclick=async()=>{const t=bd?`To: ${to}\nSubject: ${su}\n\n${bd}`:to;
  try{await navigator.clipboard.writeText(t)}catch(_){const a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove()}
  $('.mmok',d)[0].hidden=false};
 document.body.appendChild(d);$('.btn',d)[0].focus();
}
$('[data-mail]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();mailDialog({})}));
const cf=document.getElementById('cf');if(cf)cf.onsubmit=e=>{e.preventDefault();const f=e.target;
 mailDialog({title:'Your message is ready',lead:'Choose how you would like to send it. The message is already written.',subject:'Portfolio enquiry from '+f.n.value,body:f.b.value+'\n\nFrom: '+f.n.value+' ('+f.m.value+')'})};

/* Gallery lightbox with previous/next, keyboard and swipe. */
(function(){
 const items=()=>$('.gi').filter(g=>!g.closest('.hide'));let i=0,box=null;
 function show(n){const list=items();i=(n+list.length)%list.length;const img=$('img',list[i])[0];
  $('img',box)[0].src=img.src;$('img',box)[0].alt=img.alt;$('.lbc',box)[0].textContent=img.alt;$('.lbn',box)[0].textContent=(i+1)+' / '+list.length}
 function open(n){box=document.createElement('div');box.className='lb';
  box.innerHTML='<button class="lbx" aria-label="Close">&times;</button><button class="lbp" aria-label="Previous">&lsaquo;</button><button class="lbq" aria-label="Next">&rsaquo;</button><figure><img alt=""><figcaption><span class="lbc"></span><span class="lbn"></span></figcaption></figure>';
  document.body.appendChild(box);document.body.style.overflow='hidden';
  const close=()=>{box.remove();box=null;document.body.style.overflow=''};
  box.onclick=e=>{if(e.target===box)close()};$('.lbx',box)[0].onclick=close;$('.lbp',box)[0].onclick=()=>show(i-1);$('.lbq',box)[0].onclick=()=>show(i+1);
  let x0=null;box.ontouchstart=e=>x0=e.touches[0].clientX;box.ontouchend=e=>{if(x0===null)return;const dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>50)show(i+(dx<0?1:-1));x0=null};
  box.close=close;show(n)}
 $('.gi').forEach(g=>{const go=()=>open(items().indexOf(g));g.onclick=go;g.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go()}}});
 document.addEventListener('keydown',e=>{if(!box)return;if(e.key==='Escape')box.close();if(e.key==='ArrowLeft')show(i-1);if(e.key==='ArrowRight')show(i+1)});
})();
document.addEventListener('keydown',e=>{if(e.key==='Escape')$('.mm').forEach(x=>x.remove())});

/* Booking calendar. Times are defined in East Africa Time (UTC+3, no daylight saving). Durations are in minutes. */
(function(){
 const grid=document.getElementById('days');if(!grid||typeof BOOK==='undefined')return;
 const EAT=3,MS=36e5,pad=n=>String(n).padStart(2,'0');
 const t0=new Date(Date.now()+EAT*MS),today={y:t0.getUTCFullYear(),m:t0.getUTCMonth(),d:t0.getUTCDate()};
 const limit=Date.UTC(today.y,today.m,today.d)+BOOK.weeks_ahead*7*864e5;
 let view={y:today.y,m:today.m},selDay=null,selMin=null,dur=BOOK.default_duration||BOOK.durations[0];
 const instant=(y,m,d,min)=>new Date(Date.UTC(y,m,d,0,min)-EAT*MS);
 const fmt=min=>pad(Math.floor(min/60))+':'+pad(min%60);
 const fmtDur=n=>n<60?n+' minutes':(n===60?'1 hour':(n/60)+' hours');
 const local=new Intl.DateTimeFormat([],{hour:'2-digit',minute:'2-digit'});
 const longDate=new Intl.DateTimeFormat('en-GB',{weekday:'long',day:'numeric',month:'long',year:'numeric',timeZone:'UTC'});
 document.getElementById('tzl').textContent=BOOK.tzlabel;
 const starts=()=>{const step=dur<=30?15:30,a=[];for(let m=BOOK.start*60;m+dur<=BOOK.end*60;m+=step)a.push(m);return a};
 const ok=(y,m,d,min)=>instant(y,m,d,min).getTime()>=Date.now()+BOOK.notice_hours*MS;
 const open=(y,m,d)=>BOOK.days.includes(new Date(Date.UTC(y,m,d)).getUTCDay())&&Date.UTC(y,m,d)<=limit&&starts().some(min=>ok(y,m,d,min));
 function draw(){
  document.getElementById('mt').textContent=new Date(Date.UTC(view.y,view.m,1)).toLocaleString('en-GB',{month:'long',year:'numeric',timeZone:'UTC'});
  document.getElementById('pm').disabled=(view.y===today.y&&view.m===today.m);
  const first=(new Date(Date.UTC(view.y,view.m,1)).getUTCDay()+6)%7,n=new Date(Date.UTC(view.y,view.m+1,0)).getUTCDate();
  let h='';for(let i=0;i<first;i++)h+='<span></span>';
  for(let d=1;d<=n;d++){const o=open(view.y,view.m,d),sel=selDay&&selDay.y===view.y&&selDay.m===view.m&&selDay.d===d;
   h+=`<button type="button" data-d="${d}" class="${o?'ok':''} ${sel?'sel':''}" ${o?'':'disabled'}>${d}</button>`}
  grid.innerHTML=h;$('button[data-d]',grid).forEach(b=>b.onclick=()=>{selDay={y:view.y,m:view.m,d:+b.dataset.d};selMin=null;document.getElementById('bf').hidden=true;draw();slots()});
 }
 function slots(){
  const box=document.getElementById('sl'),title=document.getElementById('sd');
  const lenSel=`<label class="small">Length of call<select id="dur">${BOOK.durations.map(x=>`<option value="${x}" ${x===dur?'selected':''}>${fmtDur(x)}</option>`).join('')}</select></label>`;
  if(!selDay){box.innerHTML=lenSel+'<p class="small">Pick a day on the calendar to see open times.</p>';bind();return}
  title.textContent=longDate.format(new Date(Date.UTC(selDay.y,selDay.m,selDay.d)));
  const list=starts().filter(min=>ok(selDay.y,selDay.m,selDay.d,min));
  box.innerHTML=lenSel+'<div class="slist">'+list.map(min=>`<button type="button" data-h="${min}" class="${min===selMin?'sel':''}"><span>${fmt(min)} to ${fmt(min+dur)}</span><small>${local.format(instant(selDay.y,selDay.m,selDay.d,min))} your time</small></button>`).join('')+'</div>';
  $('button[data-h]',box).forEach(b=>b.onclick=()=>{selMin=+b.dataset.h;slots();const bf=document.getElementById('bf');bf.hidden=false;summary();bf.scrollIntoView({behavior:'smooth',block:'nearest'})});
  bind();
 }
 function bind(){const s=document.getElementById('dur');if(s)s.onchange=()=>{dur=+s.value;selMin=null;document.getElementById('bf').hidden=true;draw();slots()}}
 function summary(){
  if(selMin===null)return'';const when=longDate.format(new Date(Date.UTC(selDay.y,selDay.m,selDay.d)))+', '+fmt(selMin)+' to '+fmt(selMin+dur)+' EAT';
  document.getElementById('sum').innerHTML=`<b>${when}</b><br>${fmtDur(dur)}`;return when}
 document.getElementById('top').innerHTML=BOOK.topics.map(t=>`<option>${t}</option>`).join('');
 document.getElementById('pm').onclick=()=>{view.m--;if(view.m<0){view.m=11;view.y--}draw()};
 document.getElementById('nm').onclick=()=>{view.m++;if(view.m>11){view.m=0;view.y++}draw()};
 document.getElementById('bf').onsubmit=async ev=>{ev.preventDefault();const f=ev.target,when=summary();
  const text=`Call request\n\nWhen: ${when}\nLength: ${fmtDur(dur)}\nAbout: ${f.t.value}\nName: ${f.n.value}\nEmail: ${f.m.value}\n\n${f.b.value}`;
  if(BOOK.endpoint){try{const r=await fetch(BOOK.endpoint,{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({name:f.n.value,email:f.m.value,message:text})});
    if(r.ok){f.innerHTML='<h3>Request sent</h3><p>Thank you. I will reply by email to confirm the time.</p>';return}}catch(_){}}
  mailDialog({title:'Your request is ready',lead:'Choose how you would like to send it. The message is already written.',subject:'Call request: '+when,body:text})};
 if(BOOK.calcom){document.getElementById('cal-embed').innerHTML=`<iframe src="${BOOK.calcom}" title="Booking calendar" style="width:100%;height:720px;border:0;margin-top:26px;border-radius:12px"></iframe>`}
 draw();slots();
})();
