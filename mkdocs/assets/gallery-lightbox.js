/* Gallery lightbox – opens a fullscreen video player when a gallery item is
   clicked, with prev/next arrows to cycle widgets and a name overlay.        */
(function () {
  'use strict';

  var items   = [];  // [{src, title}]
  var current = 0;
  var overlay = null;
  var videoEl = null;
  var titleEl = null;
  var indexEl = null;

  /* ── collect gallery data ─────────────────────────────────────────────── */
  function buildItems() {
    items = Array.from(document.querySelectorAll('.gallery-item')).map(function (item) {
      var vid      = item.querySelector('video');
      var titleEl  = item.querySelector('.gallery-title');
      var demoLink = item.querySelector('.gallery-links a');
      return {
        src:   vid      ? vid.src                       : '',
        title: titleEl  ? titleEl.textContent.trim()    : '',
        demo:  demoLink ? demoLink.href                 : null,
      };
    }).filter(function (it) { return it.src; });
  }

  /* ── lightbox open / close / navigate ────────────────────────────────── */
  function open(index) {
    current = ((index % items.length) + items.length) % items.length;
    if (!overlay) createOverlay();
    update();
    overlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    overlay.focus();
  }

  function close() {
    if (!overlay) return;
    overlay.style.display = 'none';
    document.body.style.overflow = '';
    videoEl.pause();
    videoEl.src = '';
  }

  function navigate(dir) {
    current = ((current + dir) % items.length + items.length) % items.length;
    update();
  }

  function update() {
    var item = items[current];
    videoEl.src = item.src;
    videoEl.load();
    videoEl.play().catch(function () {});
    titleEl.textContent = item.title;
    if (item.demo) {
      titleEl.href  = item.demo;
      titleEl.style.pointerEvents = 'auto';
    } else {
      titleEl.removeAttribute('href');
      titleEl.style.pointerEvents = 'none';
    }
    indexEl.textContent = (current + 1) + ' / ' + items.length;
  }

  /* ── build DOM ────────────────────────────────────────────────────────── */
  function createOverlay() {
    overlay = document.createElement('div');
    overlay.className = 'lb-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('tabindex', '-1');

    var backdrop = document.createElement('div');
    backdrop.className = 'lb-backdrop';
    backdrop.addEventListener('click', close);

    var dialog = document.createElement('div');
    dialog.className = 'lb-dialog';

    var closeBtn = document.createElement('button');
    closeBtn.className = 'lb-close';
    closeBtn.setAttribute('aria-label', 'Close');
    closeBtn.innerHTML = '&times;';
    closeBtn.addEventListener('click', close);

    videoEl = document.createElement('video');
    videoEl.className = 'lb-video';
    videoEl.loop       = true;
    videoEl.muted      = true;   // start muted; user can unmute via controls
    videoEl.controls   = true;
    videoEl.playsInline = true;

    var caption = document.createElement('div');
    caption.className = 'lb-caption';

    titleEl = document.createElement('a');
    titleEl.className = 'lb-title';
    titleEl.target    = '_blank';
    titleEl.rel       = 'noopener noreferrer';

    indexEl = document.createElement('span');
    indexEl.className = 'lb-index';

    caption.appendChild(titleEl);
    caption.appendChild(indexEl);

    var prevBtn = document.createElement('button');
    prevBtn.className = 'lb-arrow lb-prev';
    prevBtn.setAttribute('aria-label', 'Previous');
    prevBtn.innerHTML = '&#8592;';
    prevBtn.addEventListener('click', function (e) { e.stopPropagation(); navigate(-1); });

    var nextBtn = document.createElement('button');
    nextBtn.className = 'lb-arrow lb-next';
    nextBtn.setAttribute('aria-label', 'Next');
    nextBtn.innerHTML = '&#8594;';
    nextBtn.addEventListener('click', function (e) { e.stopPropagation(); navigate(1); });

    dialog.appendChild(closeBtn);
    dialog.appendChild(videoEl);
    dialog.appendChild(caption);
    dialog.appendChild(prevBtn);
    dialog.appendChild(nextBtn);

    overlay.appendChild(backdrop);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    overlay.addEventListener('keydown', function (e) {
      if (e.key === 'Escape')      close();
      if (e.key === 'ArrowLeft')   navigate(-1);
      if (e.key === 'ArrowRight')  navigate(1);
    });
  }

  /* ── hook gallery clicks ─────────────────────────────────────────────── */
  function init() {
    buildItems();
    if (!items.length) return;

    Array.from(document.querySelectorAll('.gallery-item')).forEach(function (item, i) {
      var link = item.querySelector('.gallery-img');
      if (!link) return;
      // Replace any previous listener by cloning
      var clone = link.cloneNode(true);
      link.parentNode.replaceChild(clone, link);
      clone.style.cursor = 'zoom-in';
      clone.addEventListener('click', function (e) {
        e.preventDefault();
        open(i);
      });
    });
  }

  /* ── boot ────────────────────────────────────────────────────────────── */
  // MkDocs Material exposes document$ (RxJS) for instant navigation;
  // fall back to DOMContentLoaded for plain MkDocs.
  if (typeof document$ !== 'undefined') {
    document$.subscribe(function () { init(); });
  } else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
