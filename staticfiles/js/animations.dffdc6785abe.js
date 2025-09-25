// Intersection Observer for section animations
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('section');
    
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
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
});
