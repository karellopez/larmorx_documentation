---
title: "`betsurf`"
kicker: "Programs · FSL"
lede: "The inner skull, outer skull and scalp surfaces, as FSL's `betsurf` finds them."
description: "LARMORX reference for FSL 6.0.7.23 `betsurf`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  command: "larmorx fsl betsurf"
  python: "lx.fsl.betsurf"
  api: "docs/api/fsl-bet.md"
  evidence: "/evidence/fsl-bet/#betsurf"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "validated"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    crates/larmorx-cli/src/replica.rs: bdcff4968024a104
    crates/larmorx-core/src/cli.rs: 01fa0015abc1a111
    crates/larmorx-fsl/src/cli/betsurf.rs: 05d2c5fea516456d
    docs/api/fsl-bet.md: f4f96e777188b16d
    python/larmorx/fsl/bet.py: 24b8fa0168bd33f6
    validation/tools.toml: f010241e8fae68e6
---

## What it does {#what-it-does}

The inner skull, outer skull and scalp surfaces, as FSL's `betsurf` finds them.

## Command line {#command-line}

```text
larmorx fsl betsurf [options] <t1> <t2> <bet_mesh.vtk> <t1_to_standard.mat> <output>
larmorx fsl betsurf --t1only [options] <t1> <bet_mesh.vtk> <t1_to_standard.mat> <output>
```

Everything after `larmorx fsl betsurf` is the original's command line: the arguments of FSL 6.0.7.23's `betsurf`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl betsurf ...
```

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

Returns a `BetsurfResult`: the `inskull`, `outskull` and `outskin` surfaces, their masks
(`masks=True`, `-m`), the skull's mask (`skull_mask=True`, `-s`) and the surfaces drawn as images
(`outlines=True`, `-o`), all int16 on the T1's grid. `brain_surface` is `bet(..., mesh=True).mesh`
or a VTK file; `t1_to_standard` FLIRT's 4 x 4 matrix to MNI152 (a path or an array; it only decides
which profiles cross the eyes); without `t2` the surfaces come from the T1 alone (`--t1only`).
`precision` is `-p`. `lx.fsl.read_vtk(path)` reads a VTK mesh as FSL writes it.

Its result, `BetsurfResult`, holds what `betsurf` computed.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">inskull</span></code> | <code><span class="nw">Surface</span></code> | The inner skull, outer skull and scalp surfaces. |
| <code><span class="nw">outskull</span></code> | <code><span class="nw">Surface</span></code> | The inner skull, outer skull and scalp surfaces. |
| <code><span class="nw">outskin</span></code> | <code><span class="nw">Surface</span></code> | The inner skull, outer skull and scalp surfaces. |
| <code><span class="nw">inskull&#95;mask</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | Their masks (int16, 1 inside), with <code><span class="nw">masks&#61;True</span></code>. |
| <code><span class="nw">outskull&#95;mask</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | Their masks (int16, 1 inside), with <code><span class="nw">masks&#61;True</span></code>. |
| <code><span class="nw">outskin&#95;mask</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | Their masks (int16, 1 inside), with <code><span class="nw">masks&#61;True</span></code>. |
| <code><span class="nw">skull&#95;mask</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The skull between the two skull surfaces (int16), with <code><span class="nw">skull&#95;mask&#61;True</span></code>. |
| <code><span class="nw">inskull&#95;outline</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The surfaces drawn as 1 on the T1's grid (int16), with <code><span class="nw">outlines&#61;True</span></code>. |
| <code><span class="nw">outskull&#95;outline</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The surfaces drawn as 1 on the T1's grid (int16), with <code><span class="nw">outlines&#61;True</span></code>. |
| <code><span class="nw">outskin&#95;outline</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The surfaces drawn as 1 on the T1's grid (int16), with <code><span class="nw">outlines&#61;True</span></code>. |

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

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl betsurf ...`) and are arguments of `lx.fsl.betsurf`. Each one given wins over the environment variable it replaces.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Replaces <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code>. As for <code><span class="nw">bet</span></code> (the original's record: <code><span class="nw">docs&#47;validation&#47;fsl&#45;bet&#46;md</span></code>). |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | Replaces <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code>. As for <code><span class="nw">bet</span></code> (the original's record: <code><span class="nw">docs&#47;validation&#47;fsl&#45;bet&#46;md</span></code>). |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | Replaces <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code>. As for <code><span class="nw">bet</span></code> (the original's record: <code><span class="nw">docs&#47;validation&#47;fsl&#45;bet&#46;md</span></code>). |

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
| replica | `larmorx-nc` | FSL Licence: non-commercial use only | validated | [fsl-bet-replica](repo:docs/validation/fsl-bet-replica.md), [fsl-bet-replica-full](repo:docs/validation/fsl-bet-replica-full.md) |
| clean room | `larmorx` | Apache-2.0 | experimental | [fsl-bet](repo:docs/validation/fsl-bet.md) |

**Two implementations.** FSL is distributed under the FSL Licence (non-commercial use only), so
larmorx keeps its FSL tools in two implementations ([licensing](repo:docs/licensing.md)): the bit-exact
**replica**, `larmorx-nc fsl bet|bet2|betsurf` (package `larmorx-nc`, `crates-nc/`, under the FSL
Licence's terms; translated from FSL's source:
[PROVENANCE](repo:crates-nc/larmorx-nc-bet/PROVENANCE.md)), and the clean-room **original** in
the main package (Apache-2.0, `crates/larmorx-fsl`), written from
[`specs/bet.md`](repo:specs/bet.md), the BET paper and black-box runs of FSL
([PROVENANCE](repo:crates/larmorx-fsl/PROVENANCE.md); since 2026-10-30 `bet2` and the `bet`
script, since 2026-10-31 `betsurf`). `implementation="auto"` runs the replica, as a separate
program, when `larmorx-nc` is installed (`pip install larmorx-nc`), else the clean-room original;
`"replica"` and `"clean-room"` (`"original"`, 0.1.0rc1's spelling, still works) choose.
Each image's `implementation` names the one that ran. The command line chooses alike
(`--implementation auto|replica|clean-room` before the family, or `LARMORX_IMPLEMENTATION`).

**Status: `validated`** (the replica), against FSL 6.0.7.23 itself
([record](repo:docs/validation/fsl-bet-replica.md), standard tier, re-made 2026-11-04 with `-S`, `-B`,
`-A`, `-A2`, standard_space_roi and fslroi: 263 cases, 201 compared, every one bit-identical, 600
of 600 files byte for byte, FSL's own step from 6.0.7.17 in every case;
[full tier](repo:docs/validation/fsl-bet-replica-full.md), against FSL 6.0.7.17: 173 cases, 129
compared, 364 of 364 files byte for byte): every compared case gives FSL's exit status, messages and files byte
for byte (images: header and data; meshes as text), fMRIPrep's 29 BET calls on its twelve oracle
runs with BOLD runs included (the data panel's), whose outputs also have the values of fMRIPrep's
own (and of fMRIPrep's build of FSL in its image). 47 cases are rejected by both alike; in 13, FSL
crashes on what it leaves undefined and `reproduce` fills it (below); 1 waits for fslpy's `imcp`
conversion (standard_space_roi, below). The records include random testing's permanent cases (17 in the standard tier) (`difftest/...`; BET's
random testing: [docs/validation/difftest.md](repo:docs/validation/difftest.md)), and the replica needs no
more memory than FSL in any measured call (`tests/parity/test_memory_peak.py`).

**Status: `experimental`** ([record](repo:docs/validation/fsl-bet.md), standard tier against FSL
6.0.7.23, re-made 2026-11-05 in the clean-room catch-up: **198 of the 200 compared cases within the
thresholds**, the other two missing one (below); of its 252 cases 46 more are rejected by both
alike, 6 are where `reproduce` fills what FSL leaves undefined, none pending; the 164 cases kept
from part 2b's record (2026-10-31, 168 cases) unchanged in status and details, the 88 new ones
`standard_space_roi`'s and `fslroi`'s 57 (45 within the thresholds, every one FSL's bit for bit, 12
rejected by both: [fsl-roi.md](repo:docs/api/fsl-roi.md)) and the options' 31: `-S` and `-B` FSL's bit for bit on
every case (every output and every `-d` file; an adult, a tumour, an 82-year-old with the neck,
`-S -n`, a NaN head, a pair output) but a 3.5-year-old's `-B`, `-A` and `-A2` with bet2's outputs and
FLIRT's matrices FSL's and betsurf's masks within its thresholds, `-F` and `-Z` of int8 heads FSL's;
part 2b's numbers follow): exit statuses and messages FSL's byte
for byte; 217 of 217
brains, masks and outlines of `bet2` and `bet` bit-identical to FSL's (part 2a's record
counted 12 reported Dice values with phantoms' known brains among them, as "within the
thresholds"), 13 of 13 skull images bit-identical, the meshes FSL's to the file's 6 decimals, the
surfaces that rerun after a self-intersecting first pass (a 75-year-old's T1w, 7 T, a tumour)
bit for bit, fMRIPrep's 29 BET calls on its oracle runs all bit-identical (and with fMRIPrep's
own outputs' values); headers FSL's byte for byte but for `descrip` (`larmorx fsl bet2`), the
qform's quaternion included. The 142 cases of part 2a's record are unchanged; the 26 new ones
are betsurf's (its options, messages and failure cases, FSL-48, -52, -53, -54 among them, and
five real heads with bet2's meshes and FLIRT's matrices made by FSL).

## Evidence {#evidence}

How `betsurf`'s ports compare with FSL 6.0.7.23, case by case: [its evidence](/evidence/fsl-bet/#betsurf).

## More in the repository {#more}

The API page [docs/api/fsl-bet.md](repo:docs/api/fsl-bet.md) holds what `betsurf` shares with the page's other programs:

- [Upstream defects (D13)](repo:docs/api/fsl-bet.md#upstream-defects-d13)
- [Deliberate differences](repo:docs/api/fsl-bet.md#deliberate-differences)
- [Known last-bit differences](repo:docs/api/fsl-bet.md#known-last-bit-differences)
- [Speed](repo:docs/api/fsl-bet.md#speed)
- [Rust](repo:docs/api/fsl-bet.md#rust)
- [The clean-room original (crates/larmorx-fsl)](repo:docs/api/fsl-bet.md#the-clean-room-original-crateslarmorx-fsl)
