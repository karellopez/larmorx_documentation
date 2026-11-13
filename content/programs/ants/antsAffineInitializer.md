---
title: "`antsAffineInitializer`"
kicker: "Programs · ANTs and ITK"
lede: "`antsAffineInitializer` finds an affine transform that aligns two images."
description: "LARMORX reference for ANTs 2.6.5 `antsAffineInitializer`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: ants
  original: "ANTs 2.6.5"
  software: "ANTs"
  command: "larmorx ants antsAffineInitializer"
  python: "lx.ants.affine_initializer"
  api: "docs/api/ants-affine-initializer.md"
  evidence: "/evidence/ants-ai/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-ants/src/cli/affine_initializer.rs: "913e01507d2f1388"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "91be42d24bb3ba2b"
    docs/api/ants-affine-initializer.md: "40c993f8851376f0"
    python/larmorx/ants/initializers.py: "bacadf661f34b676"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

It aligns their
centres of mass (and, optionally, their principal axes), then takes the best start point of a
multi-start search over rotations about the fixed image's principal axes, each refined by
conjugate-gradient iterations of Mattes mutual information on every 10th voxel (as many as the
eighth argument says, by default 20; ANTs always runs 20); in 2D, 3D and 4D (in 4D the initial
alignment only). niworkflows' `RobustMNINormalization` runs it when it is given no initial
transform (fMRIPrep's template registration).

## Command line {#command-line}

```text synopsis
larmorx ants antsAffineInitializer ImageDimension <Image1.ext> <Image2.ext> TransformOutput.mat Optional-SearchFactor Optional-Radian-Fraction Optional-bool-UsePrincipalAxes Optional-uint-UseLocalSearch Optional-Image1Mask
```

Everything after `larmorx ants antsAffineInitializer` is the original's command line: the arguments of ANTs 2.6.5's `antsAffineInitializer`, as ANTs takes them. LARMORX's own options stand between `larmorx` and the family `ants`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        ants antsAffineInitializer ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

## Python {#python}

```python
lx.ants.affine_initializer(
    fixed: Any,
    moving: Any,
    *,
    search_factor: float = 10.0,
    radian_fraction: float = 0.25,
    principal_axes: bool = False,
    local_search_iterations: int = 20,
    fixed_mask: Any = None,
    dimension: int | None = None,
    n_threads: int = 1,
    upstream_defects: UpstreamDefectsName = "fix",
) -> ItkTransform
```

Where `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

An affine transform that aligns `moving` to `fixed`, as `antsAffineInitializer` (ANTs v2.6.5) finds it: the images' centres of mass (and, with `principal_axes`, their principal axes) aligned, then the best of a multi-start search over rotations about the fixed image's principal axes (2D and 3D; in 4D the alignment alone).

Returns the transform as an `ItkTransform` (the search's best, fixed to moving).

```python
import larmorx as lx

t = lx.ants.affine_initializer(
    "tpl-MNI152NLin2009cAsym_res-01_T1w.nii.gz", "sub-01_T1w.nii.gz",
    search_factor=15, radian_fraction=0.1, principal_axes=False,
)
t                        # ItkTransform('AffineTransform_double_3_3', 12 parameters, 3 fixed)
```

Its result, `ItkTransform`, holds one transform as ITK stores it.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">name</span></code> | <code><span class="nw">str</span></code> |  |
| <code><span class="nw">parameters</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">fixed&#95;parameters</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `antsAffineInitializer` accepts (`crates/larmorx-ants/src/cli/affine_initializer.rs`) and the arguments of `lx.ants.affine_initializer` (`python/larmorx/ants/initializers.py`), whose defaults and descriptions are taken from it. Under each option, in grey, ANTs's own help for it.

| ANTs argument (positional) | Python | Default | Notes |
|---|---|---|---|
| 1 <code><span class="nw">ImageDimension</span></code> | <code><span class="nw">dimension</span></code> | <code><span class="nw">None</span></code> | default: the fixed image's; <code><span class="nw">std&#58;&#58;stoi</span></code>; any number but 2, 3, 4 runs as 2D in ANTs (ANTS-56; corrected, an error) |
| 2, 3 <code><span class="nw">Image1</span></code>, <code><span class="nw">Image2</span></code> | <code><span class="nw">fixed</span></code>, <code><span class="nw">moving</span></code> |  | read as float images; a missing image, or one whose values sum to 0, aborts (<code><span class="nw">zero</span> <span class="nw">image1</span> <span class="nw">error</span></code>) |
| 4 <code><span class="nw">TransformOutput</span></code> | the result |  | the returned <code><span class="nw">ItkTransform</span></code>; written twice: the initial alignment, then the search's best (<code><span class="nw">&#46;mat</span></code>, <code><span class="nw">&#46;txt</span></code>, <code><span class="nw">&#46;tfm</span></code>, HDF5) |
| 5 <code><span class="nw">SearchFactor</span></code> | <code><span class="nw">search&#95;factor</span></code> | <code><span class="nw">10&#46;0</span></code> | degrees (×0.0174532925), <code><span class="nw">atof</span></code>; default 10 |
| 6 <code><span class="nw">Radian&#45;Fraction</span></code> | <code><span class="nw">radian&#95;fraction</span></code> | <code><span class="nw">0&#46;25</span></code> | <code><span class="nw">atof</span></code>, clamped to <code><span class="nw">&#91;0&#46;01&#44;</span> <span class="nw">1&#93;</span></code>; the angles run over <code><span class="nw">&#91;&#8722;&#960;&#183;f&#44;</span> <span class="nw">&#960;&#183;f</span> <span class="nw">&#43;</span> <span class="nw">step&#93;</span></code>; default 0.25 (<code><span class="nw">&#960;&#47;4</span></code>) |
| 7 <code><span class="nw">UsePrincipalAxes</span></code> | <code><span class="nw">principal&#95;axes</span></code> | <code><span class="nw">False</span></code> | <code><span class="nw">std&#58;&#58;stoi</span></code>, non-zero is true; default false |
| 8 <code><span class="nw">UseLocalSearch</span></code> | <code><span class="nw">local&#95;search&#95;iterations</span></code> | <code><span class="nw">20</span></code> | each start point's conjugate-gradient iterations, read with <code><span class="nw">std&#58;&#58;stoi</span></code> (0: no local search; text, a negative value or one beyond <code><span class="nw">int</span></code>: an error); default 20. **Not read by ANTs**, which always runs 20 (ANTS-54, corrected; <code><span class="nw">reproduce</span></code> runs 20) |
| 9 <code><span class="nw">Image1Mask</span></code> | <code><span class="nw">fixed&#95;mask</span></code> | <code><span class="nw">None</span></code> | the metric's fixed mask; one that cannot be read is no mask |
| fewer than 2 arguments | – |  | the usage on standard error, exit 0; 2 or 3 arguments abort (ANTS-57) |
| <code><span class="nw">ITK&#95;GLOBAL&#95;DEFAULT&#95;NUMBER&#95;OF&#95;THREADS</span></code>, <code><span class="nw">NSLOTS</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | the result does not depend on it |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects&#61;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | ANTS-54, ANTS-56, ITK-19, ITK-21 ([upstream defects](repo:docs/api/upstream-defects.md)) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `ants` on the command line (`larmorx --n-threads 4 ants antsAffineInitializer ...`); `lx.ants.affine_initializer` takes `n_threads` and `upstream_defects` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;affine&#95;initializer</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `fixed.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `moving.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# niworkflows' call (15 0.1 0 10), with the local search's iterations as asked.
t = lx.ants.affine_initializer("fixed.nii.gz", "moving.nii.gz", search_factor=15,
                               radian_fraction=0.1, local_search_iterations=10)
t.name  # -> 'AffineTransform_double_3_3'
```

```bash
larmorx ants antsAffineInitializer 3 fixed.nii.gz moving.nii.gz transform.mat 15 0.1 0 10
```

## Ports {#ports}

`antsAffineInitializer` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [ants-affine-initializer](repo:docs/validation/ants-affine-initializer.md) |

**The replica: status `validated`** against `antsAffineInitializer` itself (its
[record](repo:docs/validation/ants-affine-initializer.md), 2026-10-28, standard tier): every compared
case identical to ANTs 2.6.5 at one thread (exit status, both streams, the transform file byte
for byte), including the usage, every abort and its messages, 2D, 3D and 4D, masks, oblique
grids and real images (the MNI template and fMRIPrep's preprocessed T1w; full tier: fMRIPrep's
own call in the template registration of all five oracle runs, on stand-ins for the masked
images nipype did not keep).

| Tier | Cases | Identical to the unmodified ANTs | Rejected by both | Expected divergences | Failures |
|---|---|---|---|---|---|
| standard | 41 | 26 | 13 | 2 | 0 |
| full ([record](repo:docs/validation/ants-affine-initializer-full.md)) | 46 | 31 | 13 | 2 | 0 |

"Rejected by both" includes the aborts (everything ANTs printed before it stopped is
identical); the expected divergences are the two search factors whose loop never ends in ANTs.
**ANTs' own thread band** (4 cases): up to 1.3e-6 in a parameter on the MNI template,
1e-15 on the phantoms; larmorx gives the one-thread result at any thread count. The
comparison runs larmorx with ANTs' defects reproduced (`reproduce`); every case also runs in
larmorx's default mode, where ANTS-54 and ITK-21 ([Upstream defects](repo:docs/api/ants-affine-initializer.md#upstream-defects-d13))
are named exactly where they change the transform (the fix pass of each case).

**On the data panel** ([record](repo:docs/validation/ants-affine-initializer-panel.md), 2026-10-26):
fMRIPrep's own call in the template registration of all fourteen finished oracle runs (no node
of its own: niworkflows runs it inside `register_template_wf/.../registration`, with nipype's
`15 0.1 0 10`), on the masked images remade exactly from each node's recorded inputs
(`larmorx_validation.parity.niworkflows_inputs`; the 3.5-year-old, the glioma, the stroke, the
7 T MP2RAGE, the 1.5 T MPRAGE, the 82-year-old among them): **14 of
14 identical to the unmodified ANTs 2.6.5 at one thread**, ANTs' own band at 2 and 3 threads
6.5e-9 in a parameter. fMRIPrep did not keep the transform it made (at the node's six or eight
threads); its effect is in the registration's record.

`antsAffineInitializer` has one port, in `pip install larmorx`: **the replica**
(`crates/larmorx-ants`, `crates/larmorx-registration`; Apache-2.0; Rust
`larmorx_ants::affine_initializer`), translated from ANTs 2.6.5's `antsAffineInitializer` on ITK
5.4.5 (Apache-2.0). **Results do not depend on threads**: larmorx gives ANTs' one-thread result
at any thread count.

## Evidence {#evidence}

How each of `antsAffineInitializer`'s ports was measured against ANTs, case by case: [its evidence](/evidence/ants-ai/).

## More in the repository {#more}

The API page [docs/api/ants-affine-initializer.md](repo:docs/api/ants-affine-initializer.md) holds what `antsAffineInitializer` shares with the page's other programs:

- [Memory and speed](repo:docs/api/ants-affine-initializer.md#memory-and-speed)
- [Upstream defects (D13)](repo:docs/api/ants-affine-initializer.md#upstream-defects-d13)
