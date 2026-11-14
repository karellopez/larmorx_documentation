---
title: "`fast`"
kicker: "Programs · FSL"
lede: "`fast` segments a skull-stripped brain image into tissue classes (by default CSF, grey matter and white matter) with a hidden Markov random field fitted by expectation-maximisation."
description: "LARMORX reference for FSL 6.0.7.23 `fast`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl fast"
  python: "lx.fsl.fast"
  api: "docs/api/fsl-fast.md"
  evidence: "/evidence/fsl-fast/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "be80bfe4fac23290"
    crates/larmorx-fsl/src/cli/fast.rs: "935944b0450115d5"
    docs/api/fsl-fast.md: "3f08db5aab5d41e2"
    python/larmorx/fsl/fast.py: "243c08196e31ac1c"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

It also
estimates a bias field and the partial volume of each class in each voxel, on one image or 2 to 8
co-registered channels, with FSL's tissue priors if asked.

## Command line {#command-line}

```text synopsis
larmorx fsl fast [options] file(s)
```

Everything after `larmorx fsl fast` is the original's command line: the arguments of FSL 6.0.7.23's `fast`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl fast ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>fast</code>'s usage text, as the clean room prints it</summary>

```text
Part of FSL (ID: 2412.6-dirty)
FAST 
Copyright(c) 2004-2012, University of Oxford

Usage: 
fast [options] file(s)

Optional arguments (You may optionally specify one or more of):
	-n,--class	number of tissue-type classes; default=3
	-I,--iter	number of main-loop iterations during bias-field removal; default=4
	-l,--lowpass	bias field smoothing extent (FWHM) in mm; default=20
	-t,--type	type of image 1=T1, 2=T2, 3=PD; default=T1
	-f,--fHard	initial segmentation spatial smoothness (during bias field estimation); default=0.02
	-g,--segments	outputs a separate binary image for each tissue type
	-a <standard2input.mat> initialise using priors; you must supply a FLIRT transform
	-A <prior1> <prior2> <prior3>    alternative prior images
	--nopve	turn off PVE (partial volume estimation)
	-b		output estimated bias field
	-B		output bias-corrected image
	-N,--nobias	do not remove bias field
	-S,--channels	number of input images (channels); default 1
	-o,--out	output basename
	-P,--Prior	use priors throughout; you must also set the -a option
	-W,--init	number of segmentation-initialisation iterations; default=15
	-R,--mixel	spatial smoothness for mixeltype; default=0.3
	-O,--fixed	number of main-loop iterations after bias-field removal; default=4
	-H,--Hyper	segmentation spatial smoothness; default=0.1
	-v,--verbose	switch on diagnostic messages
	-h,--help	display this message
	-s,--manualseg <filename> Filename containing intensities
	-p		outputs individual probability maps
```

</details>

## Python {#python}

```python
lx.fsl.fast(
    images: Any,
    *,
    n_classes: int = 3,
    image_type: ImageType = "T1",
    bias_iterations: int = 4,
    bias_lowpass: float = 20.0,
    no_bias: bool = False,
    fixed_iterations: int = 4,
    init_iterations: int = 15,
    initial_smoothness: float = 0.02,
    smoothness: float = 0.1,
    mixel_smoothness: float = 0.3,
    pve: bool = True,
    segments: bool = False,
    probabilities: bool = False,
    restored: bool = False,
    bias_field: bool = False,
    manual_means: Any = None,
    priors_matrix: Any = None,
    priors: Sequence[Any] | None = None,
    priors_throughout: bool = False,
    fsldir: str | os.PathLike[str] | None = None,
    verbose: bool = False,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
) -> FastResult
```

Where `ImageType` is one of `"T1"`, `"T2"`, `"PD"`; `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

Segment `images` into `n_classes` tissue types (FSL's `fast`).

FSL's settings are the call's (CLAUDE.md rule 6): the outputs are NIfTI-1 read back, and no FSL
variable of the process reaches the program. Invalid arguments raise `ValueError` before anything
runs (also the values FAST would use without meaning: FSL-99).

```python
import larmorx as lx

# fMRIPrep's call: fast -I 0 -N -p -g -S 1 <T1w brain>
r = lx.fsl.fast(
    "T1w_brain.nii.gz", bias_iterations=0, no_bias=True, probabilities=True, segments=True
)
csf, gm, wm = r.partial_volumes          # lx.Image each, on the input's grid
labels = r.segmentation.data             # 1 CSF, 2 grey matter, 3 white matter, 0 outside

# The bias field and the corrected image, then a T2w + T1w pair (channel 1 first).
r = lx.fsl.fast("T1w_brain.nii.gz", bias_field=True, restored=True)
r2 = lx.fsl.fast(["T1w_brain.nii.gz", "T2w_brain.nii.gz"], restored=True)
```

Its result, `FastResult`, holds what `fast` wrote, read back (each on the input's grid; channel 1's header).

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">segmentation</span></code> | <code><span class="nw">Image</span></code> | The hard segmentation (<code><span class="nw">&#95;seg</span></code>): each voxel's class, 1 to <code><span class="nw">n&#95;classes</span></code>, 0 outside the mask (int32). |
| <code><span class="nw">segments</span></code> | <code><span class="nw">tuple&#91;Image&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">segments&#61;True</span></code>: one binary image per class (<code><span class="nw">&#95;seg&#95;&#60;n&#62;</span></code>, int32), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">probabilities</span></code> | <code><span class="nw">tuple&#91;Image&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">probabilities&#61;True</span></code>: each class's posterior probability (<code><span class="nw">&#95;prob&#95;&#60;n&#62;</span></code>, float32), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">partial&#95;volumes</span></code> | <code><span class="nw">tuple&#91;Image&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | Each class's partial-volume fraction (<code><span class="nw">&#95;pve&#95;&#60;n&#62;</span></code>, float32); <code><span class="nw">None</span></code> with <code><span class="nw">pve&#61;False</span></code>. |
| <code><span class="nw">pve&#95;segmentation</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The segmentation by largest partial volume (<code><span class="nw">&#95;pveseg</span></code>, int32), or <code><span class="nw">None</span></code>. |
| <code><span class="nw">mixeltype</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | Each voxel's mixel type (<code><span class="nw">&#95;mixeltype</span></code>, int32: 0 to <code><span class="nw">n&#95;classes</span> <span class="nw">&#45;</span> <span class="nw">1</span></code> a pure class, then the mixtures of two classes), or <code><span class="nw">None</span></code>. |
| <code><span class="nw">restored</span></code> | <code><span class="nw">tuple&#91;Image&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">restored&#61;True</span></code>: each channel's bias-corrected image (<code><span class="nw">&#95;restore</span></code> for one channel, <code><span class="nw">&#95;restore&#95;&#60;n&#62;</span></code> for several), in channel order, else <code><span class="nw">None</span></code>. |
| <code><span class="nw">bias&#95;fields</span></code> | <code><span class="nw">tuple&#91;Image&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">bias&#95;field&#61;True</span></code>: each channel's estimated bias field (<code><span class="nw">&#95;bias</span></code>, <code><span class="nw">&#95;bias&#95;&#60;n&#62;</span></code>), in channel order, else <code><span class="nw">None</span></code>. |
| <code><span class="nw">stdout</span></code> | <code><span class="nw">str</span></code> | FAST's standard output (its diagnostic messages with <code><span class="nw">verbose&#61;True</span></code>). |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `fast` accepts (`crates/larmorx-fsl/src/cli/fast.rs`) and the arguments of `lx.fsl.fast` (`python/larmorx/fsl/fast.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">fast</span></code> option | Python | Default | Notes |
|---|---|---|---|
| the last word(s) | <code><span class="nw">images</span></code> |  | one image (path or <code><span class="nw">lx&#46;Image</span></code>), or a list of channels, channel 1 first (the command line names channel 1 **last**: <code><span class="nw">larmorx</span> <span class="nw">fsl</span> <span class="nw">fast</span> <span class="nw">&#45;S</span> <span class="nw">2</span> <span class="nw">&#45;B</span> <span class="nw">&#45;o</span> <span class="nw">out</span> <span class="nw">T2w&#95;brain&#46;nii&#46;gz</span> <span class="nw">T1w&#95;brain&#46;nii&#46;gz</span></code>) |
| <code><span class="nw">&#45;S</span></code>, <code><span class="nw">&#45;&#45;channels</span></code> | <code><span class="nw">images</span></code> |  | the number of channels (default 1): the list's length<span class="opt-help">FSL: “number of input images (channels); default 1”</span> |
| <code><span class="nw">&#45;n</span></code>, <code><span class="nw">&#45;&#45;class</span></code> | <code><span class="nw">n&#95;classes</span></code> | <code><span class="nw">3</span></code> | tissue classes<span class="opt-help">FSL: “number of tissue-type classes; default=3”</span> |
| <code><span class="nw">&#45;t</span></code>, <code><span class="nw">&#45;&#45;type</span></code> | <code><span class="nw">image&#95;type</span></code> | <code><span class="nw">&#34;T1&#34;</span></code> | <code><span class="nw">&#34;T1&#34;</span></code>, <code><span class="nw">&#34;T2&#34;</span></code> (reverses the class order: brightest first), <code><span class="nw">&#34;PD&#34;</span></code>; 1, 2, 3 on the command line<span class="opt-help">FSL: “type of image 1=T1, 2=T2, 3=PD; default=T1”</span> |
| <code><span class="nw">&#45;I</span></code>, <code><span class="nw">&#45;&#45;iter</span></code> | <code><span class="nw">bias&#95;iterations</span></code> | <code><span class="nw">4</span></code> | main-loop iterations with the bias field<span class="opt-help">FSL: “number of main-loop iterations during bias-field removal; default=4”</span> |
| <code><span class="nw">&#45;l</span></code>, <code><span class="nw">&#45;&#45;lowpass</span></code> | <code><span class="nw">bias&#95;lowpass</span></code> | <code><span class="nw">20&#46;0</span></code> | the bias field's smoothing (FWHM, mm)<span class="opt-help">FSL: “bias field smoothing extent (FWHM) in mm; default=20”</span> |
| <code><span class="nw">&#45;N</span></code>, <code><span class="nw">&#45;&#45;nobias</span></code> | <code><span class="nw">no&#95;bias&#61;True</span></code> | <code><span class="nw">False</span></code> | no bias field<span class="opt-help">FSL: “do not remove bias field”</span> |
| <code><span class="nw">&#45;O</span></code>, <code><span class="nw">&#45;&#45;fixed</span></code> | <code><span class="nw">fixed&#95;iterations</span></code> | <code><span class="nw">4</span></code> | main-loop iterations after the bias field (also added to the initialisation's iterations)<span class="opt-help">FSL: “number of main-loop iterations after bias-field removal; default=4”</span> |
| <code><span class="nw">&#45;W</span></code>, <code><span class="nw">&#45;&#45;init</span></code> | <code><span class="nw">init&#95;iterations</span></code> | <code><span class="nw">15</span></code> | initialisation iterations<span class="opt-help">FSL: “number of segmentation-initialisation iterations; default=15”</span> |
| <code><span class="nw">&#45;f</span></code>, <code><span class="nw">&#45;&#45;fHard</span></code> | <code><span class="nw">initial&#95;smoothness</span></code> | <code><span class="nw">0&#46;02</span></code> | the MRF weight while the bias field is estimated<span class="opt-help">FSL: “initial segmentation spatial smoothness (during bias field estimation); default=0.02”</span> |
| <code><span class="nw">&#45;H</span></code>, <code><span class="nw">&#45;&#45;Hyper</span></code> | <code><span class="nw">smoothness</span></code> | <code><span class="nw">0&#46;1</span></code> | the MRF weight afterwards<span class="opt-help">FSL: “segmentation spatial smoothness; default=0.1”</span> |
| <code><span class="nw">&#45;R</span></code>, <code><span class="nw">&#45;&#45;mixel</span></code> | <code><span class="nw">mixel&#95;smoothness</span></code> | <code><span class="nw">0&#46;3</span></code> | the MRF weight of the mixel types (partial volumes)<span class="opt-help">FSL: “spatial smoothness for mixeltype; default=0.3”</span> |
| <code><span class="nw">&#45;&#45;nopve</span></code> | <code><span class="nw">pve&#61;False</span></code> | <code><span class="nw">True</span></code> | no partial volumes<span class="opt-help">FSL: “turn off PVE (partial volume estimation)”</span> |
| <code><span class="nw">&#45;g</span></code>, <code><span class="nw">&#45;&#45;segments</span></code> | <code><span class="nw">segments&#61;True</span></code> | <code><span class="nw">False</span></code> | one binary image per class<span class="opt-help">FSL: “outputs a separate binary image for each tissue type”</span> |
| <code><span class="nw">&#45;p</span></code> | <code><span class="nw">probabilities&#61;True</span></code> | <code><span class="nw">False</span></code> | each class's posterior probability<span class="opt-help">FSL: “outputs individual probability maps”</span> |
| <code><span class="nw">&#45;B</span></code> | <code><span class="nw">restored&#61;True</span></code> | <code><span class="nw">False</span></code> | the bias-corrected image(s)<span class="opt-help">FSL: “output bias-corrected image”</span> |
| <code><span class="nw">&#45;b</span></code> | <code><span class="nw">bias&#95;field&#61;True</span></code> | <code><span class="nw">False</span></code> | the bias field(s)<span class="opt-help">FSL: “output estimated bias field”</span> |
| <code><span class="nw">&#45;s</span></code>, <code><span class="nw">&#45;&#45;manualseg</span></code> | <code><span class="nw">manual&#95;means</span></code> | <code><span class="nw">None</span></code> | the initial class intensities: a file, or <code><span class="nw">n&#95;classes</span></code> numbers (several channels: <code><span class="nw">n&#95;channels</span></code> rows of <code><span class="nw">n&#95;classes</span></code>) |
| <code><span class="nw">&#45;a</span></code> | <code><span class="nw">priors&#95;matrix</span></code> | <code><span class="nw">None</span></code> | the standard-to-input FLIRT matrix (4 x 4 array or file): initialise from tissue priors registered with it |
| <code><span class="nw">&#45;A</span></code> | <code><span class="nw">priors</span></code> | <code><span class="nw">None</span></code> | the CSF, grey- and white-matter priors in standard space (three images); without them FSL's standard priors from <code><span class="nw">fsldir</span></code><span class="opt-help">FSL: “alternative prior images”</span> |
| <code><span class="nw">&#45;P</span></code>, <code><span class="nw">&#45;&#45;Prior</span></code> | <code><span class="nw">priors&#95;throughout&#61;True</span></code> | <code><span class="nw">False</span></code> | use the priors in every iteration (needs <code><span class="nw">priors&#95;matrix</span></code>)<span class="opt-help">FSL: “use priors throughout; you must also set the -a option”</span> |
| <code><span class="nw">&#45;o</span></code>, <code><span class="nw">&#45;&#45;out</span></code> | the result |  | the outputs' basename<span class="opt-help">FSL: “output basename”</span> |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> | <code><span class="nw">verbose&#61;True</span></code> | <code><span class="nw">False</span></code> | FAST's diagnostic messages (in the result's <code><span class="nw">stdout</span></code>)<span class="opt-help">FSL: “switch on diagnostic messages”</span> |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | command line only |  | <span class="opt-help">FSL: “display this message”</span> |
| <code><span class="nw">FSLDIR</span></code> | <code><span class="nw">fsldir</span></code> | <code><span class="nw">None</span></code> | the FSL installation whose <code><span class="nw">data&#47;standard&#47;tissuepriors</span></code> the standard priors come from (needed only for <code><span class="nw">priors&#95;matrix</span></code> without <code><span class="nw">priors</span></code>) |
| <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | threads (0: all); the results do not depend on it (the clean room's: the same bits on any count) |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects as FSL has them |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl fast ...`) and are arguments of `lx.fsl.fast`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all); the results do not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects corrected, or FSL's behaviour (<code><span class="nw">docs&#47;api&#47;fsl&#45;fast&#46;md</span></code>, "Defects of the original, corrected by default"). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `T1w_brain.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# fMRIPrep's call: fast -I 0 -N -p -g -S 1 <T1w brain>
r = lx.fsl.fast(
    "T1w_brain.nii.gz", bias_iterations=0, no_bias=True, probabilities=True, segments=True
)
len(r.partial_volumes)  # -> 3
```

```bash
larmorx fsl fast -I 0 -N -p -g -S 1 T1w_brain.nii.gz
```

## Ports {#ports}

`fast` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-fast-replica](repo:docs/validation/fsl-fast-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-fast](repo:docs/validation/fsl-fast.md) |

**The replica** against FSL 6.0.7.23 itself ([its record](repo:docs/validation/fsl-fast-replica.md), the
standard comparison): fMRIPrep's call bit-identical in three of fMRIPrep's runs (ds000005, an
adult; ds000228, a 3.5-year-old; ds005003, a glioma), every file FAST writes, its standard output
and error; every option, 2 to 8 channels, the priors, the odd inputs and every message, exit
status and failure case of the command line: 59 of 59 compared cases bit-identical, 27 rejected
by both alike, 1 refused where FSL reads past a smaller channel (FSL-104). With `-a`, FSL's FLIRT
is the replica's own, run in the same process (no FSL installation needed when `-A` names the
priors).

**The clean room** against FSL 6.0.7.23 ([its record](repo:docs/validation/fsl-fast.md), the standard
comparison, `specs/fast.md` §11's thresholds, 2026-11-05): 64 of 65 compared cases within the
thresholds, fMRIPrep's three calls included (with `reproduce`, as FSL is built with glibc's
functions, fMRIPrep's calls and every single-channel case FSL's values bit for bit, two to eight
channels FSL's segmentations); 35 rejected by both alike (every abort and message of FSL's,
the lines of standard output an abort loses among them), 2 expected divergences (FSL-104's
refusal, and `multi/s2-manualseg-cycle`, below); the one outside, `multi/s5`, is explained (five
channels with nearly singular covariances, decided by the matrix arithmetic's last bits). Its
default is held to the replica's default (the same corrections): with glibc's functions it is the
replica's default bit for bit on every single-channel case, and with its correctly rounded
functions it stays within the narrow band of FSL-202's corrected variance on one channel
(fMRIPrep's calls: the same labels as the replica's default); several channels have no FSL-202,
so there the two defaults lie FSL's own last-bit band apart (`multi/s3`, `multi/s2-n4`: to every
digit FSL against FSL with correctly rounded maths), and `multi/s2-manualseg-cycle`, whose
defaults both correct FSL-98's cycle, is the expected divergence measured in
[the findings](repo:docs/findings/fsl-fast-clean-room.md). It is built for speed: fMRIPrep's call on the
standard comparison's three T1w brains takes 2.4 to 5.2 s on one thread, 0.4 to 0.9 s on 14 (FSL
22 to 60 s, the replica 15 to 31 s).

FSL is distributed under the FSL Licence (non-commercial use only), so `fast` has two ports, a
replica and a clean room, in different packages ([licensing](repo:docs/licensing.md)):

- **The replica** is bit-exact: `larmorx-nc fsl fast`, in the package `larmorx-nc`
  (`crates-nc/larmorx-nc-fast`), under the FSL Licence's terms, translated from FSL's source.
- **The clean room** is in the main package (crate `larmorx-fsl`, module `fast`, Apache-2.0),
  written from [`specs/fast.md`](repo:specs/fast.md), the FAST paper, FSL's documentation and
  black-box runs of FSL's program ([PROVENANCE](repo:crates/larmorx-fsl/PROVENANCE.md)). It
  segments one channel and several (any number: `-S 9` and more too, which the replica refuses),
  with the tissue priors (`-a` registered by LARMORX's own FLIRT in this process, `-A`, `-P`).

`implementation="auto"` (the default) runs the replica when `larmorx-nc` is installed, else the
clean room; `"replica"` needs `larmorx-nc` (`pip install larmorx-nc`; otherwise
`ReplicaNotFoundError`); `"clean-room"` (`"original"`, 0.1.0rc1's spelling, still works) runs the
clean room. The command line chooses alike (`--implementation` before the family, or
`LARMORX_IMPLEMENTATION`).

## Evidence {#evidence}

How each of `fast`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-fast/).

## More in the repository {#more}

The API page [docs/api/fsl-fast.md](repo:docs/api/fsl-fast.md) holds what `fast` shares with the page's other programs:

- [Defects of the original, corrected by default](repo:docs/api/fsl-fast.md#defects-of-the-original-corrected-by-default)
- [The clean room](repo:docs/api/fsl-fast.md#the-clean-room)
- [Not yet](repo:docs/api/fsl-fast.md#not-yet)
- [History](repo:docs/api/fsl-fast.md#history)
