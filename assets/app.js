(function(){
  // Menu des rubriques
  var b=document.querySelector('.menu-btn'), m=document.getElementById('menu');
  if(b&&m){
    b.addEventListener('click',function(){var o=m.hasAttribute('hidden');if(o)m.removeAttribute('hidden');else m.setAttribute('hidden','');b.setAttribute('aria-expanded',o?'true':'false');});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!m.hasAttribute('hidden')){m.setAttribute('hidden','');b.setAttribute('aria-expanded','false');b.focus();}});
  }
  // Cases à cocher mémorisées sur l'appareil
  var P='adg-kit:';
  function get(k){try{return localStorage.getItem(P+k)==='1'}catch(e){return false}}
  function set(k,v){try{v?localStorage.setItem(P+k,'1'):localStorage.removeItem(P+k)}catch(e){}}
  document.querySelectorAll('.checks input[data-k]').forEach(function(c){
    c.checked=get(c.dataset.k);
    c.addEventListener('change',function(){set(c.dataset.k,c.checked)});
  });
  // Sommaire : rubrique visible en surbrillance
  var links=[].slice.call(document.querySelectorAll('.toc a'));
  if(links.length&&'IntersectionObserver' in window){
    var map={};links.forEach(function(a){map[a.getAttribute('href').slice(1)]=a});
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){links.forEach(function(a){a.classList.remove('on')});var a=map[e.target.id];if(a)a.classList.add('on');}})},{rootMargin:'-30% 0px -60% 0px'});
    document.querySelectorAll('.post[id]').forEach(function(p){io.observe(p)});
  }
})();
(function(){
  // Recherche par mots-clés (petite boîte dans la barre du haut)
  var panel=document.getElementById('search');
  if(!panel||!window.ADG_IDX) return;
  var wrap=panel.parentNode, q=wrap.querySelector('.search-q'), res=panel.querySelector('.search-res');
  function norm(s){return (s||'').normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[’']/g,"'");}
  var IDX=window.ADG_IDX.map(function(e){return {e:e,p:norm(e.p),k:norm(e.k),s:norm(e.s),t:norm(e.t)}});
  function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function show(){panel.removeAttribute('hidden')}
  function hide(){panel.setAttribute('hidden','')}
  function snippet(text,terms){
    var n='',map=[];
    for(var i=0;i<text.length;i++){var c=norm(text[i]);for(var j=0;j<c.length;j++){n+=c[j];map.push(i);}}
    var first=-1;terms.forEach(function(t){var p=n.indexOf(t);if(p>=0&&(first<0||p<first))first=p});
    var start=0,end=Math.min(text.length,120);
    if(first>=0){var o=map[first];start=Math.max(0,o-45);end=Math.min(text.length,o+75);}
    var hits=[];terms.forEach(function(t){var p=0;while((p=n.indexOf(t,p))>=0){hits.push([map[p],map[p+t.length-1]+1]);p+=t.length;}});
    hits.sort(function(a,b){return a[0]-b[0]});
    var out='',cur=start;
    hits.forEach(function(h){if(h[0]<cur||h[0]>=end)return;out+=esc(text.slice(cur,h[0]))+'<mark>'+esc(text.slice(h[0],Math.min(h[1],end)))+'</mark>';cur=Math.min(h[1],end);});
    out+=esc(text.slice(cur,end));
    return (start>0?'… ':'')+out+(end<text.length?' …':'');
  }
  function run(){
    var terms=norm(q.value.trim()).split(/[\s,;:.!?()«»"]+/).filter(function(t){return t.length>1}).map(function(t){return t.length>3?t.replace(/(s|x)$/,''):t});
    if(!terms.length){res.innerHTML='';hide();return;}
    var out=[];
    IDX.forEach(function(x){
      var score=0,ok=true;
      terms.forEach(function(t){
        var s=0;
        if(x.p.indexOf(t)>=0)s+=8;
        if(x.k.indexOf(t)>=0)s+=5;
        if(x.s.indexOf(t)>=0)s+=2;
        s+=Math.min(x.t.split(t).length-1,5);
        if(!s)ok=false; score+=s;
      });
      if(ok)out.push([score,x]);
    });
    out.sort(function(a,b){return b[0]-a[0]});
    res.innerHTML=out.length?out.slice(0,12).map(function(r){var e=r[1].e;
      return '<li><a href="'+e.u+'"><span class="r-s">'+esc(e.s)+'</span><span class="r-p">'+esc(e.p)+'</span><span class="r-t">'+snippet(e.t,terms)+'</span></a></li>';}).join('')
      :'<li class="none">'+esc((window.ADG_UI||{}).none||'')+'</li>';
    show();
  }
  var timer;q.addEventListener('input',function(){clearTimeout(timer);timer=setTimeout(run,120)});
  q.addEventListener('focus',function(){if(q.value.trim())run()});
  q.addEventListener('keydown',function(e){
    if(e.key==='Enter'){var a=res.querySelector('a');if(a)a.click();}
    if(e.key==='Escape'){q.value='';hide();q.blur();}
  });
  document.addEventListener('click',function(e){if(!wrap.contains(e.target))hide();});
  res.addEventListener('click',function(e){if(e.target.closest('a')){hide();q.blur();}});
})();
(function(){
  // Dates clés : calcul à partir de la date du mariage, fichier .ics avec rappels, liens Google et Outlook.com
  var box=document.getElementById('agenda'), C=window.ADG_CAL;
  if(!box||!C) return;
  var inp=box.querySelector('.cal-date'), out=box.querySelector('.cal-out'), list=box.querySelector('.cal-list'), ics=box.querySelector('.cal-ics');
  var KEY='adg-kit:date-mariage', url=null;
  function pad(n){return (n<10?'0':'')+n}
  function ymd(d){return d.getFullYear()+pad(d.getMonth()+1)+pad(d.getDate())}
  function iso(d){return d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate())}
  function add(w,o){var d=new Date(w.getFullYear(),w.getMonth(),w.getDate());
    if(o[0]==='m'){var day=d.getDate();d.setDate(1);d.setMonth(d.getMonth()+o[1]);var last=new Date(d.getFullYear(),d.getMonth()+1,0).getDate();d.setDate(Math.min(day,last));}
    else d.setDate(d.getDate()+o[1]);
    return d;}
  function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function icsText(s){return s.replace(/\\/g,'\\\\').replace(/;/g,'\;').replace(/,/g,'\\,').replace(/\n/g,'\\n')}
  function fold(line){var o='',b=0;while(line.length>60){o+=line.slice(0,60)+'\r\n ';line=line.slice(60);}return o+line;}
  function render(){
    var v=inp.value; if(!v){out.hidden=true;return;}
    try{localStorage.setItem(KEY,v)}catch(e){}
    var p=v.split('-'), w=new Date(+p[0],+p[1]-1,+p[2]), today=new Date(); today.setHours(0,0,0,0);
    var fmt=new Intl.DateTimeFormat(C.lang,{weekday:'long',day:'numeric',month:'long',year:'numeric'});
    var L=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Auberge des Gallant//Kit mariage//FR','CALSCALE:GREGORIAN','METHOD:PUBLISH'];
    var stamp=new Date().toISOString().replace(/[-:]/g,'').replace(/\.\d+/,'');
    var html='', ov={}, OK='adg-kit:cal-ov:'+v;
    try{ov=JSON.parse(localStorage.getItem(OK)||'{}')}catch(e){}
    var soon=new Date(today); soon.setDate(soon.getDate()+7);
    C.items.forEach(function(it,i){
      var d0=add(w,it.o), past=d0<today, d=d0;
      if(past){var q=(ov[i]||'').split('-'); d=q.length===3?new Date(+q[0],+q[1]-1,+q[2]):new Date(soon);}
      var e=new Date(d); e.setDate(e.getDate()+1);
      var g='https://calendar.google.com/calendar/render?action=TEMPLATE&text='+encodeURIComponent(it.t)+'&dates='+ymd(d)+'/'+ymd(e)+'&details='+encodeURIComponent(it.d)+'&location='+encodeURIComponent('Auberge des Gallant');
      var o='https://outlook.live.com/calendar/0/action/compose?subject='+encodeURIComponent(it.t)+'&startdt='+iso(d)+'&enddt='+iso(e)+'&allday=true&body='+encodeURIComponent(it.d)+'&location='+encodeURIComponent('Auberge des Gallant');
      var head=past?'<span class="cl-d cl-late">'+esc(C.ui.past)+'<label>'+esc(C.ui.own)+' <input type="date" class="cl-own" data-i="'+i+'" value="'+iso(d)+'"></label></span>'
                    :'<span class="cl-d">'+esc(fmt.format(d))+'</span>';
      html+='<li'+(past?' class="past"':'')+'>'+head+'<span class="cl-t">'+esc(it.t)+'</span><span class="cl-x">'+esc(it.d)+'</span>'+
        '<span class="cl-b"><a href="'+g+'" target="_blank" rel="noopener">'+esc(C.ui.g)+'</a><a href="'+o+'" target="_blank" rel="noopener">'+esc(C.ui.o)+'</a></span></li>';
      L.push('BEGIN:VEVENT','UID:adg-'+v+'-'+i+'@kitmariageadg','DTSTAMP:'+stamp,'DTSTART;VALUE=DATE:'+ymd(d),'DTEND;VALUE=DATE:'+ymd(e),
        fold('SUMMARY:'+icsText(it.t)),fold('DESCRIPTION:'+icsText(it.d)),'LOCATION:Auberge des Gallant','TRANSP:TRANSPARENT',
        'BEGIN:VALARM','ACTION:DISPLAY',fold('DESCRIPTION:'+icsText(it.t)),'TRIGGER:-P6DT15H','END:VALARM',
        'BEGIN:VALARM','ACTION:DISPLAY',fold('DESCRIPTION:'+icsText(it.t)),'TRIGGER:-PT15H','END:VALARM','END:VEVENT');
    });
    L.push('END:VCALENDAR');
    list.innerHTML=html;
    list.querySelectorAll('.cl-own').forEach(function(x){x.addEventListener('change',function(){
      if(!x.value)return; ov[x.dataset.i]=x.value; try{localStorage.setItem(OK,JSON.stringify(ov))}catch(e){} render();});});
    if(url) URL.revokeObjectURL(url);
    url=URL.createObjectURL(new Blob([L.join('\r\n')+'\r\n'],{type:'text/calendar;charset=utf-8'}));
    ics.href=url;
    out.hidden=false;
  }
  try{var s=localStorage.getItem(KEY);if(s)inp.value=s}catch(e){}
  inp.addEventListener('change',render); inp.addEventListener('input',render);
  ics.addEventListener('click',function(e){if(ics.getAttribute('href')==='#')e.preventDefault()});
  render();
})();
