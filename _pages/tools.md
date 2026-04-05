---
permalink: /tools/
title: "Tools"
author_profile: true
classes: wide
redirect_from:
  - /tools/
  - /tools.html
---

{% assign tool_sections = site.data.tools.sections %}

{% for section in tool_sections %}
  <section class="tool-section">
    <h2 class="page-section-title">{{ section.title }}</h2>

    <div class="tool-grid">
      {% for tool in section.items %}
        <article class="tool-card tool-card--{{ section.theme }}{% if tool.placeholder %} tool-card--placeholder{% endif %}">
          {% if tool.image %}
            <div class="tool-card__image-wrap">
              <img
                class="tool-card__image"
                src="{{ tool.image | relative_url }}"
                alt="{{ tool.image_alt | default: tool.name }}"
              >
            </div>
          {% endif %}

          <h3 class="tool-card__title">{{ tool.name }}</h3>

          {% if tool.status_label or tool.highlight %}
            <p class="tool-card__status">
              {% if tool.status_label %}
                <span class="tool-card__status-label{% if tool.status_type %} tool-card__status-label--{{ tool.status_type }}{% endif %}">
                  {{ tool.status_label }}
                </span>
              {% endif %}
              {% if tool.highlight %}
                <span class="tool-card__highlight">{{ tool.highlight }}</span>
              {% endif %}
            </p>
          {% endif %}

          {% if tool.description %}
            <p class="tool-card__description">{{ tool.description }}</p>
          {% endif %}

          {% if tool.tags and tool.tags.size > 0 %}
            <div class="tool-tags">
              {% for tag in tool.tags %}
                <span class="tool-tag">{{ tag }}</span>
              {% endfor %}
            </div>
          {% endif %}

          {% if tool.links and tool.links.size > 0 %}
            <div class="tool-card__actions">
              {% include resource_links.html links=tool.links %}
            </div>
          {% endif %}
        </article>
      {% endfor %}
    </div>
  </section>
{% endfor %}
