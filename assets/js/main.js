/* ============================================
   RIGHT CHOICE LOCKSMITH, Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ---- NAVBAR SCROLL EFFECT ---- */
  const navbar = document.querySelector('.navbar');
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  });

  /* ---- MOBILE MENU ---- */
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  hamburger?.addEventListener('click', () => {
    mobileMenu.classList.toggle('open');
    const spans = hamburger.querySelectorAll('span');
    if (mobileMenu.classList.contains('open')) {
      spans[0].style.transform = 'translateY(7px) rotate(45deg)';
      spans[1].style.opacity = '0';
      spans[2].style.transform = 'translateY(-7px) rotate(-45deg)';
    } else {
      spans[0].style.transform = '';
      spans[1].style.opacity = '';
      spans[2].style.transform = '';
    }
  });

  /* ---- CLOSE MENU ON LINK CLICK ---- */
  function closeMobileMenu() {
    if (!mobileMenu) return;
    mobileMenu.classList.remove('open');
    const spans = hamburger?.querySelectorAll('span') || [];
    spans[0] && (spans[0].style.transform = '');
    spans[1] && (spans[1].style.opacity = '');
    spans[2] && (spans[2].style.transform = '');
  }
  document.querySelectorAll('#mobileMenu a').forEach(a => {
    a.addEventListener('click', closeMobileMenu);
  });

  /* ---- DESKTOP DROPDOWNS ---- */
  document.querySelectorAll('.nav-dropdown').forEach(dd => {
    const btn = dd.querySelector('.nav-drop-btn');
    const panel = dd.querySelector('.nav-drop-panel');
    if (!btn || !panel) return;

    // Click toggle (for touch/keyboard users)
    btn.addEventListener('click', e => {
      e.stopPropagation();
      const isOpen = dd.hasAttribute('data-open');
      // close all
      document.querySelectorAll('.nav-dropdown[data-open]').forEach(d => {
        d.removeAttribute('data-open');
        d.querySelector('.nav-drop-btn')?.setAttribute('aria-expanded', 'false');
      });
      if (!isOpen) {
        dd.setAttribute('data-open', '');
        btn.setAttribute('aria-expanded', 'true');
      }
    });

    // Keyboard: Escape closes
    btn.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        dd.removeAttribute('data-open');
        btn.setAttribute('aria-expanded', 'false');
        btn.focus();
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        dd.setAttribute('data-open', '');
        btn.setAttribute('aria-expanded', 'true');
        panel.querySelector('a')?.focus();
      }
    });

    // Keyboard nav inside panel
    panel.addEventListener('keydown', e => {
      const items = Array.from(panel.querySelectorAll('a'));
      const idx = items.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') { e.preventDefault(); items[idx + 1]?.focus(); }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (idx === 0) btn.focus();
        else items[idx - 1]?.focus();
      }
      if (e.key === 'Escape') {
        dd.removeAttribute('data-open');
        btn.setAttribute('aria-expanded', 'false');
        btn.focus();
      }
    });
  });

  // Outside click closes all dropdowns
  document.addEventListener('click', () => {
    document.querySelectorAll('.nav-dropdown[data-open]').forEach(d => {
      d.removeAttribute('data-open');
      d.querySelector('.nav-drop-btn')?.setAttribute('aria-expanded', 'false');
    });
  });

  /* ---- MOBILE ACCORDIONS ---- */
  document.querySelectorAll('.mob-accord-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const panel = btn.nextElementSibling;
      const isOpen = btn.getAttribute('aria-expanded') === 'true';
      // close sibling accordions
      btn.closest('.mobile-menu')?.querySelectorAll('.mob-accord-btn').forEach(b => {
        b.setAttribute('aria-expanded', 'false');
        b.nextElementSibling?.classList.remove('open');
      });
      if (!isOpen) {
        btn.setAttribute('aria-expanded', 'true');
        panel?.classList.add('open');
      }
    });
  });

  /* ---- SMOOTH SCROLL FOR NAV LINKS ---- */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const offset = 70;
        const top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

  /* ---- COUNTER ANIMATION ---- */
  const counters = document.querySelectorAll('[data-count]');
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.done) {
        entry.target.dataset.done = 'true';
        const target = entry.target.dataset.count;
        const isNum = !isNaN(target);
        if (!isNum) { entry.target.textContent = target; return; }
        const end = parseInt(target);
        const duration = 1600;
        const step = end / (duration / 16);
        let current = 0;
        const suffix = entry.target.dataset.suffix || '';
        const timer = setInterval(() => {
          current = Math.min(current + step, end);
          entry.target.textContent = Math.floor(current) + suffix;
          if (current >= end) clearInterval(timer);
        }, 16);
      }
    });
  }, { threshold: 0.5 });
  counters.forEach(c => counterObserver.observe(c));

  /* ---- SCROLL REVEAL ---- */
  const reveals = document.querySelectorAll('.reveal');
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  reveals.forEach(el => revealObserver.observe(el));


});
