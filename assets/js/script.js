/* ==========================================================================
   NetPulse: do ping ao alerta de rede
   script.js: interações da página e gráficos em JavaScript puro (SVG)
   ========================================================================== */
(function () {
  'use strict';

  /* ------------------------------------------------------------------------
     1. DADOS REAIS
     ------------------------------------------------------------------------ */
  var DADOS = {
    // Mediana do RTT (ms) dos 30 fluxos no Período A, em ordem crescente
    medianasMs: [24.84, 26.78, 28.38, 39.66, 43.75, 48.67, 63.86, 65.22, 83.84, 98.63,
      108.06, 109.05, 123.51, 125.52, 128.57, 135.48, 151.72, 167.45, 174.48, 191.65,
      214.43, 224.48, 226.43, 242.89, 244.65, 269.21, 283.37, 326.79, 339.09, 404.4],

    // Classe-alvo (classe futura, 12 min adiante) em cada conjunto
    classesAlvo: [
      { nome: 'Treino', OK: 39871, RISCO: 4227, FALHA: 5885 },
      { nome: 'Validação', OK: 10269, RISCO: 922, FALHA: 1350 },
      { nome: 'Teste', OK: 8152, RISCO: 653, FALHA: 3713 }
    ],

    // Matrizes de confusão no teste. Linhas: classe real. Colunas: classe prevista.
    // Ordem das classes: OK, RISCO, FALHA
    matrizes: {
      referencia: [[7289, 510, 353], [456, 100, 97], [369, 73, 3271]],
      arvore: [[6946, 1065, 141], [361, 265, 27], [282, 1624, 1807]],
      floresta: [[7396, 581, 175], [453, 147, 53], [313, 588, 2812]]
    },

    // Importância dos atributos (soma 1 em cada modelo)
    importancia: {
      arvore: { perda_pct: 0.0, aumento_pct: 0.07126330880534801, z_robusto: 0.6480891906329268,
        jitter_atual: 0.008997586534060013, jitter_relativo: 0.13178006627082103, timeout_atual: 0.0,
        n5_timeout: 0.0, n5_aumento80: 0.0, n5_risco: 0.13986984775684402 },
      floresta: { perda_pct: 0.00030588930962369566, aumento_pct: 0.24482770845054294,
        z_robusto: 0.37316147698260965, jitter_atual: 0.14678998493085005,
        jitter_relativo: 0.16294785639535894, timeout_atual: 1.881147137428059e-05,
        n5_timeout: 0.00037266515602581455, n5_aumento80: 0.0002900768385981448,
        n5_risco: 0.0712855304650165 }
    }
  };

  var CLASSES = ['OK', 'RISCO', 'FALHA'];
  var NOMES = { referencia: 'Repetir classe atual', arvore: 'Árvore de Decisão', floresta: 'Random Forest' };
  var SERIES = ['referencia', 'arvore', 'floresta'];
  var COR_SERIE = { referencia: '#7f95b0', arvore: '#1687d7', floresta: '#35bb7c' };
  var COR_CLASSE = { OK: '#35bb7c', RISCO: '#e0a31a', FALHA: '#c8323e' };
  var CLASSE_BARRA = { OK: 'bar--ok', RISCO: 'bar--risco', FALHA: 'bar--falha' };
  var SERIE_BARRA = { referencia: 'bar--ref', arvore: 'bar--tree', floresta: 'bar--rf' };

  /* ------------------------------------------------------------------------
     2. UTILITÁRIOS
     ------------------------------------------------------------------------ */
  var NS = 'http://www.w3.org/2000/svg';
  var nf1 = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  var nf2 = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  var nf3 = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 3, maximumFractionDigits: 3 });
  var nint = new Intl.NumberFormat('pt-BR');

  function pct1(v) { return nf1.format(v * 100) + '%'; }
  function media(arr) { return arr.reduce(function (a, b) { return a + b; }, 0) / arr.length; }
  function soma(arr) { return arr.reduce(function (a, b) { return a + b; }, 0); }

  function svgEl(nome, attrs, pai) {
    var e = document.createElementNS(NS, nome);
    for (var k in attrs) { if (Object.prototype.hasOwnProperty.call(attrs, k)) e.setAttribute(k, attrs[k]); }
    if (pai) pai.appendChild(e);
    return e;
  }
  function svgTexto(pai, texto, attrs) {
    var t = svgEl('text', attrs, pai);
    t.textContent = texto;
    if (attrs && attrs.fill) { t.style.fill = attrs.fill; t.style.stroke = 'none'; t.removeAttribute('fill'); }
    return t;
  }
  function criarSvg(w, h) {
    var s = svgEl('svg', { viewBox: '0 0 ' + w + ' ' + h, 'class': 'chart', 'aria-hidden': 'true', focusable: 'false' });
    s.setAttribute('width', w);
    s.setAttribute('height', h);
    return s;
  }
  function elemento(tag, classe, texto) {
    var e = document.createElement(tag);
    if (classe) e.className = classe;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }

  function quebrar(texto, maxChars) {
    if (texto.length <= maxChars) return [texto];
    var meio = texto.length / 2, melhor = -1, dist = 999;
    for (var i = 0; i < texto.length; i++) {
      if (texto[i] === ' ' && Math.abs(i - meio) < dist) { melhor = i; dist = Math.abs(i - meio); }
    }
    return melhor < 0 ? [texto] : [texto.slice(0, melhor), texto.slice(melhor + 1)];
  }

  /* ------------------------------------------------------------------------
     3. MÉTRICAS DERIVADAS DAS MATRIZES DE CONFUSÃO
     ------------------------------------------------------------------------ */
  function calcularMetricas(m) {
    var total = soma(m.map(soma));
    var recall = m.map(function (linha, i) { return linha[i] / soma(linha); });
    var precisao = m.map(function (_, j) { return m[j][j] / (m[0][j] + m[1][j] + m[2][j]); });
    var f1 = recall.map(function (r, i) { return 2 * precisao[i] * r / (precisao[i] + r); });
    return {
      acuracia: (m[0][0] + m[1][1] + m[2][2]) / total,
      f1macro: media(f1),
      balanced: media(recall),
      recallFalha: recall[2],
      recallRisco: recall[1]
    };
  }

  /* ------------------------------------------------------------------------
     4. NAVEGAÇÃO
     ------------------------------------------------------------------------ */
  function iniciarNavegacao() {
    var botao = document.getElementById('menu-toggle');
    var toc = document.getElementById('toc');
    var barra = document.getElementById('progress-bar');
    var links = toc ? Array.prototype.slice.call(toc.querySelectorAll('a[href^="#"]')) : [];

    function abrirMenu(abrir) {
      if (!botao || !toc) return;
      toc.classList.toggle('is-open', abrir);
      document.body.classList.toggle('menu-open', abrir);
      botao.setAttribute('aria-expanded', abrir ? 'true' : 'false');
    }

    if (botao && toc) {
      botao.addEventListener('click', function () {
        abrirMenu(!toc.classList.contains('is-open'));
      });
      links.forEach(function (a) {
        a.addEventListener('click', function () { abrirMenu(false); });
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && toc.classList.contains('is-open')) {
          abrirMenu(false);
          botao.focus();
        }
      });
      document.addEventListener('click', function (e) {
        if (toc.classList.contains('is-open') && !toc.contains(e.target) && !botao.contains(e.target)) abrirMenu(false);
      });
      window.addEventListener('resize', function () {
        if (window.innerWidth > 1100) abrirMenu(false);
      });
    }

    var secoes = links.map(function (a) {
      return document.getElementById(a.getAttribute('href').slice(1));
    });

    var aguardando = false;
    function atualizar() {
      aguardando = false;
      if (barra) {
        var total = document.documentElement.scrollHeight - window.innerHeight;
        var p = total > 0 ? Math.min(1, Math.max(0, window.scrollY / total)) : 0;
        barra.style.transform = 'scaleX(' + p.toFixed(4) + ')';
      }

      var linha = 120, ativa = -1;
      secoes.forEach(function (s, i) {
        if (s && s.getBoundingClientRect().top <= linha) ativa = i;
      });
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) ativa = links.length - 1;

      links.forEach(function (a, i) {
        var ligado = i === ativa;
        a.classList.toggle('is-active', ligado);
        if (ligado) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
      });
    }
    function agendar() {
      if (!aguardando) { aguardando = true; window.requestAnimationFrame(atualizar); }
    }
    window.addEventListener('scroll', agendar, { passive: true });
    window.addEventListener('resize', agendar);
    atualizar();
  }

  /* ------------------------------------------------------------------------
     5. INFRAESTRUTURA DOS GRÁFICOS
     ------------------------------------------------------------------------ */
  var graficos = [];
  var observador = null;

  function registrar(id, desenhar, tabela) {
    var el = document.getElementById(id);
    if (!el) return;
    var g = { el: el, desenhar: desenhar, larguraAtual: 0, visivel: false };
    g.slot = elemento('div', 'chart-slot');
    g.legendaSlot = elemento('div', 'chart-legend-slot');
    g.dica = elemento('div', 'chart-tooltip');
    g.dica.hidden = true;
    el.appendChild(g.slot);
    el.appendChild(g.legendaSlot);
    el.appendChild(g.dica);
    if (tabela) el.appendChild(montarTabelaDados(el, tabela()));
    graficos.push(g);
    montar(g);
    if (observador) observador.observe(el); else { g.visivel = true; marcarVisivel(g); }
  }

  function larguraDe(el) {
    var w = Math.floor(el.clientWidth || el.getBoundingClientRect().width || 0);
    return Math.max(280, w);
  }

  function montar(g) {
    var w = larguraDe(g.el);
    g.larguraAtual = w;
    var resultado = g.desenhar(w);
    g.slot.innerHTML = '';
    g.legendaSlot.innerHTML = '';
    g.slot.appendChild(resultado.svg);
    if (resultado.legenda) g.legendaSlot.appendChild(resultado.legenda);
    if (resultado.nota) g.legendaSlot.appendChild(resultado.nota);
    ligarDica(g, resultado.svg);
    marcarVisivel(g);
  }

  function marcarVisivel(g) {
    var svg = g.slot.querySelector('svg');
    if (svg && g.visivel) {
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () { svg.classList.add('is-visible'); });
      });
    }
  }

  function ligarDica(g, svg) {
    function mostrar(e) {
      var alvo = e.target && e.target.closest ? e.target.closest('[data-tip]') : null;
      if (!alvo) { g.dica.hidden = true; return; }
      var caixa = g.el.getBoundingClientRect();
      g.dica.textContent = alvo.getAttribute('data-tip');
      g.dica.style.left = Math.min(Math.max(e.clientX - caixa.left, 90), caixa.width - 90) + 'px';
      g.dica.style.top = (e.clientY - caixa.top - 6) + 'px';
      g.dica.hidden = false;
    }
    svg.addEventListener('pointermove', mostrar);
    svg.addEventListener('pointerdown', mostrar);
    svg.addEventListener('pointerleave', function () { g.dica.hidden = true; });
  }

  function iniciarGraficos() {
    if ('IntersectionObserver' in window) {
      observador = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (en) {
          if (!en.isIntersecting) return;
          graficos.forEach(function (g) {
            if (g.el === en.target) { g.visivel = true; marcarVisivel(g); }
          });
          observador.unobserve(en.target);
        });
      }, { threshold: 0.2 });
    }

    registrar('chart-intro', desenharIntro, tabelaIntro);
    registrar('chart-medianas', desenharMedianas, tabelaMedianas);
    registrar('chart-classes', desenharClasses, tabelaClasses);
    registrar('chart-metricas', desenharMetricas, tabelaMetricas);
    registrar('chart-importancia', desenharImportancia, tabelaImportancia);

    var pendente = null;
    function aoRedimensionar() {
      window.clearTimeout(pendente);
      pendente = window.setTimeout(function () {
        graficos.forEach(function (g) {
          if (Math.abs(larguraDe(g.el) - g.larguraAtual) >= 2) montar(g);
        });
      }, 120);
    }
    if ('ResizeObserver' in window) {
      var ro = new ResizeObserver(aoRedimensionar);
      graficos.forEach(function (g) { ro.observe(g.el); });
    } else {
      window.addEventListener('resize', aoRedimensionar);
    }
  }

  function montarTabelaDados(el, dados) {
    var det = elemento('details', 'details');
    det.appendChild(elemento('summary', '', 'Ver os dados deste gráfico'));
    var wrap = elemento('div', 'table-wrap');
    var tab = elemento('table', 'table table--compact table--results');
    var cab = elemento('thead');
    var trc = elemento('tr');
    dados.cabecalho.forEach(function (c) {
      var th = elemento('th', '', c);
      th.setAttribute('scope', 'col');
      trc.appendChild(th);
    });
    cab.appendChild(trc);
    tab.appendChild(cab);
    var corpo = elemento('tbody');
    dados.linhas.forEach(function (linha) {
      var tr = elemento('tr');
      linha.forEach(function (c, i) {
        var cel = elemento(i === 0 ? 'th' : 'td', '', c);
        if (i === 0) cel.setAttribute('scope', 'row');
        tr.appendChild(cel);
      });
      corpo.appendChild(tr);
    });
    tab.appendChild(corpo);
    wrap.appendChild(tab);
    det.appendChild(wrap);
    return det;
  }

  function montarLegenda(itens) {
    var ul = elemento('ul', 'legend');
    itens.forEach(function (it) {
      var li = elemento('li', 'legend__item');
      var sw = elemento('span', 'legend__swatch');
      sw.style.background = it.cor;
      li.appendChild(sw);
      li.appendChild(elemento('span', '', it.nome));
      ul.appendChild(li);
    });
    return ul;
  }

  function grade(svg, escala, ticks, y1, y2, yTexto, formato) {
    ticks.forEach(function (t) {
      var x = escala(t);
      svgEl('line', { x1: x, x2: x, y1: y1, y2: y2, 'class': 'chart__grid' }, svg);
      svgTexto(svg, formato(t), { x: x, y: yTexto, 'text-anchor': 'middle', 'class': 'chart__tick' });
    });
  }

  /* ------------------------------------------------------------------------
     6. GRÁFICO 1: Intro
     ------------------------------------------------------------------------ */
  function desenharIntro(w) {
    var menor = DADOS.medianasMs[0];
    var maior = DADOS.medianasMs[DADOS.medianasMs.length - 1];
    var h = 184, x0 = 12, x1 = w - 16, max = 420;
    var sx = function (v) { return x0 + (v / max) * (x1 - x0); };
    var svg = criarSvg(w, h);

    grade(svg, sx, [0, 100, 200, 300, 400], 22, 138, 156, function (t) { return String(t); });
    svgTexto(svg, 'RTT mediano do fluxo (ms)', { x: (x0 + x1) / 2, y: 177, 'text-anchor': 'middle', 'class': 'chart__tick' });

    svgTexto(svg, 'Fluxo de menor latência típica', { x: x0, y: 44, 'class': 'chart__label' });
    svgEl('rect', { x: x0, y: 52, width: sx(menor) - x0, height: 24, rx: 4, 'class': 'bar bar--h bar--flow', 'data-tip': 'Menor mediana: ' + nf1.format(menor) + ' ms' }, svg);
    svgTexto(svg, nf1.format(menor) + ' ms', { x: sx(menor) + 8, y: 69, 'class': 'chart__value' });

    svgTexto(svg, 'Fluxo de maior latência típica', { x: x0, y: 104, 'class': 'chart__label' });
    svgEl('rect', { x: x0, y: 112, width: sx(maior) - x0, height: 24, rx: 4, 'class': 'bar bar--h bar--flow', 'data-tip': 'Maior mediana: ' + nf1.format(maior) + ' ms' }, svg);
    svgTexto(svg, nf1.format(maior) + ' ms', { x: sx(maior) - 8, y: 129, 'text-anchor': 'end', 'class': 'chart__value', fill: '#fff' });

    var xr = sx(100), rotulo = 'Limite fixo hipotético: 100 ms';
    svgEl('line', { x1: xr, x2: xr, y1: 20, y2: 140, 'class': 'chart__ref' }, svg);
    var cabe = xr + rotulo.length * 6.6 < w - 4;
    svgTexto(svg, rotulo, { x: cabe ? xr + 6 : xr - 6, y: 14, 'text-anchor': cabe ? 'start' : 'end', 'class': 'chart__ref-label' });

    return { svg: svg };
  }
  function tabelaIntro() {
    var m = DADOS.medianasMs;
    return { cabecalho: ['Fluxo', 'Mediana do RTT (ms)'], linhas: [
      ['Menor latência típica', nf2.format(m[0])],
      ['Maior latência típica', nf2.format(m[m.length - 1])]
    ] };
  }

  /* ------------------------------------------------------------------------
     7. GRÁFICO 2: Medianas
     ------------------------------------------------------------------------ */
  function desenharMedianas(w) {
    var dados = DADOS.medianasMs;
    var esq = 44, dir = 10, topo = 24, base = 40;
    var h = w < 480 ? 260 : 310;
    var areaW = w - esq - dir, areaH = h - topo - base, max = 450;
    var sy = function (v) { return topo + areaH - (v / max) * areaH; };
    var passo = areaW / dados.length, largura = passo * 0.72;
    var svg = criarSvg(w, h);

    [0, 100, 200, 300, 400].forEach(function (t) {
      svgEl('line', { x1: esq, x2: w - dir, y1: sy(t), y2: sy(t), 'class': 'chart__grid' }, svg);
      svgTexto(svg, String(t), { x: esq - 8, y: sy(t) + 4, 'text-anchor': 'end', 'class': 'chart__tick' });
    });
    svgTexto(svg, 'ms', { x: esq - 8, y: topo - 10, 'text-anchor': 'end', 'class': 'chart__tick' });
    svgEl('line', { x1: esq, x2: w - dir, y1: sy(0), y2: sy(0), 'class': 'chart__axis' }, svg);

    dados.forEach(function (v, i) {
      var x = esq + i * passo + (passo - largura) / 2;
      svgEl('rect', {
        x: x, y: sy(v), width: largura, height: sy(0) - sy(v), rx: Math.min(3, largura / 3),
        'class': 'bar bar--flow',
        'data-tip': 'Fluxo ' + (i + 1) + ' de 30 (ordem crescente): ' + nf2.format(v) + ' ms'
      }, svg);
    });

    var xMin = esq + passo / 2, xMax = esq + (dados.length - 0.5) * passo;
    svgTexto(svg, nf1.format(dados[0]), { x: xMin + 10, y: sy(dados[0]) - 6, 'text-anchor': 'start', 'class': 'chart__value' });
    svgTexto(svg, nf1.format(dados[dados.length - 1]), { x: xMax, y: sy(dados[dados.length - 1]) - 6, 'text-anchor': 'end', 'class': 'chart__value' });

    svgTexto(svg, 'Os 30 fluxos, do menor para o maior RTT típico', { x: esq + areaW / 2, y: h - 10, 'text-anchor': 'middle', 'class': 'chart__tick' });
    return { svg: svg };
  }
  function tabelaMedianas() {
    return { cabecalho: ['Posição (ordem crescente)', 'Mediana do RTT (ms)'],
      linhas: DADOS.medianasMs.map(function (v, i) { return [String(i + 1), nf2.format(v)]; }) };
  }

  /* ------------------------------------------------------------------------
     8. GRÁFICO 3: Classes
     ------------------------------------------------------------------------ */
  function desenharClasses(w) {
    var estreito = w < 440;
    var esq = estreito ? 86 : 112, dir = 20, topo = 16, alturaBarra = 36, espaco = 26;
    var h = topo + 3 * (alturaBarra + espaco) + 30;
    var x0 = esq, x1 = w - dir;
    var sx = function (f) { return x0 + f * (x1 - x0); };
    var svg = criarSvg(w, h);
    var yEixo = topo + 3 * (alturaBarra + espaco) - espaco + 14;

    grade(svg, sx, [0, 0.25, 0.5, 0.75, 1], topo - 4, yEixo - 6, yEixo + 8, function (t) { return Math.round(t * 100) + '%'; });

    DADOS.classesAlvo.forEach(function (c, i) {
      var y = topo + i * (alturaBarra + espaco);
      var total = c.OK + c.RISCO + c.FALHA;
      svgTexto(svg, c.nome, { x: esq - 10, y: y + 15, 'text-anchor': 'end', 'class': 'chart__label' });
      svgTexto(svg, nint.format(total) + (estreito ? '' : ' registros'), { x: esq - 10, y: y + 31, 'text-anchor': 'end', 'class': 'chart__tick' });

      var acumulado = 0;
      CLASSES.forEach(function (k) {
        var f = c[k] / total, xi = sx(acumulado), wi = sx(acumulado + f) - xi;
        svgEl('rect', {
          x: xi, y: y, width: Math.max(wi - 1, 0), height: alturaBarra,
          'class': 'bar bar--h ' + CLASSE_BARRA[k],
          'data-tip': c.nome + ', ' + k + ': ' + nint.format(c[k]) + ' registros (' + pct1(f) + ')'
        }, svg);
        if (wi > 30) {
          svgTexto(svg, pct1(f), { x: xi + wi / 2, y: y + 23, 'text-anchor': 'middle', 'class': 'chart__value', fill: k === 'FALHA' ? '#fff' : '#0b1c30' });
        }
        acumulado += f;
      });
    });

    var legenda = montarLegenda(CLASSES.map(function (k) { return { nome: k, cor: COR_CLASSE[k] }; }));
    return { svg: svg, legenda: legenda };
  }
  function tabelaClasses() {
    return { cabecalho: ['Conjunto', 'OK', 'RISCO', 'FALHA', 'Total'],
      linhas: DADOS.classesAlvo.map(function (c) {
        var t = c.OK + c.RISCO + c.FALHA;
        return [c.nome, nint.format(c.OK) + ' (' + pct1(c.OK / t) + ')', nint.format(c.RISCO) + ' (' + pct1(c.RISCO / t) + ')',
          nint.format(c.FALHA) + ' (' + pct1(c.FALHA / t) + ')', nint.format(t)];
      }) };
  }

  /* ------------------------------------------------------------------------
     9. GRÁFICO 4: Métricas
     ------------------------------------------------------------------------ */
  function itensMetricas() {
    var m = {};
    SERIES.forEach(function (s) { m[s] = calcularMetricas(DADOS.matrizes[s]); });
    return [
      { nome: 'Acurácia', chave: 'acuracia', fmt: pct1 },
      { nome: 'F1 macro', chave: 'f1macro', fmt: function (v) { return nf3.format(v); } },
      { nome: 'Balanced accuracy', chave: 'balanced', fmt: pct1 },
      { nome: 'Recall de FALHA', chave: 'recallFalha', fmt: pct1 },
      { nome: 'Recall de RISCO', chave: 'recallRisco', fmt: pct1 }
    ].map(function (it) {
      it.valores = {};
      SERIES.forEach(function (s) { it.valores[s] = m[s][it.chave]; });
      return it;
    });
  }

  function desenharMetricas(w) {
    var itens = itensMetricas();
    var svg;
    if (w >= 680) svg = metricasVertical(w, itens); else svg = metricasHorizontal(w, itens);
    var legenda = montarLegenda(SERIES.map(function (s) { return { nome: NOMES[s], cor: COR_SERIE[s] }; }));
    var nota = elemento('p', 'figure__note', 'O F1 macro varia de 0 a 1; no gráfico, a altura total (100%) equivale a 1,0.');
    return { svg: svg, legenda: legenda, nota: nota };
  }

  function metricasVertical(w, itens) {
    var esq = 40, dir = 8, topo = 26, base = 54, h = 380;
    var areaW = w - esq - dir, areaH = h - topo - base;
    var sy = function (v) { return topo + areaH - v * areaH; };
    var grupo = areaW / itens.length, folga = 4, larg = Math.min(46, (grupo - 16) / 3);
    var svg = criarSvg(w, h);

    [0, 0.25, 0.5, 0.75, 1].forEach(function (t) {
      svgEl('line', { x1: esq, x2: w - dir, y1: sy(t), y2: sy(t), 'class': 'chart__grid' }, svg);
      svgTexto(svg, Math.round(t * 100) + '%', { x: esq - 8, y: sy(t) + 4, 'text-anchor': 'end', 'class': 'chart__tick' });
    });
    svgEl('line', { x1: esq, x2: w - dir, y1: sy(0), y2: sy(0), 'class': 'chart__axis' }, svg);

    itens.forEach(function (it, gi) {
      var cx = esq + gi * grupo + grupo / 2;
      var inicio = cx - (3 * larg + 2 * folga) / 2;
      SERIES.forEach(function (s, si) {
        var v = it.valores[s], x = inicio + si * (larg + folga);
        svgEl('rect', { x: x, y: sy(v), width: larg, height: sy(0) - sy(v), rx: 3, 'class': 'bar ' + SERIE_BARRA[s],
          'data-tip': it.nome + ', ' + NOMES[s] + ': ' + it.fmt(v) }, svg);
        svgTexto(svg, it.fmt(v), { x: x + larg / 2, y: sy(v) - 6, 'text-anchor': 'middle', 'class': 'chart__value' });
      });
      quebrar(it.nome, 14).forEach(function (linha, li) {
        svgTexto(svg, linha, { x: cx, y: h - base + 22 + li * 16, 'text-anchor': 'middle', 'class': 'chart__label' });
      });
    });
    return svg;
  }

  function metricasHorizontal(w, itens) {
    var x0 = 8, x1 = w - 54, alturaBarra = 16, passoBarra = 20, bloco = 22 + 3 * passoBarra + 14, topo = 16;
    var h = topo + itens.length * bloco + 4;
    var sx = function (v) { return x0 + v * (x1 - x0); };
    var svg = criarSvg(w, h);

    [0, 0.5, 1].forEach(function (t) {
      svgEl('line', { x1: sx(t), x2: sx(t), y1: 6, y2: h - 4, 'class': 'chart__grid' }, svg);
    });
    itens.forEach(function (it, gi) {
      var y = topo + gi * bloco;
      svgTexto(svg, it.nome, { x: x0, y: y + 10, 'class': 'chart__label' });
      SERIES.forEach(function (s, si) {
        var v = it.valores[s], yb = y + 18 + si * passoBarra;
        svgEl('rect', { x: x0, y: yb, width: Math.max(sx(v) - x0, 1), height: alturaBarra, rx: 3, 'class': 'bar bar--h ' + SERIE_BARRA[s],
          'data-tip': it.nome + ', ' + NOMES[s] + ': ' + it.fmt(v) }, svg);
        svgTexto(svg, it.fmt(v), { x: sx(v) + 6, y: yb + 12, 'class': 'chart__value' });
      });
    });
    return svg;
  }

  function tabelaMetricas() {
    return { cabecalho: ['Métrica'].concat(SERIES.map(function (s) { return NOMES[s]; })),
      linhas: itensMetricas().map(function (it) {
        return [it.nome].concat(SERIES.map(function (s) { return it.fmt(it.valores[s]); }));
      }) };
  }

  /* ------------------------------------------------------------------------
     10. GRÁFICO 5: Importância
     ------------------------------------------------------------------------ */
  function atributosOrdenados() {
    var f = DADOS.importancia.floresta;
    return Object.keys(f).sort(function (a, b) { return f[b] - f[a]; });
  }
  function fmtImportancia(v) { return v < 0.0005 ? '0,0%' : pct1(v); }

  function desenharImportancia(w) {
    var atributos = atributosOrdenados();
    var largo = w >= 560;
    var colRotulo = largo ? 128 : 0;
    var x0 = 8 + colRotulo, x1 = w - 56, max = 0.7;
    var sx = function (v) { return x0 + (v / max) * (x1 - x0); };
    var alturaBarra = 14, folga = 3;
    var bloco = largo ? 2 * alturaBarra + folga + 12 : 20 + 2 * alturaBarra + folga + 12;
    var topo = 8, h = topo + atributos.length * bloco;
    var svg = criarSvg(w, h);

    [0, 0.2, 0.4, 0.6].forEach(function (t) {
      svgEl('line', { x1: sx(t), x2: sx(t), y1: 0, y2: h, 'class': 'chart__grid' }, svg);
    });

    atributos.forEach(function (a, i) {
      var y = topo + i * bloco;
      var yBarras = largo ? y : y + 20;
      if (largo) svgTexto(svg, a, { x: 8, y: y + alturaBarra + 4, 'class': 'chart__label' });
      else svgTexto(svg, a, { x: 8, y: y + 13, 'class': 'chart__label' });
      [['floresta', 0], ['arvore', 1]].forEach(function (par) {
        var s = par[0], v = DADOS.importancia[s][a], yb = yBarras + par[1] * (alturaBarra + folga);
        svgEl('rect', { x: x0, y: yb, width: Math.max(sx(v) - x0, 1.5), height: alturaBarra, rx: 3, 'class': 'bar bar--h ' + SERIE_BARRA[s],
          'data-tip': a + ', ' + NOMES[s] + ': ' + nf3.format(v * 100) + '% da importância' }, svg);
        svgTexto(svg, fmtImportancia(v), { x: sx(v) + 6, y: yb + 11, 'class': 'chart__value' });
      });
    });

    var legenda = montarLegenda(['floresta', 'arvore'].map(function (s) { return { nome: NOMES[s], cor: COR_SERIE[s] }; }));
    return { svg: svg, legenda: legenda };
  }
  function tabelaImportancia() {
    return { cabecalho: ['Atributo', 'Random Forest', 'Árvore de Decisão'],
      linhas: atributosOrdenados().map(function (a) {
        return [a, nf3.format(DADOS.importancia.floresta[a] * 100) + '%', nf3.format(DADOS.importancia.arvore[a] * 100) + '%'];
      }) };
  }

  /* ------------------------------------------------------------------------
     11. MATRIZES DE CONFUSÃO (Corrigidas para exibir Risco e % corretamente)
     ------------------------------------------------------------------------ */
  function iniciarMatrizes() {
    var area = document.getElementById('matrizes');
    var btnContagem = document.getElementById('matriz-contagem');
    var btnPercentual = document.getElementById('matriz-percentual');
    if (!area) return;
    var modo = 'contagem';

    function desenhar() {
      area.innerHTML = '';
      SERIES.forEach(function (s) {
        var m = DADOS.matrizes[s];
        var bloco = elemento('div', 'matrix');
        bloco.appendChild(elemento('h4', 'matrix__title', NOMES[s]));

        var tab = elemento('table', 'matrix__table');
        tab.appendChild(elemento('caption', 'sr-only', 'Matriz de confusão: ' + NOMES[s] + '. Linhas: classe real. Colunas: classe prevista.'));

        var cab = elemento('thead');
        var tr1 = elemento('tr');
        tr1.appendChild(elemento('td'));
        var thSpan = elemento('th', '', 'Classe prevista');
        thSpan.setAttribute('colspan', '3');
        tr1.appendChild(thSpan);
        cab.appendChild(tr1);

        var tr2 = elemento('tr');
        tr2.appendChild(elemento('td'));
        CLASSES.forEach(function (k) {
          var th = elemento('th', '', k);
          th.setAttribute('scope', 'col');
          tr2.appendChild(th);
        });
        cab.appendChild(tr2);
        tab.appendChild(cab);

        var corpo = elemento('tbody');
        m.forEach(function (linha, i) {
          var tr = elemento('tr');
          var th = elemento('th', '', CLASSES[i]);
          th.setAttribute('scope', 'row');
          tr.appendChild(th);
          var totalLinha = soma(linha);
          
          linha.forEach(function (n, j) {
            var frac = totalLinha > 0 ? n / totalLinha : 0;
            var textoCel = modo === 'contagem' ? nint.format(n) : pct1(frac);
            var td = elemento('td', 'matrix__cell' + (i === j ? ' matrix__cell--diag' : ''), textoCel);
            
            var intensidade = Math.min(1, frac * 0.85);
            td.style.setProperty('--v', intensidade.toFixed(3));
            if (intensidade > 0.5) td.classList.add('is-strong');
            td.setAttribute('title', 'Real ' + CLASSES[i] + ', prevista ' + CLASSES[j] + ': ' + nint.format(n) + ' (' + pct1(frac) + ' da classe real)');
            tr.appendChild(td);
          });
          corpo.appendChild(tr);
        });
        tab.appendChild(corpo);
        bloco.appendChild(tab);
        bloco.appendChild(elemento('p', 'matrix__axis', 'Linhas: classe real. Colunas: classe prevista.'));
        area.appendChild(bloco);
      });
    }

    function definirModo(novo) {
      modo = novo;
      if (btnContagem && btnPercentual) {
        btnContagem.classList.toggle('is-active', novo === 'contagem');
        btnPercentual.classList.toggle('is-active', novo === 'percentual');
        btnContagem.setAttribute('aria-pressed', novo === 'contagem' ? 'true' : 'false');
        btnPercentual.setAttribute('aria-pressed', novo === 'percentual' ? 'true' : 'false');
      }
      desenhar();
    }
    if (btnContagem) btnContagem.addEventListener('click', function () { definirModo('contagem'); });
    if (btnPercentual) btnPercentual.addEventListener('click', function () { definirModo('percentual'); });
    desenhar();
  }

  /* ------------------------------------------------------------------------
     12. INICIALIZAÇÃO
     ------------------------------------------------------------------------ */
  function iniciar() {
    iniciarNavegacao();
    iniciarMatrizes();
    iniciarGraficos();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();