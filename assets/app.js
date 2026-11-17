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
