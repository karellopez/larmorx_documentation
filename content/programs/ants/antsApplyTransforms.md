---
title: "`antsApplyTransforms`"
kicker: "Programs · ANTs and ITK"
lede: "`antsApplyTransforms` resamples an image onto the grid of a reference image through a chain of ITK transforms (linear transforms, displacement fields, B-spline transforms and composites of them), or writes the chain itself as one transform."
description: "LARMORX reference for ANTs 2.6.5 `antsApplyTransforms`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: ants
  original: "ANTs 2.6.5"
  software: "ANTs"
  command: "larmorx ants antsApplyTransforms"
  python: "lx.ants.apply_transforms"
  api: "docs/api/ants-apply-transforms.md"
  evidence: "/evidence/ants-apply-transforms/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-ants/src/cli/apply_transforms.rs: "273396bbed751a07"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "be80bfe4fac23290"
    docs/api/ants-apply-transforms.md: "4b5e49727fac01af"
    python/larmorx/ants/apply_transforms.py: "73d57b88561149f0"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

[Transform outputs](repo:docs/api/ants-apply-transforms.md#transform-outputs)
says how it writes the chain. fMRIPrep runs it for the masks, references, tissue maps and segmentations it moves to the
templates and the T1w, its confounds' masks and its reports' images.

## Command line {#command-line}

```text synopsis
larmorx ants antsApplyTransforms ...
```

Everything after `larmorx ants antsApplyTransforms` is the original's command line: the arguments of ANTs 2.6.5's `antsApplyTransforms`, as ANTs takes them. LARMORX's own options stand between `larmorx` and the family `ants`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        ants antsApplyTransforms ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>antsApplyTransforms</code>'s usage text, as the replica prints it</summary>

```text
COMMAND:
     antsApplyTransforms (larmorx port of ANTs v2.6.5)
          Resamples an image through a chain of transforms onto a reference grid.

OPTIONS:
     -d, --dimensionality 3
     -e, --input-image-type 0/1/2/3/4/5/6
                            scalar/vector/tensor/time-series/multichannel/five-dimensional/physical-vector
                            (larmorx supports scalar and time-series)
     --time-index <index>   extract one volume of a time series
     -i, --input inputFileName
     -r, --reference-image imageFileName
     -o, --output warpedOutputFileName
                  [warpedOutputFileName,0]
     -n, --interpolation Linear
                         NearestNeighbor
                         MultiLabel[<sigma=imageSpacing>,<alpha=4.0>]
                         Gaussian[<sigma=imageSpacing>,<alpha=1.0>]
                         BSpline[<order=3>]
                         CosineWindowedSinc
                         WelchWindowedSinc
                         HammingWindowedSinc
                         LanczosWindowedSinc
                         GenericLabel[<interpolator=Linear>]
     -u, --output-data-type char/uchar/short/int/float/double/default
     -t, --transform transformFileName
                     [transformFileName,useInverse]
     -f, --default-value value
     --float 0/1
     -v, --verbose (0)/1
     -h
     --help
```

</details>

## Python {#python}

```python
lx.ants.apply_transforms(
    image: Any,
    reference: Any,
    transforms: TransformLike | Sequence[TransformLike] = (),
    *,
    invert: Sequence[bool] | None = None,
    interpolation: str = "linear",
    sigma: float | Sequence[float] | None = None,
    alpha: float | None = None,
    order: int = 3,
    time_series: bool | None = None,
    default_value: float = 0.0,
    dtype: Any = None,
    precision: Precision = "float64",
    n_threads: int = 1,
    upstream_defects: UpstreamDefectsName = "fix",
) -> Image
```

Where `Precision` is one of `"float64"`, `"float32"`; `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

Resample `image` onto the grid of `reference` through `transforms` (`antsApplyTransforms`).

Resamples `image` onto the grid of `reference`. Returns an `lx.Image`: float64 data (float32
with `precision="float32"`) on the reference grid, plus a time axis for a series.

**Precision.** `precision="float64"` (the default) computes in double, as ANTs does by
default; `precision="float32"` computes in single precision exactly as
`antsApplyTransforms --float 1` does: the image is read as float32, transform files are read as
ITK's float reader reads them (a text file's numbers rounded once to float), points, transform
arithmetic and continuous indices are float, and the result is float32. What is float and what
stays double, step by step: [ants-float.md](repo:docs/findings/ants-float.md).

**Transform order.** As with `-t`, for each point of the output grid the *first* transform
acts first. So `[warp, affine]` maps an output point `x` to `affine(warp(x))`. Equivalently,
the image moves by the affine first, then the warp; that is ANTs' "last transform is applied
first". `apply_transforms_to_points` maps points the same way.

**Files and in-memory images.** Paths are read as ITK reads them: ITK's choice between qform
and sform, and ITK's rescaling of scaled integer data through float32. This is what makes the
output match ANTs bit for bit. `lx.Image` objects, nibabel images and `(array, affine)` pairs
are placed by their affine.

```python
import larmorx as lx

# fMRIPrep's T1w → MNI (an .h5 composite: affine + warp), onto the 2 mm template grid
mni = lx.ants.apply_transforms(
    "sub-01_desc-preproc_T1w.nii.gz",
    "tpl-MNI152NLin2009cAsym_res-02_T1w.nii.gz",
    ["sub-01_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5"],
    interpolation="lanczos",
    n_threads=8,
)
mni.save("sub-01_space-MNI_T1w.nii.gz")

# A 4D BOLD series into T1w space, labels with GenericLabel
bold_t1 = lx.ants.apply_transforms(bold_path, t1w_path, [xfm_txt], interpolation="lanczos")
aseg = lx.ants.apply_transforms(aseg_path, boldref_path, [xfm_txt], interpolation="genericlabel", dtype="int16")
```

Its result, `Image`, holds a voxel array placed in world space by an affine.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">data</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">affine</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">header</span></code> | <code><span class="nw">NiftiHeader</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">implementation</span></code> | <code><span class="nw">Implementation</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `antsApplyTransforms` accepts (`crates/larmorx-ants/src/cli/apply_transforms.rs`) and the arguments of `lx.ants.apply_transforms` (`python/larmorx/ants/apply_transforms.py`), whose defaults and descriptions are taken from it. Under each option, in grey, ANTs's own help for it.

| ANTs option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;d</span> <span class="nw">3</span></code>, <code><span class="nw">&#45;&#45;dimensionality</span></code> | – |  | 3D only for now |
| <code><span class="nw">&#45;i</span> <span class="nw">file</span></code>, <code><span class="nw">&#45;&#45;input</span></code> | <code><span class="nw">image</span></code> |  | path, <code><span class="nw">lx&#46;Image</span></code>, nibabel image or <code><span class="nw">&#40;array&#44;</span> <span class="nw">affine&#41;</span></code> |
| <code><span class="nw">&#45;r</span> <span class="nw">file</span></code>, <code><span class="nw">&#45;&#45;reference&#45;image</span></code> | <code><span class="nw">reference</span></code> |  | only its grid is used |
| <code><span class="nw">&#45;o</span> <span class="nw">file</span></code>, <code><span class="nw">&#45;&#45;output</span></code> | the result |  | the returned image (its <code><span class="nw">&#46;save&#40;path&#41;</span></code> writes it) |
| <code><span class="nw">&#45;o</span> <span class="nw">Linear&#91;file&#44;&#60;invert&#61;0&#62;&#93;</span></code> | (another function) |  | <code><span class="nw">lx&#46;ants&#46;combine&#95;transforms&#40;&#46;&#46;&#46;&#44;</span> <span class="nw">output&#61;&#34;linear&#34;&#44;</span> <span class="nw">invert&#95;linear&#61;&#46;&#46;&#46;&#41;</span></code>: [Transform outputs](repo:docs/api/ants-apply-transforms.md#transform-outputs) |
| <code><span class="nw">&#45;o</span> <span class="nw">CompositeTransform&#91;file&#93;</span></code> | (another function) |  | <code><span class="nw">lx&#46;ants&#46;combine&#95;transforms&#40;&#46;&#46;&#46;&#44;</span> <span class="nw">output&#61;&#34;composite&#34;&#41;</span></code>: [Transform outputs](repo:docs/api/ants-apply-transforms.md#transform-outputs) |
| <code><span class="nw">&#45;o</span> <span class="nw">DisplacementField&#91;file&#93;</span></code>, <code><span class="nw">&#45;o</span> <span class="nw">&#91;file&#44;1&#93;</span></code> | (another function) |  | <code><span class="nw">lx&#46;ants&#46;combine&#95;transforms&#40;&#46;&#46;&#46;&#44;</span> <span class="nw">output&#61;&#34;displacement&#95;field&#34;&#44;</span> <span class="nw">reference&#61;&#46;&#46;&#46;&#41;</span></code>: [Transform outputs](repo:docs/api/ants-apply-transforms.md#transform-outputs) |
| <code><span class="nw">&#45;t</span> <span class="nw">file</span></code> / <code><span class="nw">&#45;t</span> <span class="nw">&#91;file&#44;1&#93;</span></code>, <code><span class="nw">&#45;&#45;transform</span></code> | <code><span class="nw">transforms&#61;&#91;file&#93;</span></code>, <code><span class="nw">invert&#61;&#91;True&#93;</span></code> | <code><span class="nw">transforms&#61;&#40;&#41;</span></code>, <code><span class="nw">invert&#61;None</span></code> | files or <code><span class="nw">lx&#46;transforms&#46;read&#40;&#46;&#46;&#46;&#41;</span></code> lists: linear transforms, displacement fields, B-spline transforms (<code><span class="nw">BSplineTransform&#95;double&#95;3&#95;3</span></code>, <code><span class="nw">&#95;float&#95;3&#95;3</span></code>, as antsRegistration's <code><span class="nw">BSpline</span></code> stage writes them) and composites of them; linear transforms only can be inverted (a field or a B-spline transform has no inverse: <code><span class="nw">&#91;file&#44;1&#93;</span></code> fails, as in ANTs). **Nothing is inverted by default**, unlike ANTsPy, which inverts the first of <code><span class="nw">&#91;&#46;mat&#44;</span> <span class="nw">warp&#93;</span></code> |
| <code><span class="nw">&#45;t</span> <span class="nw">identity</span></code> | <code><span class="nw">transforms&#61;&#40;&#41;</span></code> | <code><span class="nw">&#40;&#41;</span></code> | Transform files (<code><span class="nw">&#46;mat</span></code>, <code><span class="nw">&#46;txt</span></code>, <code><span class="nw">&#46;h5</span></code>, warp <code><span class="nw">&#46;nii&#46;gz</span></code>; B-spline transforms included, as antsRegistration's <code><span class="nw">BSpline</span></code> stage writes them) or <code><span class="nw">ItkTransform</span></code> lists, in <code><span class="nw">&#45;t</span></code> order: for each point of the output grid the first transform is applied first, so <code><span class="nw">&#91;warp&#44;</span> <span class="nw">affine&#93;</span></code> moves the image by the affine, then the warp, as <code><span class="nw">&#45;t</span> <span class="nw">warp</span> <span class="nw">&#45;t</span> <span class="nw">affine</span></code> does. |
| <code><span class="nw">&#45;n</span> <span class="nw">Linear</span></code>, <code><span class="nw">&#45;&#45;interpolation</span></code> | <code><span class="nw">interpolation&#61;&#34;linear&#34;</span></code> | <code><span class="nw">&#34;linear&#34;</span></code> | default |
| <code><span class="nw">&#45;n</span> <span class="nw">NearestNeighbor</span></code> | <code><span class="nw">interpolation&#61;&#34;nearest&#34;</span></code> | <code><span class="nw">&#34;linear&#34;</span></code> | <code><span class="nw">linear</span></code>, <code><span class="nw">nearest</span></code>, <code><span class="nw">bspline</span></code> (<code><span class="nw">order</span></code> 0–5), <code><span class="nw">gaussian</span></code> and <code><span class="nw">multilabel</span></code> (<code><span class="nw">sigma</span></code> in mm, default the input spacing; <code><span class="nw">alpha</span></code> in sigmas, default 1 and 4), <code><span class="nw">genericlabel</span></code>, or a windowed sinc: <code><span class="nw">lanczos</span></code>, <code><span class="nw">hamming</span></code>, <code><span class="nw">cosine</span></code>, <code><span class="nw">welch</span></code>, <code><span class="nw">blackman</span></code>. ANTs' names (<code><span class="nw">LanczosWindowedSinc</span></code>, ...) work too. |
| <code><span class="nw">&#45;n</span> <span class="nw">BSpline&#91;order&#93;</span></code> | <code><span class="nw">interpolation&#61;&#34;bspline&#34;</span></code>, <code><span class="nw">order&#61;3</span></code> | <code><span class="nw">interpolation&#61;&#34;linear&#34;</span></code>, <code><span class="nw">order&#61;3</span></code> | orders 0–5 |
| <code><span class="nw">&#45;n</span> <span class="nw">Gaussian&#91;sigma&#44;alpha&#93;</span></code> | <code><span class="nw">interpolation&#61;&#34;gaussian&#34;</span></code>, <code><span class="nw">sigma&#61;</span></code>, <code><span class="nw">alpha&#61;</span></code> | <code><span class="nw">interpolation&#61;&#34;linear&#34;</span></code>, <code><span class="nw">sigma&#61;None</span></code>, <code><span class="nw">alpha&#61;None</span></code> | sigma in mm (one value or three); defaults: input spacing, 1 |
| <code><span class="nw">&#45;n</span> <span class="nw">MultiLabel&#91;sigma&#44;alpha&#93;</span></code> | <code><span class="nw">interpolation&#61;&#34;multilabel&#34;</span></code>, <code><span class="nw">sigma&#61;</span></code>, <code><span class="nw">alpha&#61;</span></code> | <code><span class="nw">interpolation&#61;&#34;linear&#34;</span></code>, <code><span class="nw">sigma&#61;None</span></code>, <code><span class="nw">alpha&#61;None</span></code> | alpha default 4 (ANTs ignores the command line's, ANTS-33 in [Upstream defects](repo:docs/api/ants-apply-transforms.md#upstream-defects-d13)) |
| <code><span class="nw">&#45;n</span> <span class="nw">GenericLabel&#91;Linear&#93;</span></code> | <code><span class="nw">interpolation&#61;&#34;genericlabel&#34;</span></code> | <code><span class="nw">&#34;linear&#34;</span></code> | <code><span class="nw">GenericLabel&#91;NearestNeighbor&#93;</span></code> interpolates each label's mask by nearest neighbour (ANTs ignores the parameter, ANTS-33) |
| <code><span class="nw">&#45;n</span> <span class="nw">LanczosWindowedSinc</span></code> (and Cosine, Hamming, Welch, Blackman) | <code><span class="nw">interpolation&#61;&#34;lanczos&#34;</span></code>, <code><span class="nw">&#34;cosine&#34;</span></code>, <code><span class="nw">&#34;hamming&#34;</span></code>, <code><span class="nw">&#34;welch&#34;</span></code>, <code><span class="nw">&#34;blackman&#34;</span></code> | <code><span class="nw">&#34;linear&#34;</span></code> | ANTs' names are accepted too |
| <code><span class="nw">&#45;e</span> <span class="nw">0</span></code> / <code><span class="nw">&#45;e</span> <span class="nw">3</span></code>, <code><span class="nw">&#45;&#45;input&#45;image&#45;type</span></code> | <code><span class="nw">time&#95;series&#61;None&#47;False&#47;True</span></code> | <code><span class="nw">None</span></code> | 4D images are resampled volume by volume by default; <code><span class="nw">False</span></code> with 4D is an error, as <code><span class="nw">&#45;e</span> <span class="nw">0</span></code> is |
| <code><span class="nw">&#45;&#45;time&#45;index</span> <span class="nw">t</span></code> | <code><span class="nw">image&#46;data&#91;&#46;&#46;&#46;&#44;</span> <span class="nw">t&#93;</span></code> |  |  |
| <code><span class="nw">&#45;f</span> <span class="nw">value</span></code>, <code><span class="nw">&#45;&#45;default&#45;value</span></code> | <code><span class="nw">default&#95;value&#61;</span></code> | <code><span class="nw">0&#46;0</span></code> | value outside the input |
| <code><span class="nw">&#45;u</span> <span class="nw">type</span></code>, <code><span class="nw">&#45;&#45;output&#45;data&#45;type</span></code> | <code><span class="nw">dtype&#61;</span></code> | <code><span class="nw">None</span></code> | <code><span class="nw">char</span></code>, <code><span class="nw">uchar</span></code>, <code><span class="nw">short</span></code>, <code><span class="nw">int</span></code>, <code><span class="nw">float</span></code>, <code><span class="nw">double</span></code>; default: the computation type (float64, or float32 with <code><span class="nw">precision&#61;&#34;float32&#34;</span></code>). Integers truncate toward zero; out-of-range values clamp (ANTs wraps them, ANTS-06 in [Upstream defects](repo:docs/api/ants-apply-transforms.md#upstream-defects-d13); [finding](repo:docs/findings/ants-cli.md)) |
| <code><span class="nw">&#45;&#45;float</span> <span class="nw">1</span></code> | <code><span class="nw">precision&#61;&#34;float32&#34;</span></code> | <code><span class="nw">&#34;float64&#34;</span></code> | single precision exactly as ANTs computes it ([finding](repo:docs/findings/ants-float.md)); <code><span class="nw">&#45;&#45;float</span> <span class="nw">0</span></code> is <code><span class="nw">&#34;float64&#34;</span></code>, the default |
| <code><span class="nw">&#45;z</span></code>, <code><span class="nw">&#45;&#45;static&#45;cast&#45;for&#45;R</span></code> | (command line only) |  | accepted; it changes nothing the port writes |
| <code><span class="nw">&#45;v</span> <span class="nw">1</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> | – |  |  |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | (command line only) |  | ANTs' help |
| <code><span class="nw">ITK&#95;GLOBAL&#95;DEFAULT&#95;NUMBER&#95;OF&#95;THREADS</span></code> (or <code><span class="nw">NSLOTS</span></code>, as ITK reads them) | <code><span class="nw">n&#95;threads&#61;1</span></code> (0 = all CPUs) | <code><span class="nw">1</span></code> | the result does not depend on it |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | <code><span class="nw">fix</span></code> (default) or <code><span class="nw">reproduce</span></code> ([Upstream defects](repo:docs/api/ants-apply-transforms.md#upstream-defects-d13)) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `ants` on the command line (`larmorx --n-threads 4 ants antsApplyTransforms ...`); `lx.ants.apply_transforms` takes `n_threads` and `upstream_defects` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Worker threads (0 = all). The result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;apply&#95;transforms</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (the default) corrects ITK's and ANTs' defects: the floor of indices just below an integer (ITK-01), versors that fail to load in single precision (ITK-10), the <code><span class="nw">dtype</span></code> cast (ANTS-06); <code><span class="nw">&#34;reproduce&#34;</span></code> gives ANTs' result, MultiLabel's <code><span class="nw">alpha</span></code> ignored as ANTs ignores it (ANTS-33). An <code><span class="nw">UpstreamDefectWarning</span></code> names each defect that changed the result (<code><span class="nw">docs&#47;api&#47;upstream&#45;defects&#46;md</span></code>). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `t1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# No transform (the identity), Lanczos interpolation, onto the image's own grid.
out = lx.ants.apply_transforms("t1w.nii.gz", "t1w.nii.gz", interpolation="lanczos")
out.data.dtype  # -> dtype('float64')
```

```bash
larmorx ants antsApplyTransforms -d 3 -i t1w.nii.gz -r t1w.nii.gz -t identity -n LanczosWindowedSinc -o out.nii.gz --float 1
```

## Ports {#ports}

`antsApplyTransforms` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [ants-apply-transforms](repo:docs/validation/ants-apply-transforms.md) |

**The replica: status `validated`** against antsApplyTransforms itself (its
[record](repo:docs/validation/ants-apply-transforms.md), 2026-10-22). The record covers 258 cases:
- every interpolator;
- every transform type and file format, `.h5` files written by ITK (linear, inverted, float,
  six types in one composite, a dense group of nine affines, a float field) and by larmorx
  included, and B-spline transforms (antsRegistration's `BSpline` stage output, A5 part 3: text,
  MATLAB and HDF5 files, float coefficients, inside composites and chains, the inverse refused);
- awkward geometries, output types and time series;
- real fMRIPrep derivatives;
- all of them again with `--float 1`, ANTs' single-precision pipeline;
- the transform outputs, every form and format, and the errors around them.

All 258 agree (20 of them errors both programs report; 4 expected divergences, where ANTs
crashes and larmorx refuses, ANTS-48). Of the 200 resampling cases compared, 185 are
byte-identical to the unmodified ANTs program, among them all 102 `--float 1` cases; the other
15 (two of them through fMRIPrep's `.h5` composite, one through a B-spline transform with
Lanczos) differ only where ITK calls the platform's `exp`, `log`, `sin` or `cos` (Gaussian and
windowed sinc in double), by at most about 1e-15 relative ([why](repo:docs/findings/platform-math.md)).
With correctly rounded maths preloaded into ANTs, all 200 are byte-identical. The 40 cases of
B-spline transforms (A5 part 3: text, MATLAB and HDF5 files, float coefficients, composites,
chains, interpolators, time series, `--float 1`, the transform outputs, and the inverses both
programs refuse) all agree. The 46 transform-output cases (`-o Linear[...]`,
`-o CompositeTransform[...]`, `-o DisplacementField[...]`) write ANTs's files: text and MATLAB
byte for byte, NIfTI fields bit for bit, HDF5 dataset for dataset. All 14 of fMRIPrep's
`--float 1` outputs in the ds000005 oracle run are byte-identical to fMRIPrep's own
([stage record](repo:docs/validation/fmriprep-stages.md)). Compared with ANTs' defects reproduced
(`LARMORX_UPSTREAM_DEFECTS=reproduce`); the record's "D13 fix pass" lists what larmorx's
default changes.

**On the data panel** ([record](repo:docs/validation/ants-apply-transforms-panel.md), 2026-10-26):
every antsApplyTransforms node of the fourteen finished fMRIPrep oracle runs, each replayed from
its own command line with its inputs (421 calls: masks, references, tissue maps and
segmentations to the templates and the T1w, the confounds' masks, the reports' images; 179
through fMRIPrep's `.h5` composites, 166 with `--float 1`; `Gaussian`, `MultiLabel`,
`LanczosWindowedSinc`, `Linear` and `NearestNeighbor`), and four
calls fMRIPrep never makes (the 600-volume multiband-8 series to the T1w, the raw 7 T MP2RAGE to
MNI, the stroke's lesion mask to MNI, the 82-year-old's FLAIR onto its T1w): **425 of 425
bit-identical with CORE-MATH, 329 to the unmodified ANTs**, all 167 `--float 1` calls among them
(the others where ITK calls glibc's `exp`, `log`, `sin` or `cos` in double).

`antsApplyTransforms` has one port, in `pip install larmorx`: **the replica** (Rust crates
`larmorx-ants`, `larmorx-interp`, `larmorx-transform`, `larmorx-io`; Apache-2.0), translated from
ANTs 2.6.5 on ITK 5.4.5. Its result does not depend on the thread count.

## Evidence {#evidence}

How each of `antsApplyTransforms`'s ports was measured against ANTs, case by case: [its evidence](/evidence/ants-apply-transforms/).

## More in the repository {#more}

The API page [docs/api/ants-apply-transforms.md](repo:docs/api/ants-apply-transforms.md) holds what `antsApplyTransforms` shares with the page's other programs:

- [Transform outputs](repo:docs/api/ants-apply-transforms.md#transform-outputs)
- [lx.ants.apply_transforms_to_points(points, transforms=(), *, invert=None, coordinates="lps", n_threads=1)](repo:docs/api/ants-apply-transforms.md#lxantsapply_transforms_to_pointspoints-transforms--invertnone-coordinateslps-n_threads1)
- [lx.ants.combine_transforms(transforms=(), *, invert=None, output="composite", ...)](repo:docs/api/ants-apply-transforms.md#lxantscombine_transformstransforms--invertnone-outputcomposite-)
- [lx.transforms](repo:docs/api/ants-apply-transforms.md#lxtransforms)
- [Rust](repo:docs/api/ants-apply-transforms.md#rust)
- [Upstream defects (D13)](repo:docs/api/ants-apply-transforms.md#upstream-defects-d13)
- [Deliberate and known differences](repo:docs/api/ants-apply-transforms.md#deliberate-and-known-differences)
- [Performance](repo:docs/api/ants-apply-transforms.md#performance)
