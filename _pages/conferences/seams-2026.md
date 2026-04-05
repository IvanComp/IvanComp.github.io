---
layout: single
title: "SEAMS '26"
permalink: /conferences/seams-2026/
author_profile: false
classes: wide
conference_id: "seams-2026"
---

{% assign conference = site.data.conferences | where: "id", page.conference_id | first %}
{% include conference_detail.html conference=conference %}
