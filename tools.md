---
permalink: /tools/
title: "Tools"
author_profile: true
redirect_from: 
  - /tools/
  - /tools.html
---
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">

<style>
.tools-container {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 20px;
}

.tool-card {
    flex: 1 1 calc(33.333% - 20px);
    background: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    padding: 15px;
    width: 300px; /* Larghezza fissa */
    height: 350px; /* Altezza fissa */
}

.tool-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.tool-card img {
    max-width: 80%;
    max-height: 50%; /* I loghi si ridimensionano dinamicamente */
    height: auto;
    margin-bottom: 5px; /* Ridotto il margine inferiore */
    border-radius: 5px;
}

.tool-card h3 {
    font-size: 20px;
    color: #333;
    margin-top: 5px; /* Ridotto il margine superiore */
    margin-bottom: 10px;
}

.tool-card p {
    font-size: 14px;
    color: #666;
    margin-bottom: 15px;
}

.tool-card .buttons {
    display: flex;
    justify-content: center;
    gap: 10px;
}

.tool-card a {
    display: inline-block;
    background-color: white; /* Sfondo bianco */
    color: #444; /* Scritta grigio scuro */
    text-decoration: none;
    padding: 8px 12px;
    border-radius: 5px;
    font-size: 14px;
    border: 1px solid #ddd; /* Bordo grigio chiaro */
    transition: background-color 0.2s ease, color 0.2s ease;
}

.tool-card a:hover {
    background-color: #f0f0f0; /* Sfondo grigio chiaro al hover */
    color: #000; /* Testo più scuro al hover */
}

.section-title {
    display: flex;
    align-items: center;
    font-size: 24px;
    font-weight: bold;
    margin-top: 10px; /* Spazio sopra la scritta */
    margin-bottom: 0px; /* Nessun margine sotto la scritta */
    border-bottom: none; /* Rimuove la riga sotto */
}

.section-title::before {
    content: "";
    display: inline-block;
    width: 4px; /* Larghezza della barra */
    height: 24px; /* Altezza della barra */
    margin-right: 10px; /* Spaziatura dalla scritta */
    border-radius: 2px;
}

.business-section::before {
    background-color: #e34234; /* Rosso carminio pastello */
}

.performance-section::before {
    background-color: #556b2f; /* Verde pastello scuro */
}

.status-stable {
    color: #28a745; /* Verde */
    font-weight: bold;
}

.status-development {
    color: #e34234; /* Rosso */
    font-weight: bold;
}

.business-tool {
    border-top: 3px solid #e34234; /* Rosso carminio pastello */
    padding: 12px; /* Compensazione per il bordo */
}

/* Bordo verde per Performance Analysis */
.performance-tool {
    border-top: 3px solid #556b2f; /* Verde pastello scuro */
    padding: 12px; /* Compensazione per il bordo */
}

.badge {
    display: inline-block;
    font-size: 0.55rem; /* Testo piccolo */
    font-weight: 500; /* Font medio */
    padding: 0.25rem 0.225rem; /* Spaziatura interna (py-0.5 px-2.5) */
    border-radius: 0.175rem; /* Angoli arrotondati (rounded) */
    color: #a0a5aa; /* Testo chiaro (dark mode) */
    background-color: #F9F9F9; /* Sfondo scuro (dark:bg-gray-700) */
    border: 1px solid transparent; /* Bordo trasparente di default */
    border-color: #a0a5aa; /* Bordo grigio chiaro */
}

/* Hover effect per dark mode */
.badge:hover {
    opacity: 0.85; /* Effetto hover */
}

</style>

<div class="section-title business-section">Business Process Management</div>

<div class="tools-container">
  <!-- BPMN Inspector -->
  <div class="tool-card business-tool">
    <img src="../assets/images/tools/BPMNInspector.png" alt="BPMN Inspector" style="max-width: 90%; height: 120px;">
    <h3>BPMN Inspector</h3>
    <p>Status: <span class="status-stable"><em>v1.0.0 Stable </em></span>🏆 Best Paper Award<br> 
    A web application designed to streamline the inspection process of BPMN models.</p>
     <p> <span class="badge badge">BPMN</span> <span class="badge badge">Quantitative Analysis</span> <span class="badge badge">Business Process</span> </p>
    <div class="buttons">
      <a href="https://github.com/PROSLab/BPMN-Inspector" class="github" target="_blank">
        <i class="fab fa-github" style="margin-right: 5px;"></i>GitHub
      </a>
      <a href="/tools/bpmn-inspector/" class="info" target="_blank">Additional Information</a>
    </div>
  </div>

  <!-- DOLLY -->
  <div class="tool-card business-tool">
    <img src="../assets/images/tools/DOLLY.png" alt="DOLLY" style="max-width: 90%; height: 120px;">
    <h3>DOLLY</h3>
    <p>Status: <span class="status-development"><em>In Development</em></span><br>
    A JAVA framework to optimize IoT-Enhanced Business Processes with Digital Twins.</p>
    <p>  <span class="badge badge">Digital Process Twin</span> <span class="badge badge">IoT-Enhanced BP</span> <span class="badge badge">Process Simulation</span> </p>
   <div class="buttons">
      <a href="https://github.com/IvanComp/DOLLY" class="github" target="_blank">
        <i class="fab fa-github" style="margin-right: 5px;"></i>GitHub
      </a>
      <a href="/tools/dolly/" class="info" target="_blank">Additional Information</a>
    </div>
  </div>
</div>

<div class="section-title performance-section" style="margin-top: 30px" >Performance Analysis</div>

<div class="tools-container">
  <!-- AP4Fed -->
  <div class="tool-card performance-tool">
    <img src="../assets/images/tools/AP4FED.svg" alt="AP4Fed" style="max-width: 90%; height: 120px;">
    <h3>AP4Fed</h3>
    <p>Status: <span class="status-stable"><em>v1.0.0 Stable </em></span><br>
    A Federated Learning platform built on top of Flower with advanced design capabilities.</p>
   <p> <span class="badge badge">Performance-Analysis</span> <span class="badge badge">Architectural-Patterns</span> <span class="badge badge">Federated-Learning</span> </p>
    <div class="buttons">
      <a href="https://github.com/IvanComp/AP4Fed" class="github" target="_blank">
        <i class="fab fa-github" style="margin-right: 5px;"></i>GitHub
      </a>
      <a href="/tools/ap4fed/" class="info" target="_blank">Additional Information</a>
    </div> 
  </div>

  <div class="tool-card" style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
    <img src="../assets/images/tools/develop.gif" alt="Developing new things..." style="max-width: 80%; height: auto;">
    <h3 style="margin-top: 10px;">Developing New Things...</h3>
  </div>
</div>