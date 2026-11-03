---
title: fslmaths
kicker: Tools · FSL
lede: >-
  FSL's image calculator: an image, then a chain of operations applied from left to right
  (arithmetic, thresholds, voxelwise functions, masks, kernels and filters, reductions along a
  dimension, statistical transforms, temporal filtering, the threshold-free cluster enhancement),
  then an output. fMRIPrep calls it in every BOLD reference's brain mask and fourteen times in
  its optional goodvoxels mask. An exact replica of FSL 6.0.7.23's source in the separate
  larmorx-nc package (the FSL Licence's non-commercial terms), experimental, which gives every
  file fslmaths writes, its messages and its exit status bit for bit in every compared case of
  its record but two, fMRIPrep's calls included. The clean-room original is still to be written.
description: LARMORX's fslmaths, an exact replica validated against FSL 6.0.7.23 — fMRIPrep's mask combination on its oracle runs and its goodvoxels mask's fourteen calls, one call per operation family on a real BOLD series (the FFT convolution among them), glibc's double functions on a real image (GLIBC-07), random testing's trial, and every parity case of the record with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>exact replica (<code>larmorx-nc</code>, under the FSL Licence's terms, run as a separate program), translated from FSL 6.0.7.23's source (fsl-avwutils 2209.6, with fsl-newimage 2601.0's image functions, fsl-miscmaths 2412.6 and fsl-cprob 2111.0); clean-room original (<code>larmorx</code>, Apache-2.0): planned, to be written from <a href="{{ repo('specs/fslmaths.md') }}">specs/fslmaths.md</a></dd>
<dt>Status</dt><dd><span class="status-tag status-tag--experimental">experimental</span> (replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/fsl-maths-replica.md') }}">fsl-maths-replica</a> (standard tier, FSL 6.0.7.23) · API <a href="{{ repo('docs/api/fsl-maths.md') }}">fsl-maths</a> · its companion: <a href="{{ link('/tools/fsl-stats/') }}">fslstats</a></dd>
</dl>

## What it is

`fslmaths <input> [operations] <output>` reads an image, applies each operation in turn to the current image and writes the result: arithmetic with a number or another image (`-add`, `-sub`, `-mul`, `-div`, `-rem`, `-mas`, `-max`, `-min`), thresholds by value or by percentage of the robust range (`-thr`, `-thrp`, `-thrP` and their upper forms), voxelwise functions (`-exp`, `-log`, the trigonometric functions, `-sqrt`, `-abs`, `-bin`, `-nan`, `-index`, `-grid`, seeded noise), kernels and the operations that use them (dilations and erosions, mean and median filters, Gaussian smoothing, convolutions by direct sums or by the FFT, subsampling, edges, hole filling), mean normalisation, reductions along a dimension (`-Tmean`, `-Tstd`, `-Tmax`, `-Tmedian`, `-Tperc`, `-Tar1` and their X, Y and Z forms), p-values, ranks and z ↔ p conversions, regions, band-pass temporal filtering (`-bptf`), the threshold-free cluster enhancement (`-tfce`, `-tfceS`), ROC curves (`-roc`) and the diffusion tensor's decomposition. `-dt` chooses the type it computes in (float by default, or double), `-odt` the output's.

fMRIPrep calls it in niworkflows' BOLD reference workflows (`combine_masks`: `fslmaths <mask> -mul <mask> <out>`, the reference's brain mask as the product of two masks) and, with `--project-goodvoxels`, fourteen times in its goodvoxels mask, with four fslstats calls between them.

```bash
larmorx fsl fslmaths mask_a.nii.gz -mul mask_b.nii.gz combined.nii.gz
larmorx fsl fslmaths bold.nii.gz -Tstd -div mean.nii.gz cov.nii.gz
```

```python
import larmorx as lx

combined = lx.fsl.fslmaths("mask_a.nii.gz", "-mul", "mask_b.nii.gz")   # the command line's operations
smooth = lx.fsl.smooth("mean.nii.gz", sigma=3.0)                       # one typed wrapper per family
```

FSL is distributed under the FSL Licence, which allows non-commercial use only, so LARMORX keeps its FSL tools in two implementations: the exact replica translated from FSL's source, in the separate package `larmorx-nc` (`pip install larmorx-nc`), and a clean-room original in LARMORX itself, written from a behavioural specification without FSL's code. For fslmaths only the replica exists so far: `larmorx fsl fslmaths` and `lx.fsl.fslmaths` run it when `larmorx-nc` is installed, and a clear error names the package otherwise. The replica follows FSL 6.0.7.23 and needs no FSL installation; what fslmaths needs from FSL's libraries (newimage's image functions, kernels, morphology, convolutions, connected components and TFCE, the Cephes probability functions of fsl-cprob, Armadillo's Kiss FFT and symmetric eigen-decomposition) is translated once into `larmorx-nc`'s shared core, beside what mcflirt, BET, FLIRT, FAST and topup use; BET's own `fslmaths` and `fslstats` calls run the same code. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

The replica is a translation of FSL's source, so the question for it is whether it gives FSL's bytes: every file fslmaths writes (each image's header and data), its standard output and error, and its exit status.

{{ ev.agreement('fsl-maths', 'replica') }}

The record runs 421 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-maths-replica.md)): 358 give FSL's files byte for byte, in 61 FSL refuses the input or stops and the replica does the same, with the same message and exit status (*rejected by both*), and 2 differ by one unit in the last place of a few values, where FSL's result comes from glibc 2.35's mathematical functions that are not correctly rounded and the replica's is (GLIBC-07, *expected divergence*, [below](#glibc)). They cover fMRIPrep's calls (the four `combine_masks` calls of three oracle runs and the goodvoxels mask's fourteen), every operation and option of the command line in every data type, the odd headers and sizes, FSL's own failure cases, and the defects LARMORX corrects by default: each case also runs the replica's default mode, which names every correction where it changes the result (below).

## In fMRIPrep: a BOLD reference's brain mask {#combine}

fMRIPrep's `combine_masks` node of ds005040's head-motion reference: the mask of BET's first pass on the reference times the template's brain mask brought onto it, given to FSL 6.0.7.23 and to the replica in its reproduce and default modes. Each mask is drawn over the reference it was computed from. Below the viewer, every `combine_masks` call of the record: ds000005, ds005040 (both kinds of reference) and ds003592, each the same bytes as FSL's and as fMRIPrep's own output.

{{ ev.example('fsl-maths', 'combine') }}

## In fMRIPrep: the goodvoxels mask {#goodvoxels}

With `--project-goodvoxels`, fMRIPrep leaves out of the surface projection the voxels whose temporal coefficient of variation is high compared with their neighbourhood in the cortical ribbon: fourteen fslmaths calls and four fslstats calls (`init_goodvoxels_bold_mask_wf`). The oracle runs do not use the option, so the workflow is built from fMRIPrep's code on ds005040's BOLD series in T1w space, each call with its arguments as the workflow makes them and its inputs FSL's outputs of the calls before it. The runs have no FreeSurfer reconstruction, so the cortical ribbon is a stand-in: the anatomical segmentation's grey matter at each BOLD voxel. Every call's output is FSL's bit for bit, and so are the four numbers fslstats prints between them ([fslstats' page](/tools/fsl-stats/#goodvoxels)).

{{ ev.example('fsl-maths', 'goodvoxels') }}

## One call per operation family {#families}

fslmaths' operation families on the same real series, one call each: arithmetic with images (the temporal SNR), a threshold by the robust range, a voxelwise function, reductions along time, morphology, the three kinds of filters (Gaussian smoothing by separable sums, a mean filter whose large spherical kernel fslmaths convolves by the FFT, a median filter), edges, normalisation, temporal filtering, a region and the threshold-free cluster enhancement. Every output is FSL's bit for bit, in both modes.

{{ ev.example('fsl-maths', 'families') }}

## GLIBC-07: glibc's double-precision functions {#glibc}

FSL's build takes its mathematical functions from glibc 2.35, whose double-precision `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `exp`, `log` and `pow` are not always correctly rounded: for a small share of arguments the result is one unit in the last place from the exact value. LARMORX computes them correctly rounded, the same on every platform (CORE-MATH). In fslmaths' default type, float, the double result is rounded to float and no value differs; with `-dt double` the last place shows. The table runs each function on a real image (FSL's mean of ds005040's series, scaled into the function's range): for `exp` and `log` the reproduce mode gives glibc's own bits and the default mode corrects them with a notice; for the six functions whose glibc code is IBM's Accurate Mathematical Library (LGPL), no permissive code gives glibc's bits, so the replica is correctly rounded in both modes and differs from FSL on those values (*expected divergence*). glibc chooses the build of each of these functions at run time (an FMA build on every x86-64 CPU since 2013, as on the oracle machine); FSL's own double results therefore depend on the CPU, and "glibc's bits" here are the FMA build's.

{{ ev.table('fsl-maths', 'glibc-double') }}

The record's two expected divergences are both GLIBC-07. [`fn/double-tan`](#case=fn/double-tan): `-dt double -tan`, 3 of 210 values one unit in the last place. [`difftest/fft-twiddles-glibc-sincos`](#case=difftest/fft-twiddles-glibc-sincos), from random testing: a mean filter of a 30 × 1 × 3 float image that fslmaths convolves by the FFT, 1 of 90 voxels one unit in the last place. fslmaths' FFT (Armadillo's Kiss FFT) takes each twiddle factor from glibc's `sincos`, which is not correctly rounded on 0.148 % of the angles (of the transform lengths 1 to 256, 80 hold a factor one unit in the last place from the exact one), while the replica computes the factors correctly rounded. Given FSL's own factors, the replica's FFT gives Armadillo's values on every length from 1 to 256 (0 of 197,376 values differ) and this case FSL's output bit for bit ([the probe](repo:validation/probes/fsl-avwutils-lib/README.md)): the difference is the factors, nothing else. It is rare: a float result usually rounds it away (the FFT convolution of the real series above is FSL's bit for bit), and fMRIPrep's calls convolve by separable sums. An exact reproduction of glibc's functions is planned by a clean-room implementation of their behaviour.

## Random testing {#random}

Differential random testing's trial of this part: 24 minutes of random chains of operations on random images, each run by FSL 6.0.7.23 (through the oracle cache) and by the replica, every file compared.

{{ ev.table('fsl-maths', 'trial') }}

## Every case {#cases}

Each case of the record, with what it tests, its command line, its verdict and the reason. Search, filter (or select a segment of the chart above), sort; `#case=<name>` links to one.

{{ ev.cases('fsl-maths') }}

## Corrections by default {#corrections}

The replica corrects FSL's deterministic defects by default and warns, with `upstream_defects="reproduce"` (`LARMORX_UPSTREAM_DEFECTS=reproduce`) giving FSL's behaviour byte for byte where FSL's is defined ([register](repo:docs/findings/upstream-defects.md)); where FSL crashes or reads memory it never wrote, the replica refuses in both modes or gives a defined result. Values converted to an integer type outside its range, or NaN, are clamped (NaN to 0) instead of wrapping around (FSL-151). The thresholds, `-bin`, `-binv` and `-mas` bound their range without wrapping or rounding back to the maximum (FSL-152). A NaN first voxel no longer makes the image's minimum and maximum NaN, and NaN voxels stay out of the robust range and of the reductions' maxima and minima (FSL-153). `-dt char` and `-dt input` on a uint8 image compute in unsigned bytes (FSL-154). `-dt input` on int8, uint16, uint32, int64, uint64 or float128 images, where FSL writes nothing and exits with status 0, computes in the closest type and writes the result (FSL-155). Integer divisions by zero are refused instead of crashing (FSL-156). `-odt input` on int8 and uint16 images rounds as the other integer outputs do and writes int8 as int8 (FSL-157). An operation missing its arguments is refused instead of reading past the command line (FSL-158), and an image of another size than the input for `-div`, `-rem`, `-max` and `-min` is refused (FSL-159). A Gaussian kernel of zero width leaves the image as it is instead of making it NaN (FSL-160); a kernel without voxels, an unknown kernel type and a negative width are refused (FSL-161). `-fmedian`, `-dilD`, `-rank` and `-ranknorm` leave NaN values out instead of stopping (FSL-162). `-subsamp2` and `-subsamp2offc` of a 4D image subsample every volume (FSL-163); `-dog_edge` of a 4D image filters every volume (FSL-164); `-fillh` of a single slice fills it (FSL-165); `-tensor_decomp` leaves a voxel whose tensor holds NaN or infinity at 0 (FSL-166). The standard deviation along a dimension takes the clamped variance, 0 for a single value (FSL-167); the percentiles leave NaN out (FSL-168), and so do `-pval`, `-pval0` and `-cpval` (FSL-169). `-ztop` of an infinite z gives 0 or 1 (FSL-170); `-bptf` with a width beyond an int is refused (FSL-171); `-ptoz` of a p-value below about 1.1 × 10<sup>−16</sup> gives its z (FSL-172). `-tfce` and `-tfceS` refuse a step that cannot advance (FSL-174), connectivities other than 6, 18 and 26 (FSL-176) and a voxel outside the image (FSL-178); `-tfce` of an image without positive values gives zeros (FSL-175); `-tfceS` sizes its arrays for every threshold (FSL-177). `-roc` refuses a noise image of another size (FSL-179) and a truth image without true or false voxels (FSL-180). A value more than about two billion bin widths above a histogram's range counts in its last bin (FSL-187: the robust range of `-thrp`, `-thrP`, `-uthrp`, `-uthrP`, shared with fslstats, BET and FLIRT). `-subsamp2` of an image 3 voxels wide computes its unused background value without writing past it (FSL-75, FLIRT's). glibc's double `exp`, `log` and `pow` are correctly rounded (GLIBC-07, [above](#glibc)).

## Known limits {#limits}

The replica is experimental. The record's standard tier holds fMRIPrep's calls on three oracle runs; its full tier, the data panel and long random testing run in the final validation phase. The goodvoxels calls use a stand-in for the cortical ribbon, the segmentation's grey matter: they are to be checked again with a real ribbon once an fMRIPrep run with FreeSurfer's reconstruction exists. glibc's double-precision `sin`, `cos`, `tan`, `asin`, `acos` and `atan`, and the FFT's twiddle factors (glibc's `sincos`), are correctly rounded in both modes: their glibc bits wait for a clean-room implementation of glibc's behaviour. Images compressed with zstd or bzip2 are decompressed whole before they are read (gzip and uncompressed images are read as a stream). The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md). There is no benchmark report yet: speed is measured with the clean-room original.
