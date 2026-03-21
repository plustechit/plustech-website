// ── NAVBAR SCROLL
const navbar = document.querySelector('.navbar');
const scrollTopBtn = document.getElementById('scrollTop');

window.addEventListener('scroll', () => {
  if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 20);
  if (scrollTopBtn) scrollTopBtn.classList.toggle('show', window.scrollY > 300);
});

if (scrollTopBtn) scrollTopBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

// ── HAMBURGER
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', () => mobileMenu.classList.toggle('open'));
  document.addEventListener('click', e => {
    if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) mobileMenu.classList.remove('open');
  });
}

// ── ACTIVE NAV
(function setActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a, .mobile-menu a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path || (path === '/' && href === '/') || (path !== '/' && href !== '/' && path.startsWith(href))) {
      a.classList.add('active');
    }
  });
})();

// ── TOAST
function showToast(msg, type = 'default') {
  let toast = document.getElementById('toast');
  if (!toast) { toast = document.createElement('div'); toast.id = 'toast'; document.body.appendChild(toast); }
  toast.textContent = msg;
  toast.className = 'show ' + type;
  setTimeout(() => toast.className = '', 3500);
}

// ── FADE IN OBSERVER
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); } });
}, { threshold: 0.1 });
document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

// ── AUTH HELPERS
const Auth = {
  getToken: () => localStorage.getItem('plustech_token'),
  getUser: () => { try { return JSON.parse(localStorage.getItem('plustech_user')); } catch { return null; } },
  setSession: (token, user) => { localStorage.setItem('plustech_token', token); localStorage.setItem('plustech_user', JSON.stringify(user)); },
  clearSession: () => { localStorage.removeItem('plustech_token'); localStorage.removeItem('plustech_user'); },
  isLoggedIn: () => !!localStorage.getItem('plustech_token'),
  logout: () => { Auth.clearSession(); window.location.href = '/login'; }
};

// ── UPDATE NAV BASED ON AUTH
(function updateNavAuth() {
  const loginLink = document.getElementById('navLoginLink');
  const registerLink = document.getElementById('navRegisterLink');
  const dashLink = document.getElementById('navDashLink');
  const logoutBtn = document.getElementById('navLogoutBtn');

  if (Auth.isLoggedIn()) {
    const u = Auth.getUser();
    if (loginLink) loginLink.style.display = 'none';
    if (registerLink) registerLink.style.display = 'none';
    if (dashLink) {
      dashLink.style.display = 'inline-flex';
      dashLink.href = (u && u.role === 'admin') ? '/admin' : '/dashboard';
      dashLink.querySelector('button').textContent = (u && u.role === 'admin') ? 'Admin Panel' : 'Dashboard';
    }
    if (logoutBtn) {
      logoutBtn.style.display = 'inline-flex';
      logoutBtn.addEventListener('click', Auth.logout);
    }
  } else {
    if (dashLink) dashLink.style.display = 'none';
    if (logoutBtn) logoutBtn.style.display = 'none';
  }
})();

// ── API HELPER
async function api(endpoint, options = {}) {
  const token = Auth.getToken();
  const res = await fetch(endpoint, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': 'Bearer ' + token } : {}),
      ...options.headers
    },
    ...options
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Something went wrong');
  return data;
}
