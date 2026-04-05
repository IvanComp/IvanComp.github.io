---
layout: single
title: "QualITA'25"
permalink: /conferences/qualita-2025/
author_profile: false
classes: wide
conference_id: "qualita-2025"
---

{% assign conference = site.data.conferences | where: "id", page.conference_id | first %}
{% include conference_detail.html conference=conference %}
