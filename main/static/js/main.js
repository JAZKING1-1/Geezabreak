// Core functionality only
document.addEventListener('DOMContentLoaded', () => {
  // Section animations (for .section-animate and .feature-card)
  const observeCards = () => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) entry.target.classList.add('animate');
      });
    }, { threshold: 0.2 });

    document.querySelectorAll('.section-animate, .feature-card').forEach(el => observer.observe(el));
  };

  // Initialize features
  observeCards();

  // Feedback modal functions
  window.openFeedback = function() { const m = document.getElementById('feedbackModal'); if(m) m.style.display = 'block'; }
  window.closeFeedback = function() { const m = document.getElementById('feedbackModal'); if(m) m.style.display = 'none'; }

  // Pointer vs keyboard nav helper
  document.addEventListener('mousedown', () => document.body.classList.remove('keyboard-nav'));

  // Scroll to top button
  const scrollTopBtn = document.createElement('button');
  scrollTopBtn.innerHTML = '↑';
  scrollTopBtn.className = 'scroll-top-btn';
  scrollTopBtn.setAttribute('aria-label', 'Scroll to top');
  document.body.appendChild(scrollTopBtn);
  window.addEventListener('scroll', () => scrollTopBtn.classList.toggle('show', window.scrollY > 300));
  scrollTopBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  // Enhanced keyboard navigation
  let lastKeyPressTime = 0;
  document.addEventListener('keydown', e => {
    const currentTime = Date.now();
    if (currentTime - lastKeyPressTime > 100) {
      if (e.key === 'Tab') document.body.classList.add('keyboard-nav');
      if (e.key === 'Escape') document.body.classList.remove('keyboard-nav');
    }
    lastKeyPressTime = currentTime;
  });

  // Referral form client-side validation
  const form = document.getElementById('referral-form');
  if (form) form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!form.checkValidity()) { alert('Please fill all required fields.'); return; }
    alert('Referral submitted successfully!'); form.reset();
  });

  // Anonymous comment toggle
  const anonBtn = document.getElementById('anonymousBtn');
  const nameInput = document.getElementById('commentName');
  if (anonBtn && nameInput) {
    // Ensure button starts in correct state
    anonBtn.textContent = 'Anonymous';
    anonBtn.classList.remove('active');

    anonBtn.addEventListener('click', () => {
      nameInput.value = '';
      nameInput.placeholder = 'Anonymous';
      nameInput.disabled = true;
      anonBtn.classList.add('active');
      anonBtn.textContent = 'Anonymous ✓';
      // Ensure only one button is visible
      anonBtn.style.display = 'inline-flex';
    });

    nameInput.addEventListener('focus', () => {
      nameInput.disabled = false;
      nameInput.placeholder = 'Your Name';
      anonBtn.classList.remove('active');
      anonBtn.textContent = 'Anonymous';
      // Ensure button remains visible
      anonBtn.style.display = 'inline-flex';
    });

    // Prevent any potential duplication from form resets
    nameInput.addEventListener('input', () => {
      if (nameInput.value.trim() !== '') {
        anonBtn.classList.remove('active');
        anonBtn.textContent = 'Anonymous';
      }
    });
  }

  // Filter games by category
  window.filterGames = function(category) {
    document.querySelectorAll('.game-card').forEach(card => {
      card.style.display = (category === 'all' || card.dataset.category === category) ? 'block' : 'none';
    });
  }

});


/* --- Polaroid Story Wall: random rotations, hover tilt, Swiper re-init, and lightbox --- */
(function(){
  // Apply random rotation to all polaroids and check image dimensions
  document.querySelectorAll('.polaroid').forEach(function(el, idx){
    // More gentle rotation range (-7 to +7 degrees)
    var r = (Math.random()*14) - 7; 
    el.style.setProperty('--rot', r + 'deg');
    // slightly larger tilt on hover for small screens
    el.style.setProperty('--tilt-on-hover', (r>0? r-2 : r+2) + 'deg');
    // small entrance stagger
    el.style.transitionDelay = (idx * 45) + 'ms';
    
    // Check image dimensions and adjust object-fit behavior
    var img = el.querySelector('img');
    if (img) {
      img.onload = function() {
        // If image is much wider than tall, use contain instead of cover
        if (this.naturalWidth > this.naturalHeight * 1.3) {
          this.style.objectFit = 'contain';
        }
        // If image is roughly square or taller than wide
        else if (this.naturalWidth <= this.naturalHeight * 1.1) {
          this.style.objectFit = 'contain';
        }
      };
      // Trigger for already-loaded images
      if (img.complete) img.onload();
    }
  });

  // Re-init Swiper instances used on impact shelves, if Swiper is loaded
  try{
    if(window.Swiper){
      ['#impactRow1', '#impactRow2'].forEach(function(sel, i){
        var el = document.querySelector(sel);
        if(!el) return;
        // destroy existing instance if present
        var key = '_impact' + (i+1);
        if(window[key] && window[key].destroy) { try{ window[key].destroy(true, true); }catch(e){} }
        window[key] = new Swiper(sel + ' .swiper', {
          slidesPerView: 'auto', spaceBetween: 14, freeMode: true, loop: false,
          autoplay: { delay: 2200, disableOnInteraction: false, pauseOnMouseEnter: true },
          speed: 900,
          breakpoints: { 768: { spaceBetween:20 } }
        });
      });
    }
  }catch(e){ console.warn('Swiper re-init failed', e); }

  // Lightbox: open modal when clicking a polaroid
  var modal = document.querySelector('.impact-modal');
  if(!modal){
    modal = document.createElement('div'); modal.className='impact-modal'; modal.setAttribute('hidden','');
    modal.innerHTML = "<div class='impact-modal__backdrop'></div><figure class='impact-modal__content' role='dialog' aria-modal='true'><button class='impact-modal__close' aria-label='Close'>&times;</button><img src='' alt=''><figcaption></figcaption></figure>";
    document.body.appendChild(modal);
  }
  var modalImg = modal.querySelector('img');
  var modalCaption = modal.querySelector('figcaption');
  var closeBtn = modal.querySelector('.impact-modal__close');

  function openModal(src, caption){ modal.removeAttribute('hidden'); modalImg.src = src; modalCaption.textContent = caption || ''; document.body.style.overflow='hidden'; }
  function closeModal(){ modal.setAttribute('hidden',''); modalImg.src=''; modalCaption.textContent=''; document.body.style.overflow=''; }

  closeBtn.addEventListener('click', closeModal);
  modal.querySelector('.impact-modal__backdrop').addEventListener('click', closeModal);
  document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeModal(); });

  document.querySelectorAll('.polaroid').forEach(function(fig){
    var img = fig.querySelector('img');
    var caption = fig.querySelector('figcaption') ? fig.querySelector('figcaption').textContent.trim() : (fig.dataset && fig.dataset.caption) || '';
    fig.style.cursor='zoom-in';
    fig.addEventListener('click', function(){ openModal(img.src, caption); });
  });

});

/* ---------- Our Impact carousel (added) ---------- */
(function(){
  const el = document.getElementById('impactCarousel');
  if(!el) return;

  const slides = [...el.querySelectorAll('.impact-slide')];
  const dotsWrap = document.getElementById('impactDots');
  const dots = slides.map((_, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.addEventListener('click', () => snapTo(i));
    if (dotsWrap) dotsWrap.appendChild(b);
    return b;
  });

  const slideW = () => slides[0]?.getBoundingClientRect().width || 0;
  const gap = parseFloat(getComputedStyle(el).gap) || 0;

  function indexNearCenter(){
    const {left, width} = el.getBoundingClientRect();
    let nearestIdx = 0, min = Infinity;
    slides.forEach((s, i) => {
      const r = s.getBoundingClientRect();
      const centerDist = Math.abs((r.left + r.width/2) - (left + width/2));
      if(centerDist < min){ min = centerDist; nearestIdx = i; }
    });
    return nearestIdx;
  }

  function markCenter(){
    const idx = indexNearCenter();
    slides.forEach((s, i) => s.classList.toggle('is-center', i === idx));
    dots.forEach((d, i) => d.setAttribute('aria-current', i === idx ? 'true' : 'false'));
    current = idx;
  }

  function snapTo(idx, behavior='smooth'){
    const x = idx * (slideW() + gap);
    el.scrollTo({ left: x, behavior });
  }

  let scrollTimer;
  el.addEventListener('scroll', () => {
    markCenter();
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(() => snapTo(indexNearCenter()), 140);
  }, {passive:true});

  let current = 0;
  const btnPrev = document.querySelector('.impact-btn.prev');
  const btnNext = document.querySelector('.impact-btn.next');
  btnPrev?.addEventListener('click', () => snapTo(Math.max(0, current-1)));
  btnNext?.addEventListener('click', () => snapTo(Math.min(slides.length-1, current+1)));
  el.setAttribute('tabindex','0');
  el.addEventListener('keydown', (e) => {
    if(e.key === 'ArrowRight') { e.preventDefault(); snapTo(Math.min(slides.length-1, current+1)); }
    if(e.key === 'ArrowLeft')  { e.preventDefault(); snapTo(Math.max(0, current-1)); }
  });

  let auto = true, autoTimer;
  function startAuto(){ stopAuto(); if(!auto) return; autoTimer = setInterval(() => { const next = (current + 1) % slides.length; snapTo(next); }, 4000); }
  function stopAuto(){ clearInterval(autoTimer); }

  ['mouseenter','focusin','touchstart','pointerdown'].forEach(ev=>{ el.addEventListener(ev, ()=>{ auto=false; stopAuto(); }, {passive:true}); });
  ['mouseleave','focusout'].forEach(ev=>{ el.addEventListener(ev, ()=>{ auto=true; startAuto(); }); });

  window.addEventListener('load', () => { markCenter(); startAuto(); });
  window.addEventListener('resize', () => { setTimeout(()=> snapTo(current, 'auto'), 80); });
})();

/* ---------- Infinite two-row impact wall helper ---------- */
(function(){
  const rows = document.querySelectorAll('.impact-row');
  if(!rows.length) return;

  rows.forEach(row => {
    const track = row.querySelector('.impact-track');
    if(!track) return;

    const slides = Array.from(track.children);
    const clone = slides.map(s => s.cloneNode(true));
    clone.forEach(c => track.appendChild(c));

    const speedPxPerSec = 90;
    const fullWidth = Array.from(track.children).reduce((acc, el) => acc + el.getBoundingClientRect().width, 0);
    const halfWidth = fullWidth / 2;
    const dur = Math.max(20, Math.round(halfWidth / speedPxPerSec));
    track.style.setProperty('--dur', `${dur}s`);

    track.addEventListener('focusin', () => track.style.animationPlayState = 'paused');
    track.addEventListener('focusout', () => track.style.animationPlayState = 'running');
  });
})();

/* Story Wall lane sync & sizing (simple, dependency-free) */
(function(){
  const rows = document.querySelectorAll('.rope-row .track');
  if(!rows || !rows.length) return;

  rows.forEach((track, i) => {
    const speedSec = parseFloat(track.dataset.speed || '32');
    const offset = parseFloat(track.dataset.offset || '0'); // 0..1 start offset

    // set CSS custom property for this instance
    track.style.setProperty('--speed', speedSec + 's');

    // start offset so rows aren't aligned; implemented by animation-delay
    const reverse = track.classList.contains('track--reverse');
    const delay = -(speedSec * offset);
    track.style.animationDelay = (reverse ? delay : -delay) + 's';

    // if content width < container, clone an extra block to ensure seamless fill
    const totalWidth = Array.from(track.children).reduce((w,ul)=>{
      return w + ul.scrollWidth;
    }, 0);
    const container = track.closest('.rope-row');
    if (totalWidth < container.clientWidth * 1.2) {
      const clone = track.children[0].cloneNode(true);
      clone.setAttribute('aria-hidden', 'true');
      track.appendChild(clone);
    }

  });

  // small resize guard to ensure loops always cover
  let t; window.addEventListener('resize', ()=>{ clearTimeout(t); t = setTimeout(()=>{
    document.querySelectorAll('.rope-row .track').forEach(tr=>{
      const container = tr.closest('.rope-row');
      const totalWidth = Array.from(tr.children).reduce((w,ul)=> w + ul.scrollWidth, 0);
      if(totalWidth < container.clientWidth * 1.2){
        const clone = tr.children[0].cloneNode(true); clone.setAttribute('aria-hidden','true'); tr.appendChild(clone);
      }
    });
  }, 120); });
})();

// Swiper initialization for testimonials
var swiper = new Swiper(".mySwiper", {
    slidesPerView: 1,
    spaceBetween: 20,
    loop: true,
    autoplay: { delay: 5000 },
    pagination: { el: ".swiper-pagination", clickable: true },
    navigation: { nextEl: ".swiper-button-next", prevEl: ".swiper-button-prev" },
    breakpoints: {
      768: { slidesPerView: 2 },
      1024: { slidesPerView: 3 }
    }
  });
