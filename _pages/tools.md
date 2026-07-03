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
<div class="tools-page">
  <section class="tool-section">
    <div class="tool-section__header">
      <h2 class="page-section-title">Available Tools</h2>
    </div>

    <div class="tool-list">
      {% for section in tool_sections %}
        {% for tool in section.items %}
            <article class="tool-item tool-item--{{ section.theme }}{% if tool.placeholder %} tool-item--placeholder{% endif %}">
              {% if tool.image %}
                {% if tool.links and tool.links.size > 0 %}
                  <a class="tool-item__media" href="{{ tool.links.last.url | relative_url }}" aria-label="{{ tool.name }}">
                    <img
                      class="tool-item__image"
                      src="{{ tool.image | relative_url }}"
                      alt="{{ tool.image_alt | default: tool.name }}"
                    >
                  </a>
                {% else %}
                  <div class="tool-item__media" aria-label="{{ tool.name }}">
                  <img
                    class="tool-item__image"
                    src="{{ tool.image | relative_url }}"
                    alt="{{ tool.image_alt | default: tool.name }}"
                  >
                  </div>
                {% endif %}
              {% endif %}

              <div class="tool-item__body">
                <div class="tool-item__heading">
                  <div>
                    {% unless tool.placeholder %}
                      <p class="tool-item__domain">{{ tool.domain | default: section.title }}</p>
                    {% endunless %}
                    <h3 class="tool-item__title">{{ tool.name }}</h3>
                  </div>

                  {% if tool.status_label or tool.highlight %}
                    <div class="tool-item__badges">
                      {% if tool.status_label %}
                        <span class="tool-badge tool-badge--{{ tool.status_type | default: 'neutral' }}">{{ tool.status_label }}</span>
                      {% endif %}
                      {% if tool.highlight %}
                        {% if tool.highlight_url %}
                          <a class="tool-badge tool-badge--award" href="{{ tool.highlight_url | relative_url }}">
                            <i class="fas fa-award" aria-hidden="true"></i>
                            {{ tool.highlight }}
                          </a>
                        {% else %}
                          <span class="tool-badge tool-badge--award">
                            <i class="fas fa-award" aria-hidden="true"></i>
                            {{ tool.highlight }}
                          </span>
                        {% endif %}
                      {% endif %}
                    </div>
                  {% endif %}
                </div>

                {% if tool.summary %}
                  <p class="tool-item__summary">{{ tool.summary }}</p>
                {% elsif tool.description %}
                  <p class="tool-item__summary">{{ tool.description }}</p>
                {% endif %}

                <dl class="tool-item__meta">
                  {% if tool.year %}
                    <div>
                      <dt>Year</dt>
                      <dd>{{ tool.year }}</dd>
                    </div>
                  {% endif %}
                  {% if tool.availability %}
                    <div>
                      <dt>Availability</dt>
                      <dd>{{ tool.availability }}</dd>
                    </div>
                  {% endif %}
                  {% if tool.tags and tool.tags.size > 0 %}
                    <div>
                      <dt>Focus</dt>
                      <dd>{{ tool.tags | join: ", " }}</dd>
                    </div>
                  {% endif %}
                </dl>

                  {% if tool.links and tool.links.size > 0 %}
                  <div class="tool-item__actions">
                    {% include resource_links.html links=tool.links class_name="resource-links--compact" %}
                  </div>
                {% endif %}
              </div>
            </article>
        {% endfor %}
      {% endfor %}
    </div>
  </section>
</div>
