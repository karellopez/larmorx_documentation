---
title: Validation
kicker: Documentation
lede: How every LARMORX tool is compared with the original program, how to read the evidence on its page, what each verdict means, and where every tool stands.
description: How LARMORX tools are validated against the original programs (ANTs, AFNI, FSL, fMRIPrep, nibabel), how to read the worked examples and metrics, the verdict taxonomy, and a summary of every tool.
evidence: true
wide: true
---

## The method {#method}

**The original program is the oracle.** Each LARMORX tool is run beside the program it reimplements, on the same files with the same arguments, and their outputs, exit statuses and messages are compared. The originals are exact builds of the pinned releases: ANTs 2.6.5 on ITK 5.4.5, built by the repository's script with GCC 14.3 (older GCCs drop float roundings the source asks for, so the build matters), AFNI 25.2.09, FSL 6.0.7, nibabel, and fMRIPrep 25.2.6 itself, run on real datasets with its own image. Where the original's result depends on how it runs, its own variability is measured too: ANTs at 1 to 12 threads, another build or version of the same program, and the original with CORE-MATH's correctly rounded maths library preloaded in place of glibc's.

**Three ways of reimplementing.** A *port* translates source whose licence allows it (ANTs, ITK) and aims at the original's bits. Where the licence restricts the source (AFNI's MCW code, FSL, Workbench), there are two: an exact *replica* in a separate package under the original's licence (`larmorx-gpl` for AFNI), which aims at the original's bits, and a *clean-room original* in LARMORX itself (Apache-2.0), written without the source, from a behavioural specification, which aims at the original's behaviour within stated thresholds and at speed ([licensing](repo:docs/licensing.md)). Every AFNI tool so far has both.

**Default and reproduce modes.** When an original has a deterministic defect that changes its results, LARMORX corrects it by default and warns; `upstream_defects="reproduce"` (on the command line `LARMORX_UPSTREAM_DEFECTS=reproduce`) gives the original's result, defect included. The parity records compare in reproduce mode, so they compare with the original as it is; every defect is in the [register](repo:docs/findings/upstream-defects.md).

**Corrections checked against known results.** Where a correction's result can be computed
another way (SciPy's morphology, NumPy, or the original program itself on an input where its
defect cannot arise), the record checks LARMORX's default against it, bit for bit; such a case
carries the verdict *deliberate correction*, and its comparison with the original, in reproduce
mode, is bit for bit like every other. Where an input makes no sense and the original silently
does something arbitrary (AFNI-41, AFNI-48), LARMORX refuses it by default with a message naming
the defect, and reproduce mode gives the original's result.

**Parity tiers.** Each tool's suite of cases runs in tiers: *smoke* under pytest, *standard* for the records quoted on this site (fMRIPrep's, sMRIPrep's and sdcflows' own command lines on real data, every option, generated edge cases, the invalid inputs), *full* where a tool has more. Parity needs the originals, so it runs on a Linux x86-64 workstation, never in continuous integration.

```bash
pytest tests/parity                                                    # the smoke tier
python -m larmorx_validation parity ants-n4 --tier standard --out docs/validation
```

**Golden tests on six platforms.** Every function's output on small generated inputs is checked, bit for bit, against LARMORX's own Linux x86-64 output on Linux (x86-64, aarch64), macOS (Intel, Apple silicon) and Windows (x64, arm64), in continuous integration ([golden tests](repo:docs/validation/golden.md)). So a comparison made on Linux holds on every platform.

## How to read the evidence {#reading}

Each tool's page under [Tools](/tools/) leads with its record's cases by verdict, then shows **worked examples** on real data:

- **What was run, on what.** The dataset and subject, the exact command (fMRIPrep's own, read from its working directory, where the pipeline calls the tool), and every program with its version, build, thread count and mode.
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

## The records {#records}

Every record lives in the main repository, in [docs/validation](repo:docs/validation/): what was compared, the thresholds, the environment and every case. Benchmark reports are in [docs/benchmarks](repo:docs/benchmarks/). The stage-by-stage comparisons with fMRIPrep 25.2.6 on four oracle runs are in the `fmriprep-stages` records.
