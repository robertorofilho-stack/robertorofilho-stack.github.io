/* Dr. Roberto Rodrigues — interações do site
   Movimento com Clareza · sem dependências externas */
(function () {
  "use strict";

  /* ============================================================
     CONFIGURAÇÃO CENTRAL — editar aqui, sem reconstruir páginas
     ============================================================ */
  var CONFIG = {
    // Identificadores de métricas (preencher quando fornecidos; vazios = nada carrega)
    GA4_ID: "",            // ex.: "G-XXXXXXX"
    GOOGLE_ADS_ID: "",     // ex.: "AW-XXXXXXX"
    META_PIXEL_ID: "",     // ex.: "1234567890"

    // Widgets oficiais da Doctoralia (Docplanner).
    // Ao receber os códigos gerados no painel da Doctoralia, cole-os nos campos
    // *_CODE abaixo (HTML completo). Enquanto vazios, o site usa o embed padrão
    // do perfil público + link direto como alternativa.
    DOCTORALIA_DOCTOR_SLUG: "roberto-rodrigues-5",
    DOCTORALIA_URL: "https://www.doctoralia.com.br/roberto-rodrigues-5/ortopedista-traumatologista/fortaleza",
    DOCTORALIA_WIDGET_OPINIOES_CODE: "",
    DOCTORALIA_WIDGET_AGENDAMENTO_CODE: ""
  };

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* modo de captura interna (screenshots de revisão): ?shot=1 esconde elementos fixos */
  if (location.search.indexOf("shot=1") !== -1) document.documentElement.classList.add("shotmode");

  /* ---------------- medição (com consentimento) ---------------- */
  window.dataLayer = window.dataLayer || [];
  function device() { return window.matchMedia("(max-width: 760px)").matches ? "mobile" : "desktop"; }
  function track(evt, pos) {
    var payload = {
      event: evt,
      cta_position: pos || "",
      page_path: location.pathname,
      device: device()
    };
    window.dataLayer.push(payload);
    if (window.fbq && evt.indexOf("click_") === 0) { try { window.fbq("trackCustom", evt, payload); } catch (e) {} }
    if (window.console && console.debug) console.debug("[evt]", payload);
  }
  document.addEventListener("click", function (e) {
    var el = e.target.closest("[data-evt]");
    if (el) track(el.getAttribute("data-evt"), el.getAttribute("data-pos"));
  });

  function loadAnalytics() {
    if (CONFIG.GA4_ID) {
      var s = document.createElement("script");
      s.async = true;
      s.src = "https://www.googletagmanager.com/gtag/js?id=" + CONFIG.GA4_ID;
      document.head.appendChild(s);
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag("js", new Date());
      window.gtag("config", CONFIG.GA4_ID, { anonymize_ip: true });
      if (CONFIG.GOOGLE_ADS_ID) window.gtag("config", CONFIG.GOOGLE_ADS_ID);
    }
    if (CONFIG.META_PIXEL_ID && !window.fbq) {
      !(function (f, b, e, v, n, t, s) {
        if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
        if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = [];
        t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0];
        s.parentNode.insertBefore(t, s);
      })(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
      window.fbq("init", CONFIG.META_PIXEL_ID);
      window.fbq("track", "PageView");
    }
  }

  /* ---------------- consentimento (LGPD) ---------------- */
  var consentBar = document.getElementById("consentBar");
  function getConsent() { try { return localStorage.getItem("rr-consent"); } catch (e) { return null; } }
  function setConsent(v) { try { localStorage.setItem("rr-consent", v); } catch (e) {} }
  var stored = getConsent();
  if (stored === "all") loadAnalytics();
  else if (!stored && consentBar) consentBar.hidden = false;
  document.querySelectorAll(".js-consent").forEach(function (b) {
    b.addEventListener("click", function () {
      var v = b.getAttribute("data-consent");
      setConsent(v);
      if (consentBar) consentBar.hidden = true;
      if (v === "all") loadAnalytics();
    });
  });

  /* ---------------- header: encolhe ao rolar ---------------- */
  var head = document.getElementById("siteHead");
  var lastY = 0;
  function onScroll() {
    var y = window.scrollY;
    if (head) head.classList.toggle("scrolled", y > 24);
    var sticky = document.getElementById("stickyCta");
    if (sticky) sticky.classList.toggle("show", y > 560);
    lastY = y;
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------------- menu mobile ---------------- */
  var burger = document.querySelector(".js-burger");
  if (burger) {
    burger.addEventListener("click", function () {
      var open = document.body.classList.toggle("menu-open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
      burger.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
    });
    document.querySelectorAll(".mainnav a").forEach(function (a) {
      a.addEventListener("click", function () {
        document.body.classList.remove("menu-open");
        burger.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------------- submenu Atendimento ---------------- */
  document.querySelectorAll(".has-sub").forEach(function (li) {
    var t = li.querySelector(".sub-toggle");
    t.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = li.classList.toggle("open");
      t.setAttribute("aria-expanded", open ? "true" : "false");
    });
    if (window.matchMedia("(min-width: 921px)").matches) {
      li.addEventListener("mouseenter", function () { li.classList.add("open"); t.setAttribute("aria-expanded", "true"); });
      li.addEventListener("mouseleave", function () { li.classList.remove("open"); t.setAttribute("aria-expanded", "false"); });
    }
  });
  document.addEventListener("click", function (e) {
    document.querySelectorAll(".has-sub.open").forEach(function (li) {
      if (!li.contains(e.target)) { li.classList.remove("open"); li.querySelector(".sub-toggle").setAttribute("aria-expanded", "false"); }
    });
  });

  /* ---------------- modal de agendamento ---------------- */
  var modal = document.getElementById("modalAgenda");
  var lastFocus = null;
  function openModal() {
    if (!modal) return;
    lastFocus = document.activeElement;
    modal.hidden = false;
    requestAnimationFrame(function () { modal.classList.add("show"); });
    var first = modal.querySelector(".op");
    if (first) first.focus();
    document.body.style.overflow = "hidden";
  }
  function closeModal() {
    if (!modal) return;
    modal.classList.remove("show");
    document.body.style.overflow = "";
    setTimeout(function () { modal.hidden = true; }, reduceMotion ? 0 : 240);
    if (lastFocus) lastFocus.focus();
  }
  document.querySelectorAll(".js-open-modal").forEach(function (b) {
    b.addEventListener("click", openModal);
  });
  if (modal) {
    modal.addEventListener("click", function (e) {
      if (e.target === modal || e.target.closest(".js-close-modal")) closeModal();
      if (e.target.closest(".op")) closeModal();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !modal.hidden) closeModal();
      if (e.key === "Tab" && !modal.hidden) {
        var f = modal.querySelectorAll("a[href], button:not([disabled])");
        if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
        else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
      }
    });
  }

  /* ---------------- revelação suave + Linha do Movimento ---------------- */
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add(en.target.classList.contains("movline") ? "in-view" : "rv-in");
          io.unobserve(en.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    document.querySelectorAll(".rv, .movline").forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll(".rv").forEach(function (el) { el.classList.add("rv-in"); });
    document.querySelectorAll(".movline").forEach(function (el) { el.classList.add("in-view"); });
  }

  /* ---------------- widgets oficiais da Doctoralia ----------------
     Contêineres: #DOCTORALIA_WIDGET_OPINIOES e #DOCTORALIA_WIDGET_AGENDAMENTO.
     1) Se um código do painel foi colado em CONFIG.*_CODE, ele é usado.
     2) Caso contrário, injeta o embed padrão do perfil público (Docplanner).
     3) Se o script externo não renderizar, o cartão-fallback com link permanece. */
  function defaultEmbed(tipo) {
    var a = document.createElement("a");
    a.id = "zl-url";
    a.className = "zl-url";
    a.href = CONFIG.DOCTORALIA_URL;
    a.rel = "nofollow";
    a.setAttribute("data-zlw-doctor", CONFIG.DOCTORALIA_DOCTOR_SLUG);
    a.setAttribute("data-zlw-type", tipo === "agendamento" ? "big_with_calendar" : "certificate");
    a.setAttribute("data-zlw-opinion", tipo === "agendamento" ? "false" : "true");
    a.setAttribute("data-zlw-hide-branding", "false");
    a.textContent = "Roberto Rodrigues — Doctoralia";
    return a;
  }
  var widgets = document.querySelectorAll("[data-doc-widget]");
  if (widgets.length) {
    var needScript = false;
    widgets.forEach(function (w) {
      var tipo = w.getAttribute("data-doc-widget");
      var target = w.querySelector(".doc-embed");
      var custom = tipo === "agendamento" ? CONFIG.DOCTORALIA_WIDGET_AGENDAMENTO_CODE : CONFIG.DOCTORALIA_WIDGET_OPINIOES_CODE;
      if (custom) {
        var tpl = document.createElement("div");
        tpl.innerHTML = custom;
        tpl.querySelectorAll("script").forEach(function (old) {
          var s = document.createElement("script");
          if (old.src) s.src = old.src; else s.textContent = old.textContent;
          old.replaceWith(s);
        });
        while (tpl.firstChild) target.appendChild(tpl.firstChild);
      } else {
        target.appendChild(defaultEmbed(tipo));
        needScript = true;
      }
      function checkRendered() {
        var fr = target.querySelector("iframe");
        if (fr && fr.offsetHeight > 120) { w.classList.add("loaded"); return true; }
        return false;
      }
      var mo = new MutationObserver(function () {
        if (checkRendered()) mo.disconnect();
      });
      mo.observe(target, { childList: true, subtree: true, attributes: true });
      var tries = 0;
      var iv = setInterval(function () {
        tries++;
        if (checkRendered() || tries > 20) clearInterval(iv);
      }, 500);
    });
    if (needScript) {
      var zl = document.createElement("script");
      zl.src = "https://platform.docplanner.com/js/widget.js";
      zl.async = true;
      document.body.appendChild(zl);
    }
  }
})();
