---
permalink: /
title: "About Me"
author_profile: true
redirect_from: 
  - /aboutme/
  - /about.html
---


Hello! I’m Ivan Compagnucci, a PostDoctoral Researcher at Gran Sasso Science Institute.

I received my M.Sc. in Computer Science (May 2020) and my Ph.D. in Computer Science and Mathematics (July 2024) from the University of Camerino. My doctoral disseration proposed an approach to support IoT-Enhanced Business Processes with the Digital Twin paradigm.

My research focuses on modeling and monitoring business processes that integrate features, data and concepts concerning the Internet of Things (IoT) world. The goal is to align enterprise or organization business processes with emerging IoT technologies, aiming to achieve a synergy that enables continuous technology innovation. Recently, I started to work on the novel paradigm of Digital Process Twin.

Click [here](../files/IvanCompagnucciCV.pdf) to download my academic CV.


# News

Available soon 🛠️

<script src="https://unpkg.com/globe.gl@2.29.1"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3"></script>

<style>
  .cm-card{
    position: fixed;
    top: 100px;
    right: 16px;
    width: 200px;
    margin-right:50px;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    background:#fff;
    box-shadow: 0 6px 18px rgba(2,6,23,.10);
    z-index: 1000;
    overflow: hidden;
  }
  .cm-head{
    display:flex; align-items:center; justify-content:space-between;
    font-weight:600; color:#0f172a;
    padding:.6rem .8rem; background:#f8fafc; border-bottom:1px solid #e2e8f0;
  }
  .cm-wrap{
    position:relative; width:100%; height:220px;
    display:flex; align-items:center; justify-content:center;
  }
  #cm-mini{ width:100%; height:100%; }
  #cm-mini canvas{ display:block; margin:auto; }
  .cm-link{ position:absolute; inset:0; z-index:5; text-indent:-9999px; overflow:hidden; cursor:pointer; }
  @media (max-width: 900px){ .cm-card{ display:none; } }
</style>

<div class="cm-card">
  <div class="cm-head">
    <span>Conference Map  ➡️</span>
  </div>
  <div class="cm-wrap">
    <div id="cm-mini"></div>
    <a class="cm-link" href="{{ '/conferencemap/' | relative_url }}">Apri Conference Map</a>
  </div>
</div>

<script>
(function () {
  const mount = document.getElementById('cm-mini');
  if (!mount || !window.Globe) return;

  // Palette coerente con la tua pagina mappa
  const COLORS = {
    ocean:  '#95c5e9',   // mare
    land:   '#799286',   // terre
    border: '#654321',   // confini
    points: '#c40000'    // puntini
  };

  // Punti (solo coordinate) dal tuo YAML
  const DATA = [
  {% for c in site.data.conferences %}
    { lat: {{ c.lat }}, lng: {{ c.lng }} }{% unless forloop.last %},{% endunless %}
  {% endfor %}
  ];

  // Oceano tinta unita (SVG data URI)
  const hex = COLORS.ocean.replace('#','').slice(0,6);
  const OCEAN_TEX =
    `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='4' height='2'><rect width='100%' height='100%' fill='%23${hex}'/></svg>`;

  const globe = Globe({ waitForGlobeReady:true, animateIn:true })(mount)
    .backgroundColor('#ffffff')
    .globeImageUrl(OCEAN_TEX)
    .bumpImageUrl(null);

  // materiale neutro
  const mat = globe.globeMaterial();
  mat.color.set('#ffffff'); mat.emissive.set('#000000'); mat.bumpScale = 0;

  // puntini
  globe.pointsData(DATA)
    .pointLat(d=>d.lat).pointLng(d=>d.lng)
    .pointAltitude(0.20).pointRadius(0.3)
    .pointColor(()=>COLORS.points);

  // >>> TERRE + CONFINI (nuovo)
  (async () => {
    let world = null;
    for (const u of [
      'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json',
      'https://unpkg.com/world-atlas@2/countries-110m.json'
    ]) { try { world = await fetch(u).then(r => r.json()); break; } catch(e){} }
    if (!world) return;

    const countries = topojson.feature(world, world.objects.countries).features;
    globe
      .polygonsData(countries)
      .polygonsTransitionDuration(0)
      .polygonAltitude(0.05)                        // basso per non “sporcare”
      .polygonCapColor(() => COLORS.land)           // riempimento terra
      .polygonSideColor(() => 'rgba(0,0,0,0)')      // niente lato
      .polygonStrokeColor(() => COLORS.border);     // confini
  })();

  // auto-rotate (preview), niente pan/zoom
  const controls = globe.controls();
  controls.autoRotate = true;
  controls.autoRotateSpeed = 1.3;
  controls.enablePan = false;
  controls.enableZoom = false;
  globe.pointOfView({ lat: 15, lng: 0, altitude: 3.1 });
  if (globe.onRender) globe.onRender(() => controls.update());

  // dimensiona al contenitore
  const fit = () => globe.width(mount.clientWidth).height(mount.clientHeight);
  new ResizeObserver(fit).observe(mount);
  window.addEventListener('resize', fit);
  fit();
})();
</script>