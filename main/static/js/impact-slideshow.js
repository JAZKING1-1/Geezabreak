(() => {
  const root = document.querySelector('.impact-slideshow');
  if (!root) return;

  const slidesWrap = root.querySelector('#impactSlides');
  const slides = Array.from(root.querySelectorAll('.impact-slide'));
  const captionEl = root.querySelector('#impactCaption');
  const dotsWrap = root.querySelector('#impactDots');
  const btnPrev = root.querySelector('.impact-prev');
  const btnNext = root.querySelector('.impact-next');
  const btnPlay = root.querySelector('.impact-play');

  let idx = 0;
  let timer = null;
  const interval = 5000;

  function render() {
    slides.forEach((s,i) => s.classList.toggle('is-active', i === idx));
    const caption = slides[idx]?.dataset.caption || '';
    if (captionEl) captionEl.textContent = caption;
    // update dots
    Array.from(dotsWrap.children).forEach((btn, i) => btn.setAttribute('aria-selected', String(i === idx)));
  }

  function next(n = 1){ idx = (idx + n + slides.length) % slides.length; render(); }
  function prev(){ next(-1); }

  function start(){
    stop();
    timer = setInterval(()=> next(1), interval);
    if (btnPlay) { btnPlay.textContent = '⏸'; btnPlay.setAttribute('data-playing','true'); btnPlay.setAttribute('aria-label','Pause slideshow'); }
  }
  function stop(){ clearInterval(timer); timer = null; if (btnPlay){ btnPlay.textContent = '▶'; btnPlay.setAttribute('data-playing','false'); btnPlay.setAttribute('aria-label','Play slideshow'); } }

  // dots
  slides.forEach((s,i)=>{
    const b=document.createElement('button'); b.type='button'; b.className='impact-dot'; b.setAttribute('aria-selected', 'false'); b.setAttribute('aria-label', `Slide ${i+1}`);
    b.addEventListener('click', ()=>{ idx=i; render(); stop(); });
    dotsWrap.appendChild(b);
  });

  // attach events
  btnNext?.addEventListener('click', ()=>{ next(1); stop(); });
  btnPrev?.addEventListener('click', ()=>{ prev(); stop(); });
  btnPlay?.addEventListener('click', ()=>{ if (timer) stop(); else start(); });

  // keyboard
  root.addEventListener('keydown', (e)=>{
    if (e.key === 'ArrowRight') { next(1); stop(); }
    if (e.key === 'ArrowLeft') { prev(); stop(); }
    if (e.key === ' ' || e.key === 'Spacebar') { e.preventDefault(); if (timer) stop(); else start(); }
  });

  // initialize
  render();
  start();

  // pause on hover
  root.addEventListener('mouseenter', ()=> stop());
  root.addEventListener('mouseleave', ()=> start());
})();
