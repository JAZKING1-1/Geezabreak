// Dynamic Referral Form functionality

document.addEventListener('DOMContentLoaded', function() {
  console.log('[ReferralDynamic v3] script loaded');
  // Add scroll to top button
  const scrollTopBtn = document.createElement('button');
  scrollTopBtn.classList.add('scroll-top-btn');
  scrollTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
  scrollTopBtn.setAttribute('aria-label', 'Scroll to top');
  document.body.appendChild(scrollTopBtn);

  // Add progress bar
  const progressBar = document.createElement('div');
  progressBar.classList.add('form-progress');
  document.body.appendChild(progressBar);

  // Show/hide scroll to top button based on scroll position
  window.addEventListener('scroll', function() {
    const scrollPosition = window.scrollY;
    const pageHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercentage = (scrollPosition / pageHeight) * 100;
    
    // Update progress bar
    progressBar.style.width = scrollPercentage + '%';
    
    // Show/hide scroll button
    if (scrollPosition > 300) {
      scrollTopBtn.classList.add('visible');
    } else {
      scrollTopBtn.classList.remove('visible');
    }
  });

  // Scroll to top when button is clicked
  scrollTopBtn.addEventListener('click', function() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  // (Temporarily disabled focus highlight to avoid null .closest errors on elements without wrapper)

  // Make form sections collapsible on mobile
  const cardHeaders = document.querySelectorAll('.card__head');
  const isMobile = window.innerWidth < 768;
  
  if (isMobile) {
    cardHeaders.forEach(header => {
      header.style.cursor = 'pointer';
      
      // Add toggle indicator
      const indicator = document.createElement('span');
      indicator.innerHTML = '<i class="fas fa-chevron-down"></i>';
      indicator.style.marginLeft = 'auto';
      indicator.style.transition = 'transform 0.3s ease';
      header.appendChild(indicator);
      
      header.addEventListener('click', function() {
        const content = this.nextElementSibling;
        const isOpen = content.style.display !== 'none';
        
        if (isOpen) {
          content.style.display = 'none';
          indicator.style.transform = 'rotate(0deg)';
        } else {
          content.style.display = 'block';
          indicator.style.transform = 'rotate(180deg)';
        }
      });
    });
  }

  // Add smooth scroll for error links
  const errorLinks = document.querySelectorAll('.error-summary a');
  errorLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href').substring(1);
      const targetElement = document.getElementById(targetId);
      
      if (targetElement) {
        // Scroll to the element with offset for sticky header
        window.scrollTo({
          top: targetElement.getBoundingClientRect().top + window.pageYOffset - 150,
          behavior: 'smooth'
        });
        
        // Focus the element
        targetElement.focus();
      }
    });
  });

  // Ward filtering removed to keep full ward list available across all localities.
});
