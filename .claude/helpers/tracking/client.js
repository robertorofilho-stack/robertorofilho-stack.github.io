// Snippet de navegador. Pixel + servidor com o MESMO event_id => Meta deduplica (janela 48h).
// Pré-requisito: o snippet padrão do fbq já carregado e fbq('init', PIXEL_ID) executado.
(function () {
  var ENDPOINT = 'https://track.SEUDOMINIO.com/event'; // Worker
  var KEY = 'rr_ext_id', FBC = 'rr_fbc';
  function rid() { return (crypto.randomUUID && crypto.randomUUID()) || String(Date.now()) + Math.random(); }
  function cookie(n) { var m = document.cookie.match('(^|;)\\s*' + n + '=([^;]+)'); return m ? m[2] : undefined; }
  // Persistência tripla: cookie + localStorage (+ banco/e-mail no servidor). Guarda fbclid -> fbc.
  var fbclid = new URLSearchParams(location.search).get('fbclid');
  if (fbclid) { try { localStorage.setItem(FBC, 'fb.1.' + Date.now() + '.' + fbclid); } catch (e) {} }
  var ext; try { ext = localStorage.getItem(KEY) || (localStorage.setItem(KEY, rid()), localStorage.getItem(KEY)); } catch (e) { ext = rid(); }

  window.track = function (name, custom, user) {
    var eventId = rid();
    if (window.fbq) fbq('track', name, custom || {}, { eventID: eventId });
    var u = Object.assign({ external_id: ext, fbp: cookie('_fbp'), fbc: cookie('_fbc') || (function () { try { return localStorage.getItem(FBC) || undefined; } catch (e) {} })() }, user || {});
    return fetch(ENDPOINT, { method: 'POST', keepalive: true, headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ name: name, eventId: eventId, url: location.href, custom: custom, user: u }) });
  };
})();
