---
title: topup and applytopup
kicker: Evidence · FSL
lede: >-
  `topup` estimates the off-resonance field that displaces echo-planar images along their phase
  encoding, from images acquired with opposite phase encodings, and `applytopup` corrects images
  with it; fMRIPrep runs topup for every reversed-phase-encoding (PEPOLAR) field map. The replica
  (`larmorx-nc`) gives FSL 6.0.7.23's files, messages and exit status byte for byte in all 107 of
  its compared cases, out of 177, fMRIPrep's own calls among them. The clean room (`larmorx`) is
  within its record's thresholds in all 106 of its compared cases, out of 187, and 14 more are
  expected divergences, each with its reason. On fMRIPrep's two calls it is as close to FSL as FSL
  at another thread count, but for the field's correlation on ds005040 (0.999958, against FSL's
  own 0.999966), and it runs 10 to 12 times as fast as FSL on one thread, about 40 times on 14.
description: >-
  How LARMORX's two ports of FSL's topup and applytopup, a replica and a clean room, compare with
  FSL 6.0.7.23: fMRIPrep's field-map estimation on two real reversed-phase-encoding pairs with
  every file topup writes and fMRIPrep's own outputs, FSL's own thread band as the yardstick, a
  correction by default inside topup, the movements estimated, applytopup's least-squares
  restoration, Jacobian modulation and vb3D, every case of both records with its verdict, three
  random-testing runs with the clean room's triage, and the speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx-nc</code> <span class="port-licence">FSL Licence: non-commercial use only</span>: translated from FSL 6.0.7.23's source (fsl-topup 2203.5, with fsl-basisfield, fsl-warpfns and fsl-miscmaths' optimisers and sparse matrices); it runs as a separate program</li>
<li class="port port--clean-room"><span class="port-name">clean room</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: crate <code>larmorx-fsl</code>, written from <a href="{{ repo('specs/topup.md') }}">specs/topup.md</a>, the topup papers, FSL's user guides and runs of FSL 6.0.7.23, without FSL's source (2026-11-03; brought up to the specification's answers on 2026-11-05)</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--experimental">experimental</span>; clean room <span class="status-tag status-tag--experimental">experimental</span></dd>
<dt>Records</dt><dd>the replica's: <a href="{{ repo('docs/validation/fsl-topup-replica.md') }}">standard comparison</a> (FSL 6.0.7.23) · the clean room's: <a href="{{ repo('docs/validation/fsl-topup.md') }}">standard comparison</a> (FSL 6.0.7.23) · benchmark <a href="{{ repo('docs/benchmarks/fsl-topup.md') }}">fsl-topup</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/fsl-topup.md') }}">fsl-topup</a></dd>
</dl>

## What is compared {#what-it-is}

An echo-planar image is displaced along its phase-encoding axis wherever the magnetic field departs from its nominal value: by the off-resonance (in Hz) times the read-out time, in voxels. Its intensity is compressed or stretched by the displacement's Jacobian. Two images with opposite phase encodings are displaced in opposite directions, so the field that makes them agree can be estimated.

topup models the field as a cubic (or quadratic) B-spline. It resamples each image through the displacement the field gives it (and, with `--estmov`, through its own rigid-body movement), multiplies by the Jacobian, and minimises the squared differences between the corrected images plus a regularisation of the field's bending energy (or membrane energy), weighted by `--lambda`. It works level by level, each level with its knot spacing (`--warpres`), subsampling, smoothing and number of iterations, by Levenberg-Marquardt or scaled conjugate gradients.

It writes the field's coefficients and the movements (`--out`). On request it also writes the corrected images (`--iout`), the field in Hz (`--fout`), each image's displacement field (`--dfout`), rigid-body matrix (`--rbmout`) and Jacobian (`--jacout`), and a log. applytopup corrects other images with topup's result: by Jacobian modulation of each image alone (`--method=jac`), by the least-squares restoration of pairs with opposite phase encodings into one image (`lsr`, the default), or by one of three undocumented variational Bayes restorations (`vb2D`, `vb3D`, `vb4D`).

fMRIPrep calls topup for every reversed-phase-encoding field map, in sdcflows' PEPOLAR workflow (`fmap_preproc_wf/<estimator>/topup`). It gives topup the average of each phase encoding's images, merged into one series, with sdcflows' configuration `b02b0.cnf` (seven levels from 14 mm to 4 mm knots, without movements): `topup --config=b02b0.cnf --datain=<encoding file> --imain=<merged pair> --out --iout --fout --jacout=jac --logout --rbmout=xfm --dfout=warpfield`. sdcflows turns the coefficients into the field map fMRIPrep uses. fMRIPrep does not call applytopup: its own resampler applies the field.

The two ports run beside FSL 6.0.7.23's `topup` and `applytopup` on the same files with the same arguments. fMRIPrep's own outputs are the files it wrote in its run, with topup in fMRIPrep 25.2.6's image.

```bash
larmorx fsl topup --imain=b0_pair --datain=acqparams.txt --config=b02b0.cnf --out=tu --fout=field --iout=corrected
larmorx fsl applytopup --imain=dwi_up,dwi_dn --inindex=1,2 --datain=acqparams.txt --topup=tu --out=hifi
```

The first estimates the field from a pair and writes it with the corrected pair. The second corrects two images of opposite phase encodings with that result.

```python
import larmorx as lx

acq = [[0, 1, 0, 0.0138], [0, -1, 0, 0.0138]]   # phase-encoding vector and read-out time (s)
r = lx.fsl.topup("b0_pair.nii.gz", acq, config="b02b0.cnf", fsldir="/opt/fsl", corrected=True)
field_hz = r.field                     # lx.Image on the input's grid
hifi = lx.fsl.applytopup(["dwi_up.nii.gz", "dwi_dn.nii.gz"], acq, [1, 2], r).corrected
```

The calls above leave `implementation` at `"auto"`. The [API page](repo:docs/api/fsl-topup.md) describes every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its two ports {#ports}

FSL comes under the FSL Licence, which allows non-commercial use only. So LARMORX has two ports of its FSL programs. The replica is translated from FSL's source and lives in its own package, `larmorx-nc` (`pip install larmorx-nc`). The clean room is in `larmorx` itself. It is written without FSL's code, from topup's behavioural specification ([specs/topup.md](repo:specs/topup.md)), the papers (Andersson, Skare and Ashburner 2003; Smith et al. 2004), FSL's user guides and runs of FSL's programs as a black box.

`implementation="auto" | "replica" | "clean-room"` chooses between them (`"original"` in 0.1.0rc1). On the command line, `larmorx --implementation clean-room fsl topup ...` does the same from the next release; in 0.1.0rc1 it is the environment variable `LARMORX_IMPLEMENTATION`. `auto`, and `larmorx fsl topup`, take the replica when `larmorx-nc` is installed, else the clean room.

The replica follows FSL 6.0.7.23. It runs none of FSL's programs and needs no FSL installation; FSL's configurations by name need its `etc/flirtsch` folder, or `fsldir`. The FSL libraries topup needs are translated once into `larmorx-nc`'s shared core, beside those of mcflirt, BET, FLIRT and FAST: the B-spline fields with their bending- and membrane-energy regularisers, the sparse matrices, the non-linear optimisers, the warps, the spline interpolation with its derivatives, and LAPACK's and OpenBLAS's arithmetic as FSL's build calls it.

The clean room has every option, message, exit status and failure case of both programs: the configuration files, both minimisers per level, both regularisers, both spline orders, the precisions and interpolations, the movements, every output, `--debug`, `--trace` and `--profile`, and applytopup's `jac`, `lsr`, `vb2D`, `vb3D` and `vb4D`. It computes `sin`, `cos` and `exp` correctly rounded on every platform. It is built for speed, and its result is the same bits at any thread count ([speed](#speed)):

- the B-spline field's products run along whole lines and planes;
- the Levenberg-Marquardt steps are solved by preconditioned conjugate gradients on the Hessian stored by its diagonals;
- the arrays are recycled, and every parallel loop runs in fixed blocks summed in a fixed order.

Where the specification leaves a convention open, the clean room follows FSL's as black-box runs measured it:

- an oblique phase encoding wraps along no axis;
- the scaled conjugate gradients' second gradient keeps the current point's regulariser weight;
- `--debug`'s images are written in FSL's order.

**The C library's last digits (since 2026-11-04).** topup smooths the images at each level of its schedule (`--fwhm`) with a Gaussian whose weights FSL computes with glibc's `exp`. glibc is the C library of Linux, and its results are now and then one unit in the last place away from the exact value rounded once. LARMORX computes `exp` correctly rounded, the same on every platform. Since 2026-11-04 the clean room's `reproduce` computes it exactly as glibc 2.35 does, and its default, `fix`, correctly rounded. That is GLIBC-07 in the [register](repo:docs/findings/upstream-defects.md), and topup names it nowhere: whether a fit moved with such last bits cannot be told without running it twice (a decision of the project of 2026-11-04, recorded with GLIBC-07). On topup it changed no value. The weights are kept in single precision, no number moved on any case of the record, and the two modes still agree on fMRIPrep's calls.

**The clean-room catch-up (2026-11-05).** The specification's answers of 2026-11-03 ([specs/topup.md](repo:specs/topup.md) §13) are now in the clean room, and every example below was run again with it.

- Its `reproduce` takes FSL's forward differences of single-precision rotation matrices for the movements' derivatives (FSL-201): the first gradients of FSL's `--debug` files to 2 × 10<sup>−5</sup> and 10<sup>−6</sup>. Its default keeps the exact derivatives and names FSL-201 on every run that estimates the movements.
- Its `reproduce` lays FSL-145's coefficient count exactly, and stops with FSL's error where a level refits a single coefficient. It follows FSL-133's index on lines whose length does not divide 2<sup>32</sup>, and lays FSL-134's field of another shape as FSL does.
- In `fix` and in `reproduce`, the regulariser samples the quadratic B-splines' bending energy as FSL does, the spline prefilter starts from FSL's truncated sums on short axes, and applytopup's least-squares restoration builds its matrices row by row as FSL walks them.
- The record's cases that FSL-133, FSL-134 and FSL-145 kept apart now pass.
- Random testing after the catch-up found one more defect of FSL, registered and corrected by default: FSL-242, a level of scaled conjugate gradients whose last step is rejected ends at that worse point. It also found that FSL counts every such iteration toward `--miter`, which the clean room now does too ([below](#random)).

## The verdicts at a glance {#verdicts}

The replica is a translation of FSL's source, so the question for it is whether it gives FSL's bytes: every file topup and applytopup write (each image's header and data, the coefficients, the movements, the matrices, the log), their standard output and error, and their exit status.

{{ ev.agreement('fsl-topup', 'replica') }}

The replica's record runs 177 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-topup-replica.md), made again on 2026-11-06). 107 give FSL's files byte for byte. In 67 FSL refuses the input or stops, and the replica does the same, with the same message and exit status (*rejected by both*). 3 are refused by the replica in `fix` and in `reproduce` (*expected divergence*): a negative `--warpres`, where FSL needs more memory than any machine holds (FSL-124), and fields on another grid, which FSL reads past its lines (FSL-134).

Some of the cases came later:

- three with the specification's answers to the clean room's questions (2026-11-03): quadratic splines on an axis shorter than two knot spacings, and on one shorter than one spacing at a level that refits it, where FSL stops with an index error and the replica's default finishes (FSL-145); and four volumes encoded along y and x (FSL-146);
- one with an answer written for PRELUDE's specification (2026-11-06): `--method=jac` with a coefficient field whose voxel sizes differ from the images' (`at/jac-coef-aniso`; with a field image, `at/jac-field-aniso`). FSL scales the Jacobian by the voxel sizes' ratio along each encoded axis, and the replica's default takes the Jacobian of the displacement applied (FSL-273).

The cases cover:

- fMRIPrep's call on its two fMRIPrep runs, whose files are fMRIPrep's own too;
- every option of topup: double and single precision, spline and linear interpolation, both regularisers, quadratic and cubic splines, the scaling, the regridding, the minimisers per level, the movements, FSL's shipped configurations and configurations of their own, `--acqp`, x, y and oblique phase encodings, three and four volumes, `--debug`, `--trace`, `--profile`;
- its thread counts;
- every option and method of applytopup, on lines of 30, 32 and 96 voxels and in every data type;
- every message, exit status and failure case of both command lines.

Each case also runs the replica's default, `fix`, where LARMORX corrects FSL's deterministic defects and names them ([below](#corrections)).

The clean room is written without FSL's source, so its record holds it to the thresholds of [specs/topup.md](repo:specs/topup.md) §12 instead:

- FSL's exit status, files and messages, the numbers in them to 4 significant digits, the headers and the log identical;
- inside the brain, the field within 0.5 Hz at the 99th percentile and 0.1 Hz on average, with a correlation of at least 0.999;
- the corrected images within 10<sup>−3</sup> relative;
- the movements within 0.05 mm and 0.001 rad.

It also shows how close the clean room comes. Each case it passes is run again and classified from every file against FSL's, and against FSL's own thread band where the record measures it: FSL at four threads against FSL at one (FSL-116), on fMRIPrep's two calls and the thread cases.

{{ ev.agreement('fsl-topup', 'original') }}

The clean room's record runs 187 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-topup.md), made again on 2026-11-07). 106 are within the thresholds, 67 are rejected by both alike (the same message and exit status), and 14 are expected divergences, each with its reason in the record. None is outside.

- **Bit-identical, 9 of the 106.** They give FSL's values bit for bit.
- **Within FSL's own band, 2.** fMRIPrep's call on ds001600 and the case at `--nthr=4` lie within FSL's own thread band in every metric of the record.
- **Open, 95.** They are within the thresholds, but not bit for bit: the clean room computes in its own order of operations. On 92 of them FSL's own band is not measured; that band is measured in the final validation phase. On the other three the clean room lies beyond the band FSL's thread settings give: fMRIPrep's call on ds005040 in two metrics of 24 (the field's correlation with FSL's, for `--fout` and for the coefficients' field: 0.999958 against FSL's own 0.999966; the field's 99th percentile, 0.61 Hz, is inside FSL's 0.64), and the two thread cases whose settings leave FSL's own result all but unchanged.
- **Expected divergences, 14.** In 6 the movements are estimated and have not converged. There `reproduce` takes FSL's forward differences (FSL-201), but FSL's own path is not determined beyond its inputs' last bits, so the record holds them to FSL's own spread with the read-out times changed by 1 to 256 last bits ([below](#movements)). 4 are applytopup's variational restorations: FSL-143's diverging iterations, reproduced, which amplify the last bits, and vb2D's transients in a few slices. One is FSL-126's negative weight, with which both minimisations diverge. And 3 inputs are refused in `fix` and in `reproduce`: a negative `--warpres` (FSL-124: FSL needs more memory than a machine holds) and fields on another grid (FSL-134: FSL reads past its lines).

The five cases that FSL-133's lines and FSL-134's field of another shape kept apart pass since the catch-up, and `opt/fsl145-one-coefficient` is rejected by both alike. Two cases came on 2026-11-07:

- `at/jac-coef-aniso`, with the specification's answer on applytopup's Jacobian (FSL-273, [specs/topup.md](repo:specs/topup.md) §7.3): `--method=jac` with a coefficient field of other voxel sizes. FSL divides the field's derivatives by the field's own voxel sizes while it lays the displacement in the images', so its Jacobian is scaled along each encoded axis by the ratio of the two. The clean room takes the Jacobian of the displacement it applies by default (scale 1, naming FSL-273), and FSL's scales in `reproduce` ([findings](repo:docs/findings/fsl-topup-clean-room.md)).
- random testing's permanent case `difftest/time-step-zero-series`: fMRIPrep's call on a series whose time step is 0, its `--iout` compared (the time step as FSL's image layer reads it).

## In fMRIPrep: the field map from a reversed-phase-encoding pair {#example}

fMRIPrep's own call on ds005040's pair, given to FSL 6.0.7.23 at one thread (as fMRIPrep runs it) and at four, to the replica in `reproduce` and in `fix` (and at four threads), and to the clean room in `reproduce` and in `fix` on 14 threads (and on one). The two input panels are the pair before the correction. Choose an output above the panels to see each image corrected, the field, the Jacobians and the displacements.

The replica's differences from FSL are zero in every one. FSL's own result at four threads differs from its result at one (FSL-116). That comparison, *FSL topup, --nthr=4 − --nthr=1*, is the yardstick of how much FSL itself moves, and the replica gives FSL's one-thread result at any thread count.

The clean room's differences from FSL are of about the yardstick's size, on the same scale beside it. This call's scaled conjugate gradients at full resolution (60 iterations with almost no regularisation at a knot spacing of one voxel) carry any last-bit difference forward, the clean room's as FSL's own at another thread count. Below the viewer: every file topup writes, with fMRIPrep's own outputs (topup in fMRIPrep's image), and the record's metrics of the clean room beside FSL's own thread band.

{{ ev.example('fsl-topup', 'fmriprep-ds005040') }}

## A second run: ds001600 {#ds001600}

fMRIPrep's call on the data panel's ds001600, a Siemens Prisma pair whose two phase encodings have different read-out times and were acquired on different grids (sdcflows resampled one onto the other first). The same runs and comparisons as above; the viewer opens on the field. Here the clean room lies within FSL's own thread band in every metric of the record.

{{ ev.example('fsl-topup', 'fmriprep-ds001600') }}

## Membrane energy, and a correction by default {#membrane}

With `--regmod=membrane_energy` and Levenberg-Marquardt (the record's case `opt/membrane-lm`, on the half-resolution pair), FSL takes the regulariser's Hessian in other units than its cost and gradient: each first derivative divided by the voxel size in millimetres, where the cost counts in voxels. The replica's default takes the Hessian in the cost's units (FSL-117), so its steps follow the cost they minimise; its `reproduce` gives FSL's bytes.

This case estimates the movements too (topup's default), so since 2026-11-03 the default also takes their exact rotation derivatives (FSL-201, [below](#movements)). The comparison *replica, fix − reproduce* shows both corrections together, in the field. The clean room's default makes the same two corrections.

{{ ev.example('fsl-topup', 'membrane') }}

## Movements estimated, and a correction by default {#movements}

With `--estmov=1` topup also estimates each volume's rigid-body movement against the first. Here it is the record's case `opt/levels`: two levels on the half-resolution pair, the first at subsampling 2 by Levenberg-Marquardt with the movements, the second at full resolution by scaled conjugate gradients; every output written. fMRIPrep's configuration estimates none; FSL's own `b02b0.cnf` does, in its first five levels.

FSL takes the cost's derivatives with respect to the rotations as forward differences of rotation matrices built in single precision. So its gradient and its Hessian of the movements are not the cost's, and its minimisers end elsewhere than the cost's minimum. That is FSL-201, registered on 2026-11-03 with the specification's answers to the clean room's questions, after measuring that the exact derivatives end at a lower or equal cost in 18 of 22 runs (the other four, cut short, 0.004 to 0.13 % higher) and at a lower one in all 8 random cases whose volumes moved. The replica's default computes the exact derivatives (*deliberate correction*); its `reproduce` gives FSL's bytes.

The clean room's default computes them too, and since 2026-11-05 its `reproduce` takes FSL's forward differences. The movement table below the viewer shows the two defaults within 6 × 10<sup>−6</sup> mm and 3 × 10<sup>−7</sup> rad of each other, where FSL's movements lie 3 × 10<sup>−4</sup> mm and 8 × 10<sup>−5</sup> rad from them. The clean room's `reproduce` ends 5 × 10<sup>−4</sup> mm and 1.3 × 10<sup>−4</sup> rad from FSL. Its first gradients are FSL's, but FSL's path here is not determined beyond its inputs' last bits: a rotation's derivative jumps by about 2 % when its angle's rounding to single precision flips. That is why the record holds this case as an expected divergence, measured against FSL's own spread.

{{ ev.example('fsl-topup', 'movements') }}

## applytopup: least-squares restoration {#lsr}

applytopup's default method (the record's case `at/lsr-y`): the two images of opposite phase encodings restored into one, line by line along the phase encoding, with the field and movements of FSL's topup on the same pair. FSL resamples the first image with trilinear interpolation whatever `--interp` asks (FSL-132). The replica's default uses the method asked for, spline by default, and its `reproduce` gives FSL's bytes. On this call the clean room's `fix` and `reproduce` give the same values.

{{ ev.example('fsl-topup', 'lsr') }}

## applytopup: Jacobian modulation {#jac}

`--method=jac` (the record's case `at/jac-y`): one image corrected by itself, resampled along the phase encoding and multiplied by the displacement's Jacobian. FSL-132 reaches it too, and both ports' defaults correct it. With a phase encoding along z, which topup does not estimate, FSL leaves the image uncorrected without a word; the clean room's default refuses such a call (FSL-144), and its `reproduce` gives FSL's output.

{{ ev.example('fsl-topup', 'jac') }}

## applytopup --method=vb3D, and a correction by default {#vb3d}

One of applytopup's undocumented variational Bayes restorations (the record's case `at/vb3d-y`): a smoothness prior within and between slices whose weights are estimated over 20 iterations. FSL builds the prior's coupling between slices with half its weight, so the precision it assembles is not positive definite and its iterations diverge. FSL's output spans about ±4 × 10<sup>10</sup> for an input of at most 1.1 × 10<sup>5</sup>, and the replica's `reproduce` gives the same bytes. The replica's default gives the prior its full weight (FSL-143), and its restoration stays in the input's range, as vb2D's does; so does the clean room's default. FSL's panel is shown in the default's window; choose *each image's own* window to read it.

{{ ev.example('fsl-topup', 'vb3d') }}

## Random testing {#random}

The replica's random-testing run (2026-11-03), 27 minutes long, drew 14,460 random calls, each run by FSL 6.0.7.23 (through the cache of the original's runs) and by the replica, every file compared. Every case agreed bit for bit. The record's refusals, failures and thread counts are left to the record.

{{ ev.table('fsl-topup', 'trial') }}

The clean room's first random-testing run (2026-11-03) drew the replica's cases again, so every run of FSL was served by the cache of the original's runs: 14,400 random calls in 11 minutes, each compared as the record compares. 7,401 agreed within the thresholds. Each of the 6,999 that differed is in one category below:

- most are causes already named: FSL's movement derivatives in cases that estimate the movements (4,462; registered since as FSL-201), FSL-133's lines (484), FSL-143's divergence (51), and other paths of fits the data hardly determine (of the differing cases that print their costs, about four in five end within 0.1 % of FSL's final cost or below it);
- two defects of FSL, registered and corrected by default with `reproduce` switches: FSL-145 (with `--splineorder=2`, an axis shorter than two knot spacings gets two coefficients, one when it is shorter than one spacing, which force the field towards 0 at its far end) and FSL-146 (with volumes encoded along different axes, such as AP, PA, LR and RL, FSL's gradient is not its cost's, so its minimisers step in a wrong direction; 895 cases);
- the clean room's own mistakes (the quadratic B-splines' count, the scaled conjugate gradients' weight) and the suite's (385 cases), each fixed and kept as a permanent case of the record;
- two categories stayed open, with their reproducers: the quadratic splines' regulariser Hessian at an even knot spacing (47 cases) and least-squares restorations on lines whose length divides 2<sup>32</sup> (8 cases). The specification answers both since 2026-11-03 (specs/topup.md §4.6 and §7.4), for the clean room's next part.

{{ ev.table('fsl-topup', 'trial-original') }}

{{ ev.table('fsl-topup', 'trial-original-triage') }}

The clean-room catch-up's random-testing run (2026-11-05) drew the earlier run's cases again and further, on the clean room with the specification's answers: 17,535 random calls in 30 minutes. 13,300 agreed within the thresholds, among them 3,695 of the earlier run's 6,999 differences. Each of the 4,223 that differed is in one category below:

- three in four estimate the movements and lie within 10 times FSL's own band of a last-bit change of its read-out times: FSL-201's path, which `reproduce` follows to its first gradients but not along a path FSL's own last bits move as far (an expected divergence, as in the record);
- the run found FSL-242, and that FSL counts every iteration of its scaled conjugate gradients toward `--miter`, both fixed in the clean room after it, each with a permanent case of the record; and the suite's own mistake with a NIfTI-2 quaternion (fixed);
- left open, with their reproducers: the movements beyond 10 times FSL's band (179 of them run away, most with scaled conjugate gradients, which FSL warns against: measured with `--debug`, FSL-201's forward differences divided by those gradients' small step), fits without movements that the data hardly determine, and the quadratic splines' bending energy on FSL-145's layout, a question for the specification.

{{ ev.table('fsl-topup', 'trial-catchup') }}

{{ ev.table('fsl-topup', 'trial-catchup-triage') }}

## Every case {#cases}

Each case of the two records, the replica's and the clean room's, both against FSL 6.0.7.23 (a column each), with what it tests, its command line, each port's verdict and the reason. The ten cases random testing gave the clean room are its own. Search, filter by category or verdict (or select a segment of a chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('fsl-topup') }}

## Speed {#speed}

topup at one thread is how fMRIPrep runs it. With `--nthr` FSL runs threaded, and its result then changes (FSL-116). On fMRIPrep's two calls the clean room takes 2.8 and 7.7 s on one thread, 10 to 12 times as fast as FSL at one thread, and 0.8 and 2.0 s on 14 threads, 39 to 41 times as fast, the same bits at both; FSL at `--nthr=14` takes 12.3 and 27.4 s. applytopup's least-squares restoration of ds005040's pair takes the clean room 0.13 s on one thread and 0.04 s on 14, against FSL's 0.42 s. The replica, a translation, runs at about FSL's speed in topup (29.7 and 71.4 s) and takes 3.5 s for the restoration ([the report](repo:docs/benchmarks/fsl-topup.md)). These timings are informal: one run each, on a machine running other work beside them. The clean room's peak memory on fMRIPrep's call on ds005040, as the memory test measures it at one thread, is 74 MiB, against FSL's 88.

{{ ev.speed('fsl-topup') }}

## Corrections by default {#corrections}

The replica corrects FSL's deterministic defects by default, `fix`, and warns. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives FSL's behaviour byte for byte, where FSL's behaviour is defined ([register](repo:docs/findings/upstream-defects.md)).

In topup:

- Above one thread (`--nthr`, or `FSL_NUM_THREADS` for some of its matrices), FSL's result changes with the thread count. The replica gives FSL's one-thread result at any count (FSL-116, never reproduced).
- The membrane energy's Hessian in the cost's units (FSL-117, [above](#membrane)).
- With the movements estimated, the exact derivatives with respect to the rotations, where FSL takes forward differences of single-precision rotation matrices (FSL-201, since 2026-11-03, [above](#movements)).
- With `--regrid=1` and subsamplings whose largest does not divide the others, FSL stops at the first level with the smaller one; the replica's grid grows by their least common multiple (FSL-118).
- The field maps `--fout` and `--featout` write keep the input's intent parameters in place (FSL-119: FSL shifts them by one).
- A row-count mismatch of `--acqp` names the `--acqp` file (FSL-120).
- With `FSLDIR` unset and a configuration name not found, a clear error instead of FSL's exception (FSL-121).
- A configuration line longer than 1023 characters after its first word no longer ends the reading silently (FSL-122).
- A negative `--miter`, `--fwhm` or `--lambda`, which FSL uses as given (a negative `--fwhm` smooths nothing), is refused (FSL-123, FSL-125, FSL-126). A negative `--warpres` is refused in `fix` and in `reproduce` (FSL-124: FSL's knot spacing wraps and it exhausts the memory).

In applytopup:

- Every volume is resampled with the interpolation asked for (FSL-132, [above](#lsr)).
- The least-squares restoration wraps a negative index around its line (FSL-133: FSL wraps it by 2<sup>32</sup> modulo the line's length, wrong for lengths that do not divide 2<sup>32</sup>, such as 30 or 96).
- `--method=jac` with a field image scales the displacement along y by the y voxel size (FSL-134: FSL takes the x one). With a field whose voxel sizes differ from the images', it modulates by the Jacobian of the displacement applied (FSL-273, 2026-11-06: FSL divides the field's derivatives by the field's own voxel sizes). A field on another grid is refused, in `fix` and in `reproduce`, where FSL reads past its lines.
- An unknown `--method`, which FSL ignores silently (exit status 0, no output), and `lsr` or `vb*` without movements, where FSL aborts, are refused with a reason (FSL-135).
- The variational methods count values in 64-bit integers (FSL-141: FSL's 32-bit ones wrap on very large images).
- vb3D and vb4D count the data points of every image (FSL-142) and build their prior with its full weight (FSL-143, [above](#vb3d)).

Five defects of FSL's libraries that topup and applytopup never reach are in the register too (FSL-127 to FSL-131).

The clean room makes the same corrections by default, with the same notices, each named where it changes an output: on `lsr` and vb3D here, FSL-132's correction changes none of the clean room's values, so its notice is FSL-143's alone on vb3D. Its `reproduce` follows FSL where FSL's behaviour is defined. Since 2026-11-05 that includes FSL-201's forward differences, FSL-133's index on lines whose length does not divide 2<sup>32</sup> and FSL-134's field in another shape, which the specification describes since its answers of 2026-11-03; its default restores those lines circularly and refuses that field. It adds four corrections that black-box runs found:

- `--method=jac` with a phase encoding along z leaves the image uncorrected silently, which the default refuses (FSL-144);
- `--splineorder=2` lays two coefficients on an axis shorter than two knot spacings, so the field is forced towards 0 at its far end; the default lays the general count (FSL-145);
- with volumes encoded along different axes, FSL's gradient leaves out of each axis' term the volumes not encoded along it; the default minimises with the cost's own gradient (FSL-146: the default's final cost was as low as FSL's or lower in 86 to 89 % of the differing four-volume cases of the random-testing run of 2026-11-03);
- with scaled conjugate gradients, a level whose last step is rejected ends at that worse point; the default ends at the lowest cost the level found (FSL-242, 2026-11-05).

The replica has the first three, with their switches, since 2026-11-03: its `reproduce` lays FSL's count exactly, one coefficient on an axis shorter than one spacing, and gives FSL's error when a level refits a single coefficient.

## Known limits {#limits}

Both ports are experimental. Each record's standard comparison holds fMRIPrep's calls on its two fMRIPrep runs. The full comparisons, the data panel's other PEPOLAR runs, the long random-testing runs and FSL's own band on every case come in the final validation phase.

The clean room is held to thresholds, not to FSL's bytes. Where the movements are estimated and do not converge, it ends elsewhere than FSL even in `reproduce`, which takes FSL's forward differences (FSL-201) along a path FSL's own last bits move. On fits the data hardly determine (no regularisation, a few hundred voxels at a subsampled level) it can reach another minimum, as low as FSL's.

The questions it left for the specification until 2026-11-03 ([specs/topup.md](repo:specs/topup.md) §13) are followed since 2026-11-05. The catch-up's random-testing run left new ones:

- the quadratic splines' bending energy on an axis of FSL-145's two coefficients (§4.6);
- the smoothing on an axis shorter than its kernel (§4.4);
- a field image's Jacobian scales when its voxel sizes differ from the images' (§7.3), answered on 2026-11-07 ([above](#verdicts): FSL-273).

The replica refuses, in `fix` and in `reproduce` and with a message, applytopup's restorations of lines of fewer than 8 or more than 256 voxels along the phase encoding, and band systems that need LAPACK's blocked band factorisation: FSL's arithmetic there follows other paths of OpenBLAS and Armadillo, which the replica does not reproduce yet.

Neither port reproduces FSL's results above one thread: they depend on the thread count (FSL-116).

The cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output. The clean room's cover two levels with every output, the other options, FSL-117 and FSL-145 reproduced, applytopup's `lsr`, `jac` and `vb` methods, FSL-132 reproduced, and the Python functions. The benchmark is informal: one run each, on a shared machine.

## History {#history}

- **2026-11-03**: the replica, translated from FSL 6.0.7.23's source, and its random-testing run, 14,460 calls in 27 minutes. The clean room, written from [specs/topup.md](repo:specs/topup.md), the papers, FSL's user guides and runs of FSL, and its first random-testing run, 14,400 calls in 11 minutes. The specification's answers to the clean room's questions the same day (§13): FSL-201 registered and corrected by default in the replica; the replica's switches for FSL-144, FSL-145 and FSL-146.
- **2026-11-04**: the clean room's `reproduce` computes `exp` as glibc 2.35 does (GLIBC-07); no value of the record moved.
- **2026-11-05**: the clean-room catch-up. The specification's answers of 2026-11-03 are in the clean room since, and every example was run again; its random-testing run of 17,535 calls in 30 minutes found FSL-242, corrected by default.
- **2026-11-06**: the replica's record made again, 177 cases, `at/jac-coef-aniso` among them (FSL-273, an answer written for PRELUDE's specification).
- **2026-11-07**: the clean room's record made again, 187 cases: `at/jac-coef-aniso`, with the specification's answer on applytopup's Jacobian (FSL-273, §7.3), and random testing's case `difftest/time-step-zero-series`.
