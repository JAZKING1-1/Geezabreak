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

  // --- Dynamic Ward Filtering Based on Service Selection ---
  // If ANY of Family Support, Respite Sitting, Respite Care is selected
  // then restrict ward list to: Calton (9), Springburn/Robroyston (17), Shettleston (19),
  // Baillieston (20), North East (21), Dennistoun (22), East Centre (18)
  const SERVICE_FIELD_NAMES = ['srv_family_support','srv_respite_sitting','srv_respite_care'];
  const RESTRICTED_WARD_IDS = [9,17,19,20,21,22,18]; // numeric values from Django choices
  const wardSelect = document.getElementById('id_ward');
  // Try by id first, fallback to name selector (if form prefixing ever added)
  const serviceInputs = SERVICE_FIELD_NAMES.map(name =>
    document.querySelector(`#id_${name}`) || document.querySelector(`input[name="${name}"]`)
  ).filter(Boolean);
  if (!wardSelect) {
    console.warn('[WardFilter] Could not find ward <select> with id_ward');
  }
  if (serviceInputs.length !== SERVICE_FIELD_NAMES.length) {
    console.warn('[WardFilter] Missing some service inputs', SERVICE_FIELD_NAMES, serviceInputs);
  }

  function initWardFilter(){
    if (!(wardSelect && serviceInputs.length)) return;
    // Clone original full option list once
    const fullOptions = Array.from(wardSelect.options).map(o => ({value: o.value, text: o.text}));
    // Create / reuse a hint span for feedback
    let hint = wardSelect.parentElement.querySelector('.dynamic-ward-hint');
    if (!hint) {
      hint = document.createElement('small');
      hint.className = 'hint dynamic-ward-hint';
      wardSelect.parentElement.appendChild(hint);
    }

    function applyWardFilter() {
      const restrict = serviceInputs.some(inp => inp && inp.checked);
      console.log('[WardFilter] applyWardFilter restrict=', restrict);
      // Preserve current selection value
      const current = wardSelect.value;
      // Clear all options
      wardSelect.innerHTML = '';
      let source = fullOptions;
      if (restrict) {
        source = fullOptions.filter(o => RESTRICTED_WARD_IDS.includes(parseInt(o.value)));
        console.log('[WardFilter] Filtering wards. Remaining:', source.map(o=>o.text));
      }
      source.forEach(o => {
        const opt = document.createElement('option');
        opt.value = o.value; opt.textContent = o.text; wardSelect.appendChild(opt);
      });
      // Restore selection if still valid
      if (source.some(o => o.value === current)) {
        wardSelect.value = current;
      } else {
        // If previous choice invalid now, reset
        wardSelect.selectedIndex = 0;
      }
      // Accessible hint text
      if (restrict) {
        hint.textContent = 'Filtered: only wards served by selected service(s) shown.';
      } else {
        hint.textContent = 'Full ward list displayed.';
      }
    }

    // Attach listeners
  serviceInputs.forEach(inp => inp.addEventListener('change', applyWardFilter));
  // Also listen to clicks (some mobile browsers fire click before change)
  serviceInputs.forEach(inp => inp.addEventListener('click', applyWardFilter));
    // Initial run in case of server-side validation returning with selections
    applyWardFilter();
  }
  // Run now & again after short delay (in case form widgets load late)
  initWardFilter();
  setTimeout(initWardFilter, 300);
  setTimeout(initWardFilter, 1000);
});
