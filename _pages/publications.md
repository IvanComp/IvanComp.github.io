---
title: "Publications"
permalink: /publications/
layout: single
classes: wide publications-layout
---

<div class="publications-page">
  <div class="publications-toolbar">
    <h1 class="page__title publications-toolbar__title">Publications</h1>
    <div class="publication-filter">
      <label for="publication-filter"><strong>Filter by:</strong></label>
      <select id="publication-filter">
        {% for filter in site.data.publications.filters %}
          <option value="{{ filter.id }}">{{ filter.label }}</option>
        {% endfor %}
      </select>
    </div>
  </div>

  {% for section in site.data.publications.sections %}
    {% assign slides_enabled = false %}
    {% if section.id == 'conferences' or section.id == 'workshops' %}
      {% assign slides_enabled = true %}
    {% endif %}
    <section class="publication-section" data-category="{{ section.id }}">
      <h2>{{ section.title }}</h2>

      <ul class="publication-list">
        {% for entry in section.entries %}
          {% assign has_slides = false %}
          {% if slides_enabled and entry.slides_url and entry.slides_url != blank %}
            {% assign has_slides = true %}
          {% endif %}
          <li class="publication-item{% if entry.image %} publication-item--with-image{% endif %}">
            {% if entry.image %}
              <img
                class="publication-item__cover"
                src="{{ entry.image | relative_url }}"
                alt="{{ entry.image_alt | default: entry.citation }}"
                loading="lazy"
              >
            {% endif %}

            <div class="publication-item__content">
              <span class="publication-item__text">
                <span class="{{ section.icon }}-icon"></span>
                {{ entry.citation | markdownify | remove: '<p>' | remove: '</p>' }}
              </span>

              {% if entry.links or has_slides %}
                <span class="publication-item__links">
                  {% if entry.links %}
                    {% for link in entry.links %}
                      {% if link.url and link.url != blank %}
                        {% if link.url contains '://' %}
                          {% assign href = link.url %}
                        {% else %}
                          {% assign href = link.url | relative_url %}
                        {% endif %}
                        <a class="publication-item__link" href="{{ href }}"{% if link.new_tab %} target="_blank" rel="noopener"{% endif %}>{{ link.label }}</a>
                      {% endif %}
                    {% endfor %}
                  {% endif %}
                  {% if has_slides %}
                    {% if entry.slides_url contains '://' %}
                      {% assign slides_href = entry.slides_url %}
                    {% else %}
                      {% assign slides_href = entry.slides_url | relative_url %}
                    {% endif %}
                    <a class="publication-item__link publication-item__link--slides" href="{{ slides_href }}" target="_blank" rel="noopener">Slide</a>
                  {% endif %}
                </span>
              {% endif %}

              {% if entry.badges %}
                <span class="publication-item__badges">
                  {% for badge in entry.badges %}
                    <img class="publication-item__badge" src="{{ badge.image | relative_url }}" alt="{{ badge.alt }}">
                  {% endfor %}
                </span>
              {% endif %}
            </div>
          </li>
        {% endfor %}
      </ul>
    </section>
  {% endfor %}
</div>

<script>
  document.addEventListener('DOMContentLoaded', function() {
    const filter = document.getElementById('publication-filter');
    const sections = document.querySelectorAll('.publication-section');

    filter.addEventListener('change', function() {
      const selectedCategory = this.value;

      sections.forEach(section => {
        if (selectedCategory === 'all' || section.dataset.category === selectedCategory) {
          section.style.display = 'block';
        } else {
          section.style.display = 'none';
        }
      });
    });
  });
</script>
