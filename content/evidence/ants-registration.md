---
title: antsRegistration
kicker: Evidence · ANTs
lede: >-
  `antsRegistration` aligns one image with another through a sequence of stages, each a
  transform optimised against one or more metrics. LARMORX's port is a replica of ANTs 2.6.5's
  program on ITK 5.4.5, with every stage ANTs has (linear, SyN, B-spline SyN, B-spline,
  displacement-field, exponential and time-varying velocity-field) and every image and
  point-set metric. In `reproduce` it gives ANTs' exit status, output and files in every
  compared case of its two records once ANTs uses correctly rounded maths (399 of 399 and 71 of
  71). With ANTs as built, 355 of the 399 and 16 of the 71 match; the others differ only where
  glibc's `exp`, `log`, `sin` or `cos` is not correctly rounded. On sMRIPrep's own template
  registration it gives ANTs' one-thread result with correctly rounded maths on any number of
  threads.
description: >-
  How LARMORX's replica of ANTs' antsRegistration compares with ANTs 2.6.5: sMRIPrep's
  T1w-to-MNI registration of a real T1w with SyN, B-spline SyN and a time-varying velocity
  field, the displacement fields against ANTs' own variability between thread counts, the
  linear stages' parameters, the corrections and what they change, two calls of the data
  panel, and every case of the records with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: translated from ANTs 2.6.5's and ITK 5.4.5's source (Apache-2.0)</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span>, with its data panel (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/ants-registration.md') }}">standard comparison</a>, <a href="{{ repo('docs/validation/ants-registration-full.md') }}">full comparison</a> (<a href="{{ repo('docs/validation/ants-registration-velocity-full.md') }}">its velocity-field cases</a>), <a href="{{ repo('docs/validation/ants-registration-corrections.md') }}">the corrections' effects</a>, <a href="{{ repo('docs/validation/ants-registration-panel.md') }}">data panel</a> (<a href="{{ repo('docs/validation/ants-registration-panel-template.md') }}">its template registrations at full size</a>), all against ANTs 2.6.5</dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/ants-registration.md') }}">ants-registration</a></dd>
</dl>

## What is compared {#what-it-is}

`antsRegistration` aligns a moving image with a fixed one through a sequence of stages, each a transform (rigid, affine, SyN, velocity fields and others) optimised against one or more metrics over a schedule of resolutions. sMRIPrep uses it for the brain extraction and the registration to the MNI template, fMRIPrep for the BOLD reference and the field map's registration.

The replica runs beside ANTs 2.6.5's `antsRegistration` on the same files with the same arguments. ANTs is the repository's build (GCC 14.3), run as built and with correctly rounded maths, at one thread and at 2, 4 and 8 for its own variability.

```bash
larmorx ants antsRegistration -d 3 -o '[t1_to_mni_,t1_to_mni_Warped.nii.gz]' -t 'Rigid[0.05]' -m 'Mattes[mni.nii.gz,t1w.nii.gz,1,56,Regular,0.25]' -c '[100x100,1e-6,20]' -f 2x1 -s 2x1vox -t 'SyN[0.1,3,0]' -m 'CC[mni.nii.gz,t1w.nii.gz,1,4]' -c '[100x70x50x20,1e-6,10]' -f 8x4x2x1 -s 3x2x1x0vox
```

```python
import larmorx as lx

rigid = lx.ants.RegistrationStage(
    transform="Rigid", gradient_step=0.1,
    metrics=lx.ants.RegistrationMetric("Mattes", "fixed.nii.gz", "moving.nii.gz",
                                       bins=32, sampling="Regular", sampling_percentage=0.25),
    iterations=[1000, 500, 250], shrink_factors=[4, 2, 1], smoothing_sigmas=[2, 1, 0],
)
tvf = lx.ants.RegistrationStage(
    "TimeVaryingVelocityField", 0.5, lx.ants.RegistrationMetric("CC", "fixed.nii.gz", "moving.nii.gz", radius=4),
    iterations=[100, 70, 50, 20], shrink_factors=[8, 4, 2, 1], smoothing_sigmas=[3, 2, 1, 0],
    number_of_time_indices=4, update_field_variance=3.0,
)
res = lx.ants.registration([rigid, tvf], warped=True, random_seed=42)
```

The [API page](repo:docs/api/ants-registration.md) maps every option and stage. How to read what follows: [how to read the evidence](/validation/#reading).

### Its port {#ports}

ANTs and ITK come under the Apache-2.0 licence, as LARMORX does, so the replica is in `larmorx` itself. It is translated from ANTs' and ITK's source, step by step, to give their results bit for bit. A clean room of ANTs' programs is planned after FreeSurfer ([roadmap](/roadmap/)).

The replica computes the C library's maths (`exp`, `log`, `sin`, `cos`) correctly rounded, the same on every platform. Where glibc's are not correctly rounded for a value a run meets, ANTs as built differs from the replica, and a registration's iterations carry the change on.

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-registration', 'port') }}

In `reproduce`, every case that runs gives ANTs' exit status, standard output with every iteration's DIAGNOSTIC line, standard error and every file: the unmodified binary's at one thread, or, where glibc's `exp`, `log`, `sin` or `cos` is not correctly rounded for a value the run meets, the same binary's with CORE-MATH's correctly rounded functions preloaded. The other cases are inputs both programs refuse (93) and expected divergences (21): crashes of ANTs that the replica refuses with a message, and ANTs' samplings seeded from the clock. No case is open.

## In sMRIPrep: a real T1w registered to MNI space {#example}

fMRIPrep's own registration of a T1w to MNI152NLin2009cAsym, run on every third voxel of its images as the standard comparison runs it (a full-size run takes ANTs about an hour at one thread; the full comparison and the data panel run it whole). Choose the output: the warped T1w, or one component of the displacement field that SyN found. *Checkerboard* and *Swipe* (under *Compare*) set the template against the warped T1w; the difference panels set the replica against ANTs as built next to ANTs against itself at 8 threads, on one scale.

{{ ev.example('ants-registration', 'template-syn') }}

{{ ev.example('ants-registration', 'template-bsplinesyn') }}

## A velocity-field registration {#velocity}

The same command with its SyN stage replaced by a time-varying velocity field: the deformation is the flow of a velocity field over space and four time points, integrated from time 0 to 1 by fourth-order Runge–Kutta, and its inverse the flow back. ANTs has no script that sets this stage, so it takes SyN's levels, iterations, metric and smoothing. The exponential stages (a stationary velocity field, its displacement the exponential by scaling and squaring) and the time-varying B-spline field are in the record the same way, on the same images.

{{ ev.example('ants-registration', 'template-tvf') }}

## Against the original's own variability {#variability}

ANTs' result moves with its thread count: its metrics add up partial sums per thread, in an order that depends on the threads. The record measures this variability, ANTs at 2, 4 and 8 threads against its own one-thread result, and gives for each case the replica's distance from ANTs at one thread.

{{ ev.dots('ants-registration', 'band') }}

## The corrections, and what they change {#corrections}

Where ANTs has a deterministic defect that changes a result, the replica corrects it by default, `fix`, and warns. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives ANTs' behaviour, and every comparison above runs with it. The record's list of what `fix` changed names, case by case, the corrections a command meets and what they change; none applies to sMRIPrep's commands above. The corrections change the point-set metrics, the B-spline field meshes and what can follow a B-spline transform; each was measured on phantoms whose answer is known, or against the closest runs ANTs can do ([findings](repo:docs/findings/ants-velocity.md#the-corrections-decided-on-2026-10-21-and-what-they-change)).

{{ ev.table('ants-registration', 'corrections-igdm') }}

{{ ev.table('ants-registration', 'corrections-jhct') }}

{{ ev.table('ants-registration', 'corrections-mesh') }}

ANTs cannot run a stage after a B-spline transform (ITK-35), so the last table sets the corrected stage against the two closest runs ANTs can do: the same stage on the moving image resampled through the B-spline transform, and ANTs given the B-spline transform sampled as a displacement field (at half its control-point spacing) as its initial transform. The field is close for two B-spline stages (a quarter of a millimetre: the field's sampling). For a linear stage it is not, because ITK takes a field's Jacobian from its nearest voxel and the linear stage stops early; the replica given the same field stops with it, identically. That reference also varies from run to run: a linear stage after a displacement field estimates its parameter scales and learning rate from 1000 voxels that ITK draws with a generator seeded from the clock, whatever the seed (ANTS-72; with `time` and `clock` fixed by a preloaded library, every run is identical). The record therefore runs it five times and gives the median, and the last column how far ANTs' own runs are apart.

{{ ev.table('ants-registration', 'corrections-chain') }}

**A reference that varies:** for the linear stages after a B-spline transform, read the "with the field" columns as the median of a varying reference, next to its own spread: ANTs' runs with the field as initial transform are several millimetres apart from each other (the last column), as far as they are from the replica. The replica's results and the reference on the resampled image are identical from run to run.

## On the data panel {#data-panel}

The [data panel](/validation/data-panel/) is the fixed set of fourteen OpenNeuro subjects on which LARMORX's programs are validated: 1.5, 3 and 7 T; Siemens, GE and Philips; single-band, multiband and multi-echo BOLD; a 3.5-year-old to an 82-year-old; a tumour, a stroke with its lesion mask, strong motion. Its record replays every call fMRIPrep 25.2.6 made of the program in its fourteen runs on these subjects, the node's own `command.txt` with its inputs from the run's working directory (calls repeated word for word are compared once), and runs the program on panel images fMRIPrep never gives it. ANTs runs at one thread, as built and with correctly rounded maths, and at 2 and 3 threads for its own variability where it has any; the replica in `reproduce`, and in `fix` for the corrections. The panel's cases are in the case explorer below (the categories *data panel: fMRIPrep's calls* and *data panel: fMRIPrep's calls, every third voxel*).

**71 of 71 compared cases identical to ANTs with correctly rounded maths, 16 of them as built**: every `antsRegistration` node of the fourteen runs with fMRIPrep's seed (the BOLD references' registrations to the template, the field maps' coregistrations, sMRIPrep's brain extraction at full size) and the whole template registrations on every third voxel. At full size, about 2.4 hours of ANTs at one thread each, the fourteen template registrations have [their own record](repo:docs/validation/ants-registration-panel-template.md): 14 of 14 identical to ANTs with correctly rounded maths. The template registration's inputs, which niworkflows writes for itself and nipype does not keep, are made again exactly from each node's recorded inputs. In `fix` the replica corrects ITK-31 in sMRIPrep's brain extractions, whose SyN stage has a fixed mask only: the panel's record names it in 28 cases, and their values change ([register](repo:docs/findings/upstream-defects.md)).

{{ ev.table('ants-registration', 'panel-nodes') }}

Images on a small grid (a BOLD reference, a template at 2 mm) are shown as whole volumes; the panel's large anatomical images (up to 17.5 million voxels) as three full-resolution slices through the voxel where the replica and ANTs as built differ most (the centre of the field of view where they agree), the whole field of view shown, defaced heads included (the data panel's defacing check).

{{ ev.example('ants-registration', 'panel-boldref-7t') }}

{{ ev.table('ants-registration', 'panel-boldref-7t-transforms') }}

{{ ev.example('ants-registration', 'panel-coregister-philips') }}

{{ ev.table('ants-registration', 'panel-coregister-philips-transforms') }}

## Every case {#cases}

Each case of the two records, the standard comparison and the data panel, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('ants-registration') }}

## Speed {#speed}

No benchmark report yet: the benchmark of `antsRegistration` is pending ([next steps](repo:docs/next-steps.md)).

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original and the replica, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a case of the record, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/tools/ants-registration/', 'ants-registration') }}

## Known limits {#limits}

- MINC transform files are refused with a message.
- The expected divergences: without a seed ANTs seeds its sampling from the clock (the replica uses a fixed seed), and so do three of the velocity-field stages whatever the seed (ANTS-82) and a linear stage after a displacement field (ANTS-72); crashes and reads of unwritten memory are not reproduced (ANTS-51, ANTS-66, ANTS-77); messages ANTs prints only with `--verbose` (ANTS-45).
- A stage after a B-spline transform runs in the replica (ITK-35, corrected), not in ANTs; give it a mask: the B-spline transform is the identity outside its valid region, so the composite jumps at that border.
- The comparison with ANTs is made on Linux x86-64; the cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output.

## History {#history}

- **2026-10-21**: the corrections of the point-set metrics, the B-spline field meshes and the stages after a B-spline transform decided, each measured ([findings](repo:docs/findings/ants-velocity.md#the-corrections-decided-on-2026-10-21-and-what-they-change)).
- **2026-10-27**: the data panel's record, every `antsRegistration` node of the fourteen runs and the template registrations on every third voxel.
- **2026-10-28**: the standard comparison made again, with eight cases from random testing; the fourteen template registrations of the data panel at full size.
