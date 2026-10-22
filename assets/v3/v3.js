/* TEMA V3 — interações (Diretor de Site, 21/10/2026). Sem dependência; o 3D carrega sob demanda. */
(function () {
  "use strict";
  var reduz = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fino = window.matchMedia("(pointer: fine)").matches;

  // título do hero: palavra por palavra
  document.querySelectorAll("[data-palavras]").forEach(function (h) {
    h.innerHTML = h.textContent.trim().split(/\s+/).map(function (w, i) {
      return '<span class="p" style="transition-delay:' + (i * 70) + 'ms">' + w + "</span>";
    }).join(" ");
    requestAnimationFrame(function () { requestAnimationFrame(function () { h.classList.add("on"); }); });
  });

  // luz que segue o cursor + leve inclinação da foto (só mouse)
  var hero = document.querySelector(".v3-hero"), foto = document.querySelector(".v3-hero-foto");
  if (hero && fino && !reduz) {
    hero.addEventListener("pointermove", function (e) {
      var r = hero.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      hero.style.setProperty("--mx", (x * 100).toFixed(1) + "%");
      hero.style.setProperty("--my", (y * 100).toFixed(1) + "%");
      if (foto) { foto.style.setProperty("--ry", ((x - .5) * 6).toFixed(2) + "deg"); foto.style.setProperty("--rx", ((.5 - y) * 4).toFixed(2) + "deg"); }
    });
  }

  // brilho que acompanha o cursor nos cards
  document.querySelectorAll(".v3-card").forEach(function (c) {
    c.addEventListener("pointermove", function (e) {
      var r = c.getBoundingClientRect();
      c.style.setProperty("--cx", (e.clientX - r.left) + "px"); c.style.setProperty("--cy", (e.clientY - r.top) + "px");
    });
  });

  // entrada por rolagem
  if ("IntersectionObserver" in window && !reduz) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("on"); io.unobserve(en.target); } });
    }, { threshold: .14, rootMargin: "0px 0px -40px 0px" });
    document.querySelectorAll(".v3-rv").forEach(function (el, i) { el.style.transitionDelay = (i % 3) * 80 + "ms"; io.observe(el); });
  } else {
    document.querySelectorAll(".v3-rv").forEach(function (el) { el.classList.add("on"); });
  }

  // contadores
  function contar(el) {
    var alvo = parseInt(el.getAttribute("data-conta"), 10); if (!alvo || reduz) return;
    var t0 = null, dur = 1400;
    function passo(t) { if (!t0) t0 = t; var k = Math.min(1, (t - t0) / dur); el.textContent = Math.round(alvo * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(passo); }
    requestAnimationFrame(passo);
  }
  if ("IntersectionObserver" in window) {
    var ioc = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { contar(en.target); ioc.unobserve(en.target); } }); }, { threshold: .6 });
    document.querySelectorAll("[data-conta]").forEach(function (el) { ioc.observe(el); });
  }

  // linha de progresso dos caminhos + parallax da foto do médico
  var passos = document.querySelector(".v3-passos"), itens = passos ? passos.querySelectorAll(".v3-passo") : [];
  var par = document.querySelector("[data-parallax] img");
  var pendente = false;
  function aoRolar() {
    pendente = false;
    var vh = window.innerHeight;
    if (passos) {
      var r = passos.getBoundingClientRect(), p = Math.min(1, Math.max(0, (vh * .62 - r.top) / r.height));
      passos.style.setProperty("--prog", p.toFixed(3));
      itens.forEach(function (li) { li.classList.toggle("on", li.getBoundingClientRect().top < vh * .62); });
    }
    if (par && !reduz) {
      var rp = par.parentElement.parentElement.getBoundingClientRect();
      if (rp.bottom > 0 && rp.top < vh) par.style.setProperty("--py", ((rp.top - vh / 2) * -.08).toFixed(1) + "px");
    }
  }
  window.addEventListener("scroll", function () { if (!pendente) { pendente = true; requestAnimationFrame(aoRolar); } }, { passive: true });
  aoRolar();

  // explorador "onde dói": sintomas e estruturas trocam a imagem da série (crossfade)
  var serie = document.getElementById("serieJoelho"), resposta = document.getElementById("expResposta");
  var botoes = document.querySelectorAll(".v3-chip, .v3-estr-b");
  function esc(s) { var d = document.createElement("div"); d.textContent = s; return d.innerHTML; }
  function mostrar(k) {
    if (!serie) return;
    var alvo = serie.querySelector('img[data-k="' + k + '"]') || serie.querySelector('img[data-k="mestre"]');
    if (alvo.dataset.src) { alvo.src = alvo.dataset.src; alvo.removeAttribute("data-src"); }
    serie.querySelectorAll("img").forEach(function (im) { im.classList.toggle("on", im === alvo); });
  }
  // pré-carrega a série quando o explorador chega perto da tela
  if (serie && "IntersectionObserver" in window) {
    var iop = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return; iop.disconnect();
      serie.querySelectorAll("img[data-src]").forEach(function (im) { var i = new Image(); i.src = im.dataset.src; });
    }, { rootMargin: "400px" });
    iop.observe(serie);
  }
  botoes.forEach(function (b) {
    b.addEventListener("click", function () {
      var ativo = b.getAttribute("aria-pressed") === "true";
      botoes.forEach(function (o) { o.setAttribute("aria-pressed", "false"); });
      if (ativo) {
        mostrar("mestre");
        resposta.innerHTML = '<p class="v3-resposta-vazio">Toque em um sintoma ou numa estrutura para ver onde ela fica no joelho.</p>';
        return;
      }
      b.setAttribute("aria-pressed", "true");
      var k = b.getAttribute("data-estrutura"); mostrar(k);
      var html;
      if (b.classList.contains("v3-chip")) {
        html = '<p class="r-k">Pode estar relacionado a</p><p class="r-t">' + esc(b.getAttribute("data-cond")) + "</p>" +
          '<p class="r-a">Um mesmo sintoma pode ter causas diferentes. Só a avaliação define a causa no seu caso.</p>';
      } else {
        html = '<p class="r-k">Estrutura em destaque</p><p class="r-t">' + esc(b.getAttribute("data-rotulo")) + "</p>" +
          '<p class="r-a">Ilustração educativa da anatomia do joelho.</p>';
      }
      resposta.innerHTML = html + '<a class="v3-link" href="' + esc(b.getAttribute("data-url")) + '">Entender melhor →</a>';
      resposta.classList.remove("trocou"); void resposta.offsetWidth; resposta.classList.add("trocou");
    });
  });
})();
