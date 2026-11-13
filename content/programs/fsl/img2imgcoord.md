---
title: "`img2imgcoord`"
kicker: "Programs · FSL"
description: "LARMORX reference for FSL 6.0.7.23 `img2imgcoord`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl img2imgcoord"
  python: "lx.fsl.img2imgcoord"
  api: "docs/api/fsl-flirt.md"
  evidence: "/evidence/fsl-flirt/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "24c23485c8957683"
    crates/larmorx-fsl/src/cli/coords.rs: "95fb82e3197438b2"
    docs/api/fsl-flirt.md: "abc8e4a5001ff9ef"
    python/larmorx/fsl/flirt_tools.py: "a0b788dabe4a5b66"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

`img2imgcoord` maps coordinates from one image to another through a FLIRT matrix: voxels by
default, millimetres with `-mm`.

## Command line {#command-line}

```text synopsis
larmorx fsl img2imgcoord [options] <filename containing coordinates>
```

Everything after `larmorx fsl img2imgcoord` is the original's command line: the arguments of FSL 6.0.7.23's `img2imgcoord`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl img2imgcoord ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>img2imgcoord</code>'s usage text, as the clean room prints it</summary>

```text
Usage: img2imgcoord [options] <filename containing coordinates>

  Options are:
        -src <filename of source image>        
        -dest <filename of destination image>  
        -xfm <filename of affine transform     (e.g. source2dest.mat)>
        -warp <filename of warpfield (e.g. intermediate2dest_warp.nii.gz)>
        -premat <filename of pre-warp affine transform  (e.g. source2intermediate.mat)>   (default=identity)
        -vox                                   (all coordinates in voxels - default)
        -mm                                    (all coordinates in mm)
        -v                                     (verbose)
        -help

 Notes:
  (1) if '-' is used as coordinate filename then coordinates are read from standard input
  (2) the first three options are compulsory
```

</details>

## Python {#python}

```python
lx.fsl.img2imgcoord(
    coords: Any,
    src: Any,
    dest: Any,
    *,
    xfm: Any = None,
    mm: bool = False,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
) -> np.ndarray
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`).

FSL's `img2imgcoord`: `coords` (N x 3, or a file of rows `x y z`) in `src`'s voxels (NIfTI's), or millimetres with `mm`, mapped through `xfm` (FLIRT's matrix from `src` to `dest`; the identity without one) to `dest`'s; returned as N x 3.

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `img2imgcoord` accepts (`crates/larmorx-fsl/src/cli/coords.rs`) and the arguments of `lx.fsl.img2imgcoord` (`python/larmorx/fsl/flirt_tools.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">img2imgcoord</span></code> option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#60;filename</span> <span class="nw">containing</span> <span class="nw">coordinates&#62;</span></code> | <code><span class="nw">coords</span></code> |  | <code><span class="nw">&#45;</span></code> or no file: standard input (refused at a terminal, as FSL) |
| <code><span class="nw">&#45;src</span></code>, <code><span class="nw">&#45;dest</span></code> | <code><span class="nw">src</span></code>, <code><span class="nw">dest</span></code> |  |  |
| <code><span class="nw">&#45;xfm</span></code>, <code><span class="nw">&#45;premat</span></code> | <code><span class="nw">xfm</span></code> | <code><span class="nw">None</span></code> | <span class="opt-help">FSL: “(default=identity)”</span> |
| <code><span class="nw">&#45;vox</span></code>, <code><span class="nw">&#45;mm</span></code> | <code><span class="nw">mm</span></code> | <code><span class="nw">False</span></code> | voxels by default<span class="opt-help">FSL: “(all coordinates in voxels - default)”</span><span class="opt-help">FSL: “(all coordinates in mm)”</span> |
| <code><span class="nw">&#45;warp</span></code> | command line only |  | FNIRT's warp fields: refused until FNIRT is ported |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;help</span></code>, <code><span class="nw">&#45;flirt</span></code> | command line only |  | <code><span class="nw">&#45;flirt</span></code> accepted and ignored<span class="opt-help">FSL: “(verbose)”</span> |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl img2imgcoord ...`); `lx.fsl.img2imgcoord` takes `n_threads` and `implementation` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all), given to the program as <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code>; the result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;fsl&#46;img2imgcoord</span></code> takes no <code><span class="nw">upstream&#95;defects</span></code>. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `boldref.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `T1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `bold2t1.mat` (the identity as a 4 × 4 text matrix), `coords.txt` (two coordinates, one `x y z` per line). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

xyz = lx.fsl.img2imgcoord([[10, 20, 30]], "boldref.nii.gz", "T1w.nii.gz", xfm="bold2t1.mat")
xyz.shape  # -> (1, 3)
```

```bash
larmorx fsl img2imgcoord -src boldref.nii.gz -dest T1w.nii.gz -xfm bold2t1.mat coords.txt
```

## Ports {#ports}

`img2imgcoord` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-flirt-replica](repo:docs/validation/fsl-flirt-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-flirt](repo:docs/validation/fsl-flirt.md) |

Both ports are complete (`specs/flirt.md` §15.2), standard input included (the prompts and the
refusal at a terminal); where FSL aborts, they print the same lines and exit with status 1. The
coordinate programs' `-warp` (a FNIRT warp field) is refused until FNIRT is ported: an unreadable
file, or an image of other than three volumes, gives FSL's messages and exit status 1, as FSL.
Matrices other than 4 × 4 where FSL would invert them beyond 4 × 4 are refused (FSL prints part
of its output, then aborts).

The replica's record holds 11 cases of `img2imgcoord`: 7 identical to FSL, 4 where both refuse or
abort alike. The clean room's holds 12: 7 identical to FSL in every byte of text and file, 5
where both refuse or abort alike.

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

How each of `img2imgcoord`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-flirt/).

## More in the repository {#more}

The API page [docs/api/fsl-flirt.md](repo:docs/api/fsl-flirt.md) holds what `img2imgcoord` shares with the page's other programs:

- [The clean room (part 1, 2026-11-02)](repo:docs/api/fsl-flirt.md#the-clean-room-part-1-2026-11-02)
- [Defects of the original, corrected by default](repo:docs/api/fsl-flirt.md#defects-of-the-original-corrected-by-default)
- [Not yet](repo:docs/api/fsl-flirt.md#not-yet)
- [History](repo:docs/api/fsl-flirt.md#history)
