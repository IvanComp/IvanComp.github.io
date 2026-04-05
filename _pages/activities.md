---
layout: single
permalink: /activities/
title: "Research Activities"
classes: wide
redirect_from: 
  - /activities/
  - /activities.html
---

<div class="activities-page">
  <section class="activity-section">
    <h2>Organizing Committee</h2>
    <ul class="activity-list">
      {% for item in site.data.activities.organizing_committee %}
        <li class="activity-item">
          <span class="activity-item__text">
            <span class="activity-item__title">{{ item.title }}</span>
            {% if item.short_name %}
              <span class="activity-item__label">({{ item.short_name }})</span>
            {% endif %}
            <span class="activity-item__venue">{{ item.venue }}</span>
            <a class="activity-item__link" href="{{ item.url }}" target="_blank" rel="noopener">Link</a>
          </span>
        </li>
      {% endfor %}
    </ul>
  </section>

  <section class="activity-section">
    <h2>Program Committee</h2>
    <ul class="activity-list">
      {% for item in site.data.activities.program_committee %}
        <li class="activity-item">
          <span class="activity-item__text">
            <span class="activity-item__title">{{ item.title }}</span>
            {% if item.short_name %}
              <span class="activity-item__label">({{ item.short_name }})</span>
            {% endif %}
            <span class="activity-item__venue">{{ item.venue }}</span>
            <a class="activity-item__link" href="{{ item.url }}" target="_blank" rel="noopener">Link</a>
          </span>
        </li>
      {% endfor %}
    </ul>
  </section>

  <section class="activity-section">
    <h2>Journal Reviews</h2>
    <ul class="activity-list">
      {% for item in site.data.activities.journal_reviews %}
        <li class="activity-item activity-item--review">
          <span class="activity-item__text">
            <span class="review-pill review-pill--{{ item.quartile | downcase }}">{{ item.quartile }}</span>
            <a class="activity-item__journal" href="{{ item.url }}" target="_blank" rel="noopener"><strong>{{ item.journal }}</strong></a>
          </span>
        </li>
      {% endfor %}
    </ul>
  </section>
</div>
