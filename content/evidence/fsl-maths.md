---
title: fslmaths
kicker: Evidence · FSL
lede: >-
  `fslmaths` is FSL's image calculator: it reads an image, applies a chain of operations from left
  to right and writes the result. fMRIPrep calls it in every BOLD reference's brain mask, and
  fourteen times in its optional goodvoxels mask. The replica (`larmorx-nc`) gives FSL 6.0.7.23's
  files, messages and exit status byte for byte in 360 of its 361 compared cases, out of 422,
  fMRIPrep's calls among them; the other is one unit in the last place where glibc's `tan` is not
  correctly rounded. The clean room (`larmorx`) is within its record's thresholds in 386 of its 391
  compared cases, out of 454, and gives FSL's values in every file in 370 of them, fMRIPrep's calls
  among them; the other 5 are expected divergences, each with its reason. On a real series it
  differs from FSL in one call of fifteen, a large kernel FSL convolves by its single-precision FFT,
  where its own sums lie closer to the exact result. On the heavy operations of a real BOLD series
  and T1w it runs 1.8 to 28 times as fast as FSL on one thread, up to 268 times on 14.
description: >-
  How LARMORX's two ports of FSL's fslmaths, a replica and a clean room, compare with FSL 6.0.7.23:
  fMRIPrep's mask combination on its runs and its goodvoxels mask's fourteen calls, one call per
  operation family on a real BOLD series (the FFT convolution among them, measured against its
  exact result), glibc's double functions on a real image (GLIBC-07), every case of both records
  with its verdict, both ports' random-testing runs with the clean room's triage, and the speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx-nc</code> <span class="port-licence">FSL Licence: non-commercial use only</span>: translated from FSL 6.0.7.23's source (fsl-avwutils 2209.6, with fsl-newimage 2601.0's image functions, fsl-miscmaths 2412.6 and fsl-cprob 2111.0); it runs as a separate program</li>
<li class="port port--clean-room"><span class="port-name">clean room</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: crate <code>larmorx-fsl</code>, written from <a href="{{ repo('specs/fslmaths.md') }}">specs/fslmaths.md</a>, FSL's usage text and documentation and runs of FSL 6.0.7.23, without FSL's source (2026-11-03)</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--experimental">experimental</span>; clean room <span class="status-tag status-tag--experimental">experimental</span></dd>
<dt>Records</dt><dd>the replica's: <a href="{{ repo('docs/validation/fsl-maths-replica.md') }}">standard comparison</a> (FSL 6.0.7.23) · the clean room's: <a href="{{ repo('docs/validation/fsl-maths.md') }}">standard comparison</a> (FSL 6.0.7.23) · benchmark <a href="{{ repo('docs/benchmarks/fsl-maths.md') }}">fsl-maths</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/fsl-maths.md') }}">fsl-maths</a> · its companion: <a href="{{ link('/evidence/fsl-stats/') }}">fslstats</a></dd>
</dl>

## What is compared {#what-it-is}

`fslmaths <input> [operations] <output>` reads an image, applies each operation in turn to the current image and writes the result. Its operations:

- arithmetic with a number or another image: `-add`, `-sub`, `-mul`, `-div`, `-rem`, `-mas`, `-max`, `-min`;
- thresholds by value or by percentage of the robust range: `-thr`, `-thrp`, `-thrP` and their upper forms;
- voxelwise functions: `-exp`, `-log`, the trigonometric functions, `-sqrt`, `-abs`, `-bin`, `-nan`, `-index`, `-grid`, seeded noise;
- kernels and the operations that use them: dilations and erosions, mean and median filters, Gaussian smoothing, convolutions by direct sums or by the FFT, subsampling, edges, hole filling;
- mean normalisation, and reductions along a dimension: `-Tmean`, `-Tstd`, `-Tmax`, `-Tmedian`, `-Tperc`, `-Tar1` and their X, Y and Z forms;
- p-values, ranks and z ↔ p conversions, regions;
- band-pass temporal filtering (`-bptf`), the threshold-free cluster enhancement (`-tfce`, `-tfceS`), ROC curves (`-roc`) and the diffusion tensor's decomposition.

`-dt` chooses the type it computes in (float by default, or double), `-odt` the output's.

fMRIPrep calls it in niworkflows' BOLD reference workflows (`combine_masks`: `fslmaths <mask> -mul <mask> <out>`, the reference's brain mask as the product of two masks). With `--project-goodvoxels` it calls it fourteen times in its goodvoxels mask, with four fslstats calls between them.

The two ports run beside FSL 6.0.7.23's `fslmaths` on the same files with the same arguments. fMRIPrep's own outputs are the files it wrote in its runs, with fslmaths in fMRIPrep 25.2.6's image.

```bash
larmorx fsl fslmaths mask_a.nii.gz -mul mask_b.nii.gz combined.nii.gz
larmorx fsl fslmaths bold.nii.gz -Tstd -div mean.nii.gz cov.nii.gz
```

The first multiplies two masks, as fMRIPrep does. The second divides a series' standard deviation over time by its mean.

```python
import larmorx as lx

combined = lx.fsl.fslmaths("mask_a.nii.gz", "-mul", "mask_b.nii.gz")   # the command line's operations
smooth = lx.fsl.smooth("mean.nii.gz", sigma=3.0)                       # one typed wrapper per family
```

The calls above leave `implementation` at `"auto"`. The [API page](repo:docs/api/fsl-maths.md) describes the generic function and the typed wrapper of every operation family. How to read what follows: [how to read the evidence](/validation/#reading).

### Its two ports {#ports}

FSL comes under the FSL Licence, which allows non-commercial use only. So LARMORX has two ports of its FSL programs. The replica is translated from FSL's source and lives in its own package, `larmorx-nc` (`pip install larmorx-nc`). The clean room is in `larmorx` itself. It is written without FSL's code, from fslmaths' behavioural specification ([specs/fslmaths.md](repo:specs/fslmaths.md)), FSL's usage text and documentation and runs of FSL 6.0.7.23 as a black box.

`implementation="auto" | "replica" | "clean-room"` chooses between them (`"original"` in 0.1.0rc1). On the command line, `larmorx --implementation clean-room fsl fslmaths ...` does the same from the next release; in 0.1.0rc1 it is the environment variable `LARMORX_IMPLEMENTATION`. `auto`, and `larmorx fsl fslmaths`, take the replica when `larmorx-nc` is installed, else the clean room.

The replica follows FSL 6.0.7.23. It needs no FSL installation. What fslmaths needs from FSL's libraries is translated once into `larmorx-nc`'s shared core, beside what mcflirt, BET, FLIRT, FAST and topup use: newimage's image functions, kernels, morphology, convolutions, connected components and TFCE, the Cephes probability functions of fsl-cprob, Armadillo's Kiss FFT and symmetric eigen-decomposition. BET's own `fslmaths` and `fslstats` calls run the same code.

The clean room has every operation of the usage text and the hidden ones, every data type in and out, every message, exit status and failure case, and the defects with their switches. By default it computes `exp`, `log`, the trigonometric functions and `pow` correctly rounded on every platform; in `reproduce` it computes them as glibc 2.35 does, but for `tan`, `asin`, `acos` and `atan` ([below](#glibc)). It is built for speed, and its result is the same bits at any thread count ([speed](#speed)):

- the separable filters and the direct sums run a row of voxels at a time, `-bptf` in blocks of voxels, the reductions per column;
- every parallel loop sums in a fixed order;
- it holds one copy of the image: the input's values are moved into the computation, the output's to the writer;
- where FSL convolves a large kernel by its FFT, the clean room takes the direct sum too, in the orientation of FSL's direct sum (FSL-192). It is faster than FSL's FFT on every kernel measured ([speed](#speed)).

Where the specification leaves a convention open, the clean room follows FSL's as black-box runs measured it:

- the Gaussian's exponent, `i² (d d)` per axis;
- the geometry of a new grid;
- `-roc`'s candidates;
- TFCE's checks, in FSL's order.

**The C library's last digits (since 2026-11-04).** fslmaths' double-precision `-sin`, `-cos`, `-exp`, `-log` and `-pow` come from the C library, glibc on Linux, and so do the weights of its Gaussian filters (`-s`, `-kernel gauss`, `-dog_edge`), of `-bptf`, `-tfce` and `-roc`. glibc's results are now and then one unit in the last place away from the exact value rounded once. LARMORX computes them correctly rounded, the same on every platform.

- Until 2026-11-04 the clean room did so in `fix` and in `reproduce`. Since then its `reproduce` computes them exactly as glibc 2.35 does, with LARMORX's versions of glibc's functions (`larmorx_core::math`).
- `tan`, `asin`, `acos` and `atan` stay correctly rounded in `fix` and in `reproduce` (as decided on 2026-11-04).
- Ten cases of its own show what that changes: nine `orig/glibc-*`, their inputs chosen where glibc's last bit differs, and `orig/edge-double`, `-edge` on a double image, whose squares FSL computes as products, black-box runs showed. Each now gives FSL's values bit for bit. No other number of the record moved, as a float result rounds such a last place away.
- Its default, `fix`, names GLIBC-07 exactly where a voxelwise function's value differs from glibc's. The filters name nothing: a filter would have to run twice to know ([GLIBC-07](#glibc) below).

## The verdicts at a glance {#verdicts}

The replica is a translation of FSL's source, so the question for it is whether it gives FSL's bytes: every file fslmaths writes (each image's header and data), its standard output and error, and its exit status.

{{ ev.agreement('fsl-maths', 'replica') }}

The replica's record runs 422 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-maths-replica.md), made again on 2026-11-04). 360 give FSL's files byte for byte. In 61 FSL refuses the input or stops, and the replica does the same, with the same message and exit status (*rejected by both*). 1 differs by one unit in the last place of a few values, where FSL's result comes from glibc 2.35's `tan`, which is not correctly rounded, and the replica's is (GLIBC-07, *expected divergence*, [below](#glibc)).

The cases cover:

- fMRIPrep's calls: the four `combine_masks` calls of three fMRIPrep runs and the goodvoxels mask's fourteen;
- every operation and option of the command line, in every data type;
- the odd headers and sizes, and FSL's own failure cases;
- the defects LARMORX corrects by default. Each case also runs the replica's default, `fix`, which names every correction where it changes the result ([below](#corrections)).

Since 2026-11-04 the replica's `reproduce` computes glibc's double `sin` and `cos`, and the twiddle factors of fslmaths' FFT, exactly as glibc 2.35 does. It does so with LARMORX's implementation of glibc's `sin`, `cos` and `sincos`, written from a behavioural specification of glibc's code ([specs/glibc-dbl.md](repo:specs/glibc-dbl.md)). Its default stays correctly rounded and names GLIBC-07 wherever a voxelwise value differs. The FFT case of random testing, an expected divergence until then, is FSL's bit for bit since.

The same day two mistakes of the replica's in the sign of a NaN were fixed, each kept by the record:

- `-ztop` of a NaN voxel. The replica's `expx2` was written as plain arithmetic, whose NaN signs the optimiser does not keep; it now takes x86-64's rules explicitly. Four cases of the record had found it.
- `-dilall` of an image holding NaN and infinities. FSL's build passes on the neighbour's NaN, the replica passed on the sum's. Random testing found it: the permanent case [`difftest/dilall-nan-order`](#case=difftest/dilall-nan-order).

The clean room is written without FSL's source, so its record holds it to the thresholds of [specs/fslmaths.md](repo:specs/fslmaths.md) §21 instead:

- FSL's exit status, messages, file names and headers identical;
- the values bit for bit, the double-precision functions within one unit in the last place per function;
- the sums within 10<sup>−5</sup> of FSL's largest value, with 99 % of the voxels within 4 units in the last place;
- TFCE, `-tensor_decomp` and `-roc` by their own measures.

It also shows how close the clean room comes: each case's verdict is read from what the record measures.

{{ ev.agreement('fsl-maths', 'original') }}

The clean room's record runs 454 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-maths.md), made again on 2026-11-07): the replica suite's cases, 18 of its own (`orig/`, ten of them since 2026-11-04) and 19 permanent cases of random testing. Two of those came on 2026-11-07: a series whose time step is 0 or negative, which FSL's image layer reads as its magnitude, and as 1 for a time step of 0, and which every output keeps. The record counts 386 within its thresholds, 63 rejected by both alike and 5 expected divergences. By what each case measures:

- **Bit-identical, 370.** FSL's values in every file, with FSL's headers, messages and exit status. fMRIPrep's four `combine_masks` calls and the goodvoxels mask's fourteen are among them, and so is the `-s 5` at 3 × 3 × 3.3 mm.
- **Open, 15.** They are within the thresholds without being bit for bit, each with its reason in the case explorer:
  - FSL's FFT path on four kernels;
  - `-subsamp2` and `-subsamp2offc` under the floating types (FSL's arithmetic there is a question for the specification);
  - the double-precision `-ztop` and `-ranknorm` (the last bits of Φ and Φ<sup>−1</sup>);
  - `-tensor_decomp`'s eigenvectors, the same up to their sign: FSL's signs are LAPACK's, the clean room's make each one's largest component positive;
  - one `-roc` area, 10<sup>−7</sup> from FSL's.
- **Expected divergences, 6.** FSL's FFT path on 3 kernels and `-subsamp2offc`'s means on 2 are within the sums' bound but not its share of voxels within 4 units in the last place: the record's 5. The sixth is `-dt double -tan` (GLIBC-07, [below](#glibc)), which the record holds within its threshold of one unit per function.

On the FFT cases the clean room lies as close to the exact result as FSL's single-precision FFT, or closer ([findings 31](repo:docs/findings/fsl-maths-original.md)). Before its double sums of 2026-11-04 two more of them were expected divergences, up to 2.6 × 10<sup>−6</sup> of FSL's largest value from FSL.

## In fMRIPrep: a BOLD reference's brain mask {#combine}

fMRIPrep's `combine_masks` node of ds005040's head-motion reference: the mask of BET's first pass on the reference, times the template's brain mask brought onto it. It was given to FSL 6.0.7.23, to the replica in `reproduce` and in `fix`, and to the clean room in `reproduce` at 14 threads and at one and in `fix`. Each mask is drawn over the reference it was computed from. Below the viewer: every `combine_masks` call of both records, on ds000005, ds005040 (both kinds of reference) and ds003592. Each gives the same bytes as FSL's and as fMRIPrep's own output, in both ports.

{{ ev.example('fsl-maths', 'combine') }}

## In fMRIPrep: the goodvoxels mask {#goodvoxels}

With `--project-goodvoxels`, fMRIPrep leaves out of the surface projection the voxels whose temporal coefficient of variation is high compared with their neighbourhood in the cortical ribbon. It takes fourteen fslmaths calls and four fslstats calls (`init_goodvoxels_bold_mask_wf`). The fMRIPrep runs do not use the option, so the workflow is built from fMRIPrep's code on ds005040's BOLD series in T1w space. Each call has its arguments as the workflow makes them, and its inputs are FSL's outputs of the calls before it. The runs have no FreeSurfer reconstruction, so the cortical ribbon is a stand-in: the anatomical segmentation's grey matter at each BOLD voxel.

Every call's output is FSL's bit for bit, in the replica and in the clean room at 14 threads and at one. So are the four numbers fslstats prints between them ([fslstats' page](/evidence/fsl-stats/#goodvoxels)).

{{ ev.example('fsl-maths', 'goodvoxels') }}

## One call per operation family {#families}

fslmaths' operation families on the same real series, one call each: arithmetic with images (the temporal SNR), a threshold by the robust range, a voxelwise function, reductions along time, morphology, the three kinds of filters, edges, normalisation, temporal filtering, a region and the threshold-free cluster enhancement. The filters are Gaussian smoothing by separable sums, a mean filter whose large spherical kernel fslmaths convolves by the FFT, and a median filter. Every output of the replica is FSL's bit for bit, in `fix` and in `reproduce`.

The clean room gives FSL's values in fourteen of the fifteen calls, at 14 threads and at one, in `fix` and in `reproduce`. The fifteenth is the mean filter with the 15 × 15 × 13 spherical kernel (1,313 voxels):

- FSL convolves it by its FFT in single precision. The clean room takes a direct sum: it adds the products in double precision and rounds the sum once. (Where FSL sums directly, the clean room keeps FSL's single-precision sum, bit for bit.)
- The two differ by up to 2 × 10<sup>−7</sup> of FSL's largest value, within §21's bound of 10<sup>−5</sup>, with 75.7 % of the voxels within 4 units in the last place, below §21's 99 % (*expected divergence*, as the record's FFT cases).
- Against the exact result, computed here in float64 from the specification's definition, FSL's FFT lies within 1.5 × 10<sup>−7</sup> of the largest value and the clean room within 7.9 × 10<sup>−8</sup>. FSL's FFT rounds relative to the image's largest values, so its small values sit many units in their last place from the exact result, where the clean room's sum is closer ([findings 31](repo:docs/findings/fsl-maths-original.md)).
- Until 2026-11-04 the clean room added each product to a single-precision sum there too, as FSL does on its direct path. Over 1,313 terms that sum drifted, 1.4 × 10<sup>−5</sup> from the exact result and from FSL, beyond §21's bound. The double sum costs the benchmark's two FFT-path calls 1.3 and 1.5 times the time.

Choose *filters: the FFT convolution* above the panels to see where they differ. The second table below the viewer gives each call's numbers.

{{ ev.example('fsl-maths', 'families') }}

## GLIBC-07: glibc's double-precision functions {#glibc}

FSL's build takes its mathematical functions from glibc 2.35. Its double-precision `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `exp`, `log` and `pow` are not always correctly rounded: for a small share of arguments the result is one unit in the last place from the exact value. LARMORX computes them correctly rounded, the same on every platform (CORE-MATH). In fslmaths' default type, float, the double result is rounded to float and no value differs; with `-dt double` the last place shows.

The table runs each function on a real image, FSL's mean of ds005040's series, scaled into the function's range. In the replica:

- for `exp` and `log`, `reproduce` gives glibc's own bits, and `fix` corrects them with a notice;
- glibc's `sin`, `cos`, `tan`, `asin`, `acos` and `atan` are IBM's Accurate Mathematical Library (LGPL, never translated). For `sin` and `cos` the replica's `reproduce` gives glibc's bits since 2026-11-04, with LARMORX's own implementation of glibc's `sin`, `cos` and `sincos`, written from a behavioural specification of glibc's code; its `fix` corrects them with a notice;
- `tan`, `asin`, `acos` and `atan` stay correctly rounded in `fix` and in `reproduce` (as decided on 2026-11-04), and differ from FSL on those values (*expected divergence*).

glibc chooses the build of each of these functions at run time: an FMA build on every x86-64 CPU since 2013, as on the machine that ran FSL. FSL's own double results therefore depend on the CPU, and "glibc's bits" here are the FMA build's.

{{ ev.table('fsl-maths', 'glibc-double') }}

Since 2026-11-04 the clean room's `reproduce` gives glibc's bits for `sin`, `cos`, `exp`, `log` and `pow`, as the specification asks of it. It uses LARMORX's versions of glibc's functions: `exp`, `log` and `pow` translated from Arm's Optimized Routines as glibc 2.35 ships them (under the MIT licence), `sin` and `cos` written from a behavioural specification of glibc's code and checked against the system's glibc on 11.8 billion arguments each. `tan`, `asin`, `acos` and `atan` stay correctly rounded in `fix` and in `reproduce` (as decided on 2026-11-04): one unit in the last place from FSL's where glibc's are not correctly rounded, within its record's threshold of one unit per function. Its default computes every one correctly rounded, the replica's default's bits, and names GLIBC-07 exactly where a value differs from glibc's.

{{ ev.table('fsl-maths', 'glibc-double-original') }}

The replica's record has one expected divergence, GLIBC-07: [`fn/double-tan`](#case=fn/double-tan), `-dt double -tan`, 3 of 210 values one unit in the last place.

Until 2026-11-04 there was a second, from random testing: [`difftest/fft-twiddles-glibc-sincos`](#case=difftest/fft-twiddles-glibc-sincos), a mean filter of a 30 × 1 × 3 float image that fslmaths convolves by the FFT, 1 of 90 voxels one unit in the last place.

- fslmaths' FFT (Armadillo's Kiss FFT) takes each twiddle factor from glibc's `sincos`, which is not correctly rounded on 0.148 % of the angles: of the transform lengths 1 to 256, 80 hold a factor one unit in the last place from the exact one. The replica computed the factors correctly rounded.
- Its `reproduce` now takes them from LARMORX's implementation of glibc's `sincos`: Armadillo's 65,792 factors and 197,376 transform values of the lengths 1 to 256 bit for bit, and this case FSL's output bit for bit ([the probe](repo:validation/probes/fsl-avwutils-lib/README.md)).
- Its default keeps the correctly rounded factors and names nothing: a filter would have to run twice to know.

It is rare. A float result usually rounds it away (the FFT convolution of the real series above is FSL's bit for bit in `fix` and in `reproduce`), and fMRIPrep's calls convolve by separable sums.

## Random testing {#random}

The replica's random-testing run (2026-11-03), 24 minutes long, drew random chains of operations on random images. Each was run by FSL 6.0.7.23 (through the cache of the original's runs) and by the replica, and every file was compared.

{{ ev.table('fsl-maths', 'trial') }}

The clean room's random-testing run (2026-11-03) drew the replica's run's chains again and more, so that run's calls of FSL were served by the cache of the original's runs: 150,000 random chains of one to four operations in 20 minutes, each compared as the record compares. 143,191 agreed within the thresholds, and 804 differed only by a correction its default names. Each of the 6,005 that differed was run again with the part's final build and put in one category below:

- most were the clean room's own mistakes, fixed with permanent cases of the record: the geometry of a new grid along x (2,022), `-roc`'s false-positive candidates (1,477), the morphological filters' messages with a kernel image, a subsampled image's quaternion, TFCE's checks in FSL's order, the integer arithmetic of `-edge` and the subsampling, and four defects now named wherever they apply (FSL-75, FSL-154, FSL-157, FSL-165);
- 1,178 are explained: degenerate tensors whose eigenvectors are not defined, the header's offsets after a grid change (at most 6 units in the last place), the last bits of `-subsamp2` under the floating types, of Φ and Φ<sup>−1</sup> and of sums that cancel to near 0, `-dog_edge`'s crossings at exact ties, signed zeros;
- 33 are `-subsamp2offc`'s means, as the record's expected divergences;
- 7 are FSL-75, FSL's heap corruption, which ends FSL before it writes, while the clean room finishes and names it;
- 10 stay open, with their reproducers: 8 display ranges after `-range`, in their last bits, and 2 `-roc` curve numbers 2.4 × 10<sup>−7</sup> and 5 × 10<sup>−7</sup> from FSL's.

{{ ev.table('fsl-maths', 'trial-original') }}

{{ ev.table('fsl-maths', 'trial-original-triage') }}

## Every case {#cases}

Each case of the two records, the replica's and the clean room's, both against FSL 6.0.7.23 (a column each), with what it tests, its command line, each port's verdict and the reason. The 37 cases only the clean room's record holds are its own: `orig/` and the permanent cases random testing gave it. Search, filter by category or verdict (or select a segment of a chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('fsl-maths') }}

## Speed {#speed}

fslmaths runs on one thread; the clean room runs on as many as it is given, with the same result.

- On fMRIPrep's goodvoxels chain (its fourteen fslmaths calls and four fslstats calls, in order) the clean room takes 0.38 s against FSL's 1.70 s, with half FSL's memory.
- On the heavy operations of a real BOLD series and T1w it is 1.8 to 28 times as fast as FSL on one thread, and up to 268 times on 14.
- The largest factors are on FSL's FFT path, whose padded transforms cost FSL 28.7 s and 228 s (and 4 GiB). The clean room's direct sum, in double precision there, takes 3.9 s and 8.1 s on one thread.
- The replica, a translation, is faster than FSL on most calls, and slower on `-bptf`.

These timings come from [the report](repo:docs/benchmarks/fsl-maths.md). They are informal: one run each, on a machine running other work beside them. `combine_masks` takes milliseconds in every port, below the report's resolution, so it is left out of the chart; the table holds it.

{{ ev.speed('fsl-maths') }}

{{ ev.table('fsl-maths', 'benchmark') }}

## Corrections by default {#corrections}

The replica corrects FSL's deterministic defects by default, `fix`, and warns. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives FSL's behaviour byte for byte, where FSL's behaviour is defined ([register](repo:docs/findings/upstream-defects.md)). Where FSL crashes or reads memory it never wrote, the replica refuses in `fix` and in `reproduce`, or gives a defined result.

- Values converted to an integer type outside its range, or NaN, are clamped (NaN to 0) instead of wrapping around (FSL-151).
- The thresholds, `-bin`, `-binv` and `-mas` bound their range without wrapping or rounding back to the maximum (FSL-152).
- A NaN first voxel no longer makes the image's minimum and maximum NaN, and NaN voxels stay out of the robust range and of the reductions' maxima and minima (FSL-153).
- `-dt char` and `-dt input` on a uint8 image compute in unsigned bytes (FSL-154).
- `-dt input` on int8, uint16, uint32, int64, uint64 or float128 images, where FSL writes nothing and exits with status 0, computes in the closest type and writes the result (FSL-155).
- Integer divisions by zero are refused instead of crashing (FSL-156).
- `-odt input` on int8 and uint16 images rounds as the other integer outputs do, and writes int8 as int8 (FSL-157).
- An operation missing its arguments is refused instead of reading past the command line (FSL-158), and an image of another size than the input for `-div`, `-rem`, `-max` and `-min` is refused (FSL-159).
- A Gaussian kernel of zero width leaves the image as it is instead of making it NaN (FSL-160); a kernel without voxels, an unknown kernel type and a negative width are refused (FSL-161).
- `-fmedian`, `-dilD`, `-rank` and `-ranknorm` leave NaN values out instead of stopping (FSL-162).
- `-subsamp2` and `-subsamp2offc` of a 4D image subsample every volume (FSL-163); `-dog_edge` of a 4D image filters every volume (FSL-164); `-fillh` of a single slice fills it (FSL-165).
- `-tensor_decomp` leaves a voxel whose tensor holds NaN or infinity at 0 (FSL-166).
- The standard deviation along a dimension takes the clamped variance, 0 for a single value (FSL-167); the percentiles leave NaN out (FSL-168), and so do `-pval`, `-pval0` and `-cpval` (FSL-169).
- `-ztop` of an infinite z gives 0 or 1 (FSL-170); `-bptf` with a width beyond an int is refused (FSL-171); `-ptoz` of a p-value below about 1.1 × 10<sup>−16</sup> gives its z (FSL-172).
- `-tfce` and `-tfceS` refuse a step that cannot advance (FSL-174), connectivities other than 6, 18 and 26 (FSL-176) and a voxel outside the image (FSL-178); `-tfce` of an image without positive values gives zeros (FSL-175); `-tfceS` sizes its arrays for every threshold (FSL-177).
- `-roc` refuses a noise image of another size (FSL-179) and a truth image without true or false voxels (FSL-180).
- A value more than about two billion bin widths above a histogram's range counts in its last bin (FSL-187: the robust range of `-thrp`, `-thrP`, `-uthrp`, `-uthrP`, shared with fslstats, BET and FLIRT).
- `-subsamp2` of an image 3 voxels wide computes its unused background value without writing past it (FSL-75, FLIRT's).
- glibc's double `exp`, `log` and `pow` are correctly rounded (GLIBC-07, [above](#glibc)).

The clean room makes the same corrections by default, with the same notices. Its `reproduce` follows FSL where FSL's behaviour is defined and known from the specification and black-box runs. For FSL-75 no output voxel depends on the corrupted value, so the clean room names it in `fix` and in `reproduce` and writes its output. It adds three corrections that its black-box runs found, registered with the same switches:

- with a kernel large enough for FSL's FFT, one NaN or infinite voxel makes FSL's whole volume NaN, where its direct sum for smaller kernels leaves NaN only within the kernel's reach; the default keeps that local result (FSL-191);
- on the same path FSL applies the kernel mirrored along every axis, where its direct sum applies it as stored, so the result of a kernel that is not point-symmetric depends on the kernel's and the image's sizes; the default keeps the direct sum's orientation at every size (FSL-192);
- `-roc` with a curve file it cannot write (a folder that does not exist) writes no curve and says nothing; the default stops with an error naming the file (FSL-193).

Its double-precision functions are correctly rounded by default ([above](#glibc)).

## Known limits {#limits}

Both ports are experimental. Each record's standard comparison holds fMRIPrep's calls on three fMRIPrep runs. The replica's full comparison, the data panel and the long random-testing runs come in the final validation phase.

The clean room is held to thresholds, not to FSL's bytes:

- where FSL convolves a large kernel by its FFT, FSL's single-precision FFT and the clean room's double sums differ by up to 2 × 10<sup>−7</sup> of FSL's largest value: within §21's bound, but below its share of voxels within 4 units in the last place on some images (expected divergences, with the clean room as close to the exact result or closer);
- FSL's arithmetic of `-subsamp2` under the floating types, the last bits of Φ and Φ<sup>−1</sup> in double precision and the eigenvectors' signs are questions for its specification;
- `erf` and `erfc` (in `-ztop`) come from the `libm` crate until LARMORX's own correctly rounded ones exist;
- random testing left 10 differences open ([above](#random)).

`tan`, `asin`, `acos` and `atan` in double precision are correctly rounded in both ports, in `fix` and in `reproduce` (as decided on 2026-11-04); since 2026-11-04 `sin`, `cos` and the FFT's twiddle factors (glibc's `sincos`) are glibc's bits in the replica's `reproduce`, and `sin`, `cos`, `exp`, `log` and `pow` in the clean room's ([above](#glibc)).

The goodvoxels calls use a stand-in for the cortical ribbon, the segmentation's grey matter. They are to be checked again with a real ribbon once an fMRIPrep run with FreeSurfer's reconstruction exists.

Images compressed with zstd or bzip2 are decompressed whole before they are read; gzip and uncompressed images are read as a stream.

The cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output. The clean room's cover the command line in three cases and the typed wrappers in four, each family with a path that makes NaN from numbers, so x86-64's NaN bits are checked on ARM too. The benchmark is informal: one run each, on a shared machine.

## History {#history}

- **2026-11-03**: the replica, translated from FSL 6.0.7.23's source, and its random-testing run, 114,906 fslmaths calls in 24 minutes beside fslstats'. The clean room, written from [specs/fslmaths.md](repo:specs/fslmaths.md), FSL's usage text and documentation and runs of FSL, and its random-testing run, 150,000 chains in 20 minutes beside fslstats'.
- **2026-11-04**: the replica's `reproduce` computes glibc's `sin`, `cos` and the FFT's twiddle factors as glibc 2.35 does; two of its mistakes in the sign of a NaN fixed; its record made again, 422 cases. The clean room's `reproduce` computes glibc's `sin`, `cos`, `exp`, `log`, `pow` and the filters' functions as glibc 2.35 does, with ten cases of its own; on FSL's FFT path it adds its products in double precision.
- **2026-11-07**: the clean room's record made again, 454 cases, with two permanent cases of random testing: series whose time step is 0 or negative.
