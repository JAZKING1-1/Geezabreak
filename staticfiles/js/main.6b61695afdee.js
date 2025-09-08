// Core functionality only
document.addEventListener('DOMContentLoaded', () => {
  // Section animations
  const observeCards = () => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate');
        }
      });
    }, { threshold: 0.2 });

    document.querySelectorAll('.section-animate').forEach(section => {
      observer.observe(section);
    });
  };

  // Initialize features
  observeCards();

  // Feedback modal functions
  window.openFeedback = function() {
    document.getElementById('feedbackModal').style.display = 'block';
  }

  window.closeFeedback = function() {
    document.getElementById('feedbackModal').style.display = 'none';
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

  // Referral form client-side validation and simulated submission
  const form = document.getElementById('referral-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      // Basic validation
      const valid = form.checkValidity();
      if (!valid) {
        alert("Please fill all required fields.");
        return;
      }
      // Simulate form submission
      alert("Referral submitted successfully!");
      form.reset();
    });
  }

  // Feedback modal functions
  window.openFeedback = function() {
    document.getElementById('feedbackModal').style.display = 'block';
  }

  window.closeFeedback = function() {
    document.getElementById('feedbackModal').style.display = 'none';
  }

  // Anonymous comment button logic
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
    const cards = document.querySelectorAll('.game-card');
    cards.forEach(card => {
      if (category === 'all' || card.dataset.category === category) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  }
});
