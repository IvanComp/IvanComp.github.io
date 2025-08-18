---
permalink: /conferencemap/
---

<style>
  html, body { overflow: hidden; }

  #globe-wrap{
    width:120%;
    height:min(150vh, 720px);
    min-height:420px;
    margin:0 auto;
    margin-top:-100px;
    -webkit-user-select:none; user-select:none; /* niente selezione/caret */
  }
  .scene-tooltip{
    background: rgba(255,255,255,0.96);
    color:#111; padding:8px 10px; border-radius:8px; font-size:12px;
    box-shadow: 0 4px 14px rgba(0,0,0,.08);
  }
  .scene-tooltip img{
    width:200px; height:auto; display:block; margin-bottom:6px; border-radius:6px;
  }
  .scene-tooltip::before, .scene-tooltip::after{ content:none !important; display:none !important; border:0 !important; }
  #globe-wrap canvas:focus{ outline:none !important; }
</style>

<div id="globe-wrap"></div>

<script src="https://unpkg.com/globe.gl@2.29.1"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3"></script>

<script>
(function () {
  const el = document.getElementById('globe-wrap');

  /* ======= PALETTE (modifica qui) ======= */
  const COLORS = {
    ocean:  '#95c5e9ff', // mare
    land:   '#799286ff',   // terre
    border: '#654321',   // confini
    points: '#c40000ff'  // puntini
  };

  // Dati da _data/conferences.yml (con description e place)
  const DATA = [
  {% for c in site.data.conferences %}
    {
      name: {{ c.name | jsonify }},
      description: {{ c.description | jsonify }},
      year: {{ c.year | jsonify }},
      place: {{ c.place | jsonify }},
      lat: {{ c.lat }},
      lng: {{ c.lng }},
      image: {{ c.image | relative_url | jsonify }},
      url:   {{ c.url   | relative_url | jsonify }}
    }{% unless forloop.last %},{% endunless %}
  {% endfor %}
  ];

  /* ===== Oceano: texture a tinta unita dal colore in PALETTE =====
     Converte #RRGGBB[AA] in SVG data-URI (Three gestisce bene SVG flat). */
  const oceanHex = COLORS.ocean.replace('#','').slice(0,6);
  const oceanAlpha = (COLORS.ocean.length === 9)
    ? (parseInt(COLORS.ocean.slice(7,9),16) / 255) : 1;
  const OCEAN_TEX =
    `data:image/svg+xml;utf8,` +
    `<svg xmlns='http://www.w3.org/2000/svg' width='4' height='2'>` +
    `<rect width='100%' height='100%' fill='%23${oceanHex}' fill-opacity='${oceanAlpha}'/></svg>`;

  const globe = Globe({ waitForGlobeReady:true, animateIn:true })(el)
    .backgroundColor('#ffffff')
    .globeImageUrl(OCEAN_TEX)   // oceano della tinta scelta
    .bumpImageUrl(null)
    .onGlobeReady(() => {
      const mat = globe.globeMaterial();
      mat.color.set('#ffffff');     // materiale neutro (non altera la texture)
      mat.emissive.set('#000000');  // niente sbiancamento
      mat.bumpScale = 0;
      const canvas = el.querySelector('canvas');
      if (canvas) canvas.setAttribute('tabindex','-1');
    });

  // Marker come punti (tooltip + click) — parametri invariati
  globe
    .pointsData(DATA)
    .pointLat(d => d.lat)
    .pointLng(d => d.lng)
    .pointAltitude(0.03)
    .pointRadius(0.35)
    .pointColor(() => COLORS.points)
    .pointLabel(d => `
      <div>
        <div><strong>${d.name}</strong></div>      
        ${d.description ? `<div style="opacity:.85">${d.description}</div>` : ``}
        ${d.place ? `<div><strong>${d.place}</strong>, (${d.year}) </div>` : ``}
        <div style="margin-top:4px;opacity:.7">See slideshow</div>
      </div>
    `)
    .onPointClick(d => { if (d && d.url) window.location.href = d.url; });

  // Paesi: terre + confini — parametri invariati
  (async () => {
    const urls = [
      'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json',
      'https://unpkg.com/world-atlas@2/countries-110m.json'
    ];
    let world = null;
    for (const u of urls) { try { world = await fetch(u).then(r => r.json()); break; } catch(e){} }
    if (!world) { console.error('No topojson loaded.'); return; }

    const countries = topojson.feature(world, world.objects.countries).features;
    globe
      .polygonsData(countries)
      .polygonsTransitionDuration(0)
      .polygonAltitude(0.02)                     // come richiesto
      .polygonCapColor(() => COLORS.land)        // terre
      .polygonSideColor(() => 'rgba(49, 49, 52, 1)')
      .polygonStrokeColor(() => COLORS.border);  // confini
  })();

  // POV e interazioni — invariati
  globe.pointOfView({ lat: 20, lng: 0, altitude: 3 });
  globe.controls().autoRotate = false;
  globe.controls().enablePan = true;

  // Resize
  function resize(){ globe.width(el.clientWidth).height(el.clientHeight); }
  window.addEventListener('resize', resize);
  resize();

  console.log('globe.gl ok, items:', DATA.length);
})();
</script>
