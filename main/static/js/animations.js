// Intersection Observer for section animations
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('section');
    
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.05  // Lower threshold for mobile devices
    };

    const sectionObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('section-animate', 'visible');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, observerOptions);

    // Add animation class to all sections
    sections.forEach(section => {
        section.classList.add('section-animate');
        sectionObserver.observe(section);
    });

    // Handle reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    function handleReducedMotion() {
        if (prefersReducedMotion.matches) {
            sections.forEach(section => {
                section.classList.remove('section-animate');
                section.classList.add('visible');
            });
        }
    }

    prefersReducedMotion.addEventListener('change', handleReducedMotion);
    handleReducedMotion(); // Check initial preference

    // Fallback: Force visibility for sections that are already in viewport on load
    setTimeout(() => {
        sections.forEach(section => {
            const rect = section.getBoundingClientRect();
            if (rect.top < window.innerHeight && rect.bottom > 0) {
                section.classList.add('visible');
            }
        });
    }, 100);

    // Aggressive fallback: Force all sections visible immediately for extreme zoom levels
    // At zoom levels like 10%+, intersection observer may not work properly
    const forceVisibility = () => {
        sections.forEach(section => {
            section.classList.add('visible');
        });
    };

    // Force visibility immediately if zoom level is extreme (viewport very large)
    if (window.innerWidth > 5000 || window.innerHeight > 5000) {
        forceVisibility();
    }

    // Also force visibility after a very short delay as backup
    setTimeout(forceVisibility, 500);

    // And again after 2 seconds as final fallback
    setTimeout(forceVisibility, 2000);
});
