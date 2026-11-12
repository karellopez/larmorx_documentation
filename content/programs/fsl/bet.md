---
title: "`bet`"
kicker: "Programs · FSL"
description: "LARMORX reference for FSL 6.0.7.23 `bet`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  command: "larmorx fsl bet"
  python: "lx.fsl.bet"
  api: "docs/api/fsl-bet.md"
  evidence: "/evidence/fsl-bet/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "validated"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    crates/larmorx-cli/src/replica.rs: bdcff4968024a104
    crates/larmorx-core/src/cli.rs: 01fa0015abc1a111
    crates/larmorx-fsl/src/cli/bet.rs: da8dac774b79a854
    docs/api/fsl-bet.md: c59408e34012b405
    python/larmorx/fsl/bet.py: 24b8fa0168bd33f6
    validation/tools.toml: 2502f59cd0e3640d
---

## What it does {#what-it-does}

FSL's `bet` script: `bet2` itself, or one of its variations (below).

## Command line {#command-line}

```text
larmorx fsl bet <input> <output> [options]
```

Everything after `larmorx fsl bet` is the original's command line: the arguments of FSL 6.0.7.23's `bet`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl bet ...
```

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

Returns a `BetResult`: `brain` (float32: the input times the mask; 4D with `"fmri"`), `mask`
(int16, 1 inside), `outline` (float32), `skull` (int16) and `mesh` (a `Surface`: `vertices`
`(n, 3)` in FSL's millimetre coordinates, `triangles` `(m, 3)`), each `None` unless asked for.
`image` is a path (any image FSL reads: NIfTI-1 or -2, single file or pair, gzipped or not,
ANALYZE) or an in-memory image. Without `variation` it runs `bet2`; with `"robust"` (`-R`),
`"small_fov"` (`-Z`) or `"fmri"` (`-F`) the `bet` script; `"eyes"` (`-S`), `"bias"` (`-B`),
`"surfaces"` (`-A`) and `"surfaces_t2"` (`-A2`, with `t2`) run the script with FLIRT,
standard_space_roi, FAST, fslmaths, fslstats and betsurf (the replica since 2026-11-04, the
clean-room original since 2026-11-05: each implementation runs its own programs, in its
process); `"surfaces"` and `"surfaces_t2"` also return betsurf's surfaces
(`BetResult.surfaces`, a `BetsurfResult` with the masks, the skull's mask and the outlines). They
read FSL's standard images (FSL's data under the FSL Licence, which this package never ships)
from `fsl_data` (a directory laid out as `$FSLDIR/data`; the variable `LARMORX_FSL_DATA`
otherwise; when given, the only place looked). Otherwise the original reads them from the copy
`larmorx-nc` installs (as data), else `$FSLDIR/data`, else larmorx's data cache, filled once by
a checksum-verified download of FSL's `fsl-data_standard` package (`larmorx fetch fsl-standard`
fetches it ahead; [fsl-roi.md](repo:docs/api/fsl-roi.md), "FSL's standard images"); the replica reads
`$FSLDIR/data`, else its own copy. An image found nowhere is refused before anything runs
(`RuntimeError` from the original, naming the image and every place looked). The
arguments are checked first (`ValueError`); FSL's
settings are the call's: the outputs are written as NIfTI-1 and read back, `FSLOUTPUTTYPE`,
`FSL_LOAD_NIFTI_EXTENSIONS` and every other `FSL*` variable of the process are never passed, and no
FSL program is looked for on the `PATH` (CLAUDE.md rule 6).

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

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `bet` accepts (`crates/larmorx-fsl/src/cli/bet.rs`) and the arguments of `lx.fsl.bet` (`python/larmorx/fsl/bet.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| FSL option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#60;input&#62;</span> <span class="nw">&#60;output&#62;</span></code> | <code><span class="nw">image</span></code>; the result |  | outputs <code><span class="nw">&#60;output&#62;</span></code>, <code><span class="nw">&#95;mask</span></code>, <code><span class="nw">&#95;overlay</span></code>, <code><span class="nw">&#95;skull</span></code>, <code><span class="nw">&#95;mesh&#46;vtk</span></code> |
| <code><span class="nw">&#45;f</span> <span class="nw">&#60;f&#62;</span></code> | <code><span class="nw">frac</span></code> | <code><span class="nw">0&#46;5</span></code> | 0 to 1; smaller gives a larger brain<span class="opt-help">FSL: “fractional intensity threshold (0-&gt;1); default=0.5; smaller values give larger brain outline estimates”</span> |
| <code><span class="nw">&#45;g</span> <span class="nw">&#60;g&#62;</span></code> | <code><span class="nw">gradient</span></code> | <code><span class="nw">0&#46;0</span></code> | -1 to 1; positive gives a larger brain at the bottom<span class="opt-help">FSL: “vertical gradient in fractional intensity threshold (-1-&gt;1); default=0; positive values give larger brain outline at bottom, smaller at top”</span> |
| <code><span class="nw">&#45;r</span> <span class="nw">&#60;r&#62;</span></code> | <code><span class="nw">radius</span></code> | <code><span class="nw">None</span></code> | mm; the initial sphere is half of it<span class="opt-help">FSL: “head radius (mm not voxels); initial surface sphere is set to half of this”</span> |
| <code><span class="nw">&#45;c</span> <span class="nw">&#60;x</span> <span class="nw">y</span> <span class="nw">z&#62;</span></code> | <code><span class="nw">centre</span></code> | <code><span class="nw">None</span></code> | voxels of the file as stored; <code><span class="nw">0</span> <span class="nw">0</span> <span class="nw">0</span></code> is "not given" (the centre of gravity), as in FSL (observed)<span class="opt-help">FSL: “centre-of-gravity (voxels not mm) of initial mesh surface.”</span> |
| <code><span class="nw">&#45;t</span></code> | <code><span class="nw">threshold&#61;True</span></code> | <code><span class="nw">False</span></code> | also thresholds the brain and mask<span class="opt-help">FSL: “apply thresholding to segmented brain image and mask”</span> |
| <code><span class="nw">&#45;m</span></code> | <code><span class="nw">mask&#61;True</span></code> | <code><span class="nw">False</span></code> | <span class="opt-help">FSL: “generate binary brain mask”</span> |
| <code><span class="nw">&#45;o</span></code> | <code><span class="nw">outline&#61;True</span></code> | <code><span class="nw">False</span></code> | <span class="opt-help">FSL: “generate brain surface outline overlaid onto original image”</span> |
| <code><span class="nw">&#45;s</span></code> | <code><span class="nw">skull&#61;True</span></code> | <code><span class="nw">False</span></code> | <span class="opt-help">FSL: “generate approximate skull image”</span> |
| <code><span class="nw">&#45;n</span></code> | <code><span class="nw">brain&#61;False</span></code> | <code><span class="nw">True</span></code> | <span class="opt-help">FSL: “don't generate segmented brain image output”</span> |
| <code><span class="nw">&#45;e</span></code> | <code><span class="nw">mesh&#61;True</span></code> | <code><span class="nw">False</span></code> | VTK; also switches the self-intersection test to the exact one<span class="opt-help">FSL: “generates brain surface as mesh in .vtk format”</span> |
| <code><span class="nw">&#45;v</span></code> | (command line only) |  | <span class="opt-help">FSL: “verbose (switch on diagnostic messages)”</span> |
| <code><span class="nw">&#45;h</span></code> | (command line only) |  | <span class="opt-help">FSL: “display this help, then exits”</span> |
| <code><span class="nw">&#45;&#45;tanh&#61;correctly&#45;rounded</span></code> (larmorx's own; also <code><span class="nw">&#45;&#45;tanh</span> <span class="nw">correctly&#45;rounded</span></code>, and passed on by <code><span class="nw">bet</span></code>) | <code><span class="nw">tanh&#61;&#34;correctly&#45;rounded&#34;</span></code> | <code><span class="nw">&#34;glibc&#34;</span></code> | the surface's smoothness weight with the correctly rounded <code><span class="nw">tanh</span></code> (CORE-MATH's, <code><span class="nw">larmorx&#95;core&#58;&#58;math&#58;&#58;tanh</span></code>) instead of glibc 2.35's bits, which FSL calls (<code><span class="nw">glibc</span></code>, the default). **GLIBC-06, the user's decision of 2026-10-31**: glibc's bits by default, the correctly rounded one on request (no notice: it is asked for). Where a surface self-intersects and is found again, the last bit can change the result (4 of the standard tier's 13 real images: findings). The clean-room original only (<code><span class="nw">implementation&#61;&#34;replica&#34;</span></code> refuses it; <code><span class="nw">&#34;auto&#34;</span></code> runs the original) |
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

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl bet ...`) and are arguments of `lx.fsl.bet`. Each one given wins over the environment variable it replaces.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Replaces <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code>. Threads (0 = all); the result does not depend on it. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | Replaces <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code>. <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica in <code><span class="nw">larmorx&#45;nc</span></code> when it is installed, else the clean-room original (always the original with <code><span class="nw">tanh&#61;&#34;correctly&#45;rounded&#34;</span></code>); <code><span class="nw">&#34;replica&#34;</span></code>: the replica (<code><span class="nw">ReplicaNotFoundError</span></code> without it); <code><span class="nw">&#34;clean&#45;room&#34;</span></code>: the clean-room original (FSL's behaviour within the thresholds of its validation record, <code><span class="nw">docs&#47;validation&#47;fsl&#45;bet&#46;md</span></code>). |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | Replaces <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code>. <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code> (FSL's output); a <code><span class="nw">UpstreamDefectWarning</span></code> names each defect that changed the result. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `boldref.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# As fMRIPrep calls BET on its BOLD reference.
r = lx.fsl.bet("boldref.nii.gz", frac=0.2, mask=True)
r.brain, r.mask
r.mask.implementation   # Implementation(kind='replica', package='larmorx-nc', ...)
```

```bash
larmorx fsl bet boldref.nii.gz boldref_brain.nii.gz -f 0.20 -m
```

## Ports {#ports}

`bet` has two ports: a replica and a clean room.

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

How `bet`'s ports compare with FSL 6.0.7.23, case by case: [its evidence](/evidence/fsl-bet/).

On the same page, for `bet`: [The standard images the variations read](/evidence/fsl-bet/#data).

## More in the repository {#more}

The API page [docs/api/fsl-bet.md](repo:docs/api/fsl-bet.md) holds what `bet` shares with the page's other programs:

- [Upstream defects (D13)](repo:docs/api/fsl-bet.md#upstream-defects-d13)
- [Deliberate differences](repo:docs/api/fsl-bet.md#deliberate-differences)
- [Known last-bit differences](repo:docs/api/fsl-bet.md#known-last-bit-differences)
- [Speed](repo:docs/api/fsl-bet.md#speed)
- [Rust](repo:docs/api/fsl-bet.md#rust)
- [The clean-room original (crates/larmorx-fsl)](repo:docs/api/fsl-bet.md#the-clean-room-original-crateslarmorx-fsl)
