---
layout: single
permalink: /awards/
title: "Awards"
redirect_from: 
  - /awards/
  - /awards.html
---

### ▸ Best Paper Award of the Demonstrations and Resources Forum (BPM'23)

**BPMN Inspector** was awarded at the 21th International Conference on Business Process Management September 11-15 in: [BPM 2023 Best Paper Award of the Demonstration and Resources Forum ](https://bpm-conference.org/awards/) with the paper entitled: BPMN Inspector: A Tool for Extracting Features from BPMN Models. 

The contribution was mentioned for its noteworthy "potential impact on BPM
practitioners and educators" in the [BPM Newsletter of November 2023](https://bpm-conference.org/assets/docs/newsletter/BPM-newsletter-2023-11.pdf
). 

<div class="slideshow-container">

  <div class="mySlides fade">
    <img src="../files/awards/2023/bpmnaward.jpeg" alt="BPMN Inspector Award 2023" />
  </div>

  <div class="mySlides fade">
    <img src="../files/awards/2023/BPM23AwardCertificate.jpg" alt="BPM'23 Award Certificate" />
  </div>

  <!-- Frecce di navigazione -->
  <a class="prev" onclick="plusSlides(-1)" role="button" aria-label="Previous slide">&#10094;</a>
  <a class="next" onclick="plusSlides(1)" role="button" aria-label="Next slide">&#10095;</a>
</div>

<!-- Indicatori sotto -->
<div class="dots-container">
  <span class="dot" onclick="currentSlide(1)" aria-label="Slide 1"></span> 
  <span class="dot" onclick="currentSlide(2)" aria-label="Slide 2"></span> 
</div>

<style>
.slideshow-container {
  position: relative;
  max-width: 80%;
  margin: 20px auto;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 18px rgba(0,0,0,0.2);
}

.mySlides {
  display: none;
  width: 100%;
}

.mySlides img {
  width: 100%;
  border-radius: 12px;
  object-fit: cover;
  transition: transform 1s ease-in-out;
}

.mySlides.fade img {
  animation: fadeEffect 1.5s;
}

@keyframes fadeEffect {
  from { opacity: 0.4; }
  to { opacity: 1; }
}

/* Frecce */
.prev, .next {
  cursor: pointer;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 42px;
  height: 42px;
  background: rgba(0,0,0,0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  transition: background 0.3s, transform 0.3s;
}

.prev { left: 15px; }
.next { right: 15px; }

.prev::before { content: "◀"; }
.next::before { content: "▶"; }

.prev:hover, .next:hover {
  background: rgba(0,0,0,0.8);
  transform: scale(1.1);
}

/* Indicatori */
.dots-container {
  text-align: center;
  margin-top: 12px;
}

.dot {
  height: 12px;
  width: 12px;
  margin: 0 3px;
  background-color: #bbb;
  border-radius: 50%;
  display: inline-block;
  transition: background-color 0.6s ease, transform 0.2s;
  cursor: pointer;
}

.active, .dot:hover {
  background-color: #444;
  transform: scale(1.2);
}
</style>

<script>
let slideIndex = 1;
let slideTimer;

function showSlides(n) {
  let slides = document.getElementsByClassName("mySlides");
  let dots = document.getElementsByClassName("dot");
  
  if (n > slides.length) { slideIndex = 1 }    
  if (n < 1) { slideIndex = slides.length }

  for (let s of slides) { s.style.display = "none"; }
  for (let d of dots) { d.className = d.className.replace(" active", ""); }

  slides[slideIndex-1].style.display = "block";  
  dots[slideIndex-1].className += " active";
}

function plusSlides(n) {
  clearTimeout(slideTimer);
  showSlides(slideIndex += n);
  slideTimer = setTimeout(autoSlides, 7000);
}

function currentSlide(n) {
  clearTimeout(slideTimer);
  showSlides(slideIndex = n);
  slideTimer = setTimeout(autoSlides, 7000);
}

function autoSlides() {
  showSlides(slideIndex += 1);
  slideTimer = setTimeout(autoSlides, 7000);
}

// Pausa autoplay su hover
const container = document.querySelector('.slideshow-container');
container.addEventListener('mouseenter', () => clearTimeout(slideTimer));
container.addEventListener('mouseleave', () => slideTimer = setTimeout(autoSlides, 7000));

showSlides(slideIndex);
slideTimer = setTimeout(autoSlides, 7000);
</script>