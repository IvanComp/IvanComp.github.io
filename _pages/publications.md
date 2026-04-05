---
title: "Publications"
permalink: /publications/
layout: single
classes: wide
---

<div class="publications-page">
  <div class="publication-filter">
    <label for="publication-filter"><strong>Filter by:</strong></label>
    <select id="publication-filter">
      {% for filter in site.data.publications.filters %}
        <option value="{{ filter.id }}">{{ filter.label }}</option>
      {% endfor %}
    </select>
  </div>

  {% for section in site.data.publications.sections %}
    <section class="publication-section" data-category="{{ section.id }}">
      <h2>{{ section.title }}</h2>

      <ul class="publication-list">
        {% for entry in section.entries %}
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

              {% if entry.links %}
                <span class="publication-item__links">
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
