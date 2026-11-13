---
title: Validation
kicker: Documentation
lede: How LARMORX compares every port with its original program, how to read the evidence pages, what each verdict means, where every program stands, random testing and the records.
description: How LARMORX's ports are compared with their original programs (ANTs, AFNI, FSL, tedana, sdcflows, fMRIPrep) and its own NIfTI reader with nibabel, the levels of testing, how to read the worked examples and metrics, the verdicts, the status of every program, random testing, the records and the data panel.
evidence: true
wide: true
---

## How LARMORX tests {#method}

**Every port runs beside its original**, on the same files with the same arguments. Their outputs, exit statuses and messages are then compared. The originals are exact builds of the pinned releases: ANTs 2.6.5 on ITK 5.4.5, built by the repository's script with GCC 14.3 (older GCCs drop float roundings the source asks for, so the build matters), AFNI 26.3.05 and FSL 6.0.7.23 (since 2026-10-29; the earlier releases 25.2.09 and 6.0.7.17 are kept for the step between the two), and fMRIPrep 25.2.6 itself, run on real datasets in its own image. LARMORX's own NIfTI reader and writer is compared with nibabel in the same way. Where the original's result depends on how it runs, its own variability is measured too: ANTs at 1 to 12 threads, another build or version of the same program, and the original with CORE-MATH's correctly rounded maths library loaded in place of glibc's.

**Two kinds of port.** A replica is translated from the original's source and gives its results bit for bit; where it does not, its record says why. A clean room is written without the source, from a description of what the original does: it gives the original's results within stated thresholds, often bit for bit, and is built for speed. ANTs' programs have replicas. AFNI's and FSL's programs have both (the clean room of FSL's `mcflirt` is `larmorx mri hmc`), and so does tedana's `t2smap` from the next release. FSL's replicas are in `larmorx-nc`, under FSL's licence; the clean rooms are in `larmorx`, under Apache-2.0. AFNI's replicas are in `larmorx` too since 2026-10-29: AFNI 26.3.05 releases the Medical College of Wisconsin's code under CC BY 4.0, so they left the GPL package `larmorx-gpl` for `larmorx` (Apache-2.0, with CC BY 4.0's credit), and their clean rooms stay, built for speed. What the words mean and where each port lives: [Concepts](/concepts/) and the [licensing notes](repo:docs/licensing.md).

**`fix` and `reproduce`.** When an original has a deterministic defect that changes its results, LARMORX corrects it by default (`fix`) and says so in a notice. `upstream_defects="reproduce"` gives the original's result, defect included: on the command line `--upstream-defects reproduce`, from the next release, and `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1. The records compare in `reproduce`, so they compare with the original as it is. Every defect is in the [register](repo:docs/findings/upstream-defects.md); more on [Concepts](/concepts/#defects).

**Corrections checked against known results.** Where a correction's result can be computed
another way (SciPy's morphology, NumPy, or the original program itself on an input where its
defect cannot arise), the record checks LARMORX's `fix` result against it, bit for bit. Such a
case carries the verdict *deliberate correction*, and its comparison with the original, in
`reproduce`, is bit for bit like every other. Where an input makes no sense and the original
silently does something arbitrary (AFNI-41, AFNI-48), LARMORX refuses it by default with a
message naming the defect, and `reproduce` gives the original's result.

**Three sizes of comparison.** A quick check, a few cases of every program, runs with the test suite before every change goes into the published code (*smoke*). The standard comparison, which this site shows, holds fMRIPrep's, sMRIPrep's and sdcflows' own command lines on real data, every option, generated edge cases and invalid inputs (*standard*). Some programs have more and larger cases (*full*). The comparisons need the originals, so they run on a Linux x86-64 workstation, never in continuous integration. Every level of testing, and when each runs: [Levels of testing](#levels).

**One data panel for every program.** Since 2026-10-24 every program is to be validated, and
shown, on the same fourteen shareable datasets: 1.5, 3 and 7 T; Siemens, GE and Philips;
single-band, multiband, multi-echo and sparse BOLD; every kind of field map; children, older
adults, a tumour and a stroke; head motion and low quality ([the data panel](/validation/data-panel/)).
The finished programs are compared on it again, one by one. ANTs' programs were the first
(2026-10-27): each of their evidence pages has a section *On the data panel*, with fMRIPrep's
calls in its fourteen runs on these datasets and the panel's own images.

```bash
pytest tests/parity
python -m larmorx_validation parity ants-n4 --tier standard --out docs/validation
```

The first command runs the quick check; the second, one program's standard comparison.

**The cross-platform checks on six platforms.** Every function's output on small generated inputs is checked, bit for bit, against LARMORX's own Linux x86-64 output, on Linux (x86-64, aarch64), macOS (Intel, Apple silicon) and Windows (x64, arm64), in continuous integration ([the cross-platform checks](repo:docs/validation/golden.md)). So a comparison made on Linux holds on every platform.

### Levels of testing {#levels}

Each level of testing answers one question. The levels that compare a port with its original
need that program, so they run on a Linux x86-64 workstation; the levels that need no original
run in continuous integration on all six platforms. Every run of an original program is computed
once and kept by the content of its inputs, so a later comparison runs only LARMORX again.

| Level | The question it answers | What it runs | Where |
|---|---|---|---|
| **Unit tests** | Does each part of the code do what it should? | The Rust and Python test suites, formatting, lints and licence headers | Continuous integration, six platforms, every change |
| **The cross-platform checks** | Does LARMORX give the same bits on every platform? | Every function on small generated inputs (at most 32³ voxels; no image data stored), checked against the checksums of LARMORX's own Linux x86-64 output | Continuous integration, six platforms, under a minute each |
| **The quick check** (*smoke*) | Does every port still agree with its original? | A few cases of every program, and every permanent case found by random testing | Workstation, before every change goes into the published code, about ten minutes |
| **The standard comparison** (*standard*) | Does the port reproduce its original, option by option? | Every option and code path; every data type, unusual header and size; the edge cases of every defect found; invalid inputs; fMRIPrep's, sMRIPrep's and sdcflows' own command lines on real data. This is the record each program's evidence page shows | Workstation, when a program is ported or updated |
| **The full comparison** (*full*) | Does it hold on more and larger cases? | Whole real images, more option combinations and thread counts | Workstation |
| **Data panel** | Does it hold on the hardest real data? | The fourteen datasets of the [data panel](/validation/data-panel/), with fMRIPrep's calls in its fourteen runs on them | Workstation |
| **Random testing** | Does it agree on inputs nobody chose? | Random valid inputs generated from a seed (phantoms, small crops of real templates, every orientation, data type and value range; nine cases in ten realistic) with random option combinations, several cases at a time, each limited to 3 GiB of memory; a run of half an hour, or a long run of several hours ([below](#random-testing)) | Workstation |
| **Heavy random cases** | Does it agree on random inputs that need more than the 3 GiB each case may use? | The random cases set aside because their outputs need more memory (some options make a small input produce a very large output), each run alone to its end with far more memory (tens of GiB, up to about 1 TiB) | Workstation, or a larger machine |
| **The original's own variability** | What does "the same result" mean for this program? | The original at several thread counts, in another build or version, and with correctly rounded maths | Workstation, with each record |
| **Memory and threads** | Does a port need no more memory than its original, whatever the thread count? | Peak memory against the original's on the same call (at most 10 % above it, plus 8 MiB); every parallel path kept to the thread count it is given, its result independent of it | Workstation, under pytest |
| **Speed** | How much faster is a clean room? | Benchmarks against the original and the replica ([benchmarks](repo:docs/benchmarks/)) | Workstation |
| **Independent review** | Does a second reader find anything? | A review of a large port's code and records by someone who did not write them | The final validation phase |
| **Comparisons with fMRIPrep** | Does a pipeline built on LARMORX reproduce fMRIPrep? | Stage by stage and end to end, against fMRIPrep's own runs | Workstation |

### Now, and before the first release {#levels-plan}

Since 2026-10-28 LARMORX is tested in two stages. Each program, as it is ported or follows a new
release of its original, is tested where it matters: every code path once and the original's
real use, so that it is published with its record and its evidence page. Once every program is
ported, one final validation phase adds the extensive testing to every program at once; each
evidence page then grows with the new evidence, and nothing it already shows is removed.

| Level | Each program, as it is ported or updated | The final validation phase, once every program is ported |
|---|---|---|
| **Unit tests and the cross-platform checks** | Every change; at least one cross-platform case for every function | Every change |
| **The quick check** | Before every change goes into the published code | Before every change goes into the published code |
| **The standard comparison** | The program's record and evidence page, with fMRIPrep's real calls on about three of its runs | Kept current with every update |
| **The full comparison** | Where a program has it (`antsRegistration`, `antsAI`, `antsAffineInitializer`, `Atropos`, the replicas of `mcflirt` and `bet`) | Every program |
| **Data panel** | Only the panel's runs whose fMRIPrep calls the record already uses | Every program (ANTs' programs since 2026-10-27) |
| **Random testing** | A run of half an hour; every difference triaged: a LARMORX mistake fixed and kept as a permanent case, a defect of the original registered | Long runs of several hours for every program, repeated |
| **Heavy random cases** | Not part of a program's testing (the heavy cases of the first long run, 2026-10-25, run in the background) | Every program, each case to its end |
| **The original's own variability** | With the record | Wider studies across thread counts |
| **Memory and threads** | Each program's calls added to the memory and thread checks | Speed and memory studies beyond the rule's check |
| **Speed** | Each clean room | Speed and memory studies |
| **Independent review** | — | Every large port |
| **Comparisons with fMRIPrep** | — (stage by stage on four runs with fMRIPrep 25.2.6, done) | Stage by stage and end to end, with the newest fMRIPrep |

**New releases of the originals.** LARMORX follows the newest release of each original program.
When one comes out, the replica follows it, then the clean room, with the same testing as a new
port; the record lists the cases where the original's own output changed between the two
releases, each with its reason. AFNI 25.2.09 to 26.3.05 was the first (2026-10-29): on the
evidence pages of [3dTshift](/evidence/afni-tshift/), [3dAutomask](/evidence/afni-automask/)
and [3dUnifize](/evidence/afni-unifize/), every example shows both releases.

## How to read the evidence {#reading}

Each program's evidence page (the [Programs](/programs/) page lists them) leads with its records' cases by verdict, then shows **worked examples** on real data:

- **What was run, on what.** The dataset and subject, the exact command (fMRIPrep's own, read from its working directory, where the pipeline calls the program), and every program with its version, build, thread count and setting (`fix` or `reproduce`).
- **What this shows.** Each worked example shows the original, the replica and the clean room side by side, where the program has them, and says in one line what it shows, with its verdict.
- **Titles.** Every figure's title says what it compares, against what, with the original's program and version: "the clean room against the original: FSL `bet` 6.0.7.23".
- **Colours.** The original is drawn in ink, with solid lines and squares; the replica in blue, with long dashes and triangles; the clean room in apricot, with short dashes and circles. Inputs, known answers and references computed another way are grey and dotted. A colour always comes with its name and its mark. The software's pastels (ANTs, AFNI, FSL, ...) only ever mark a group with its name.
- **Whole volumes, and three slices for panel cases.** Every example is a whole volume, except
  cases from the data panel beyond a program's key datasets: those show three full-resolution
  slices, one per plane, through the voxel where the comparison differs most (the example says
  so under its panels). Every metric is over every voxel of the files either way. Every example
  carries the credit line of the data it shows, and every page ends with its data credits.
- **The image viewer.** Each panel is labelled with exactly what it is: an input, the original program's output (as built, with correctly rounded maths, at another thread count), fMRIPrep's own output, or a port's output (the replica or the clean room, in `fix` or `reproduce`). Choose the plane, slice and volume, zoom and pan, set the intensity window; select a point to read every panel's exact value there. Compare two images side by side, by swiping or blinking between them, or in a checkerboard.
- **Differences.** A difference panel shows A − B on a symmetric scale whose range is printed, blue below zero and apricot above, linear or logarithmic; differences shown together share one scale, so a port's difference sits next to the original's own variability on the same footing. A difference that is zero everywhere says *bit-identical*; *Go to the largest difference* finds where they differ most.
- **The chain of causes.** Where a port and fMRIPrep's output differ, the runs between them are lined up, each step changing one thing (threads, maths library, version), so the cause of every difference is shown, not asserted.
- **Metrics.** One row per comparison, computed offline in float64 over every voxel of the outputs: the largest |Δ|, how many values differ, the RMS of Δ, the largest |Δ| relative to the image's range, 1 − the normalised cross-correlation. Each comparison of a port with its original gets a verdict and its reason, with links to the finding or register entry; the rows *the original against itself* are the yardstick. Provenance (inputs with their checksums, the commands, the commit) is under each example.
- **Every case.** The case explorer lists every case of the records: what it tests, its command line, its verdict (one per port) and reason. Search, filter, sort, and link to one case with `#case=<name>`.
- **Agreement.** One bar per category of a record's cases, as shares of the category, each case coloured by its verdict. *Bit-identical* means the same bits as the original as built. *Identical with correctly rounded maths* means the same bits once the original's maths library is replaced by CORE-MATH's, which LARMORX uses on every platform: glibc's `exp`, `log`, `sin` and `cos` are not always correctly rounded. *Within the thresholds* means within the record's stated tolerance, not bit-identity. *Rejected by both* means both programs refuse the input, compared by exit status and messages. *Expected divergence* means a documented, deliberate difference. [The verdicts](#verdicts) defines every one.
- **The original's own variability.** How much the original differs from itself: between its thread counts, its builds or its versions, or, for a deterministic original, when its input changes imperceptibly. The record measures it, and the figures place each port's differences beside it ([the verdicts](#verdicts)).
- **Images.** Masked to the brain, or the whole head where its dataset removed the face, from OpenNeuro datasets in the public domain (CC0-1.0, PDDL-1.0) or under CC-BY or CC-BY-SA, and the MNI ICBM 152 template ([its notice](/static/hero/LICENSE-MNI.txt)), each credited, with the share-alike notice where it applies. Difference maps are on a symmetric scale whose range is stated.
- **Speed.** Medians from the benchmark reports, on the machine each report names. Where a program has no benchmark report yet, its page says so.

Everything is computed by the main repository's code from its committed records and from cached runs of the original programs ([docs/figures.md](repo:docs/figures.md)); the site only displays it, and a check compares every number a page shows with the data it comes from.

## The verdicts {#verdicts}

One set of verdicts for the whole site. Every comparison of a port with its original, and every case of a record, gets exactly one of them. Each is drawn with its colour, its pattern and its name, never colour alone.

{{ ev.taxonomy() }}

## Where every program stands {#summary}

Every program ported so far, each of its ports, and how many cases of its record have each verdict, each case's verdict decided from what its record reports and measures. The programs are grouped by their software, in the order of the [Programs](/programs/) page.

{{ ev.matrix(site.tools, data.programs.groups) }}

### What each status means {#statuses}

Each port has the status its record states, one of three:

- *experimental*: the tests of its part pass, but the extensive tests of the final validation phase are still to come: the [data panel](/validation/data-panel/), long random-testing runs of several hours and the full comparison ([now, and before the first release](#levels-plan)); or a case of its record still fails, however small the miss;
- *validated*: every case of its record passes, and those extensive tests have been run;
- *stable*: validated, and its Python and command-line interface no longer change.

Since 2026-10-28 each port is tested as it is written: every code path once and the original's real use. The extensive tests wait for the final validation phase. From now on a port's part leaves it *experimental*, even where every case of its record agrees, and the final validation phase makes it *validated*. The ports marked *validated* before this definition ({{ data.programs.validated_before.date }}) keep their status, since every case of their record passed: ANTs' programs, which have their data panel since 2026-10-27, and others, among them most of AFNI's, sdcflows' and the replicas of `mcflirt` and `bet` (all of them below). The final validation phase gives them the rest of the evidence. Most ports since 2026-10-28 were left *experimental* even where every case agrees.

<p id="validated-before">Marked <em>validated</em> before {{ data.programs.validated_before.date }}, by software (<a href="{{ link('/programs/') }}">Programs</a>):</p>

{% for g in data.programs.validated_before.groups %}
- <span class="eco-chip eco-{{ g.id }}">{{ g.name }}</span> {{ g.text }}
{%- endfor %}

## Random testing {#random-testing}

The records test the cases people chose. Random testing runs random valid inputs and option combinations through each original program and its ports, in long runs of several hours: inputs drawn from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind) with options drawn in random combinations from those the program accepts, each case compared in the same way as in the records. A difference is shrunk to the smallest input and fewest options that still show it. A LARMORX mistake is fixed and the shrunk case kept as a permanent case of the comparisons; a defect of the original goes into the [register](repo:docs/findings/upstream-defects.md); a clean room's difference is reported with its reproducer ([how random testing works](repo:docs/validation/difftest.md)). From the next long run on, nine cases in ten are realistic (millimetre voxels of about 0.5 to 4 mm, the usual matrix sizes and options) and one in ten is drawn extreme (metres or micrometres, voxels of 0.01 to 50, labelled as such), and every case of a program whose memory has a known law is predicted before it runs: one predicted over its limit is checked as a guard case instead (LARMORX must stop at once with its clear error). The latest long run, program by program:

{{ ev.random_testing_summary() }}

## The records {#records}

Every record lives in the main repository, in [docs/validation](repo:docs/validation/): what was compared, the thresholds, the environment and every case. Benchmark reports are in [docs/benchmarks](repo:docs/benchmarks/). The stage-by-stage comparisons with fMRIPrep 25.2.6 on four of its runs are in the `fmriprep-stages` records.

## The data panel {#data-panel}

The fourteen datasets every program is to be shown on, why each is there, what each covers, its licence and citation, how its faces were checked and how to fetch it: [the data panel](/validation/data-panel/).
