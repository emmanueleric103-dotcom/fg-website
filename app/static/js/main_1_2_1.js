document.addEventListener('DOMContentLoaded', () => {
  // Mobile nav
  const toggle = document.getElementById('mobileToggle');
  const navLinks = document.getElementById('navLinks');
  if(toggle && navLinks){
    toggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      toggle.textContent = navLinks.classList.contains('open') ? '✕' : '☰';
    });
  }

  // Reveal on scroll
  const observer = new IntersectionObserver((entries)=>{
    entries.forEach(e=>{
      if(e.isIntersecting) e.target.classList.add('reveal');
    });
  }, {threshold:0.1});
  document.querySelectorAll('.card, .hero-card').forEach(el=>observer.observe(el));

  // Track page view via JS (enhancement, server already tracks)
  try{
    fetch('/api/track', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({path: location.pathname, referrer: document.referrer})});
  }catch(e){}

  // Contact form UX
  const form = document.getElementById('contactForm');
  if(form){
    form.addEventListener('submit', (e)=>{
      const btn = form.querySelector('button[type=submit]');
      if(btn){ btn.disabled=true; btn.textContent='Sending...'; }
    });
  }
});
