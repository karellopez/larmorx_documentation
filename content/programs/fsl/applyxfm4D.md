---
title: "`applyxfm4D`"
kicker: "Programs · FSL"
lede: "`applyxfm4D` resamples each volume of a series onto a reference's grid, through one matrix or one per volume."
description: "LARMORX reference for FSL 6.0.7.23 `applyxfm4D`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl applyxfm4D"
  python: "lx.fsl.applyxfm4d"
  api: "docs/api/fsl-flirt.md"
  evidence: "/evidence/fsl-flirt/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "bf883da07a0caa93"
    crates/larmorx-fsl/src/cli/applyxfm4d.rs: "27053a5d6d6e7bc2"
    docs/api/fsl-flirt.md: "abc8e4a5001ff9ef"
    python/larmorx/fsl/flirt_more.py: "e26d92e30bf57c9f"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

The matrices are one file (`-singlematrix`) or a directory of files named `MAT_0000n`,
`MAT_nnnn` (`-fourdigit`) or `<prefix>nnnn` (`-userprefix`). The interpolation is sinc (the
default), trilinear, nearest neighbour or spline, and the output keeps the input's data type
(char, short, int, float, double).

## Command line {#command-line}

```text synopsis
larmorx fsl applyxfm4D <input volume> <ref volume> <output volume> <transformation matrix file/dir>
```

Everything after `larmorx fsl applyxfm4D` is the original's command line: the arguments of FSL 6.0.7.23's `applyxfm4D`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl applyxfm4D ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>applyxfm4D</code>'s usage text, as the clean room prints it</summary>

```text
Usage: applyxfm4D <input volume> <ref volume> <output volume> <transformation matrix file/dir>

	--interp, -interp <nearestneighbour (or nn), trilinear, spline, sinc (default)>
	--singlematrix, -singlematrix (flag option, do not provide an argument)
	--fourdigit, -fourdigit (flag option, do not provide an argument)
	--userprefix, -userprefix <prefix>
```

</details>

## Python {#python}

```python
lx.fsl.applyxfm4d(
    in_image: str | os.PathLike,
    ref_image: str | os.PathLike,
    out_image: str | os.PathLike,
    transforms: str | os.PathLike,
    *,
    single_matrix: bool = False,
    four_digit: bool = False,
    user_prefix: str | None = None,
    interp: Interp4D = "sinc",
    three_d: bool = False,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
) -> str
```

Where `Interp4D` is one of `"sinc"`, `"trilinear"`, `"nearestneighbour"`, `"spline"`; `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

FSL's `applyxfm4D`: each volume of `in_image` resampled onto `ref_image`'s grid through `transforms` (one matrix file with `single_matrix`, else a directory of `MAT_0000n` files, `MAT_000n` with `four_digit`, `<user_prefix>000n` with `user_prefix`), written to `out_image` in the input's data type (its extension chooses the format: `.nii.gz`, `.nii`, `.hdr`/`.img`; none: `.nii.gz`); `three_d` resamples one volume (`-3D`). Returns the path written.

The images and `transforms` are paths.

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `applyxfm4D` accepts (`crates/larmorx-fsl/src/cli/applyxfm4d.rs`) and the arguments of `lx.fsl.applyxfm4d` (`python/larmorx/fsl/flirt_more.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">applyxfm4D</span></code> option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#60;input</span> <span class="nw">volume&#62;</span></code> <code><span class="nw">&#60;ref</span> <span class="nw">volume&#62;</span></code> <code><span class="nw">&#60;output</span> <span class="nw">volume&#62;</span></code> | <code><span class="nw">in&#95;image</span></code>, <code><span class="nw">ref&#95;image</span></code>, <code><span class="nw">out&#95;image</span></code> |  |  |
| <code><span class="nw">&#60;transformation</span> <span class="nw">matrix</span> <span class="nw">file&#47;dir&#62;</span></code> | <code><span class="nw">transforms</span></code> |  | a directory of <code><span class="nw">MAT&#95;0000n</span></code> files, or one file with <code><span class="nw">&#45;singlematrix</span></code> |
| <code><span class="nw">&#45;singlematrix</span></code>, <code><span class="nw">&#45;&#45;singlematrix</span></code> | <code><span class="nw">single&#95;matrix</span></code> | <code><span class="nw">False</span></code> | one matrix for every volume |
| <code><span class="nw">&#45;fourdigit</span></code>, <code><span class="nw">&#45;&#45;fourdigit</span></code> | <code><span class="nw">four&#95;digit</span></code> | <code><span class="nw">False</span></code> | the files named <code><span class="nw">MAT&#95;nnnn</span></code> |
| <code><span class="nw">&#45;userprefix</span></code>, <code><span class="nw">&#45;&#45;userprefix</span></code> | <code><span class="nw">user&#95;prefix</span></code> | <code><span class="nw">None</span></code> | the files named <code><span class="nw">&#60;prefix&#62;nnnn</span></code> |
| <code><span class="nw">&#45;interp</span></code>, <code><span class="nw">&#45;&#45;interp</span></code> | <code><span class="nw">interp</span></code> | <code><span class="nw">&#34;sinc&#34;</span></code> | <code><span class="nw">sinc</span></code> (default), <code><span class="nw">trilinear</span></code>, <code><span class="nw">nearestneighbour</span></code> (or <code><span class="nw">nn</span></code>), <code><span class="nw">spline</span></code> |
| <code><span class="nw">&#45;3D</span></code>, <code><span class="nw">&#45;&#45;3D</span></code>, <code><span class="nw">&#45;3d</span></code>, <code><span class="nw">&#45;&#45;3d</span></code> | <code><span class="nw">three&#95;d</span></code> | <code><span class="nw">False</span></code> | one volume; with sinc, the rectangular kernel the program asks for (**FSL-80**) |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;&#45;v</span></code>, <code><span class="nw">&#45;verbose</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> | command line only |  |  |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl applyxfm4D ...`) and are arguments of `lx.fsl.applyxfm4d`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all), given to the program as <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code>; the result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects corrected, or FSL's behaviour (<code><span class="nw">docs&#47;api&#47;fsl&#45;flirt&#46;md</span></code>, "Defects of the original, corrected by default"). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `bold.nii.gz` (a synthetic series of 4 such heads), `boldref.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `bold2ref.mat` (the identity as a 4 × 4 text matrix). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

path = lx.fsl.applyxfm4d(
    "bold.nii.gz", "boldref.nii.gz", "bold_on_ref.nii.gz", "bold2ref.mat", single_matrix=True
)
```

```bash
larmorx fsl applyxfm4D bold.nii.gz boldref.nii.gz bold_on_ref.nii.gz bold2ref.mat -singlematrix
```

## Ports {#ports}

`applyxfm4D` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-flirt-replica](repo:docs/validation/fsl-flirt-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-flirt](repo:docs/validation/fsl-flirt.md) |

Both ports are complete (`specs/flirt.md` §15.7), on FLIRT's shared resampling (no blur, as FSL). FSL's defects are corrected
by default, and FSL's behaviour comes with `upstream_defects="reproduce"`:

- **FSL-09**: integer outputs are rounded to the nearest and clamped (FSL truncates).
- **FSL-79**: spline interpolation of an integer image is computed as for a float image (FSL keeps
  the spline's coefficients and values in the image's type); named where the output changes.
- **FSL-80**: `-3D` with sinc uses the rectangular kernel of width 9 that the program asks for
  (FSL uses a blackman kernel of width 7); named where the output changes.
- **FSL-111**: a uint8 image's values are read as stored (FSL reads them as signed char, its
  values 128 to 255 as `v − 256`); named where a written value changes.
- **FSL-75**: the background value of a volume 3 voxels wide is taken from the whole border.
- **FSL-11**: with `FSLOUTPUTTYPE` unset, the images are written as `.nii.gz` and FSL-11 is named
  (FSL stops at its first image); command line only, as the Python function sets the type itself.

With a reference that has neither form, the output carries the input's form through the first
matrix, as a registration's `-out` does.

The replica's record holds 25 cases of `applyxfm4D`: 19 identical to FSL, 6 where both refuse
alike. The clean room's holds 25: 20 within its thresholds, 5 refused alike.

FSL's licence allows non-commercial use only, so each of FLIRT's programs has two ports, a
replica and a clean room, in different packages ([licensing](repo:docs/licensing.md) says what each
package holds):

- **The replica** is translated from FSL's source. The package `larmorx-nc` holds it (`crates-nc/`),
  under the FSL Licence's terms, and `larmorx` runs it as a separate program, `larmorx-nc fsl
  <program>`, when `larmorx-nc` is installed (`pip install larmorx-nc`).
- **The clean room** is written from [`specs/flirt.md`](repo:specs/flirt.md) by an implementer who
  never read FSL's source or the replica. It is part of `larmorx`, under Apache-2.0
  (`crates/larmorx-fsl`, with its [PROVENANCE](repo:crates/larmorx-fsl/PROVENANCE.md), section
  "FLIRT"), and runs on LARMORX's clean-room registration engine, the head-motion correction's
  (`lx.mri.hmc`).

`implementation="auto"` runs the replica when `larmorx-nc` is installed, and the clean room
otherwise. `"replica"` and `"clean-room"` choose one (`"original"`, 0.1.0rc1's spelling of
`"clean-room"`, still works); `"clean-room"` runs the clean room in this process. On the command
line, `--implementation auto|replica|clean-room` before the family chooses alike, from the next
release; in 0.1.0rc1 the variable `LARMORX_IMPLEMENTATION` chooses (`original` for the clean
room).

## Evidence {#evidence}

How each of `applyxfm4D`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-flirt/).

## More in the repository {#more}

The API page [docs/api/fsl-flirt.md](repo:docs/api/fsl-flirt.md) holds what `applyxfm4D` shares with the page's other programs:

- [The clean room (part 1, 2026-11-02)](repo:docs/api/fsl-flirt.md#the-clean-room-part-1-2026-11-02)
- [Defects of the original, corrected by default](repo:docs/api/fsl-flirt.md#defects-of-the-original-corrected-by-default)
- [Not yet](repo:docs/api/fsl-flirt.md#not-yet)
- [History](repo:docs/api/fsl-flirt.md#history)
