---
title: "`bet2`"
kicker: "Programs · FSL"
lede: "`bet2` is FSL's brain extraction itself, which the `bet` script runs."
description: "LARMORX reference for FSL 6.0.7.23 `bet2`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl bet2"
  python: "lx.fsl.bet"
  api: "docs/api/fsl-bet.md"
  evidence: "/evidence/fsl-bet/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "validated"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "2e982878694e2b59"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "1b2d6885ad466bdb"
    crates/larmorx-fsl/src/cli/bet2.rs: "533a6b3eac008baf"
    docs/api/fsl-bet.md: "d31d9c8db88492e7"
    python/larmorx/fsl/bet.py: "14e2e5d5c68509eb"
    validation/tools.toml: "ee7483adca513cdc"
---

## What it does {#what-it-does}

It deforms a tessellated
sphere onto the brain's surface in a head image and writes the brain and, on request, its mask,
its outline, an approximate skull and the surface as a mesh.

## Command line {#command-line}

```text synopsis
larmorx fsl bet2 <input_fileroot> <output_fileroot> [options]
```

Everything after `larmorx fsl bet2` is the original's command line: the arguments of FSL 6.0.7.23's `bet2`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl bet2 ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

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
| <code><span class="nw">mesh</span></code> | <code><span class="nw">Surface</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The brain's surface (<code><span class="nw">&#45;e</span></code>): its <code><span class="nw">vertices</span></code> <code><span class="nw">&#40;n&#44;</span> <span class="nw">3&#41;</span></code> in FSL's millimetre coordinates and its <code><span class="nw">triangles</span></code> <code><span class="nw">&#40;m&#44;</span> <span class="nw">3&#41;</span></code>. |
| <code><span class="nw">surfaces</span></code> | <code><span class="nw">BetsurfResult</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The inner skull, outer skull and scalp surfaces, their masks, the skull's mask and the surfaces' outlines (<code><span class="nw">&#34;surfaces&#34;</span></code> and <code><span class="nw">&#34;surfaces&#95;t2&#34;</span></code>: betsurf <code><span class="nw">&#45;o</span> <span class="nw">&#45;m</span> <span class="nw">&#45;s</span></code>). |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `bet2` accepts (`crates/larmorx-fsl/src/cli/bet2.rs`) and the arguments of `lx.fsl.bet` (`python/larmorx/fsl/bet.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| FSL option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#60;input&#62;</span> <span class="nw">&#60;output&#62;</span></code> | <code><span class="nw">image</span></code>; the result |  | outputs <code><span class="nw">&#60;output&#62;</span></code>, <code><span class="nw">&#95;mask</span></code>, <code><span class="nw">&#95;overlay</span></code>, <code><span class="nw">&#95;skull</span></code>, <code><span class="nw">&#95;mesh&#46;vtk</span></code> |
| <code><span class="nw">&#45;f</span> <span class="nw">&#60;f&#62;</span></code> | <code><span class="nw">frac</span></code> | <code><span class="nw">0&#46;5</span></code> | 0 to 1; smaller gives a larger brain<span class="opt-help">FSL: “fractional intensity threshold (0-&gt;1); default=0.5; smaller values give larger brain outline estimates”</span> |
| <code><span class="nw">&#45;g</span> <span class="nw">&#60;g&#62;</span></code> | <code><span class="nw">gradient</span></code> | <code><span class="nw">0&#46;0</span></code> | -1 to 1; positive gives a larger brain at the bottom<span class="opt-help">FSL: “vertical gradient in fractional intensity threshold (-1-&gt;1); default=0; positive values give larger brain outline at bottom, smaller at top”</span> |
| <code><span class="nw">&#45;r</span> <span class="nw">&#60;r&#62;</span></code>, <code><span class="nw">&#45;&#45;radius</span></code> | <code><span class="nw">radius</span></code> | <code><span class="nw">None</span></code> | mm; the initial sphere is half of it<span class="opt-help">FSL: “head radius (mm not voxels); initial surface sphere is set to half of this”</span> |
| <code><span class="nw">&#45;c</span> <span class="nw">&#60;x</span> <span class="nw">y</span> <span class="nw">z&#62;</span></code> | <code><span class="nw">centre</span></code> | <code><span class="nw">None</span></code> | voxels of the file as stored; <code><span class="nw">0</span> <span class="nw">0</span> <span class="nw">0</span></code> is "not given" (the centre of gravity), as in FSL<span class="opt-help">FSL: “centre-of-gravity (voxels not mm) of initial mesh surface.”</span> |
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
| <code><span class="nw">&#45;&#45;tanh&#61;correctly&#45;rounded</span></code> (LARMORX's own option; also <code><span class="nw">&#45;&#45;tanh</span> <span class="nw">correctly&#45;rounded</span></code>, and passed on by <code><span class="nw">bet</span></code>) | <code><span class="nw">tanh&#61;&#34;correctly&#45;rounded&#34;</span></code> | <code><span class="nw">&#34;glibc&#34;</span></code> | computes the surface's smoothness weight with the correctly rounded <code><span class="nw">tanh</span></code> (CORE-MATH's, <code><span class="nw">larmorx&#95;core&#58;&#58;math&#58;&#58;tanh</span></code>) instead of glibc 2.35's, which FSL calls and which is the default (<code><span class="nw">glibc</span></code>; decision GLIBC-06). No notice: it is asked for. Where a surface self-intersects and is found again, the last bit can change the result (4 of the 13 real images of the clean room's standard comparison: [its findings](repo:docs/findings/fsl-bet-clean-room.md)). Clean room only: <code><span class="nw">implementation&#61;&#34;replica&#34;</span></code> refuses it, and <code><span class="nw">&#34;auto&#34;</span></code> runs the clean room |
| <code><span class="nw">FSLOUTPUTTYPE</span></code> | (always NIfTI-1 in Python) |  | on the command line read from the environment, as FSL does (unset: <code><span class="nw">NIFTI&#95;GZ</span></code>, FSL-11) |
| (<code><span class="nw">bet</span></code>'s variations) | <code><span class="nw">variation</span></code>, <code><span class="nw">t2</span></code>, <code><span class="nw">fsl&#95;data</span></code> | <code><span class="nw">variation&#61;None</span></code>, <code><span class="nw">t2&#61;None</span></code>, <code><span class="nw">fsl&#95;data&#61;None</span></code> | <code><span class="nw">bet</span></code> only ([its options](/programs/fsl/bet/#options)) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl bet2 ...`) and are arguments of `lx.fsl.bet`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all); the result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica in <code><span class="nw">larmorx&#45;nc</span></code> when it is installed, else the clean room (always the clean room with <code><span class="nw">tanh&#61;&#34;correctly&#45;rounded&#34;</span></code>); <code><span class="nw">&#34;replica&#34;</span></code>: the replica (<code><span class="nw">ReplicaNotFoundError</span></code> without it); <code><span class="nw">&#34;clean&#45;room&#34;</span></code>: the clean room (FSL's behaviour within the thresholds of its validation record, <code><span class="nw">docs&#47;validation&#47;fsl&#45;bet&#46;md</span></code>). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code> (FSL's output); an <code><span class="nw">UpstreamDefectWarning</span></code> names each defect that changed the result. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

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
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | validated | [fsl-bet-replica](repo:docs/validation/fsl-bet-replica.md), [fsl-bet-replica-full](repo:docs/validation/fsl-bet-replica-full.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-bet](repo:docs/validation/fsl-bet.md) |

The replica gives FSL 6.0.7.23's exit status, messages and files byte for byte in 201 of the 263
cases of its record, which holds `bet`, `bet2`, `betsurf`, `standard_space_roi` and `fslroi`; 47
more are rejected by both. The clean room's record holds the same programs. Of its 380 brains,
masks and outlines (`betsurf`'s counted apart), 378 are FSL's bit for bit; the two others are
`bet -B`'s. 11 of 11 meshes have FSL's vertices to the file's 6 decimals.

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

How each of `bet2`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-bet/).

## More in the repository {#more}

The API page [docs/api/fsl-bet.md](repo:docs/api/fsl-bet.md) holds what `bet2` shares with the page's other programs:

- [The records](repo:docs/api/fsl-bet.md#the-records)
- [Defects of the original, corrected by default](repo:docs/api/fsl-bet.md#defects-of-the-original-corrected-by-default)
- [Deliberate differences](repo:docs/api/fsl-bet.md#deliberate-differences)
- [Known last-bit differences](repo:docs/api/fsl-bet.md#known-last-bit-differences)
- [Speed](repo:docs/api/fsl-bet.md#speed)
- [Rust](repo:docs/api/fsl-bet.md#rust)
- [The clean room (crates/larmorx-fsl)](repo:docs/api/fsl-bet.md#the-clean-room-crateslarmorx-fsl)
- [History](repo:docs/api/fsl-bet.md#history)
