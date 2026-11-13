---
title: "`fslroi`"
kicker: "Programs · FSL"
lede: "`fslroi` takes a box of an image (`xmin xsize ymin ysize zmin zsize`), a range of its volumes (`tmin tsize`) or both."
description: "LARMORX reference for FSL 6.0.7.23 `fslroi`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl fslroi"
  python: "lx.fsl.fslroi"
  api: "docs/api/fsl-roi.md"
  evidence: "/evidence/fsl-bet/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "validated"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "035dcd92e164879c"
    crates/larmorx-fsl/src/cli/fslroi.rs: "fb06645d5bc0727a"
    docs/api/fsl-roi.md: "eaded1db765eeabc"
    python/larmorx/fsl/regions.py: "8b0848530989c81c"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

The result keeps the image's own data type, and its header's transforms
move to the box's corner. A size of -1 is the rest of the axis, and the box may reach outside the
image (zeros there). The indices are NIfTI voxel indices, from 0.

## Command line {#command-line}

```text synopsis
larmorx fsl fslroi <input> <output> <xmin> <xsize> <ymin> <ysize> <zmin> <zsize>
larmorx fsl fslroi <input> <output> <tmin> <tsize>
```

Everything after `larmorx fsl fslroi` is the original's command line: the arguments of FSL 6.0.7.23's `fslroi`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl fslroi ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>fslroi</code>'s usage text, as the clean room prints it</summary>

```text
Usage: fslroi <input> <output> <xmin> <xsize> <ymin> <ysize> <zmin> <zsize>
       fslroi <input> <output> <tmin> <tsize>

       fslroi <input> <output> <xmin> <xsize> <ymin> <ysize> <zmin> <zsize> <tmin> <tsize>
Note: indexing (in both time and space) starts with 0 not 1! Inputting -1 for a size will set it to the full image extent for that dimension.
```

</details>

## Python {#python}

```python
lx.fsl.fslroi(
    image: Any,
    *,
    x: Region = None,
    y: Region = None,
    z: Region = None,
    t: Region = None,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
) -> Image
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

FSL's `fslroi`: the region of `image` given as `(min, size)` per axis (indices from 0, a size of -1 the rest of the axis; an axis not given whole), in the image's own type. Only `t` (`fslroi <in> <out> <tmin> <tsize>`), only space (`x`, `y`, `z`) or all four; the spatial indices are NIfTI voxel indices.

`image` is a path or an `lx.Image`; `x`, `y`, `z` and `t` are `(min, size)` pairs. Only `t`, only
space (`x`, `y`, `z`) or all four; an axis of space not given is whole, `(0, -1)`. The result is
an `lx.Image`.

Its result, `Image`, holds a voxel array placed in world space by an affine.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">data</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">affine</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">header</span></code> | <code><span class="nw">NiftiHeader</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">implementation</span></code> | <code><span class="nw">Implementation</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `fslroi` accepts (`crates/larmorx-fsl/src/cli/fslroi.rs`) and the arguments of `lx.fsl.fslroi` (`python/larmorx/fsl/regions.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">fslroi</span></code> arguments | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#60;input&#62;</span></code> | <code><span class="nw">image</span></code> |  |  |
| <code><span class="nw">&#60;output&#62;</span></code> | the result |  |  |
| <code><span class="nw">&#60;tmin&#62;</span> <span class="nw">&#60;tsize&#62;</span></code> | <code><span class="nw">t&#61;&#40;tmin&#44;</span> <span class="nw">tsize&#41;</span></code> | <code><span class="nw">None</span></code> | a range of volumes |
| <code><span class="nw">&#60;xmin&#62;</span> <span class="nw">&#60;xsize&#62;</span> <span class="nw">&#60;ymin&#62;</span> <span class="nw">&#60;ysize&#62;</span> <span class="nw">&#60;zmin&#62;</span> <span class="nw">&#60;zsize&#62;</span></code> | <code><span class="nw">x</span></code>, <code><span class="nw">y</span></code>, <code><span class="nw">z</span></code> | <code><span class="nw">x&#61;None</span></code>, <code><span class="nw">y&#61;None</span></code>, <code><span class="nw">z&#61;None</span></code> | a box; an axis not given in Python: <code><span class="nw">&#40;0&#44;</span> <span class="nw">&#45;1&#41;</span></code> |
| all ten numbers | <code><span class="nw">x</span></code>, <code><span class="nw">y</span></code>, <code><span class="nw">z</span></code>, <code><span class="nw">t</span></code> | <code><span class="nw">x&#61;None</span></code>, <code><span class="nw">y&#61;None</span></code>, <code><span class="nw">z&#61;None</span></code>, <code><span class="nw">t&#61;None</span></code> | both |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl fslroi ...`) and are arguments of `lx.fsl.fslroi`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all), given to the program as <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> and to the reading and writing of images; the result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects corrected, or FSL's behaviour (<code><span class="nw">docs&#47;api&#47;fsl&#45;roi&#46;md</span></code>, "Defects of the original, corrected by default"). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `bold.nii.gz` (a synthetic series of 4 such heads). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

first = lx.fsl.fslroi("bold.nii.gz", t=(0, 2))
first.shape  # -> (40, 48, 40, 2)
```

```bash
larmorx fsl fslroi bold.nii.gz bold_first2 0 2
```

## Ports {#ports}

`fslroi` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | validated | [fsl-bet-replica](repo:docs/validation/fsl-bet-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-bet](repo:docs/validation/fsl-bet.md) |

Both ports are complete. FSL's defects are corrected by default, and `reproduce` gives FSL's
behaviour: fslroi exits with status 1 after the errors it reports (**FSL-215**), an int8 input is
written as int8 (**FSL-217**), and with `FSLOUTPUTTYPE` unset the image is written as `.nii.gz`
(**FSL-11**). The clean room is built for speed: it converts the stored values once (or moves
them, where the type is kept) and copies the box row by row in parallel.

Both records are BET's, as these programs came with BET's options. The replica's holds 26 cases
of `fslroi`: 24 identical to FSL, 2 where both refuse alike. The clean room's holds 26: 24 within
its thresholds, 2 refused alike.

FSL is distributed under the FSL Licence (non-commercial use only), so each program has two
ports, a replica and a clean room, in different packages ([licensing](repo:docs/licensing.md)):

- **The clean room** (`crates/larmorx-fsl`, `larmorx_fsl::cli::fslroi` and `::ssroi`, Apache-2.0)
  is written from [`specs/standard_space_roi.md`](repo:specs/standard_space_roi.md), FSL's
  documentation and black-box runs of FSL 6.0.7.23 ([PROVENANCE](repo:crates/larmorx-fsl/PROVENANCE.md)),
  and runs in this process. Its `standard_space_roi` runs the clean room's own FLIRT,
  `convert_xfm`, `fslmaths`, `fslstats` and `fslroi`, and fslpy's `imcp`, in the same process: no
  FSL installation is needed.
- **The replica** is bit-exact: `larmorx-nc fsl fslroi` and `larmorx-nc fsl standard_space_roi`,
  in the package `larmorx-nc` (`crates-nc/`), under the FSL Licence's terms. It runs every program
  in the replica's own process.

`implementation="auto"` runs the replica when its program is found, else the clean room;
`"clean-room"` (`"original"`, 0.1.0rc1's spelling, still works) and `"replica"` choose. The
command line follows `--implementation` (before the family) or `LARMORX_IMPLEMENTATION` the same
way.

## Evidence {#evidence}

How each of `fslroi`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-bet/).

## More in the repository {#more}

The API page [docs/api/fsl-roi.md](repo:docs/api/fsl-roi.md) holds what `fslroi` shares with the page's other programs:

- [FSL's standard images](repo:docs/api/fsl-roi.md#fsls-standard-images)
- [Defects of the original, corrected by default](repo:docs/api/fsl-roi.md#defects-of-the-original-corrected-by-default)
- [History](repo:docs/api/fsl-roi.md#history)
