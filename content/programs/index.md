---
title: Programs
kicker: Documentation
lede: Every program and module LARMORX ports, grouped by the software it comes from. Open a group to see what each program does, which ports it has and how far each port is validated.
wide: true
description: The programs and modules LARMORX ports, grouped by their software (ANTs and ITK, AFNI, FSL, tedana, sdcflows, fMRIPrep), with each one's ports, a replica or a clean room or both, their status, and links to its reference and evidence pages.
---

Each program has two pages. Its reference says what it does, its command line, its Python call, its options and examples. Its evidence shows how its ports compare with the original, in figures: how the cases of its records agree with the original, how the differences that remain compare with the original's own variability, what it does on real data, and its speed where a benchmark report exists. The main repository's code draws every figure from a committed record ([docs/figures.md](repo:docs/figures.md)), and its provenance is linked beneath it. So far `bet`, `bet2` and `betsurf` have their reference page; the others link their API page in the repository until theirs is written.

A **port** is a **replica**, translated from the original's source to give its results bit for bit, or a **clean room**, written without that source and built for speed; some programs have both ([what the words mean](/#what-it-is)). Each port's status comes from its records: *validated* when every case of its record is within the thresholds, *experimental* while the record has no comparison yet or a case is not within them.

<div class="prog-tools" hidden data-prog-tools><button type="button" class="btn btn--secondary" data-prog-all="open">Open every group</button><button type="button" class="btn btn--secondary" data-prog-all="close">Close every group</button></div>

<div class="prog-groups">
{%- for g in data.programs.groups %}
{%- if g.get('planned') %}
<div class="prog-group prog-group--planned eco-{{ g.id }}" id="{{ g.id }}">
<div class="prog-head"><span class="prog-chip">{{ g.name }}</span><span class="prog-sum"><span class="prog-count">Planned</span><span class="prog-orig">{{ g.original }}</span></span></div>
<p class="prog-planned">{{ g.planned | md_inline }} <a href="{{ link('/roadmap/') }}">Roadmap</a></p>
</div>
{%- else %}
<details class="prog-group eco-{{ g.id }}" id="{{ g.id }}">
<summary class="prog-head"><span class="prog-chip">{{ g.name }}</span><span class="prog-sum"><span class="prog-count">{{ g.count }}</span>{% if g.original %}<span class="prog-orig">compared with {{ g.original }}</span>{% endif %}<span class="prog-ports">{% for p in g.ports %}<span class="port port--{{ p.kind }}"><span class="port-name">{{ p.name }}</span> <code>{{ p.package }}</code> <span class="port-licence">{{ p.licence }}</span></span>{% endfor %}</span></span></summary>
<ul class="prog-list">
{%- for p in g.programs %}
<li id="{{ g.id }}-{{ p.name | lower }}">
<div class="prog-name">{% if p.reference %}<a href="{{ link(p.reference) }}"><code>{{ p.name }}</code></a>{% else %}<code>{{ p.name }}</code>{% endif %}<span class="prog-kind">{{ p.kind }}</span></div>
<div class="prog-what"><p class="prog-does">{{ p.does | md_inline }}</p><p class="prog-call">{% if p.command %}<code>{{ p.command }}</code>{% endif %}{% if p.also %} <code>{{ p.also }}</code>{% endif %} <code>{{ p.python }}</code></p>{% if p.original != g.original %}<p class="prog-orig">compared with {{ p.original | md_inline }}</p>{% endif %}</div>
<ul class="prog-ports" aria-label="Its ports">{% for x in p.ports %}<li class="port port--{{ x.kind }}"><span class="port-name">{{ x.name }}</span> <span class="status-tag{% if x.status == 'experimental' %} status-tag--experimental{% else %} eco-{{ g.id }}{% endif %}">{{ x.status }}</span>{% if x.next_release %} <span class="prog-next">from the next release</span>{% endif %}</li>{% endfor %}</ul>
<p class="prog-links">{% if p.reference %}<a href="{{ link(p.reference) }}">Reference</a>{% else %}<a href="{{ repo(p.api) }}">API page</a>{% endif %}{% if p.evidence %}<a href="{{ link(p.evidence) }}">Evidence</a>{% endif %}</p>
</li>
{%- endfor %}
</ul>
</details>
{%- endif %}
{%- endfor %}
</div>

`larmorx mri hmc` is the clean room of FSL's `mcflirt` under a name of its own. `larmorx fsl mcflirt` runs the replica when `larmorx-nc` is installed, else the clean room, and `larmorx --implementation clean-room fsl mcflirt` chooses the clean room (from the next release; in 0.1.0rc1, `LARMORX_IMPLEMENTATION=original`). tedana's `t2smap` has its clean room from the next release; 0.1.0rc1 has only its replica, in `larmorx-gpl`. The confounds are being ported: `lx.confounds` holds nipype's DVARS today, and the rest follows ([roadmap](/roadmap/)). How the ports are compared with their originals, and what each verdict means: [Validation](/validation/).
