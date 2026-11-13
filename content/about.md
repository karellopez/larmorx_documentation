---
title: About
kicker: Documentation
lede: LARMORX's licence, how to cite it, its two repositories, and the credits and notices of the works this site and LARMORX use.
description: About LARMORX — its licence (Apache-2.0, an independent project), how to cite it (CITATION.cff) together with the original programs, its two repositories (the code and this site's sources), and the credits and notices of the works it includes and this site shows.
---

LARMORX is the *Library of Algorithmic Reimplementations for MRI through Open Rust eXecution*. What its name means, and how it follows the FAIR principles for research software: [The name](/#philosophy) on the home page.

## The licence {#licence}

LARMORX is open source under the [Apache-2.0](repo:LICENSE) licence: any use, commercial use included; keep the licence and the notices. Its two companion packages carry the licences their originals require: `larmorx-nc` the FSL Licence (non-commercial use only) and `larmorx-gpl` the GNU GPL version 3, under which tedana's LGPL-2.1 code may be passed on. The three packages and what each holds: [Concepts](/concepts/#packages).

LARMORX is an independent project, not affiliated with or endorsed by the developers of ANTs, AFNI, FSL, FreeSurfer or fMRIPrep.

## Citing LARMORX {#citing}

If LARMORX helped your research, please cite it, together with the original programs whose methods you used through it (for example ANTs, AFNI, FSL, sdcflows or tedana). The repository's [CITATION.cff](repo:CITATION.cff) holds the citation (GitHub's "Cite this repository" reads it):

```text
López Vilaret, K. M. (2026). LARMORX: Library of Algorithmic Reimplementations for MRI through Open Rust eXecution (version 0.1.0rc1). https://github.com/karellopez/larmorx
```

## The two repositories {#repositories}

- **[larmorx](https://github.com/karellopez/larmorx)**: the code of the three packages, their documents and API pages, every validation record ([docs/validation](repo:docs/validation/)) and benchmark report, the register of the originals' defects, the [licensing notes](repo:docs/licensing.md) and the [next steps](repo:docs/next-steps.md).
- **[larmorx_documentation](https://github.com/karellopez/larmorx_documentation)**: this site's sources. Its pages of evidence and its reference pages are made from the records and the code of `larmorx`. A mistake or an unclear page can be [reported there](https://github.com/karellopez/larmorx_documentation/issues).

## Credits and notices {#credits}

- The works `larmorx` includes and their licences are listed in its [NOTICE](repo:NOTICE); each port's crate records the files it was ported from, their versions and licences, in its `PROVENANCE.md`.
- The brain on the home page is a cloud of points sampled from the MNI ICBM 152 nonlinear asymmetric template, version 2009c (Fonov et al., 2009, 2011), from [TemplateFlow](https://www.templateflow.org/). Copyright (C) 1993–2004 Louis Collins, McConnell Brain Imaging Centre, Montreal Neurological Institute, McGill University; used under the permission in its [notice](/static/hero/LICENSE-MNI.txt).
- The datasets the evidence pages show are credited on each page, with their licences.
- Type: [Instrument Serif](/static/fonts/InstrumentSerif-OFL.txt), [Inter](/static/fonts/Inter-OFL.txt) and [JetBrains Mono](/static/fonts/JetBrainsMono-OFL.txt), with the Greek letters of [Noto Serif Display](/static/fonts/NotoSerifDisplay-OFL.txt), under the SIL Open Font License 1.1.
