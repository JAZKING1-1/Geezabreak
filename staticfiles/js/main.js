// Navigation style change on scroll
document.addEventListener('DOMContentLoaded', () => {
  const nav = document.querySelector('nav');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  });

  // Smooth scroll for internal links
  document.querySelectorAll('a[href^=\"#\"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Accessibility: show focus outlines only when using keyboard
  document.addEventListener('keydown', e => {
    if (e.key === 'Tab') {
      document.body.classList.add('keyboard-nav');
    }
  });

  document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-nav');
  });

  // Feature card animations using Intersection Observer
  const observeCards = () => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate');
        }
      });
    }, { threshold: 0.2 });

    document.querySelectorAll('.feature-card').forEach(card => {
      observer.observe(card);
    });
  };

  // Scroll to top button
  const scrollTopBtn = document.createElement('button');
  scrollTopBtn.innerHTML = '↑';
  scrollTopBtn.className = 'scroll-top-btn';
  scrollTopBtn.setAttribute('aria-label', 'Scroll to top');
  document.body.appendChild(scrollTopBtn);

  window.addEventListener('scroll', () => {
    scrollTopBtn.classList.toggle('show', window.scrollY > 300);
  });

  scrollTopBtn.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  // Enhanced keyboard navigation
  let lastKeyPressTime = 0;
  document.addEventListener('keydown', e => {
    const currentTime = new Date().getTime();
    if (currentTime - lastKeyPressTime > 100) {
      if (e.key === 'Tab') {
        document.body.classList.add('keyboard-nav');
      } else if (e.key === 'Escape') {
        document.body.classList.remove('keyboard-nav');
      }
    }
    lastKeyPressTime = currentTime;
  });

  // Initialize features
  observeCards();
});
