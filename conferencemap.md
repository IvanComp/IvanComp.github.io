---
title: "Conference Map"
permalink: /conferencemap/
---

Available soon 🛠️

<!-- Load three.js and three-globe -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three-globe@2.24.13/dist/three-globe.min.js"></script>
<!-- Container for the 3D map -->
<div id="globe-container" style="width: 20px; height: 50px;"></div>

<script>
  // Set up the scene, camera, and renderer
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(705, window.innerWidth / 500, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(1000, 500);
  renderer.setClearColor(0xffffff, 1); // Imposta lo sfondo bianco
  document.getElementById("globe-container").appendChild(renderer.domElement);

  // Add light to the scene
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
  directionalLight.position.set(10, 10, 10).normalize();
  scene.add(directionalLight);

  // Create the Globe
  const globe = new ThreeGlobe()
    .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
    .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-sky.png');
  scene.add(globe);

  // Set camera position
  camera.position.z = 270;

  // Render loop
  function animate() {
    requestAnimationFrame(animate);
    globe.rotation.y += 0.001; // Rotate the Earth slowly
    renderer.render(scene, camera);
  }
  animate();
</script>