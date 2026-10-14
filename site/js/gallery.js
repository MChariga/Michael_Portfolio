/* Gallery lightbox with previous/next, keyboard and swipe. */
(function(){
 const items=()=>$('.gi').filter(g=>!g.closest('.hide'));let i=0,box=null;
 function show(n){const list=items();i=(n+list.length)%list.length;const img=$('img',list[i])[0];
  $('img',box)[0].src=list[i].dataset.full||img.src;$('img',box)[0].alt=img.alt;$('.lbc',box)[0].textContent=img.alt;$('.lbn',box)[0].textContent=(i+1)+' / '+list.length}
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
