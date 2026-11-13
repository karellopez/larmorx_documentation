---
title: "`pointflirt`"
kicker: "Programs · FSL"
lede: "`pointflirt` finds the affine matrix that maps one set of points onto another, in the least-squares sense."
description: "LARMORX reference for FSL 6.0.7.23 `pointflirt`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl pointflirt"
  python: "lx.fsl.pointflirt"
  api: "docs/api/fsl-flirt.md"
  evidence: "/evidence/fsl-flirt/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "fa776d2ea0a17487"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "34429cb924a382b4"
    crates/larmorx-fsl/src/cli/pointflirt.rs: "9bbda1e01ffd8f90"
    docs/api/fsl-flirt.md: "21d456bedacfd6a2"
    python/larmorx/fsl/flirt_more.py: "64de6a5439fd3ed6"
    validation/tools.toml: "f0750687390307f1"
---

## What it does {#what-it-does}

The points are in millimetres, or in voxels with `--vox`, scaled by the two
images' voxel sizes. It warns when the points do not determine the matrix, and a file of exactly
three points is read with one point per column, as FSL reads it.

## Command line {#command-line}

```text synopsis
larmorx fsl pointflirt -i <invol coords> -r <refvol coords> -o <output matrix>
larmorx fsl pointflirt -i <invol coords> -r <refvol coords> -o <output matrix> --vox --invol=<input vol> --refvol=<ref vol>
```

Everything after `larmorx fsl pointflirt` is the original's command line: the arguments of FSL 6.0.7.23's `pointflirt`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl pointflirt ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>pointflirt</code>'s usage text, as the clean room prints it</summary>

```text
Part of FSL (ID: 2412.6-dirty)
pointflirt 
Copyright(c) 2001, University of Oxford (Mark Jenkinson)

Usage: 
pointflirt -i <invol coords>  -r <refvol coords> -o <output matrix>
pointflirt -i <invol coords>  -r <refvol coords> -o <output matrix> --vox --invol=<input vol> --refvol=<ref vol>

Compulsory arguments (You MUST set one or more of):
	-i	filename of input volume coordinates
	-r	filename of reference volume coordinates

Optional arguments (You may optionally specify one or more of):
	-o,--out	filename of affine matrix output
	--vox	use voxel coordinates, not mm, for input
	--invol	filename of input volume (needed for --vox option)
	--refvol	filename of reference volume (needed for --vox option)
	-v,--verbose	switch on diagnostic messages
	-h,--help	display this message
```

</details>

## Python {#python}

```python
lx.fsl.pointflirt(
    in_points: Any,
    ref_points: Any,
    *,
    in_image: Any = None,
    ref_image: Any = None,
    implementation: ImplementationName = "auto",
) -> np.ndarray
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`).

FSL's `pointflirt`: the affine 4 x 4 matrix that maps `in_points` onto `ref_points` (N x 3 arrays or text files, in mm; with `in_image` and `ref_image`, in voxels, scaled by their voxel sizes: `--vox`) in the least-squares sense.

`in_points` and `ref_points` are N × 3 arrays or text files of rows `x y z`, as many points in
each; `in_image` and `ref_image` are paths or `lx.Image` objects, given both or neither. The
result is the 4 × 4 matrix.

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `pointflirt` accepts (`crates/larmorx-fsl/src/cli/pointflirt.rs`) and the arguments of `lx.fsl.pointflirt` (`python/larmorx/fsl/flirt_more.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">pointflirt</span></code> option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;i</span></code>, <code><span class="nw">&#45;r</span></code> | <code><span class="nw">in&#95;points</span></code>, <code><span class="nw">ref&#95;points</span></code> |  | the input's and the reference's points<span class="opt-help">FSL: “filename of input volume coordinates”</span><span class="opt-help">FSL: “filename of reference volume coordinates”</span> |
| <code><span class="nw">&#45;o</span></code>, <code><span class="nw">&#45;&#45;out</span></code> | the result |  | <span class="opt-help">FSL: “filename of affine matrix output”</span> |
| <code><span class="nw">&#45;&#45;vox</span></code> | <code><span class="nw">in&#95;image</span></code>, <code><span class="nw">ref&#95;image</span></code> given | <code><span class="nw">in&#95;image&#61;None</span></code>, <code><span class="nw">ref&#95;image&#61;None</span></code> | voxel coordinates; needs <code><span class="nw">&#45;&#45;invol</span></code> and <code><span class="nw">&#45;&#45;refvol</span></code><span class="opt-help">FSL: “use voxel coordinates, not mm, for input”</span> |
| <code><span class="nw">&#45;&#45;invol</span></code>, <code><span class="nw">&#45;&#45;refvol</span></code> | <code><span class="nw">in&#95;image</span></code>, <code><span class="nw">ref&#95;image</span></code> | <code><span class="nw">in&#95;image&#61;None</span></code>, <code><span class="nw">ref&#95;image&#61;None</span></code> | the images whose voxel sizes scale the points<span class="opt-help">FSL: “filename of input volume (needed for --vox option)”</span><span class="opt-help">FSL: “filename of reference volume (needed for --vox option)”</span> |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code>, <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | command line only |  | <span class="opt-help">FSL: “switch on diagnostic messages”</span><span class="opt-help">FSL: “display this message”</span> |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl pointflirt ...`); `lx.fsl.pointflirt` takes `implementation` as an argument, and the others are the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;fsl&#46;pointflirt</span></code> takes no <code><span class="nw">n&#95;threads</span></code>. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>). The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;fsl&#46;pointflirt</span></code> takes no <code><span class="nw">upstream&#95;defects</span></code>. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `in.txt` (eight points in millimetres, one `x y z` per line), `ref.txt` (the same eight points moved by 2, −3 and 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# The second file holds the first's points moved by 2, -3 and 4 mm.
aff = lx.fsl.pointflirt("in.txt", "ref.txt")
aff[:3, 3].round(6).tolist()  # -> [2.0, -3.0, 4.0]
```

```bash
larmorx fsl pointflirt -i in.txt -r ref.txt -o in2ref.mat
```

## Ports {#ports}

`pointflirt` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-flirt-replica](repo:docs/validation/fsl-flirt-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-flirt](repo:docs/validation/fsl-flirt.md) |

Both ports are complete: every option, usage, message, exit status and failure case of
`specs/flirt.md` §15.6, with its transposition rule, `--vox` and the nullspace warning. Two
coordinate files both empty or missing are refused in both modes (**FSL-204**: FSL crashes after
its `Could not open matrix file` lines): `larmorx-nc: error: pointflirt: no points in the
coordinate files (FSL-204)`, exit status 1, the clean room after `-v`'s headings, as FSL prints
them. The clean room reads a `nan` word as 0 (the fit of the points as read) and stops on an
overflow as FSL's SVD does.

The replica's record holds 14 cases of `pointflirt`: 7 identical to FSL, 6 where both refuse
alike, and 1 of FSL-204. The clean room's holds 17: 8 within its thresholds, 7 refused alike, and
the 2 of FSL-204.

FSL's licence allows non-commercial use only, so each of FLIRT's programs has two ports, a
replica and a clean room, in different packages ([licensing](repo:docs/licensing.md) says what each
package holds):

- **The replica** is translated from FSL's source. The package `larmorx-nc` holds it (`crates-nc/`),
  under the FSL Licence's terms, and `larmorx` runs it as a separate program, `larmorx-nc fsl
  <program>`, when `larmorx-nc` is installed (`pip install larmorx-nc`).
- **The clean room** is written from [`specs/flirt.md`](repo:specs/flirt.md) by an implementer who
  never read FSL's source or the replica. It is part of `larmorx`, under Apache-2.0
  (`crates/larmorx-fsl`, with its [PROVENANCE](repo:crates/larmorx-fsl/PROVENANCE.md), section
  "FLIRT"), and runs on the main package's clean-room registration engine, shared with
  `lx.mri.hmc`.

`implementation="auto"` runs the replica when `larmorx-nc` is installed, and the clean room
otherwise. `"replica"` and `"clean-room"` choose one (`"original"`, 0.1.0rc1's spelling of
`"clean-room"`, still works); `"clean-room"` runs the clean room in this process. On the command
line, `--implementation auto|replica|clean-room` before the family chooses alike, from the next
release; in 0.1.0rc1 the variable `LARMORX_IMPLEMENTATION` chooses (`original` for the clean
room).

## Evidence {#evidence}

How each of `pointflirt`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-flirt/).

## More in the repository {#more}

The API page [docs/api/fsl-flirt.md](repo:docs/api/fsl-flirt.md) holds what `pointflirt` shares with the page's other programs:

- [The clean room (part 1, 2026-11-02)](repo:docs/api/fsl-flirt.md#the-clean-room-part-1-2026-11-02)
- [Upstream defects (D13)](repo:docs/api/fsl-flirt.md#upstream-defects-d13)
- [Not yet](repo:docs/api/fsl-flirt.md#not-yet)
- [History](repo:docs/api/fsl-flirt.md#history)
