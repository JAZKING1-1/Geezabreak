// Apply random slight rotation to each polaroid and caption
document.addEventListener('DOMContentLoaded', function() {
  // Get all polaroids
  const polaroids = document.querySelectorAll('.polaroid');
  
  // Apply random rotation to each
  polaroids.forEach(polaroid => {
    // Generate random rotation between -6 and 6 degrees
    const randomRotation = (Math.random() * 12 - 6).toFixed(1);
    polaroid.style.setProperty('--rot', `${randomRotation}deg`);
    
    // Add subtle swing animation with random delay
    const randomDelay = Math.random() * 5;
    polaroid.style.animation = `polaroid-swing 5s ease-in-out ${randomDelay.toFixed(1)}s infinite alternate`;
    
    // Find figcaption and apply a slightly different rotation for handwritten feel
    const caption = polaroid.querySelector('figcaption');
    if (caption) {
      const captionRotation = (Math.random() * 2 - 1).toFixed(1);
      caption.style.transform = `rotate(${captionRotation}deg)`;
    }
  });
});

// Apply additional swing when user scrolls near the impact wall
window.addEventListener('scroll', function() {
  const impactWall = document.querySelector('.impact-wall');
  if (!impactWall) return;
  
  const rect = impactWall.getBoundingClientRect();
  const isNearViewport = rect.top < window.innerHeight && rect.bottom > 0;
  
  if (isNearViewport) {
    document.querySelectorAll('.polaroid').forEach(polaroid => {
      polaroid.classList.add('swing-active');
      
      // Remove class after animation completes
      setTimeout(() => {
        polaroid.classList.remove('swing-active');
      }, 2000);
    });
  }
});
