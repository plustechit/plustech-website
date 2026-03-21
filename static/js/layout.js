// Shared navbar HTML injected into every page
function injectNavbar() {
  const nav = document.createElement('nav');
  nav.className = 'navbar';
  nav.innerHTML = `
    <a href="/" class="nav-logo">
      <span class="logo-plus">Plus</span><span class="logo-tech">tech</span>
      <span class="logo-badge">INSTITUTE</span>
    </a>
    <ul class="nav-links">
      <li><a href="/">Home</a></li>
      <li><a href="/courses">Courses</a></li>
      <li><a href="/about">About Us</a></li>
      <li><a href="/blog">Blog</a></li>
      <li><a href="/contact">Contact</a></li>
    </ul>
    <div class="nav-cta">
      <a href="/login" id="navLoginLink"><button class="btn-outline-nav">Login</button></a>
      <a href="/register" id="navRegisterLink"><button class="btn-primary-nav">Get Started</button></a>
      <a href="/dashboard" id="navDashLink" style="display:none"><button class="btn-outline-nav">Dashboard</button></a>
      <button class="btn-primary-nav" id="navLogoutBtn" style="display:none">Logout</button>
    </div>
    <button class="hamburger" id="hamburger" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  `;
  document.body.prepend(nav);

  const mobileMenu = document.createElement('div');
  mobileMenu.className = 'mobile-menu';
  mobileMenu.id = 'mobileMenu';
  mobileMenu.innerHTML = `
    <a href="/">Home</a>
    <a href="/courses">Courses</a>
    <a href="/about">About Us</a>
    <a href="/blog">Blog</a>
    <a href="/contact">Contact</a>
    <a href="/login">Login</a>
    <a href="/register">Register</a>
  `;
  document.body.insertBefore(mobileMenu, document.body.children[1]);
}
injectNavbar();

function injectFooter() {
  const footer = document.createElement('footer');
  footer.innerHTML = `
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <div class="nav-logo" style="margin-bottom:1rem">
            <span class="logo-plus">Plus</span><span class="logo-tech">tech</span>
            <span class="logo-badge">INSTITUTE</span>
          </div>
          <p class="footer-desc">Empowering students with industry-ready skills through expert-led online and offline programming & professional courses in Dombivli, Maharashtra.</p>
        </div>
        <div>
          <p class="footer-heading">Quick Links</p>
          <ul class="footer-links">
            <li><a href="/">Home</a></li>
            <li><a href="/courses">Courses</a></li>
            <li><a href="/about">About Us</a></li>
            <li><a href="/blog">Blog</a></li>
            <li><a href="/contact">Contact</a></li>
          </ul>
        </div>
        <div>
          <p class="footer-heading">Popular Courses</p>
          <ul class="footer-links">
            <li><a href="/courses">Python Programming</a></li>
            <li><a href="/courses">Web Development</a></li>
            <li><a href="/courses">Fullstack Developer</a></li>
            <li><a href="/courses">Tally Prime</a></li>
            <li><a href="/courses">Digital Marketing</a></li>
          </ul>
        </div>
        <div>
          <p class="footer-heading">Contact</p>
          <ul class="footer-links">
            <li><a href="tel:+919136819666">📞 +91 91368 19666</a></li>
            <li><a href="mailto:info@plustech.in">✉️ info@plustech.in</a></li>
            <li><a href="/contact">📍 203, Ananddeep CHS, Near Madhuban Cinema, Dombivli East</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© 2025 Plustech Institute. All rights reserved.</span>
        <span>Made with ❤️ for TYBSCIT Project</span>
      </div>
    </div>
  `;
  document.body.appendChild(footer);
  const scrollBtn = document.createElement('button');
  scrollBtn.id = 'scrollTop';
  scrollBtn.innerHTML = '↑';
  scrollBtn.title = 'Back to top';
  document.body.appendChild(scrollBtn);
}
injectFooter();
