---
permalink: /awards
title: "Awards"
author_profile: false
redirect_from: 
  - /awards/
  - /awards.html
---

## 2023

## ▸ Best Paper Award of the Demonstrations and Resources Forum (BPM'23)

**BPMN Inspector** was awarded at the 21th International Conference on Business Process Management September 11-15 in: [BPM 2023 Best Paper Award of the Demonstration and Resources Forum ](https://bpm-conference.org/awards/) with the paper entitled: BPMN Inspector: A Tool for Extracting Features from BPMN Models. 

The contribution was mentioned for its noteworthy "potential impact on BPM
practitioners and educators" in the [BPM Newsletter of November 2023](https://bpm-conference.org/assets/docs/newsletter/BPM-newsletter-2023-11.pdf
). 

<div class="slideshow-container">

  <!-- Prima immagine -->
  <div class="mySlides fade">
    <img src="../files/awards/2023/bpmnaward.jpeg" style="width:100%">
  </div>

  <!-- Seconda immagine -->
  <div class="mySlides fade">
    <img src="../files/awards/2023/BPM23AwardCertificate.jpg" style="width:100%">
  </div>

</div>

<!-- Controlli per cambiare immagine -->
<div style="text-align:center">
  <span class="dot" onclick="currentSlide(1)"></span> 
  <span class="dot" onclick="currentSlide(2)"></span> 
</div>

<style>
/* CSS per lo slideshow */
.slideshow-container {
  position: relative;
  max-width: 100%;
  margin: auto;
}

.mySlides {
  display: none;
}

.fade {
  -webkit-animation-name: fade;
  -webkit-animation-duration: 1.5s;
  animation-name: fade;
  animation-duration: 1.5s;
}

@-webkit-keyframes fade {
  from {opacity: .4} 
  to {opacity: 1}
}

@keyframes fade {
  from {opacity: .4} 
  to {opacity: 1}
}

/* Dot indicators */
.dot {
  height: 15px;
  width: 15px;
  margin: 0 2px;
  background-color: #bbb;
  border-radius: 50%;
  display: inline-block;
  transition: background-color 0.6s ease;
}

.active, .dot:hover {
  background-color: #717171;
}
</style>

<script>
// JavaScript per far cambiare automaticamente le immagini
let slideIndex = 0;
showSlides();

function showSlides() {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  let dots = document.getElementsByClassName("dot");
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";  
  }
  slideIndex++;
  if (slideIndex > slides.length) {slideIndex = 1}    
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";  
  dots[slideIndex-1].className += " active";
  setTimeout(showSlides, 7000); 
}
</script>