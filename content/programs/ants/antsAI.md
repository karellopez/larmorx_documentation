---
title: "`antsAI`"
kicker: "Programs · ANTs and ITK"
lede: "`antsAI` finds the linear transform that best aligns two images."
description: "LARMORX reference for ANTs 2.6.5 `antsAI`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: ants
  original: "ANTs 2.6.5"
  software: "ANTs"
  command: "larmorx ants antsAI"
  python: "lx.ants.ai"
  api: "docs/api/ants-ai.md"
  evidence: "/evidence/ants-ai/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "fa776d2ea0a17487"
    crates/larmorx-ants/src/cli/ai.rs: "7f1be4ac8dc48313"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "035dcd92e164879c"
    docs/api/ants-ai.md: "5735fd1ac297da8b"
    python/larmorx/ants/initializers.py: "bacadf661f34b676"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

It starts from an initial
alignment (centres of mass, principal axes, or the images' geometric centres or centres of mass
alone) and searches from many start points, over rotations about the principal axes and
translations on a grid, each start point refined by a few conjugate-gradient iterations, with
the `Mattes`, `GC` and `MI` metrics, `None`/`Regular`/`Random` sampling and masks, in 2D and
3D; or it aligns blobs (`-b`: ANTs' multi-scale Laplacian-of-Gaussian blob detector, patch
correlations, landmark fits; [Blob alignment](repo:docs/api/ants-ai.md#blob-alignment)). fMRIPrep runs it in sMRIPrep's
brain extraction and in the BOLD reference's skull-stripping (`init_aff`), without blobs.

## Command line {#command-line}

```text synopsis
larmorx ants antsAI ...
```

Everything after `larmorx ants antsAI` is the original's command line: the arguments of ANTs 2.6.5's `antsAI`, as ANTs takes them. LARMORX's own options stand between `larmorx` and the family `ants`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        ants antsAI ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

## Python {#python}

```python
lx.ants.ai(
    fixed: Any,
    moving: Any,
    *,
    transform: AITransform = "Rigid",
    gradient_step: float = 0.1,
    metric: AIMetric = "Mattes",
    bins: int = 32,
    sampling: Sampling = "None",
    sampling_percentage: float = 1.0,
    align_principal_axes: bool = False,
    blobs: int | tuple[int, int] | None = None,
    search_factor: float = 20.0,
    arc_fraction: float = 1.0,
    translation_search_grid: tuple[float, Sequence[float]] | None = None,
    iterations: int = 0,
    convergence_threshold: float = 1e-6,
    convergence_window: int = 5,
    fixed_mask: Any = None,
    moving_mask: Any = None,
    dimension: int | None = None,
    random_seed: int | None = None,
    n_threads: int = 1,
    upstream_defects: UpstreamDefectsName = "fix",
) -> AIResult
```

Where `AITransform` is one of `"Rigid"`, `"Affine"`, `"Similarity"`, `"AlignGeometricCenters"`, `"AlignCentersOfMass"`; `AIMetric` is one of `"Mattes"`, `"GC"`, `"MI"`; `Sampling` is one of `"None"`, `"Regular"`, `"Random"`; `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

The linear transform that best aligns `moving` to `fixed`, as `antsAI` (ANTs v2.6.5) finds it.

Returns an `AIResult`: `transform` (an `ItkTransform`, fixed to moving, read back from the file
the port writes), `start_points`, `values` and `best_value` (the search's start points and their
metric values) and `log` (ANTs' verbose output: Python always runs verbose).

```python
import larmorx as lx

res = lx.ants.ai(
    "template.nii.gz", "t1w.nii.gz",
    transform="Affine", gradient_step=0.1,
    metric="Mattes", bins=32, sampling="Regular", sampling_percentage=0.25,
    search_factor=15, arc_fraction=0.1, translation_search_grid=(40, (0, 40, 40)),
    iterations=10, convergence_threshold=1e-6, convergence_window=10,
    fixed_mask="template_mask.nii.gz", random_seed=50495,
)
res.transform            # an ItkTransform (AffineTransform_double_3_3), fixed -> moving
res.start_points, res.best_value, res.values[:3]
```

Its result, `AIResult`, holds what `ai` returns.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">transform</span></code> | <code><span class="nw">ItkTransform</span></code> |  |
| <code><span class="nw">start&#95;points</span></code> | <code><span class="nw">int</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">values</span></code> | <code><span class="nw">list&#91;tuple&#91;int&#44;</span> <span class="nw">float&#93;&#93;</span></code> |  |
| <code><span class="nw">best&#95;value</span></code> | <code><span class="nw">float</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">log</span></code> | <code><span class="nw">str</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `antsAI` accepts (`crates/larmorx-ants/src/cli/ai.rs`) and the arguments of `lx.ants.ai` (`python/larmorx/ants/initializers.py`), whose defaults and descriptions are taken from it. Under each option, in grey, ANTs's own help for it.

| ANTs option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;d</span> <span class="nw">2&#47;3</span></code>, <code><span class="nw">&#45;&#45;dimensionality</span></code> | <code><span class="nw">dimension</span></code> | <code><span class="nw">None</span></code> | default: the fixed image's<span class="opt-help">ANTs: “This option forces the image to be treated as a specified-dimensional image.  If not specified, we try to infer the dimensionality from the input image.”</span> |
| <code><span class="nw">&#45;m</span> <span class="nw">Mattes&#91;f&#44;m&#44;bins&#44;sampling&#44;p&#93;</span></code>, <code><span class="nw">&#45;&#45;metric</span></code> | <code><span class="nw">fixed</span></code>, <code><span class="nw">moving</span></code>, <code><span class="nw">metric&#61;&#34;Mattes&#34;</span></code>, <code><span class="nw">bins</span></code>, <code><span class="nw">sampling</span></code>, <code><span class="nw">sampling&#95;percentage</span></code> | <code><span class="nw">metric&#61;&#34;Mattes&#34;</span></code>, <code><span class="nw">bins&#61;32</span></code>, <code><span class="nw">sampling&#61;&#34;None&#34;</span></code>, <code><span class="nw">sampling&#95;percentage&#61;1&#46;0</span></code> | <code><span class="nw">GC&#91;f&#44;m&#44;radius&#44;&#46;&#46;&#46;&#93;</span></code> (the third parameter is read but unused), <code><span class="nw">MI&#91;f&#44;m&#44;bins&#44;&#46;&#46;&#46;&#93;</span></code> (joint-histogram MI, smoothing variance 1); the images are read from <code><span class="nw">&#45;m</span></code> whatever the metric<span class="opt-help">ANTs: “These image metrics are available:  Mattes: Mattes mutual information (recommended), GC:  global correlation,  MI:  joint histogram mutual information”</span> |
| <code><span class="nw">&#45;t</span> <span class="nw">Rigid&#91;step&#93;</span></code>, <code><span class="nw">&#45;&#45;transform</span></code> | <code><span class="nw">transform&#61;&#34;Rigid&#34;</span></code>, <code><span class="nw">gradient&#95;step&#61;step</span></code> | <code><span class="nw">transform&#61;&#34;Rigid&#34;</span></code>, <code><span class="nw">gradient&#95;step&#61;0&#46;1</span></code> | <code><span class="nw">Affine</span></code>, <code><span class="nw">Similarity</span></code>; <code><span class="nw">AlignGeometricCenters</span></code>, <code><span class="nw">AlignCentersOfMass</span></code> (no step)<span class="opt-help">ANTs: “Several transform options are available.  For the rigid, affine, and similarity transforms, the gradientStep characterizes the gradient descent optimization and is scaled appropriately for each transform using the shift scales estimator. The other two transform types finds the simple translation transform which aligns the specified image feature.  Note that the images are read from the similarity metric option although the metric isn't actually used.”</span> |
| <code><span class="nw">&#45;p</span> <span class="nw">0&#47;1</span></code>, <code><span class="nw">&#45;&#45;align&#45;principal&#45;axes</span></code> | <code><span class="nw">align&#95;principal&#95;axes</span></code> | <code><span class="nw">False</span></code> | start from the principal axes' rotation (Wahba's problem)<span class="opt-help">ANTs: “Boolean indicating alignment by principal axes.  Alternatively, one can align using blobs (see -b option).”</span> |
| <code><span class="nw">&#45;b</span> <span class="nw">n</span></code> / <code><span class="nw">&#45;b</span> <span class="nw">&#91;n&#44;m&#93;</span></code>, <code><span class="nw">&#45;&#45;align&#45;blobs</span></code> | <code><span class="nw">blobs&#61;n</span></code> / <code><span class="nw">blobs&#61;&#40;n&#44;</span> <span class="nw">m&#41;</span></code> | <code><span class="nw">blobs&#61;None</span></code>, <code><span class="nw">blobs&#61;None</span></code> | the initial transform from <code><span class="nw">n</span></code> blobs per image and up to <code><span class="nw">m</span></code> matched pairs (<code><span class="nw">m</span> <span class="nw">&#61;</span> <span class="nw">n</span></code> by default); fewer than 3 blobs: ANTs' error; <code><span class="nw">&#45;p</span></code> is then ignored ([Blob alignment](repo:docs/api/ants-ai.md#blob-alignment))<span class="opt-help">ANTs: “Boolean indicating alignment by a set of blobs.  Alternatively, one can align using blobs (see -p option).”</span> |
| <code><span class="nw">&#45;s</span> <span class="nw">&#91;factor&#44;arc&#93;</span></code> / <code><span class="nw">&#45;s</span> <span class="nw">factor</span></code>, <code><span class="nw">&#45;&#45;search&#45;factor</span></code> | <code><span class="nw">search&#95;factor</span></code> (degrees), <code><span class="nw">arc&#95;fraction</span></code> | <code><span class="nw">search&#95;factor&#61;20&#46;0</span></code>, <code><span class="nw">arc&#95;fraction&#61;1&#46;0</span></code> | angles <code><span class="nw">&#8722;180&#176;&#183;arc</span></code> to <code><span class="nw">180&#176;&#183;arc</span></code> in steps of <code><span class="nw">factor</span></code>, about each axis<span class="opt-help">ANTs: “Incremental search factor (in degrees) which will sample the arc fraction around the principal axis or default axis.”</span> |
| <code><span class="nw">&#45;g</span> <span class="nw">&#91;step&#44;AxBxC&#93;</span></code>, <code><span class="nw">&#45;&#45;translation&#45;search&#45;grid</span></code> | <code><span class="nw">translation&#95;search&#95;grid&#61;&#40;step&#44;</span> <span class="nw">&#40;A&#44;</span> <span class="nw">B&#44;</span> <span class="nw">C&#41;&#41;</span></code> | <code><span class="nw">None</span></code> | translations of the start points, in mm (ignored by <code><span class="nw">Rigid</span></code>/<code><span class="nw">Similarity</span></code> in 2D and <code><span class="nw">Similarity</span></code> in 3D in ANTs: ANTS-52)<span class="opt-help">ANTs: “Translation search grid in mm, which will translate the moving image in each dimension in increments of the step size.”</span> |
| <code><span class="nw">&#45;c</span> <span class="nw">&#91;n&#44;threshold&#44;window&#93;</span></code> / <code><span class="nw">&#45;c</span> <span class="nw">n</span></code>, <code><span class="nw">&#45;&#45;convergence</span></code> | <code><span class="nw">iterations</span></code>, <code><span class="nw">convergence&#95;threshold</span></code>, <code><span class="nw">convergence&#95;window</span></code> | <code><span class="nw">iterations&#61;0</span></code>, <code><span class="nw">convergence&#95;threshold&#61;1e&#45;6</span></code>, <code><span class="nw">convergence&#95;window&#61;5</span></code> | defaults 0, 1e-6, **5** (the help says 10: ANTS-59); 0 iterations: the initial alignment only<span class="opt-help">ANTs: “Number of iterations.”</span> |
| <code><span class="nw">&#45;x</span> <span class="nw">mask</span></code> / <code><span class="nw">&#45;x</span> <span class="nw">&#91;fixed&#44;moving&#93;</span></code>, <code><span class="nw">&#45;&#45;masks</span></code> | <code><span class="nw">fixed&#95;mask</span></code>, <code><span class="nw">moving&#95;mask</span></code> | <code><span class="nw">fixed&#95;mask&#61;None</span></code>, <code><span class="nw">moving&#95;mask&#61;None</span></code> | a mask that cannot be read is no mask<span class="opt-help">ANTs: “Image masks to limit voxels considered by the metric.”</span> |
| <code><span class="nw">&#45;o</span> <span class="nw">out&#46;mat</span></code>, <code><span class="nw">&#45;&#45;output</span></code> | the result |  | its <code><span class="nw">transform</span></code>; <code><span class="nw">&#46;mat</span></code>, <code><span class="nw">&#46;txt</span></code>, <code><span class="nw">&#46;tfm</span></code> or an HDF5 name; Python reads the file back<span class="opt-help">ANTs: “Specify the output transform (output format an ITK .mat file). ”</span> |
| <code><span class="nw">&#45;&#45;random&#45;seed</span> <span class="nw">N</span></code> / <code><span class="nw">ANTS&#95;RANDOM&#95;SEED</span></code> | <code><span class="nw">random&#95;seed</span></code> | <code><span class="nw">None</span></code> | default 1234; 0: ANTs from the clock, larmorx 121212<span class="opt-help">ANTs: “Use a fixed seed for random number generation. The default fixed seed is overwritten by this value. The fixed seed can be any nonzero int value. If the specified seed is zero, the system time will be used.”</span> |
| <code><span class="nw">&#45;v</span> <span class="nw">1</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> | the result |  | its <code><span class="nw">log</span></code>, <code><span class="nw">start&#95;points</span></code>, <code><span class="nw">values</span></code> and <code><span class="nw">best&#95;value</span></code>: Python always runs verbose; errors are explained with or without <code><span class="nw">&#45;v</span></code> (ANTS-45)<span class="opt-help">ANTs: “Verbose output.”</span> |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | – |  | the short and long menus, as ANTs prints them<span class="opt-help">ANTs: “Print the help menu (short version).”</span><span class="opt-help">ANTs: “Print the help menu.”</span> |
| <code><span class="nw">ITK&#95;GLOBAL&#95;DEFAULT&#95;NUMBER&#95;OF&#95;THREADS</span></code>, <code><span class="nw">NSLOTS</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | the result does not depend on it |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects&#61;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | ANTS-52, -53, -55, -110, -111, -112, -114, ITK-18, -19, -60 ([upstream defects](repo:docs/api/upstream-defects.md)) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `ants` on the command line (`larmorx --n-threads 4 ants antsAI ...`); `lx.ants.ai` takes `n_threads` and `upstream_defects` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;ai</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `fixed.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `moving.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# A rigid search from the centres of mass: 30-degree steps over the whole circle.
res = lx.ants.ai("fixed.nii.gz", "moving.nii.gz", transform="Rigid", search_factor=30,
                 random_seed=1)
res.transform.name  # -> 'Euler3DTransform_double_3_3'
```

```bash
larmorx ants antsAI -d 3 -m Mattes[fixed.nii.gz,moving.nii.gz,32,Regular,0.25] -t Rigid[0.1] -s [30,1] -c 0 -o initialization.mat --random-seed 1
```

## Ports {#ports}

`antsAI` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [ants-ai](repo:docs/validation/ants-ai.md) |

**The replica: status `validated`** against `antsAI` itself (its
[record](repo:docs/validation/ants-ai.md), 2026-10-28, standard tier: 132 cases, 76 pass, 52 rejected by
both alike, 4 expected divergences): every compared case identical to ANTs 2.6.5 at one thread
(exit status, standard output with every printed metric value, standard error, the transform
file byte for byte), 75 of 76 against the unmodified binary, the other once glibc's
not-correctly-rounded `cbrt` is replaced by CORE-MATH's (CLAUDE.md rule 5). fMRIPrep 25.2.6's own
`init_aff` command lines, with fMRIPrep's seed, give fMRIPrep's transforms within ANTs' 8-thread
band: all ten `init_aff` nodes of the five oracle runs (full tier) within 1.5e-9 of fMRIPrep's
files, nine of them within 1.3e-12.

| Tier | Cases | Identical to the unmodified ANTs | Identical with CORE-MATH | Rejected by both | Expected divergences | Failures |
|---|---|---|---|---|---|---|
| standard (2026-10-28) | 132 | 75 | 1 | 52 | 4 | 0 |
| full ([record](repo:docs/validation/ants-ai-full.md), 2026-10-24) | 144 | 86 | 1 | 53 | 4 | 0 |

"Rejected by both" includes the cases where ANTs aborts or crashes: everything ANTs printed
before it stopped is identical, and larmorx then exits 1 with one more line. The expected
divergences: two loops ANTs never finishes (larmorx refuses) and two clock-seeded runs
(ANTS-58). **ANTs' own thread band** (6 cases): up to 2e-13 in a transform parameter in five,
and 0.137 in the BOLD reference of ds000005's run 1 in the standard record of 2026-10-28; larmorx
gives the one-thread result at any thread count.

**On the data panel** ([record](repo:docs/validation/ants-ai-panel.md), 2026-10-26): all 36 antsAI
nodes of the fourteen finished fMRIPrep oracle runs (the brain extraction's `init_aff` in every
run, the BOLD reference's in 22 runs; the 3.5-year-old, the glioma, the stroke, 1.5 T, 7 T,
multiband-8 and multi-echo among them), with fMRIPrep's seed, and four images fMRIPrep never gives
it (a FLAIR, a glioma's T2w, an older adult's T2w, the 7 T MP2RAGE, with sMRIPrep's options):
**40 of 40 identical to ANTs 2.6.5 at one thread** (38 as built, 2 with CORE-MATH). Against
fMRIPrep's own transforms (ANTs 2.6.2 at 6 or 8 threads): 31 within 1e-8 in a parameter, five
further, by up to 6.8 mm over a 100 mm cube. Those five are ANTs' own spread above one thread:
fMRIPrep's ANTs at one thread gives exactly larmorx's transform, and both ANTs builds at
fMRIPrep's thread count land, run to run, on fMRIPrep's file, on the one-thread result or
elsewhere ([findings](repo:docs/findings/ants-ai.md), "On the data panel").

`antsAI` has one port, in `pip install larmorx`: **the replica** (`crates/larmorx-ants`,
`crates/larmorx-registration`; Apache-2.0; Rust `larmorx_ants::ai`), translated from ANTs
2.6.5's `antsAI` on ITK 5.4.5 (Apache-2.0). **Results do not depend on threads.** ANTs' do, by
about 1e-13 in a parameter (its metrics sum per work unit); larmorx always gives ANTs'
one-thread result. **`Random` sampling is never repeatable in ANTs** (its voxels are drawn from
the clock, whatever the seed; so are `Regular` sampling's perturbations with `--random-seed 0`,
ANTS-58); larmorx seeds them from the seed.

## Evidence {#evidence}

How each of `antsAI`'s ports was measured against ANTs, case by case: [its evidence](/evidence/ants-ai/).

## More in the repository {#more}

The API page [docs/api/ants-ai.md](repo:docs/api/ants-ai.md) holds what `antsAI` shares with the page's other programs:

- [Memory and speed](repo:docs/api/ants-ai.md#memory-and-speed)
- [The output transform](repo:docs/api/ants-ai.md#the-output-transform)
- [Upstream defects (D13)](repo:docs/api/ants-ai.md#upstream-defects-d13)
- [Blob alignment](repo:docs/api/ants-ai.md#blob-alignment)
