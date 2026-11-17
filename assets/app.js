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
