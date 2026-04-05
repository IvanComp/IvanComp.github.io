---
layout: single
title: "MODELS '23"
permalink: /conferences/models-2023/
author_profile: false
classes: wide
conference_id: "models-2023"
---

{% assign conference = site.data.conferences | where: "id", page.conference_id | first %}
{% include conference_detail.html conference=conference %}
