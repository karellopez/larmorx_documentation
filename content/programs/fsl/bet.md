---
title: "`bet`"
kicker: "Programs · FSL"
lede: "`bet` finds the brain in a head image."
description: "LARMORX reference for FSL 6.0.7.23 `bet`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl bet"
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
    crates/larmorx-core/src/defects.rs: "54f1863ded1d5cef"
    crates/larmorx-fsl/src/cli/bet.rs: "da8dac774b79a854"
    docs/api/fsl-bet.md: "2d69785aafd8d362"
    python/larmorx/fsl/bet.py: "f3c4fc349d3092b9"
    validation/tools.toml: "2502f59cd0e3640d"
---

## What it does {#what-it-does}

`bet` finds the brain in a head image. It writes the brain and, on request, its mask, its
outline, an approximate skull and the brain's surface as a mesh. It runs FSL's brain extraction,
`bet2`, alone or inside one of seven variations (below).

## Command line {#command-line}

```text synopsis
larmorx fsl bet <input> <output> [options]
```

Everything after `larmorx fsl bet` is the original's command line: the arguments of FSL 6.0.7.23's `bet`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl bet ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>bet</code>'s usage text, as the clean room prints it</summary>

```text
Usage:    bet <input> <output> [options]

Main bet2 options:
  -o          generate brain surface outline overlaid onto original image
  -m          generate binary brain mask
  -s          generate approximate skull image
  -n          don't generate segmented brain image output
  -f <f>      fractional intensity threshold (0->1); default=0.5; smaller values give larger brain outline estimates
  -g <g>      vertical gradient in fractional intensity threshold (-1->1); default=0; positive values give larger brain outline at bottom, smaller at top
  -r <r>      head radius (mm not voxels); initial surface sphere is set to half of this
  -c <x y z>  centre-of-gravity (voxels not mm) of initial mesh surface.
  -t          apply thresholding to segmented brain image and mask
  -e          generates brain surface as mesh in .vtk format

Variations on default bet2 functionality (mutually exclusive options):
  (default)   just run bet2
  -R          robust brain centre estimation (iterates BET several times)
  -S          eye & optic nerve cleanup (can be useful in SIENA - disables -o option)
  -B          bias field & neck cleanup (can be useful in SIENA)
  -Z          improve BET if FOV is very small in Z (by temporarily padding end slices)
  -F          apply to 4D FMRI data (uses -f 0.3 and dilates brain mask slightly)
  -A          run bet2 and then betsurf to get additional skull and scalp surfaces (includes registrations)
  -A2 <T2>    as with -A, when also feeding in non-brain-extracted T2 (includes registrations)

Miscellaneous options:
  -v          verbose (switch on diagnostic messages)
  -h          display this help, then exits
  -d          debug (don't delete temporary intermediate images)
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

`image` is a path (any image FSL reads: NIfTI-1 or -2, single file or pair, gzipped or not,
ANALYZE) or an in-memory image. Without `variation` it runs `bet2`. With `"robust"` (`-R`),
`"small_fov"` (`-Z`) or `"fmri"` (`-F`) it runs the `bet` script. `"eyes"` (`-S`), `"bias"`
(`-B`), `"surfaces"` (`-A`) and `"surfaces_t2"` (`-A2`, with `t2`) run the script with FLIRT,
standard_space_roi, FAST, fslmaths, fslstats and betsurf; each port runs its own copies of those
programs, in its own process. `"surfaces"` and `"surfaces_t2"` also return betsurf's surfaces
(`BetResult.surfaces`, a `BetsurfResult` with the masks, the skull's mask and the outlines).

These four read FSL's standard images, which are FSL's data under the FSL Licence and which this
package never ships. They come from `fsl_data` (a directory laid out as `$FSLDIR/data`), else from
the variable `LARMORX_FSL_DATA`; when given, that is the only place looked. Otherwise the clean
room reads them from the copy `larmorx-nc` installs (as data), else `$FSLDIR/data`, else
larmorx's data cache, filled once by a checksum-verified download of FSL's `fsl-data_standard`
package (`larmorx fetch fsl-standard` fetches it ahead; [fsl-roi.md](repo:docs/api/fsl-roi.md), "FSL's standard
images"). The replica reads `$FSLDIR/data`, else its own copy. An image found nowhere is refused
before anything runs, naming the image and every place looked (a `RuntimeError` from the clean
room).

The arguments are checked first (`ValueError`). FSL's settings belong to the call: the outputs are
written as NIfTI-1 and read back; `FSLOUTPUTTYPE`, `FSL_LOAD_NIFTI_EXTENSIONS` and every other
`FSL*` variable of the process are never passed; and no FSL program is looked for on the `PATH`.

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

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `bet` accepts (`crates/larmorx-fsl/src/cli/bet.rs`) and the arguments of `lx.fsl.bet` (`python/larmorx/fsl/bet.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| FSL option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#60;input&#62;</span> <span class="nw">&#60;output&#62;</span></code> | <code><span class="nw">image</span></code>; the result |  | outputs <code><span class="nw">&#60;output&#62;</span></code>, <code><span class="nw">&#95;mask</span></code>, <code><span class="nw">&#95;overlay</span></code>, <code><span class="nw">&#95;skull</span></code>, <code><span class="nw">&#95;mesh&#46;vtk</span></code> |
| <code><span class="nw">&#45;f</span> <span class="nw">&#60;f&#62;</span></code> | <code><span class="nw">frac</span></code> | <code><span class="nw">0&#46;5</span></code> | 0 to 1; smaller gives a larger brain<span class="opt-help">FSL: “fractional intensity threshold (0-&gt;1); default=0.5; smaller values give larger brain outline estimates”</span> |
| <code><span class="nw">&#45;g</span> <span class="nw">&#60;g&#62;</span></code> | <code><span class="nw">gradient</span></code> | <code><span class="nw">0&#46;0</span></code> | -1 to 1; positive gives a larger brain at the bottom<span class="opt-help">FSL: “vertical gradient in fractional intensity threshold (-1-&gt;1); default=0; positive values give larger brain outline at bottom, smaller at top”</span> |
| <code><span class="nw">&#45;r</span> <span class="nw">&#60;r&#62;</span></code> | <code><span class="nw">radius</span></code> | <code><span class="nw">None</span></code> | mm; the initial sphere is half of it<span class="opt-help">FSL: “head radius (mm not voxels); initial surface sphere is set to half of this”</span> |
| <code><span class="nw">&#45;c</span> <span class="nw">&#60;x</span> <span class="nw">y</span> <span class="nw">z&#62;</span></code> | <code><span class="nw">centre</span></code> | <code><span class="nw">None</span></code> | voxels of the file as stored; <code><span class="nw">0</span> <span class="nw">0</span> <span class="nw">0</span></code> is "not given" (the centre of gravity), as in FSL<span class="opt-help">FSL: “centre-of-gravity (voxels not mm) of initial mesh surface.”</span> |
| <code><span class="nw">&#45;t</span></code> | <code><span class="nw">threshold&#61;True</span></code> | <code><span class="nw">False</span></code> | also thresholds the brain and mask<span class="opt-help">FSL: “apply thresholding to segmented brain image and mask”</span> |
| <code><span class="nw">&#45;m</span></code> | <code><span class="nw">mask&#61;True</span></code> | <code><span class="nw">False</span></code> | <span class="opt-help">FSL: “generate binary brain mask”</span> |
| <code><span class="nw">&#45;o</span></code> | <code><span class="nw">outline&#61;True</span></code> | <code><span class="nw">False</span></code> | <span class="opt-help">FSL: “generate brain surface outline overlaid onto original image”</span> |
| <code><span class="nw">&#45;s</span></code> | <code><span class="nw">skull&#61;True</span></code> | <code><span class="nw">False</span></code> | <span class="opt-help">FSL: “generate approximate skull image”</span> |
| <code><span class="nw">&#45;n</span></code> | <code><span class="nw">brain&#61;False</span></code> | <code><span class="nw">True</span></code> | <span class="opt-help">FSL: “don't generate segmented brain image output”</span> |
| <code><span class="nw">&#45;e</span></code> | <code><span class="nw">mesh&#61;True</span></code> | <code><span class="nw">False</span></code> | VTK; also switches the self-intersection test to the exact one<span class="opt-help">FSL: “generates brain surface as mesh in .vtk format”</span> |
| <code><span class="nw">&#45;v</span></code> | (command line only) |  | <span class="opt-help">FSL: “verbose (switch on diagnostic messages)”</span> |
| <code><span class="nw">&#45;h</span></code> | (command line only) |  | <span class="opt-help">FSL: “display this help, then exits”</span> |
| <code><span class="nw">&#45;&#45;tanh&#61;correctly&#45;rounded</span></code> (LARMORX's own option; also <code><span class="nw">&#45;&#45;tanh</span> <span class="nw">correctly&#45;rounded</span></code>, and passed on by <code><span class="nw">bet</span></code>) | <code><span class="nw">tanh&#61;&#34;correctly&#45;rounded&#34;</span></code> | <code><span class="nw">&#34;glibc&#34;</span></code> | computes the surface's smoothness weight with the correctly rounded <code><span class="nw">tanh</span></code> (CORE-MATH's, <code><span class="nw">larmorx&#95;core&#58;&#58;math&#58;&#58;tanh</span></code>) instead of glibc 2.35's, which FSL calls and which is the default (<code><span class="nw">glibc</span></code>; decision GLIBC-06). No notice: it is asked for. Where a surface self-intersects and is found again, the last bit can change the result (4 of the 13 real images of the clean room's standard comparison: [its findings](repo:docs/findings/fsl-bet-original.md)). Clean room only: <code><span class="nw">implementation&#61;&#34;replica&#34;</span></code> refuses it, and <code><span class="nw">&#34;auto&#34;</span></code> runs the clean room |
| (<code><span class="nw">bet2</span></code>'s <code><span class="nw">&#45;w</span></code>) | <code><span class="nw">smoothness</span></code> | <code><span class="nw">1&#46;0</span></code> | bet2 only (<code><span class="nw">bet</span></code> does not pass it) |
| (<code><span class="nw">bet2</span></code>'s <code><span class="nw">&#45;&#45;ct</span></code>) | <code><span class="nw">head&#95;ct&#61;True</span></code> | <code><span class="nw">False</span></code> | bet2 only: the input in Hounsfield units |
| <code><span class="nw">LARMORX&#95;FSL&#95;DATA</span></code> | <code><span class="nw">fsl&#95;data</span></code> | <code><span class="nw">None</span></code> | where <code><span class="nw">&#45;S</span></code>, <code><span class="nw">&#45;B</span></code>, <code><span class="nw">&#45;A</span></code> and <code><span class="nw">&#45;A2</span></code> read FSL's standard images ([<code><span class="nw">bet</span></code>'s Python call](/programs/fsl/bet/#python)) |
| <code><span class="nw">FSLOUTPUTTYPE</span></code> | (always NIfTI-1 in Python) |  | on the command line read from the environment, as FSL does (unset: <code><span class="nw">NIFTI&#95;GZ</span></code>, FSL-11) |

| <code><span class="nw">bet</span></code> option | Python <code><span class="nw">variation</span></code> | What it does |
|---|---|---|
| (none) | <code><span class="nw">None</span></code> | bet2 |
| <code><span class="nw">&#45;R</span></code> | <code><span class="nw">&#34;robust&#34;</span></code> | bet2 again from the brain's centre until it moves less than a voxel (at most 11 runs); <code><span class="nw">&#45;n</span></code> ignored<span class="opt-help">FSL: “robust brain centre estimation (iterates BET several times)”</span> |
| <code><span class="nw">&#45;Z</span></code> | <code><span class="nw">&#34;small&#95;fov&#34;</span></code> | pads the image to 100 mm in z with copies of its end slices, crops back (FSL-45)<span class="opt-help">FSL: “improve BET if FOV is very small in Z (by temporarily padding end slices)”</span> |
| <code><span class="nw">&#45;F</span></code> | <code><span class="nw">&#34;fmri&#34;</span></code> | the first volume's mask (<code><span class="nw">&#45;f</span> <span class="nw">0&#46;3</span></code>, then the user's <code><span class="nw">&#45;f</span></code>), dilated, applied to every volume<span class="opt-help">FSL: “apply to 4D FMRI data (uses -f 0.3 and dilates brain mask slightly)”</span> |
| <code><span class="nw">&#45;S</span></code> | <code><span class="nw">&#34;eyes&#34;</span></code> | SIENA's eye and optic nerve cleanup: <code><span class="nw">bet2</span> <span class="nw">&#45;s</span></code>; <code><span class="nw">standard&#95;space&#95;roi</span> <span class="nw">&#45;b</span> <span class="nw">&#45;d</span></code> and <code><span class="nw">bet2</span> <span class="nw">&#45;n</span> <span class="nw">&#45;m</span> <span class="nw">&#45;f</span> <span class="nw">0&#46;4</span></code> on its result; MNI152's eye mask taken into the input (FLIRT <code><span class="nw">&#45;applyxfm</span></code> through standard_space_roi's inverse matrix), dilated (<code><span class="nw">&#45;dilF</span></code>, 7 more in 2D) and removed from the brain mask, the premask's brain added; what is brighter than 3.5 standard deviations above the brain's mean (<code><span class="nw">fslstats</span> <span class="nw">&#45;M</span></code>, <code><span class="nw">&#45;S</span></code>, GNU <code><span class="nw">dc</span></code>: FSL-216) removed with a little morphology; the mask (<code><span class="nw">&#95;mask</span></code>) and the skull without the eyes (<code><span class="nw">&#95;skull</span></code>) always written; no outline or mesh (<code><span class="nw">&#45;o</span></code>, <code><span class="nw">&#45;e</span></code> only in its temporary run); with <code><span class="nw">&#45;n</span></code> it fails (<code><span class="nw">brain&#61;False</span></code> refused)<span class="opt-help">FSL: “eye &amp; optic nerve cleanup (can be useful in SIENA - disables -o option)”</span> |
| <code><span class="nw">&#45;B</span></code> | <code><span class="nw">&#34;bias&#34;</span></code> | SIENA's bias field and neck cleanup: <code><span class="nw">standard&#95;space&#95;roi</span> <span class="nw">&#45;b</span> <span class="nw">&#45;d</span></code>, FAST's bias field (<code><span class="nw">fast</span> <span class="nw">&#45;b</span></code>, its messages discarded), the input divided by it; with <code><span class="nw">&#45;s</span></code> the skull from <code><span class="nw">standard&#95;space&#95;roi</span> <span class="nw">&#45;maskFOV</span> <span class="nw">&#45;roiNONE</span> <span class="nw">&#45;d</span></code> and <code><span class="nw">bet2</span></code>, moved by fslpy's <code><span class="nw">immv</span></code> (and <code><span class="nw">&#45;s</span></code> removed from the options through <code><span class="nw">echo</span></code>: FSL-63); <code><span class="nw">standard&#95;space&#95;roi</span> <span class="nw">&#45;b</span> <span class="nw">&#45;d</span></code> again and <code><span class="nw">bet</span> <span class="nw">&#45;m</span> <span class="nw">&#45;R</span> <span class="nw">&#45;d</span></code> on its result (the brain and mask always written: <code><span class="nw">&#45;R</span></code> removes <code><span class="nw">&#45;n</span></code>)<span class="opt-help">FSL: “bias field &amp; neck cleanup (can be useful in SIENA)”</span> |
| <code><span class="nw">&#45;A</span></code> | <code><span class="nw">&#34;surfaces&#34;</span></code> | FLIRT to <code><span class="nw">MNI152&#95;T1&#95;2mm</span></code> (the matrix), <code><span class="nw">bet2</span> <span class="nw">&#45;e</span></code>, <code><span class="nw">betsurf</span> <span class="nw">&#45;&#45;t1only</span> <span class="nw">&#45;o</span> <span class="nw">&#45;m</span> <span class="nw">&#45;s</span></code>: the brain, its mesh, the three surfaces, their masks and outlines, the skull's mask<span class="opt-help">FSL: “run bet2 and then betsurf to get additional skull and scalp surfaces (includes registrations)”</span> |
| <code><span class="nw">&#45;A2</span> <span class="nw">&#60;T2&#62;</span></code> | <code><span class="nw">&#34;surfaces&#95;t2&#34;</span></code>, <code><span class="nw">t2</span></code> | the T2 registered to the input by FLIRT (<code><span class="nw">&#45;interp</span> <span class="nw">sinc</span></code>), then as <code><span class="nw">&#45;A</span></code> with <code><span class="nw">betsurf</span> <span class="nw">&#45;o</span> <span class="nw">&#45;m</span> <span class="nw">&#45;s</span></code> on the registered T2<span class="opt-help">FSL: “as with -A, when also feeding in non-brain-extracted T2 (includes registrations)”</span> |
| (the last of <code><span class="nw">&#45;R</span></code>, <code><span class="nw">&#45;S</span></code>, <code><span class="nw">&#45;Z</span></code>, <code><span class="nw">&#45;F</span></code>, <code><span class="nw">&#45;A</span></code>, <code><span class="nw">&#45;A2</span></code>, <code><span class="nw">&#45;B</span></code> given) |  | the variation run |
| <code><span class="nw">&#45;d</span></code> | (command line only) | keeps the temporary files<span class="opt-help">FSL: “debug (don't delete temporary intermediate images)”</span> |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl bet ...`) and are arguments of `lx.fsl.bet`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all); the result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica in <code><span class="nw">larmorx&#45;nc</span></code> when it is installed, else the clean room (always the clean room with <code><span class="nw">tanh&#61;&#34;correctly&#45;rounded&#34;</span></code>); <code><span class="nw">&#34;replica&#34;</span></code>: the replica (<code><span class="nw">ReplicaNotFoundError</span></code> without it); <code><span class="nw">&#34;clean&#45;room&#34;</span></code>: the clean room (FSL's behaviour within the thresholds of its validation record, <code><span class="nw">docs&#47;validation&#47;fsl&#45;bet&#46;md</span></code>). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code> (FSL's output); a <code><span class="nw">UpstreamDefectWarning</span></code> names each defect that changed the result. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `boldref.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# As fMRIPrep calls BET on its BOLD reference.
r = lx.fsl.bet("boldref.nii.gz", frac=0.2, mask=True)
r.brain, r.mask
# The port that ran: the clean room of larmorx, or the replica once larmorx-nc is installed.
r.mask.implementation

# The same call, the clean room chosen.
c = lx.fsl.bet("boldref.nii.gz", frac=0.2, mask=True, implementation="clean-room")
c.mask.implementation.kind  # -> 'clean-room'
```

```bash
larmorx fsl bet boldref.nii.gz boldref_brain.nii.gz -f 0.20 -m
```

## Ports {#ports}

`bet` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | validated | [fsl-bet-replica](repo:docs/validation/fsl-bet-replica.md), [fsl-bet-replica-full](repo:docs/validation/fsl-bet-replica-full.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-bet](repo:docs/validation/fsl-bet.md) |

The replica gives FSL 6.0.7.23's exit status, messages and files byte for byte in 201 of the 263
cases of its record, which holds `bet`, `bet2` and `betsurf`; 47 more are rejected by both. The
clean room is within the thresholds in 198 of its 200 compared cases. One of the two others is
`bet`'s: a 3.5-year-old's `bet -B`, whose mask has a Dice coefficient of 0.9983 and a boundary
distance of 1.0 voxel at the 95th percentile but 2.24 voxels at most, where the threshold is 2.

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

How each of `bet`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-bet/).

On the same page, for `bet`: [The standard images the variations read](/evidence/fsl-bet/#data).

## More in the repository {#more}

The API page [docs/api/fsl-bet.md](repo:docs/api/fsl-bet.md) holds what `bet` shares with the page's other programs:

- [The records](repo:docs/api/fsl-bet.md#the-records)
- [Defects of the original, corrected by default](repo:docs/api/fsl-bet.md#defects-of-the-original-corrected-by-default)
- [Deliberate differences](repo:docs/api/fsl-bet.md#deliberate-differences)
- [Known last-bit differences](repo:docs/api/fsl-bet.md#known-last-bit-differences)
- [Speed](repo:docs/api/fsl-bet.md#speed)
- [Rust](repo:docs/api/fsl-bet.md#rust)
- [The clean room (crates/larmorx-fsl)](repo:docs/api/fsl-bet.md#the-clean-room-crateslarmorx-fsl)
- [History](repo:docs/api/fsl-bet.md#history)
