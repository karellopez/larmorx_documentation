---
title: Validation
kicker: Documentation
lede: How every LARMORX tool is compared with the original program, how to read the evidence on its page, what each verdict means, and where every tool stands.
description: How LARMORX tools are validated against the original programs (ANTs, AFNI, FSL, fMRIPrep, nibabel), how to read the worked examples and metrics, the verdict taxonomy, and a summary of every tool.
evidence: true
wide: true
---

## The method {#method}

**The original program is the oracle.** Each LARMORX tool is run beside the program it reimplements, on the same files with the same arguments, and their outputs, exit statuses and messages are compared. The originals are exact builds of the pinned releases: ANTs 2.6.5 on ITK 5.4.5, built by the repository's script with GCC 14.3 (older GCCs drop float roundings the source asks for, so the build matters), AFNI 26.3.05 (25.2.09 for the clean-room originals until they follow it), FSL 6.0.7, nibabel, and fMRIPrep 25.2.6 itself, run on real datasets with its own image. Where the original's result depends on how it runs, its own variability is measured too: ANTs at 1 to 12 threads, another build or version of the same program, and the original with CORE-MATH's correctly rounded maths library preloaded in place of glibc's.

**Three ways of reimplementing.** A *port* translates source whose licence allows it (ANTs, ITK) and aims at the original's bits. Where the licence restricts the source (AFNI's MCW code, FSL, Workbench), there are two: an exact *replica* in a separate package under the original's licence (`larmorx-gpl` for AFNI, `larmorx-nc` for FSL), which aims at the original's bits, and a *clean-room original* in LARMORX itself (Apache-2.0), written without the source, from a behavioural specification, which aims at the original's behaviour within stated thresholds and at speed ([licensing](repo:docs/licensing.md)). Every AFNI tool so far has both, and so has head-motion correction (FSL's mcflirt).

**Default and reproduce modes.** When an original has a deterministic defect that changes its results, LARMORX corrects it by default and warns; `upstream_defects="reproduce"` (on the command line `LARMORX_UPSTREAM_DEFECTS=reproduce`) gives the original's result, defect included. The parity records compare in reproduce mode, so they compare with the original as it is; every defect is in the [register](repo:docs/findings/upstream-defects.md).

**Corrections checked against known results.** Where a correction's result can be computed
another way (SciPy's morphology, NumPy, or the original program itself on an input where its
defect cannot arise), the record checks LARMORX's default against it, bit for bit; such a case
carries the verdict *deliberate correction*, and its comparison with the original, in reproduce
mode, is bit for bit like every other. Where an input makes no sense and the original silently
does something arbitrary (AFNI-41, AFNI-48), LARMORX refuses it by default with a message naming
the defect, and reproduce mode gives the original's result.

**Parity tiers.** Each tool's suite of cases runs in tiers: *smoke* under pytest, *standard* for the records quoted on this site (fMRIPrep's, sMRIPrep's and sdcflows' own command lines on real data, every option, generated edge cases, the invalid inputs), *full* where a tool has more. Parity needs the originals, so it runs on a Linux x86-64 workstation, never in continuous integration. Every level of testing, and when each runs, is under [Levels of testing](#levels).


**One data panel for every tool.** Since 2026-10-24 every tool is to be validated, and shown, on
the same fourteen shareable datasets: 1.5, 3 and 7 T; Siemens, GE and Philips; single-band,
multiband, multi-echo and sparse BOLD; every kind of field map; children, older adults, a
tumour and a stroke; head motion and low quality ([Data panel](/data-panel/)). The finished
tools are re-validated on it one by one. The ANTs tools are re-validated on the panel (2026-10-27): every
page has a section *On the data panel* with fMRIPrep's calls of the fourteen oracle runs and the
panel's own images.

```bash
pytest tests/parity                                                    # the smoke tier
python -m larmorx_validation parity ants-n4 --tier standard --out docs/validation
```

**Golden tests on six platforms.** Every function's output on small generated inputs is checked, bit for bit, against LARMORX's own Linux x86-64 output on Linux (x86-64, aarch64), macOS (Intel, Apple silicon) and Windows (x64, arm64), in continuous integration ([golden tests](repo:docs/validation/golden.md)). So a comparison made on Linux holds on every platform.

## Levels of testing {#levels}

Each level of testing answers one question. The levels that compare LARMORX with an original
program need that program, so they run on a Linux x86-64 workstation; the levels that need no
original run in continuous integration on all six platforms. Every run of an original program is
computed once and kept by the content of its inputs, so a later comparison re-runs only LARMORX.

| Level | The question it answers | What it runs | Where |
|---|---|---|---|
| **Unit tests** | Does each part of the code do what it should? | The Rust and Python test suites, formatting, lints and licence headers | Continuous integration, six platforms, every change |
| **Golden tests** | Does LARMORX give the same bits on every platform? | Every function on small generated inputs (at most 32³ voxels; no image data stored), checked against the checksums of LARMORX's own Linux x86-64 output | Continuous integration, six platforms, under a minute each |
| **Parity, smoke** | Does every tool still agree with its original? | A few cases of every tool, and every permanent case found by random testing | Workstation, at every merge, about ten minutes |
| **Parity, standard** | Does the tool reproduce its original, option by option? | Every option and code path; every data type, unusual header and size; the edge cases of every defect found; invalid inputs; fMRIPrep's, sMRIPrep's and sdcflows' own command lines on real data. This is the record each tool's page shows | Workstation, when a tool is ported or updated |
| **Parity, full** | Does it hold on more and larger cases? | Whole real images, more option combinations and thread counts | Workstation |
| **Data panel** | Does it hold on the hardest real data? | The fourteen datasets of the [Data panel](/data-panel/), with fMRIPrep's calls in its fourteen runs on them | Workstation |
| **Random testing** | Does it agree on inputs nobody chose? | Random valid inputs generated from a seed (phantoms, small crops of real templates, every orientation, data type and value range; nine cases in ten realistic) with random option combinations; a short trial or a whole night ([below](#random-testing)) | Workstation |
| **Heavy random cases** | Does it agree on random inputs too large for a night? | The random cases whose outputs need more memory than a night allows, each run to its end in a larger memory limit | Workstation, or a larger machine |
| **The original's own variability** | What does "the same result" mean for this program? | The original at several thread counts, in another build or version, and with correctly rounded maths | Workstation, with each record |
| **Memory and threads** | Does LARMORX need no more memory than the original, whatever the thread count? | Peak memory against the original's on the same call (at most 10 % above it, plus 8 MiB); every parallel path kept to the thread count it is given, its result independent of it | Workstation, under pytest |
| **Speed** | How much faster is a clean-room original? | Benchmarks against the original and the replica ([benchmarks](repo:docs/benchmarks/)) | Workstation |
| **Independent review** | Does a second reader find anything? | A review of a large port's code and records by someone who did not write them | The final validation phase |
| **Comparisons with fMRIPrep** | Does a pipeline built on LARMORX reproduce fMRIPrep? | Stage by stage and end to end, against fMRIPrep's own runs | Workstation |

### Now, and before the first release {#levels-plan}

Since 2026-10-28 LARMORX is tested in two stages. Each tool, as it is ported or follows a new
release of its original, is tested where it matters: every code path once and the original's
real use, so that it is published with its record and its page. Once every tool is ported, one
final validation phase adds the extensive testing to every tool at once; each tool's page then
grows with the new evidence, and nothing it already shows is removed.

| Level | Each tool, as it is ported or updated | The final validation phase, once every tool is ported |
|---|---|---|
| **Unit and golden tests** | Every change; at least one golden case for every function | Every change |
| **Parity, smoke** | At every merge | At every merge |
| **Parity, standard** | The tool's record and page, with fMRIPrep's real calls on about three of its runs | Kept current with every update |
| **Parity, full** | Where a tool has it (antsRegistration, antsAI, antsAffineInitializer, Atropos, the mcflirt and BET replicas) | Every tool |
| **Data panel** | Only the panel runs whose fMRIPrep calls the record already uses | Every tool (the ANTs tools since 2026-10-27) |
| **Random testing** | A 30-minute trial; every difference triaged: a LARMORX mistake fixed and kept as a permanent case, a defect of the original registered | Whole nights for every tool, repeated |
| **Heavy random cases** | Not part of a tool's testing (the first night's run in the background) | Every tool, each case to its end |
| **The original's own variability** | With the record | Wider studies across thread counts |
| **Memory and threads** | Each tool's calls added to the memory and thread checks | Speed and memory studies beyond the rule's check |
| **Speed** | Each clean-room original | Speed and memory studies |
| **Independent review** | — | Every large port |
| **Comparisons with fMRIPrep** | — (stage by stage on four runs with fMRIPrep 25.2.6, done) | Stage by stage and end to end, with the newest fMRIPrep |

**New releases of the originals.** LARMORX follows the newest release of each original program.
When one comes out, the replica follows it, then the clean-room original, with the same testing as
a port; the record lists the cases where the original's own output changed between the two
releases, each with its reason. AFNI 25.2.09 to 26.3.05 was the first (2026-10-29): on the
3dTshift, 3dAutomask and 3dUnifize pages, every example shows both releases.

## How to read the evidence {#reading}

Each tool's page under [Tools](/tools/) leads with its record's cases by verdict, then shows **worked examples** on real data:

- **What was run, on what.** The dataset and subject, the exact command (fMRIPrep's own, read from its working directory, where the pipeline calls the tool), and every program with its version, build, thread count and mode.
- **Whole volumes, and three slices for panel cases.** Every example is a whole volume, except
  cases from the data panel beyond a tool's key datasets: those show three full-resolution
  slices, one per plane, through the voxel where the comparison differs most (the example says
  so under its panels). Every metric is over every voxel of the files either way. Every example
  carries the credit line of the data it shows, and every page ends with its data credits.
- **The image viewer.** Each panel is labelled with exactly what it is: an input, the original program's output (as built, with correctly rounded maths, at another thread count), fMRIPrep's own output, LARMORX's output (replica or clean-room original, default or reproduce mode). Choose the plane, slice and volume, zoom and pan, set the intensity window; select a point to read every panel's exact value there. Compare two images side by side, by swiping or blinking between them, or in a checkerboard.
- **Differences.** A difference panel shows A − B on a symmetric scale whose range is printed, blue below zero and apricot above, linear or logarithmic; differences shown together share one scale, so LARMORX's difference sits next to the original's own variability on the same footing. A difference that is zero everywhere says *bit-identical*; *Go to the largest difference* finds where they differ most.
- **The chain of causes.** Where LARMORX and fMRIPrep's output differ, the runs between them are lined up, each step changing one thing (threads, maths library, version), so the cause of every difference is shown, not asserted.
- **Metrics.** One row per comparison, computed offline in float64 over every voxel of the outputs: the largest |Δ|, how many values differ, the RMS of Δ, the largest |Δ| relative to the image's range, 1 − the normalised cross-correlation. Each comparison of LARMORX with an original gets a verdict and its reason, with links to the finding or register entry; the rows *the original against itself* are the yardstick. Provenance (inputs with their checksums, the commands, the commit) is under each example.
- **Every case.** The case explorer lists every case of the records: what it tests, its command line, its verdict (one per implementation) and reason. Search, filter, sort, and link to one case with `#case=<name>`.

Everything is computed by the main repository's code from its committed records and from cached runs of the original programs ([docs/figures.md](repo:docs/figures.md)); the site only displays it, and a check compares every number a page shows with the data it comes from.

## The verdicts {#verdicts}

One taxonomy for the whole site. Every comparison of LARMORX with an original, and every case of a record, gets exactly one of these verdicts. Each is drawn with its colour, its pattern and its name, never colour alone.

{{ ev.taxonomy() }}

## Where every tool stands {#summary}

Every tool ported so far, each implementation, and how many cases of its record have each verdict, each case's verdict decided from what its record reports and measures.

{{ ev.matrix(site.tools) }}

## Random testing {#random-testing}

The records test the cases people chose. Random testing runs, a night at a time, random valid inputs and option combinations through each original program and LARMORX: inputs drawn from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind) with options drawn in random combinations from those the program accepts, each case compared by the same runners as the records. A difference is shrunk to the smallest input and fewest options that still show it; a LARMORX mistake is fixed and the shrunk case kept as a permanent parity case, a defect of the original goes into the [register](repo:docs/findings/upstream-defects.md), a clean-room original's difference is reported with its reproducer ([how random testing works](repo:docs/validation/difftest.md)). From the next night on, nine cases in ten are realistic (millimetre voxels of about 0.5 to 4 mm, the usual matrix sizes and options) and one in ten is drawn extreme (metres or micrometres, voxels of 0.01 to 50, labelled as such), and every case of a tool whose memory has a known law is predicted before it runs: one predicted over its limit is checked as a guard case instead (LARMORX must stop at once with its clear error). The latest night, tool by tool:

{{ ev.random_testing_summary() }}

## The records {#records}

Every record lives in the main repository, in [docs/validation](repo:docs/validation/): what was compared, the thresholds, the environment and every case. Benchmark reports are in [docs/benchmarks](repo:docs/benchmarks/). The stage-by-stage comparisons with fMRIPrep 25.2.6 on four oracle runs are in the `fmriprep-stages` records.
