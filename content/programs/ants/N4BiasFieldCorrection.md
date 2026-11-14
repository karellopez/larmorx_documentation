---
title: "`N4BiasFieldCorrection`"
kicker: "Programs · ANTs and ITK"
lede: "`N4BiasFieldCorrection` removes a smooth intensity bias field from an image."
description: "LARMORX reference for ANTs 2.6.5 `N4BiasFieldCorrection`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: ants
  original: "ANTs 2.6.5"
  software: "ANTs"
  command: "larmorx ants N4BiasFieldCorrection"
  python: "lx.ants.n4_bias_field_correction"
  api: "docs/api/ants-n4.md"
  evidence: "/evidence/ants-n4/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-ants/src/cli/n4_bias_field_correction.rs: "e02d4b32f752029d"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "be80bfe4fac23290"
    docs/api/ants-n4.md: "88086041961aaaf7"
    python/larmorx/ants/n4.py: "e76e9f0fbb2cf0a1"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

The method is N4
(Tustison et al., *N4ITK: Improved N3 Bias Correction*, IEEE TMI 29(6), 2010); fMRIPrep, sMRIPrep
and sdcflows run it on BOLD references, T1w images and field maps' magnitudes.

## Command line {#command-line}

```text synopsis
larmorx ants N4BiasFieldCorrection [-d 2/3/4] -i input [-x mask] [-w weight] [-r 0/(1)] [-s (4)]
                 [-c [50x50x50x50,0.0]] [-b [splineDistance|meshResolution,<order=3>]]
                 [-t [0.15,0.01,200]] [-o corrected | [corrected,biasField]] [-v (0)/1]
```

Everything after `larmorx ants N4BiasFieldCorrection` is the original's command line: the arguments of ANTs 2.6.5's `N4BiasFieldCorrection`, as ANTs takes them. LARMORX's own options stand between `larmorx` and the family `ants`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        ants N4BiasFieldCorrection ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>N4BiasFieldCorrection</code>'s usage text, as the replica prints it</summary>

```text
COMMAND:
     N4BiasFieldCorrection (larmorx port of ANTs v2.6.5)
          N4 is a variant of the popular N3 (nonparameteric nonuniform normalization)
          retrospective bias correction algorithm (N. Tustison et al., N4ITK: Improved N3
          Bias Correction, IEEE Transactions on Medical Imaging, 29(6):1310-1320, June 2010).

OPTIONS:
     -d, --image-dimensionality 2/3/4
     -i, --input-image inputImageFilename
     -x, --mask-image maskImageFilename
     -r, --rescale-intensities 0/(1)
     -w, --weight-image weightImageFilename
     -s, --shrink-factor 1/2/3/(4)/...
     -c, --convergence [<numberOfIterations=50x50x50x50>,<convergenceThreshold=0.0>]
     -b, --bspline-fitting [splineDistance,<splineOrder=3>]
                           [initialMeshResolution,<splineOrder=3>]
     -t, --histogram-sharpening [<FWHM=0.15>,<wienerNoise=0.01>,<numberOfHistogramBins=200>]
     -o, --output correctedImage
                  [correctedImage,<biasField>]
     --version
     -v, --verbose (0)/1
     -h
     --help
```

</details>

## Python {#python}

```python
lx.ants.n4_bias_field_correction(
    image: Any,
    mask: Any = None,
    weight: Any = None,
    *,
    shrink_factor: int = 4,
    convergence: tuple[Sequence[int], float] = ((50, 50, 50, 50), 0.0),
    bspline_fitting: float | Sequence[float] | None = None,
    spline_order: int = 3,
    histogram_sharpening: tuple[float, float, int] = (0.15, 0.01, 200),
    rescale_intensities: bool = False,
    dimension: int | None = None,
    n_threads: int = 1,
    upstream_defects: UpstreamDefectsName = "fix",
) -> N4Result
```

Where `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

`N4BiasFieldCorrection -d D -i image [-x mask] [-w weight] -s shrink -c [iters,thr] -b [fitting,order] -t [fwhm,noise,bins] [-r] -o [corrected,bias]`.

Returns an `N4Result`: `corrected` and `bias_field`, float32 images on the input's grid (the
bias field is always returned), and `iterations`, every iteration as `N4Iteration(level,
iteration, convergence)`. `image` is a path, an `lx.Image`, a nibabel image or `(array,
affine)`, read as `float`.

```python
import larmorx as lx

res = lx.ants.n4_bias_field_correction("sub-01_T1w.nii.gz")                 # ANTs' defaults
res.corrected.to_filename("sub-01_desc-n4_T1w.nii.gz")

# sMRIPrep's final N4: weight = WM probability, spline distance 200 mm, five levels
res = lx.ants.n4_bias_field_correction(
    t1w, weight=wm_probseg, shrink_factor=4,
    convergence=([50] * 5, 1e-7), bspline_fitting=200, n_threads=8,
)
corrected, bias = res.corrected, res.bias_field

# with a brain mask, rescaled to the input's range inside it (the command line's default)
res = lx.ants.n4_bias_field_correction(boldref, mask=brain_mask, bspline_fitting=200,
                                       rescale_intensities=True)
```

Its result, `N4Result`, holds the corrected image, the bias field (the image divided by it gives `corrected`, except where a mask restores or rescales voxels), and every iteration.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">corrected</span></code> | <code><span class="nw">Image</span></code> |  |
| <code><span class="nw">bias&#95;field</span></code> | <code><span class="nw">Image</span></code> |  |
| <code><span class="nw">iterations</span></code> | <code><span class="nw">tuple&#91;N4Iteration&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `N4BiasFieldCorrection` accepts (`crates/larmorx-ants/src/cli/n4_bias_field_correction.rs`) and the arguments of `lx.ants.n4_bias_field_correction` (`python/larmorx/ants/n4.py`), whose defaults and descriptions are taken from it. Under each option, in grey, ANTs's own help for it.

| ANTs option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;d</span> <span class="nw">2&#47;3&#47;4</span></code>, <code><span class="nw">&#45;&#45;image&#45;dimensionality</span></code> | <code><span class="nw">dimension</span></code> | <code><span class="nw">None</span></code> | default: the image's; a 4D file read with <code><span class="nw">&#45;d</span> <span class="nw">3</span></code> gives its first volume; in 4D the time axis is not shrunk but gets a spline too |
| <code><span class="nw">&#45;i</span> <span class="nw">image</span></code>, <code><span class="nw">&#45;&#45;input&#45;image</span></code> | <code><span class="nw">image</span></code> |  | path, <code><span class="nw">lx&#46;Image</span></code>, nibabel image or <code><span class="nw">&#40;array&#44;</span> <span class="nw">affine&#41;</span></code>; read as <code><span class="nw">float</span></code> |
| <code><span class="nw">&#45;x</span> <span class="nw">mask</span></code>, <code><span class="nw">&#45;&#45;mask&#45;image</span></code> | <code><span class="nw">mask</span></code> | <code><span class="nw">None</span></code> | N4 uses the voxels where the mask is not 0; outside it the output keeps the input's values |
| <code><span class="nw">&#45;w</span> <span class="nw">weight</span></code>, <code><span class="nw">&#45;&#45;weight&#45;image</span></code> | <code><span class="nw">weight</span></code> | <code><span class="nw">None</span></code> | the fit weights each voxel by it; voxels with weight ≤ 0 are not used |
| <code><span class="nw">&#45;s</span> <span class="nw">4</span></code>, <code><span class="nw">&#45;&#45;shrink&#45;factor</span></code> | <code><span class="nw">shrink&#95;factor&#61;4</span></code> | <code><span class="nw">4</span></code> | <code><span class="nw">ShrinkImageFilter</span></code> along the spatial axes; 0 acts as 1 |
| <code><span class="nw">&#45;c</span> <span class="nw">&#91;50x50x50x50&#44;0&#46;0&#93;</span></code>, <code><span class="nw">&#45;&#45;convergence</span></code> | <code><span class="nw">convergence&#61;&#40;&#40;50&#44;</span> <span class="nw">50&#44;</span> <span class="nw">50&#44;</span> <span class="nw">50&#41;&#44;</span> <span class="nw">0&#46;0&#41;</span></code> | <code><span class="nw">&#40;&#40;50&#44;</span> <span class="nw">50&#44;</span> <span class="nw">50&#44;</span> <span class="nw">50&#41;&#44;</span> <span class="nw">0&#46;0&#41;</span></code> | iterations per level (one level per entry) and the threshold that ends a level |
| <code><span class="nw">&#45;b</span> <span class="nw">&#91;200&#93;</span></code>, <code><span class="nw">&#45;&#45;bspline&#45;fitting</span></code> | <code><span class="nw">bspline&#95;fitting&#61;200&#46;0</span></code> | <code><span class="nw">None</span></code> | a spline distance in mm: the image is padded so that whole spans of 200 mm cover it |
| <code><span class="nw">&#45;b</span> <span class="nw">&#91;2x2x3&#93;</span></code> | <code><span class="nw">bspline&#95;fitting&#61;&#40;2&#44;</span> <span class="nw">2&#44;</span> <span class="nw">3&#41;</span></code> | <code><span class="nw">None</span></code> | mesh elements per axis (control points = elements + order) |
| <code><span class="nw">&#45;b</span> <span class="nw">&#91;&#46;&#46;&#46;&#44;3&#93;</span></code> | <code><span class="nw">spline&#95;order&#61;3</span></code> | <code><span class="nw">3</span></code> |  |
| no <code><span class="nw">&#45;b</span></code> | <code><span class="nw">bspline&#95;fitting&#61;None</span></code> | <code><span class="nw">None</span></code> | one element per axis (4 control points for cubic splines) |
| <code><span class="nw">&#45;t</span> <span class="nw">&#91;0&#46;15&#44;0&#46;01&#44;200&#93;</span></code>, <code><span class="nw">&#45;&#45;histogram&#45;sharpening</span></code> | <code><span class="nw">histogram&#95;sharpening&#61;&#40;0&#46;15&#44;</span> <span class="nw">0&#46;01&#44;</span> <span class="nw">200&#41;</span></code> | <code><span class="nw">&#40;0&#46;15&#44;</span> <span class="nw">0&#46;01&#44;</span> <span class="nw">200&#41;</span></code> | the Gaussian's FWHM, the Wiener noise, the number of bins |
| <code><span class="nw">&#45;r</span> <span class="nw">0&#47;&#40;1&#41;</span></code>, <code><span class="nw">&#45;&#45;rescale&#45;intensities</span></code> | <code><span class="nw">rescale&#95;intensities&#61;False</span></code> | <code><span class="nw">False</span></code> | **different default**: the command line rescales whenever a mask is given unless <code><span class="nw">&#45;r</span> <span class="nw">0</span></code>; Python rescales only when asked (as ANTsPy). Without a mask it never applies |
| <code><span class="nw">&#45;o</span> <span class="nw">out</span></code> / <code><span class="nw">&#45;o</span> <span class="nw">&#91;out&#44;bias&#93;</span></code>, <code><span class="nw">&#45;&#45;output</span></code> | the result |  | its <code><span class="nw">corrected</span></code> and <code><span class="nw">bias&#95;field</span></code>, float32 images on the input's grid |
| <code><span class="nw">&#45;v</span> <span class="nw">1</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> | the result |  | ANTs' progress lines; Python returns every iteration in the result's <code><span class="nw">iterations</span></code> |
| <code><span class="nw">&#45;&#45;version</span></code> | (command line only) |  | the version line |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | (command line only) |  | ANTs' short and long help |
| <code><span class="nw">ITK&#95;GLOBAL&#95;DEFAULT&#95;NUMBER&#95;OF&#95;THREADS</span></code> (or <code><span class="nw">NSLOTS</span></code>, as ITK reads them) | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | **ANTs' result depends on it; larmorx's does not**: it always gives ANTs' one-thread result |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | <code><span class="nw">fix</span></code> (default) or <code><span class="nw">reproduce</span></code> ([Upstream defects](repo:docs/api/ants-n4.md#upstream-defects-d13)) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `ants` on the command line (`larmorx --n-threads 4 ants N4BiasFieldCorrection ...`); `lx.ants.n4_bias_field_correction` takes `n_threads` and `upstream_defects` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;n4&#95;bias&#95;field&#95;correction</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `t1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# ANTs' defaults: four levels of 50 iterations, shrink factor 4.
res = lx.ants.n4_bias_field_correction("t1w.nii.gz")
res.corrected.data.dtype  # -> dtype('float32')
```

```bash
larmorx ants N4BiasFieldCorrection -d 3 -i t1w.nii.gz -o [ corrected.nii.gz, bias.nii.gz ]
```

## Ports {#ports}

`N4BiasFieldCorrection` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [ants-n4](repo:docs/validation/ants-n4.md) |

**The replica: status `validated`** against N4BiasFieldCorrection itself (its
[record](repo:docs/validation/ants-n4.md), 2026-10-24, standard tier: 52 cases, 47 pass, 5 rejected by
both alike; 46 compared cases, in 2, 3 and 4 dimensions), on every command line fMRIPrep,
sMRIPrep and sdcflows give it:
- against the **unmodified ANTs 2.6.5 binary** at one thread: 29 of 46 cases bit-identical.
  The others differ only because glibc's `expf`, `logf`, `exp` and `sincos` are not always
  correctly rounded and larmorx's are; the differences are smaller than ANTs' own difference
  between thread counts in 14 of the 17 cases, up to 5.3 times that in three, and NCC is at
  least 0.9999999 (corrected images) and 0.9999998 (bias fields);
- against the **same binary run with glibc's `expf`, `logf`, `exp`, `log`, `sin`, `cos` and
  `sincos` replaced by CORE-MATH's correctly rounded ones** (`LD_PRELOAD`,
  `scripts/build_crmath_preload.sh`), which is the arithmetic larmorx uses: **46 of 46 cases
  bit-identical**. ANTs' own code is not changed; only those C-library functions are;
- the same against **fMRIPrep 25.2.6's own ANTs (2.6.2)**, on the 45 cases of the record before
  it: 45 of 45 bit-identical with CORE-MATH, 29 of 45 as built
  ([findings](repo:docs/findings/ants-n4.md)).

**On the data panel** ([record](repo:docs/validation/ants-n4-panel.md), 2026-10-26): all 64 N4 nodes of
the fourteen finished fMRIPrep oracle runs (the BOLD references, the brain extraction's and the
final anatomical corrections, the field maps' magnitudes; the 3.5-year-old, the glioma, the
stroke, strong motion, 1.5 T, 7 T, multiband-8 and multi-echo among them), each replayed from its
node with its inputs, and sMRIPrep's final options on five images fMRIPrep never corrects (the
7 T MP2RAGE, a 3 T MP2RAGE UNIT1, the 82-year-old's FLAIR, a glioma's T2w of 6 mm slices, the
stroke's T2w fitted outside its lesion): **69 of 69 bit-identical with CORE-MATH** (20 to the
unmodified ANTs; the others within 0.042 of ANTs' own difference between one thread and two or
three). The panel also checked the input-geometry check: a mask written from the T2w's affine
(2e-6 mm off) is refused by both.

`N4BiasFieldCorrection` has one port, in `pip install larmorx`: **the replica**
(`crates/larmorx-ants`, `crates/larmorx-image`; Apache-2.0; Rust
`larmorx_ants::n4_bias_field_correction`, `larmorx_image::n4`), translated from ANTs 2.6.5's
`N4BiasFieldCorrection` on ITK 5.4.5's `N4BiasFieldCorrectionImageFilter` (Apache-2.0). Its
result does not depend on the thread count: it is always ANTs' one-thread result.

larmorx computes what ITK's C++ source defines. ANTs built by GCC 11.4 at `-O3` (Ubuntu
22.04's compiler) does not: GCC bug 110182 drops two float roundings of the B-spline fit, so
such a build gives slightly different N4 results
([findings](repo:docs/findings/ants-n4.md), "GCC 11 miscompiles the fit").

## Evidence {#evidence}

How each of `N4BiasFieldCorrection`'s ports was measured against ANTs, case by case: [its evidence](/evidence/ants-n4/).

## More in the repository {#more}

The API page [docs/api/ants-n4.md](repo:docs/api/ants-n4.md) holds what `N4BiasFieldCorrection` shares with the page's other programs:

- [Speed](repo:docs/api/ants-n4.md#speed)
- [Behaviour worth knowing](repo:docs/api/ants-n4.md#behaviour-worth-knowing)
- [Upstream defects (D13)](repo:docs/api/ants-n4.md#upstream-defects-d13)
- [Deliberate differences](repo:docs/api/ants-n4.md#deliberate-differences)
- [Rust](repo:docs/api/ants-n4.md#rust)
