---
title: "`bet2`"
kicker: "Programs · FSL"
description: "LARMORX reference for FSL 6.0.7.23 `bet2`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  command: "larmorx fsl bet2"
  python: "lx.fsl.bet"
  api: "docs/api/fsl-bet.md"
  evidence: "/evidence/fsl-bet/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "validated"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    crates/larmorx-cli/src/replica.rs: bdcff4968024a104
    crates/larmorx-core/src/cli.rs: 01fa0015abc1a111
    crates/larmorx-fsl/src/cli/bet2.rs: 533a6b3eac008baf
    docs/api/fsl-bet.md: c59408e34012b405
    python/larmorx/fsl/bet.py: 24b8fa0168bd33f6
    validation/tools.toml: f010241e8fae68e6
---

## What it does {#what-it-does}

FSL's brain extraction itself, which the `bet` script runs.

## Command line {#command-line}

```text
larmorx fsl bet2 <input_fileroot> <output_fileroot> [options]
```

Everything after `larmorx fsl bet2` is the original's command line: the arguments of FSL 6.0.7.23's `bet2`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl bet2 ...
```

<details class="usage"><summary><code>bet2</code>'s usage text, as the clean room prints it</summary>

```text
Part of FSL (ID: 2412.6-dirty)
BET (Brain Extraction Tool) v2.1 - FMRIB Analysis Group, Oxford

Usage: 
bet2 <input_fileroot> <output_fileroot> [options]

Optional arguments (You may optionally specify one or more of):
	-o,--outline	generate brain surface outline overlaid onto original image
	-m,--mask	generate binary brain mask
	-s,--skull	generate approximate skull image
	-n,--nooutput	don't generate segmented brain image output
	-f <f>		fractional intensity threshold (0->1); default=0.5; smaller values give larger brain outline estimates
	-g <g>		vertical gradient in fractional intensity threshold (-1->1); default=0; positive values give larger brain outline at bottom, smaller at top
	-r,--radius <r>	head radius (mm not voxels); initial surface sphere is set to half of this
	-w,--smooth <r>	smoothness factor; default=1; values smaller than 1 produce more detailed brain surface, values larger than one produce smoother, less detailed surface
	-c <x y z>	centre-of-gravity (voxels not mm) of initial mesh surface.
	-t,--threshold	-apply thresholding to segmented brain image and mask
	--ct	-treat input as CT image (default is MRI)
	--binaryMask <image>	Generate mesh from existing mask
	-e,--mesh	generates brain surface as mesh in vtk format
	-v,--verbose	switch on diagnostic messages
	-h,--help	displays this help, then exits
```

</details>

## Python {#python}

```python
lx.fsl.bet(
    image: Any,
    *,
    frac: float = 0.5,
    gradient: float = 0.0,
    radius: float | None = None,
    centre: Sequence[float] | None = None,
    smoothness: float = 1.0,
    threshold: bool = False,
    head_ct: bool = False,
    variation: Variation | None = None,
    t2: Any = None,
    brain: bool = True,
    mask: bool = False,
    outline: bool = False,
    skull: bool = False,
    mesh: bool = False,
    tanh: Tanh = "glibc",
    fsl_data: str | os.PathLike[str] | None = None,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
) -> BetResult
```

Where `Variation` is one of `"robust"`, `"small_fov"`, `"fmri"`, `"eyes"`, `"bias"`, `"surfaces"`, `"surfaces_t2"`; `Tanh` is one of `"glibc"`, `"correctly-rounded"`; `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

The brain, as FSL's `bet2` (or, with `variation`, the `bet` script) extracts it.

`lx.fsl.bet` without `variation` runs `bet2` (the function's description: [`bet`](/programs/fsl/bet/)).

Its result, `BetResult`, holds what `bet` computed (`None` for what was not asked for).

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">brain</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The input with every voxel outside the brain 0 (float32; 4D with <code><span class="nw">&#34;fmri&#34;</span></code>). |
| <code><span class="nw">mask</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The brain mask (int16, 1 inside). |
| <code><span class="nw">outline</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The surface drawn on the input at its maximum (float32; <code><span class="nw">&#45;o</span></code>). |
| <code><span class="nw">skull</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | An approximate skull (int16; <code><span class="nw">&#45;s</span></code>). |
| <code><span class="nw">mesh</span></code> | <code><span class="nw">Surface</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The brain's surface (<code><span class="nw">&#45;e</span></code>). |
| <code><span class="nw">surfaces</span></code> | <code><span class="nw">BetsurfResult</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The inner skull, outer skull and scalp surfaces, their masks, the skull's mask and the surfaces' outlines (<code><span class="nw">&#34;surfaces&#34;</span></code> and <code><span class="nw">&#34;surfaces&#95;t2&#34;</span></code>: betsurf <code><span class="nw">&#45;o</span> <span class="nw">&#45;m</span> <span class="nw">&#45;s</span></code>). |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `bet2` accepts (`crates/larmorx-fsl/src/cli/bet2.rs`) and the arguments of `lx.fsl.bet` (`python/larmorx/fsl/bet.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| FSL option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#60;input&#62;</span> <span class="nw">&#60;output&#62;</span></code> | <code><span class="nw">image</span></code>; the result |  | outputs <code><span class="nw">&#60;output&#62;</span></code>, <code><span class="nw">&#95;mask</span></code>, <code><span class="nw">&#95;overlay</span></code>, <code><span class="nw">&#95;skull</span></code>, <code><span class="nw">&#95;mesh&#46;vtk</span></code> |
| <code><span class="nw">&#45;f</span> <span class="nw">&#60;f&#62;</span></code> | <code><span class="nw">frac</span></code> | <code><span class="nw">0&#46;5</span></code> | 0 to 1; smaller gives a larger brain<span class="opt-help">FSL: “fractional intensity threshold (0-&gt;1); default=0.5; smaller values give larger brain outline estimates”</span> |
| <code><span class="nw">&#45;g</span> <span class="nw">&#60;g&#62;</span></code> | <code><span class="nw">gradient</span></code> | <code><span class="nw">0&#46;0</span></code> | -1 to 1; positive gives a larger brain at the bottom<span class="opt-help">FSL: “vertical gradient in fractional intensity threshold (-1-&gt;1); default=0; positive values give larger brain outline at bottom, smaller at top”</span> |
| <code><span class="nw">&#45;r</span> <span class="nw">&#60;r&#62;</span></code>, <code><span class="nw">&#45;&#45;radius</span></code> | <code><span class="nw">radius</span></code> | <code><span class="nw">None</span></code> | mm; the initial sphere is half of it<span class="opt-help">FSL: “head radius (mm not voxels); initial surface sphere is set to half of this”</span> |
| <code><span class="nw">&#45;c</span> <span class="nw">&#60;x</span> <span class="nw">y</span> <span class="nw">z&#62;</span></code> | <code><span class="nw">centre</span></code> | <code><span class="nw">None</span></code> | voxels of the file as stored; <code><span class="nw">0</span> <span class="nw">0</span> <span class="nw">0</span></code> is "not given" (the centre of gravity), as in FSL (observed)<span class="opt-help">FSL: “centre-of-gravity (voxels not mm) of initial mesh surface.”</span> |
| <code><span class="nw">&#45;w</span> <span class="nw">&#60;r&#62;</span></code>, <code><span class="nw">&#45;&#45;smooth</span></code> | <code><span class="nw">smoothness</span></code> | <code><span class="nw">1&#46;0</span></code> | bet2 only (<code><span class="nw">bet</span></code> does not pass it)<span class="opt-help">FSL: “smoothness factor; default=1; values smaller than 1 produce more detailed brain surface, values larger than one produce smoother, less detailed surface”</span> |
| <code><span class="nw">&#45;t</span></code>, <code><span class="nw">&#45;&#45;threshold</span></code> | <code><span class="nw">threshold&#61;True</span></code> | <code><span class="nw">False</span></code> | also thresholds the brain and mask<span class="opt-help">FSL: “apply thresholding to segmented brain image and mask”</span> |
| <code><span class="nw">&#45;&#45;ct</span></code> | <code><span class="nw">head&#95;ct&#61;True</span></code> | <code><span class="nw">False</span></code> | bet2 only: the input in Hounsfield units<span class="opt-help">FSL: “treat input as CT image (default is MRI)”</span> |
| <code><span class="nw">&#45;m</span></code>, <code><span class="nw">&#45;&#45;mask</span></code> | <code><span class="nw">mask&#61;True</span></code> | <code><span class="nw">False</span></code> | <span class="opt-help">FSL: “generate binary brain mask”</span> |
| <code><span class="nw">&#45;o</span></code>, <code><span class="nw">&#45;&#45;outline</span></code> | <code><span class="nw">outline&#61;True</span></code> | <code><span class="nw">False</span></code> | <span class="opt-help">FSL: “generate brain surface outline overlaid onto original image”</span> |
| <code><span class="nw">&#45;s</span></code>, <code><span class="nw">&#45;&#45;skull</span></code> | <code><span class="nw">skull&#61;True</span></code> | <code><span class="nw">False</span></code> | <span class="opt-help">FSL: “generate approximate skull image”</span> |
| <code><span class="nw">&#45;n</span></code>, <code><span class="nw">&#45;&#45;nooutput</span></code> | <code><span class="nw">brain&#61;False</span></code> | <code><span class="nw">True</span></code> | <span class="opt-help">FSL: “don't generate segmented brain image output”</span> |
| <code><span class="nw">&#45;e</span></code>, <code><span class="nw">&#45;&#45;mesh</span></code> | <code><span class="nw">mesh&#61;True</span></code> | <code><span class="nw">False</span></code> | VTK; also switches the self-intersection test to the exact one<span class="opt-help">FSL: “generates brain surface as mesh in vtk format”</span> |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> | (command line only) |  | <span class="opt-help">FSL: “switch on diagnostic messages”</span> |
| <code><span class="nw">&#45;&#45;binaryMask</span> <span class="nw">&#60;image&#62;</span></code> | (command line only) |  | <span class="opt-help">FSL: “Generate mesh from existing mask”</span> |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | (command line only) |  | <span class="opt-help">FSL: “displays this help, then exits”</span> |
| <code><span class="nw">&#45;&#45;parameter&#95;d1&#61;</span></code>, <code><span class="nw">&#45;&#45;parameter&#95;d2&#61;</span></code> | (command line only) |  | hidden search depths (7 and 3) |
| <code><span class="nw">&#45;&#45;tanh&#61;correctly&#45;rounded</span></code> (larmorx's own; also <code><span class="nw">&#45;&#45;tanh</span> <span class="nw">correctly&#45;rounded</span></code>, and passed on by <code><span class="nw">bet</span></code>) | <code><span class="nw">tanh&#61;&#34;correctly&#45;rounded&#34;</span></code> | <code><span class="nw">&#34;glibc&#34;</span></code> | the surface's smoothness weight with the correctly rounded <code><span class="nw">tanh</span></code> (CORE-MATH's, <code><span class="nw">larmorx&#95;core&#58;&#58;math&#58;&#58;tanh</span></code>) instead of glibc 2.35's bits, which FSL calls (<code><span class="nw">glibc</span></code>, the default). **GLIBC-06, the user's decision of 2026-10-31**: glibc's bits by default, the correctly rounded one on request (no notice: it is asked for). Where a surface self-intersects and is found again, the last bit can change the result (4 of the standard tier's 13 real images: findings). The clean-room original only (<code><span class="nw">implementation&#61;&#34;replica&#34;</span></code> refuses it; <code><span class="nw">&#34;auto&#34;</span></code> runs the original) |
| <code><span class="nw">FSLOUTPUTTYPE</span></code> | (always NIfTI-1 in Python) |  | on the command line read from the environment, as FSL does (unset: <code><span class="nw">NIFTI&#95;GZ</span></code>, FSL-11) |
| (<code><span class="nw">bet</span></code>'s variations) | <code><span class="nw">variation</span></code>, <code><span class="nw">t2</span></code>, <code><span class="nw">fsl&#95;data</span></code> | <code><span class="nw">variation&#61;None</span></code>, <code><span class="nw">t2&#61;None</span></code>, <code><span class="nw">fsl&#95;data&#61;None</span></code> | <code><span class="nw">bet</span></code> only ([its options](/programs/fsl/bet/#options)) |

### LARMORX's own options {#larmorx-options}

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl bet2 ...`) and are arguments of `lx.fsl.bet`. Each one given wins over the environment variable it replaces.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Replaces <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code>. Threads (0 = all); the result does not depend on it. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | Replaces <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code>. <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica in <code><span class="nw">larmorx&#45;nc</span></code> when it is installed, else the clean-room original (always the original with <code><span class="nw">tanh&#61;&#34;correctly&#45;rounded&#34;</span></code>); <code><span class="nw">&#34;replica&#34;</span></code>: the replica (<code><span class="nw">ReplicaNotFoundError</span></code> without it); <code><span class="nw">&#34;clean&#45;room&#34;</span></code>: the clean-room original (FSL's behaviour within the thresholds of its validation record, <code><span class="nw">docs&#47;validation&#47;fsl&#45;bet&#46;md</span></code>). |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | Replaces <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code>. <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code> (FSL's output); a <code><span class="nw">UpstreamDefectWarning</span></code> names each defect that changed the result. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `T1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

b = lx.fsl.bet("T1w.nii.gz", mesh=True)
b.brain, b.mesh
```

```bash
larmorx fsl bet2 T1w.nii.gz T1w_brain -e
```

## Ports {#ports}

`bet2` has two ports: a replica and a clean room.

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

How `bet2`'s ports compare with FSL 6.0.7.23, case by case: [its evidence](/evidence/fsl-bet/).

## More in the repository {#more}

The API page [docs/api/fsl-bet.md](repo:docs/api/fsl-bet.md) holds what `bet2` shares with the page's other programs:

- [Upstream defects (D13)](repo:docs/api/fsl-bet.md#upstream-defects-d13)
- [Deliberate differences](repo:docs/api/fsl-bet.md#deliberate-differences)
- [Known last-bit differences](repo:docs/api/fsl-bet.md#known-last-bit-differences)
- [Speed](repo:docs/api/fsl-bet.md#speed)
- [Rust](repo:docs/api/fsl-bet.md#rust)
- [The clean-room original (crates/larmorx-fsl)](repo:docs/api/fsl-bet.md#the-clean-room-original-crateslarmorx-fsl)
