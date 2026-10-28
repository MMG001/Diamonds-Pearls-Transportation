(function () {
  var t = document.querySelector('.menu-toggle'), n = document.getElementById('site-nav');
  if (t && n) t.addEventListener('click', function () {
    var o = t.getAttribute('aria-expanded') === 'true';
    t.setAttribute('aria-expanded', String(!o)); n.classList.toggle('open', !o);
  });
  var f = document.querySelector('.quote-form');
  if (!f) return;
  var s = f.querySelector('.form-status'), d = f.querySelector('input[type=date]');
  if (d) d.min = new Date().toISOString().slice(0, 10);
  f.addEventListener('submit', function (ev) {
    ev.preventDefault();
    if (!f.checkValidity()) { f.reportValidity(); s.textContent = 'Please complete the required fields.'; return; }
    if (f.company_website.value) return;
    var url = f.getAttribute('data-endpoint');
    if (!url) { s.textContent = 'Thank you! Online booking opens soon. Our phone line and email are coming soon as well.'; return; }
    s.textContent = 'Sending…';
    fetch(url, { method: 'POST', body: new FormData(f), headers: { Accept: 'application/json' } })
      .then(function (r) { if (!r.ok) throw 0; f.reset(); s.textContent = 'Thank you! Your request was received. We will be in touch shortly.'; })
      .catch(function () { s.textContent = 'Sorry, something went wrong. Please try again.'; });
  });
})();
