---
title: "`betsurf`"
kicker: "Programs · FSL"
description: "LARMORX reference for FSL 6.0.7.23 `betsurf`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl betsurf"
  python: "lx.fsl.betsurf"
  api: "docs/api/fsl-bet.md"
  evidence: "/evidence/fsl-bet/#betsurf"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "validated"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "2e982878694e2b59"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "57e943300dd31436"
    crates/larmorx-fsl/src/cli/betsurf.rs: "05d2c5fea516456d"
    docs/api/fsl-bet.md: "d31d9c8db88492e7"
    python/larmorx/fsl/bet.py: "14e2e5d5c68509eb"
    validation/tools.toml: "7815491966e55fc6"
---

## What it does {#what-it-does}

`betsurf` finds the inner skull, the outer skull and the scalp of a head, from `bet2`'s brain
surface (`-e`), the T1 image (and a T2) and the T1's registration to MNI152.

## Command line {#command-line}

```text synopsis
larmorx fsl betsurf [options] <t1> <t2> <bet_mesh.vtk> <t1_to_standard.mat> <output>
larmorx fsl betsurf --t1only [options] <t1> <bet_mesh.vtk> <t1_to_standard.mat> <output>
```

Everything after `larmorx fsl betsurf` is the original's command line: the arguments of FSL 6.0.7.23's `betsurf`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl betsurf ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>betsurf</code>'s usage text, as the clean room prints it</summary>

```text
Part of FSL (ID: 2412.6-dirty)
BETSURF (BET Surface Finder) v2.1 - FMRIB Analysis Group, Oxford

Usage: 
 betsurf          [options] <t1> <t2> <bet_mesh.vtk> <t1_to_standard.mat> <output>
 betsurf --t1only [options] <t1>      <bet_mesh.vtk> <t1_to_standard.mat> <output>

Optional arguments (You may optionally specify one or more of):
	-h,--help	displays this help, then exits
	-v,--verbose	switch on diagnostic messages
	-1,--t1only	extraction with t1 only
	-o,--outline	generates all surface outlines
	-m,--mask	generates binary masks from the meshes
	-s,--skullmask	generates skull binary mask
	-p,--increased_precision <int>	retessellates the meshes the indicated number of times
```

</details>

## Python {#python}

```python
lx.fsl.betsurf(
    t1: Any,
    brain_surface: Surface | str | os.PathLike[str],
    t1_to_standard: Any,
    *,
    t2: Any = None,
    masks: bool = True,
    skull_mask: bool = False,
    outlines: bool = False,
    precision: int = 0,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
) -> BetsurfResult
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

The inner skull, outer skull and scalp surfaces, as FSL's `betsurf` finds them.

`brain_surface` is `bet(..., mesh=True).mesh` or a VTK file; `t1_to_standard` is FLIRT's 4 x 4
matrix to MNI152 (a path or an array; it only decides which profiles cross the eyes). Without `t2`
the surfaces come from the T1 alone (`--t1only`). `precision` is `-p`. `lx.fsl.read_vtk(path)`
reads a VTK mesh as FSL writes it.

Its result, `BetsurfResult`, holds what `betsurf` computed.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">inskull</span></code> | <code><span class="nw">Surface</span></code> | The inner skull, outer skull and scalp surfaces. |
| <code><span class="nw">outskull</span></code> | <code><span class="nw">Surface</span></code> | The inner skull, outer skull and scalp surfaces. |
| <code><span class="nw">outskin</span></code> | <code><span class="nw">Surface</span></code> | The inner skull, outer skull and scalp surfaces. |
| <code><span class="nw">inskull&#95;mask</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | Their masks on the T1's grid (int16, 1 inside), with <code><span class="nw">masks&#61;True</span></code> (<code><span class="nw">&#45;m</span></code>). |
| <code><span class="nw">outskull&#95;mask</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | Their masks on the T1's grid (int16, 1 inside), with <code><span class="nw">masks&#61;True</span></code> (<code><span class="nw">&#45;m</span></code>). |
| <code><span class="nw">outskin&#95;mask</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | Their masks on the T1's grid (int16, 1 inside), with <code><span class="nw">masks&#61;True</span></code> (<code><span class="nw">&#45;m</span></code>). |
| <code><span class="nw">skull&#95;mask</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The skull between the two skull surfaces, on the T1's grid (int16), with <code><span class="nw">skull&#95;mask&#61;True</span></code> (<code><span class="nw">&#45;s</span></code>). |
| <code><span class="nw">inskull&#95;outline</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The surfaces drawn as 1 on the T1's grid (int16), with <code><span class="nw">outlines&#61;True</span></code> (<code><span class="nw">&#45;o</span></code>). |
| <code><span class="nw">outskull&#95;outline</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The surfaces drawn as 1 on the T1's grid (int16), with <code><span class="nw">outlines&#61;True</span></code> (<code><span class="nw">&#45;o</span></code>). |
| <code><span class="nw">outskin&#95;outline</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The surfaces drawn as 1 on the T1's grid (int16), with <code><span class="nw">outlines&#61;True</span></code> (<code><span class="nw">&#45;o</span></code>). |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `betsurf` accepts (`crates/larmorx-fsl/src/cli/betsurf.rs`) and the arguments of `lx.fsl.betsurf` (`python/larmorx/fsl/bet.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| FSL option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#60;t1&#62;</span> <span class="nw">&#91;&#60;t2&#62;&#93;</span> <span class="nw">&#60;bet&#95;mesh&#46;vtk&#62;</span> <span class="nw">&#60;t1&#95;to&#95;standard&#46;mat&#62;</span> <span class="nw">&#60;output&#62;</span></code> | <code><span class="nw">t1</span></code>, <code><span class="nw">t2</span></code>, <code><span class="nw">brain&#95;surface</span></code>, <code><span class="nw">t1&#95;to&#95;standard</span></code>; the result | <code><span class="nw">t2&#61;None</span></code> | outputs <code><span class="nw">&#60;output&#62;&#95;inskull&#95;mesh&#46;vtk</span></code>, <code><span class="nw">&#95;outskull&#95;mesh&#46;vtk</span></code>, <code><span class="nw">&#95;outskin&#95;mesh&#46;vtk</span></code> (always), their images |
| <code><span class="nw">&#45;1</span></code>, <code><span class="nw">&#45;&#45;t1only</span></code> | <code><span class="nw">t2&#61;None</span></code> | <code><span class="nw">None</span></code> | the surfaces from the T1 alone<span class="opt-help">FSL: “extraction with t1 only”</span> |
| <code><span class="nw">&#45;m</span></code>, <code><span class="nw">&#45;&#45;mask</span></code> | <code><span class="nw">masks&#61;True</span></code> (default) | <code><span class="nw">True</span></code> | <code><span class="nw">&#60;output&#62;&#95;inskull&#95;mask</span></code>, <code><span class="nw">&#95;outskull&#95;mask</span></code>, <code><span class="nw">&#95;outskin&#95;mask</span></code><span class="opt-help">FSL: “generates binary masks from the meshes”</span> |
| <code><span class="nw">&#45;s</span></code>, <code><span class="nw">&#45;&#45;skullmask</span></code> | <code><span class="nw">skull&#95;mask&#61;True</span></code> | <code><span class="nw">False</span></code> | <code><span class="nw">&#60;output&#62;&#95;skull&#95;mask</span></code> (the masks are made without <code><span class="nw">&#45;m</span></code> too)<span class="opt-help">FSL: “generates skull binary mask”</span> |
| <code><span class="nw">&#45;o</span></code>, <code><span class="nw">&#45;&#45;outline</span></code> | <code><span class="nw">outlines&#61;True</span></code> | <code><span class="nw">False</span></code> | <code><span class="nw">&#60;output&#62;&#95;inskull&#95;mesh</span></code>, <code><span class="nw">&#95;outskull&#95;mesh</span></code>, <code><span class="nw">&#95;outskin&#95;mesh</span></code> images: each surface drawn as 1<span class="opt-help">FSL: “generates all surface outlines”</span> |
| <code><span class="nw">&#45;p</span> <span class="nw">&#60;int&#62;</span></code>, <code><span class="nw">&#45;&#45;increased&#95;precision&#61;&#60;int&#62;</span></code> | <code><span class="nw">precision</span></code> | <code><span class="nw">0</span></code> | each surface retessellated that many times, 100 more steps each (the meshes written are the retessellated ones); FSL's int: <code><span class="nw">strtol</span></code> of base 0 (<code><span class="nw">0x10</span></code> reads, <code><span class="nw">08</span></code> does not); larmorx refuses more than 10 (the meshes would not fit any memory)<span class="opt-help">FSL: “retessellates the meshes the indicated number of times”</span> |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> | (command line only) |  | <code><span class="nw">extracting</span> <span class="nw">profiles</span></code>, the profiles cast and the percentage set aside (the dropped ones and those of which only the scalp counts), then each phase<span class="opt-help">FSL: “switch on diagnostic messages”</span> |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | (command line only) |  | the usage, exit 0<span class="opt-help">FSL: “displays this help, then exits”</span> |
| the mesh name <code><span class="nw">manual&#95;input</span></code> | (command line only) |  | the name read from standard input (larmorx refuses at its end, where FSL waits forever); the name <code><span class="nw">c</span></code> cancels (an empty mesh: refused, FSL-52) |
| <code><span class="nw">FSLOUTPUTTYPE</span></code> | (always NIfTI-1 in Python) |  | read when the first image is written, as FSL does (unset: <code><span class="nw">NIFTI&#95;GZ</span></code>, FSL-11) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl betsurf ...`) and are arguments of `lx.fsl.betsurf`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | As for <code><span class="nw">bet</span></code> (the clean room's record: <code><span class="nw">docs&#47;validation&#47;fsl&#45;bet&#46;md</span></code>). Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | As for <code><span class="nw">bet</span></code> (the clean room's record: <code><span class="nw">docs&#47;validation&#47;fsl&#45;bet&#46;md</span></code>). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | As for <code><span class="nw">bet</span></code> (the clean room's record: <code><span class="nw">docs&#47;validation&#47;fsl&#45;bet&#46;md</span></code>). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `T1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `T1w_to_MNI152.mat` (the identity as a 4 × 4 text matrix). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# The skull and scalp: bet2's mesh, then betsurf with the T1's registration to MNI152
b = lx.fsl.bet("T1w.nii.gz", mesh=True)
s = lx.fsl.betsurf("T1w.nii.gz", b.mesh, "T1w_to_MNI152.mat", skull_mask=True)
s.inskull_mask, s.outskull_mask, s.outskin_mask, s.skull_mask
```

```bash
larmorx fsl bet2 T1w.nii.gz T1w_brain -e
larmorx fsl betsurf --t1only -o -m -s T1w.nii.gz T1w_brain_mesh.vtk T1w_to_MNI152.mat T1w
```

## Ports {#ports}

`betsurf` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | validated | [fsl-bet-replica](repo:docs/validation/fsl-bet-replica.md), [fsl-bet-replica-full](repo:docs/validation/fsl-bet-replica-full.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-bet](repo:docs/validation/fsl-bet.md) |

The replica gives FSL 6.0.7.23's exit status, messages and files byte for byte in 201 of the 263
cases of its record, which holds `bet`, `bet2`, `betsurf`, `standard_space_roi` and `fslroi`; 47
more are rejected by both. The clean room's masks and outlines are within its thresholds (a Dice coefficient of at least 0.99, a
boundary distance of at most 1 voxel at the 95th percentile) in 114 of 116, 34 of them bit for bit.
One of the record's two misses is `betsurf`'s: the scalp of ds002603 with its T2, whose boundary
distance is 2 voxels at the 95th percentile.

FSL's licence allows non-commercial use only, so the two ports of `bet`, `bet2` and `betsurf`, a
replica and a clean room, live in different packages ([licensing](repo:docs/licensing.md) says what each
package holds):

- **The replica** is translated from FSL's source. The package `larmorx-nc` holds it, under FSL's
  licence, and `larmorx` runs it as a separate program, `larmorx-nc fsl bet|bet2|betsurf`, when
  `larmorx-nc` is installed (`pip install larmorx-nc`).
- **The clean room** is written from [`specs/bet.md`](repo:specs/bet.md), the BET paper and runs
  of FSL, without FSL's source or the replica. It is part of `larmorx`, under Apache-2.0
  (`crates/larmorx-fsl`, with its [PROVENANCE](repo:crates/larmorx-fsl/PROVENANCE.md)).

`implementation="auto"` runs the replica when `larmorx-nc` is installed, and the clean room
otherwise. `"replica"` and `"clean-room"` choose one (`"original"`, 0.1.0rc1's spelling of
`"clean-room"`, still works). Each image's `implementation` names the port that ran. On the
command line, `--implementation auto|replica|clean-room` before the family chooses alike, from the
next release; in 0.1.0rc1 the variable `LARMORX_IMPLEMENTATION` chooses (`original` for the clean
room).

## Evidence {#evidence}

How each of `betsurf`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-bet/#betsurf).

## More in the repository {#more}

The API page [docs/api/fsl-bet.md](repo:docs/api/fsl-bet.md) holds what `betsurf` shares with the page's other programs:

- [The records](repo:docs/api/fsl-bet.md#the-records)
- [Defects of the original, corrected by default](repo:docs/api/fsl-bet.md#defects-of-the-original-corrected-by-default)
- [Deliberate differences](repo:docs/api/fsl-bet.md#deliberate-differences)
- [Known last-bit differences](repo:docs/api/fsl-bet.md#known-last-bit-differences)
- [Speed](repo:docs/api/fsl-bet.md#speed)
- [Rust](repo:docs/api/fsl-bet.md#rust)
- [The clean room (crates/larmorx-fsl)](repo:docs/api/fsl-bet.md#the-clean-room-crateslarmorx-fsl)
- [History](repo:docs/api/fsl-bet.md#history)
