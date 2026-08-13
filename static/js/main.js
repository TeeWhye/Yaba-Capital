// Mobile nav toggle
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');

if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', isOpen);
  });

  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('open');
    });
  });
}


// Loan calculator
const amountSlider = document.getElementById('amountSlider');
const amountVal = document.getElementById('amountVal');
const repayVal = document.getElementById('repayVal');
const termVal = document.getElementById('termVal');
const planLabel = document.getElementById('planLabel');
const termButtons = document.querySelectorAll('.term-toggle button');

if (
  amountSlider &&
  amountVal &&
  repayVal &&
  termVal &&
  planLabel
) {
  let currentTerm = 'daily';
  const RATE = 0.05; // flat illustrative rate per cycle

  function formatNaira(n) {
    return '₦' + Math.round(n).toLocaleString('en-NG');
  }

  function updateCalc() {
    const amount = Number(amountSlider.value);

    amountVal.textContent = formatNaira(amount);

    const totalRepayable = amount * (1 + RATE);

    if (currentTerm === 'daily') {
      const days = 120;

      repayVal.textContent = formatNaira(totalRepayable / days);
      termVal.textContent = days + ' days';
      planLabel.textContent = 'Est. daily repayment';

    } else {
      const weeks = 16;

      repayVal.textContent = formatNaira(totalRepayable / weeks);
      termVal.textContent = weeks + ' weeks';
      planLabel.textContent = 'Est. weekly repayment';
    }
  }

  amountSlider.addEventListener('input', updateCalc);

  termButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      termButtons.forEach(b => b.classList.remove('active'));

      btn.classList.add('active');

      currentTerm = btn.dataset.term;

      updateCalc();
    });
  });

  updateCalc();
}


// Scroll reveal
const revealEls = document.querySelectorAll('.reveal');

if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  revealEls.forEach(el => io.observe(el));

} else {
  revealEls.forEach(el => el.classList.add('in'));
}