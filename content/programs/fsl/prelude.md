---
title: "`prelude`"
kicker: "Programs · FSL"
lede: "`prelude` unwraps a phase image (radians) inside a mask."
description: "LARMORX reference for FSL 6.0.7.23 `prelude`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl prelude"
  python: "lx.fsl.prelude"
  api: "docs/api/fsl-prelude.md"
  evidence: "/evidence/fsl-prelude/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "fa776d2ea0a17487"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "34429cb924a382b4"
    crates/larmorx-fsl/src/cli/prelude.rs: "dacb0255f0259db4"
    docs/api/fsl-prelude.md: "597817cae50bb46c"
    python/larmorx/fsl/prelude.py: "7c5ec5282578780c"
    validation/tools.toml: "f0750687390307f1"
---

## What it does {#what-it-does}

The masked phase is split into regions of
similar wrapped phase, which are merged, the best-agreeing pair first, each moved by the whole
number of 2 pi turns that best joins it to its neighbour. The result is the unwrapped phase in
radians, 0 outside the mask. sdcflows (fMRIPrep) runs it on the phase difference of a
phase-difference field map before converting it to a field in Hz: `prelude
--abs=<magnitude> --mask=<mask> --phase=<phase difference> --unwrap=<out>`.

## Command line {#command-line}

```text synopsis
larmorx fsl prelude -c <rawphase> -o <unwrappedphase> [options]
larmorx fsl prelude -p <phasevol> -a <absvol> -o <unwrappedphase> [options]
```

Everything after `larmorx fsl prelude` is the original's command line: the arguments of FSL 6.0.7.23's `prelude`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl prelude ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>prelude</code>'s usage text, as the clean room prints it</summary>

```text
Part of FSL (ID: 2412.6-dirty)
prelude (Version 2.0 in c# minor)
Phase Region Expanding Labeller for Unwrapping Discrete Estimates
Copyright(c) 2001, University of Oxford (Mark Jenkinson)

Usage: 
prelude -c <rawphase> -o <unwrappedphase> [options]
prelude -p <phasevol> -a <absvol> -o <unwrappedphase> [options]

Compulsory arguments (You MUST set one or more of):
	-o,--out,-u,--unwrap	filename for saving the unwrapped phase output

Optional arguments (You may optionally specify one or more of):
	-c,--complex	filename of complex phase input volume
	-a,--abs	filename of absolute input volume
	-p,--phase	filename of raw phase input volume
	-n,--numphasesplit	number of phase partitions to use
	--labelslices	does label processing in 2D (slice at a time)
	-s,--slices	does all processing in 2D (slice at a time)
	-f,--force3D	forces all processing to be full 3D
	-t,--thresh	intensity threshold for masking
	-m,--mask	filename of mask input volume
	--start	first image number to process (default 0)
	--end	final image number to process (default Inf)
	--savemask	filename for saving the mask volume
	-r,--rawphase	filename for saving the raw phase output
	-l,--labels	filename for saving the area labels output
	--removeramps	remove phase ramps during unwrapping
	-v,--verbose	switch on diagnostic messages
	-h,--help	display this message
```

</details>

## Python {#python}

```python
lx.fsl.prelude(
    phase: Any = None,
    magnitude: Any = None,
    *,
    complex_image: Any = None,
    mask: Any = None,
    threshold: float | None = None,
    num_phase_split: int = 8,
    slices: bool = False,
    label_slices: bool = False,
    force_3d: bool = False,
    start: int | None = None,
    end: int | None = None,
    remove_ramps: bool = False,
    save_mask: bool = False,
    save_labels: bool = False,
    save_raw_phase: bool = False,
    verbose: bool = False,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
    n_threads: int = 1,
) -> PreludeResult
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

FSL's `prelude`: the phase of `phase` (radians; a range above 3 pi is refused, values beyond [-pi, pi] are rewrapped first) unwrapped inside a mask, with `magnitude` (`-p`, `-a`), or the phase and magnitude of `complex_image` (`-c`: complex values) instead.

Inputs are paths or in-memory images (an `lx.Image`, a nibabel image, an `(array, affine)`
pair); in-memory images are written to a temporary directory in their own type (uint8, int16,
int32, float32, float64; other types as float32; a complex array as complex64). A run that fails
raises `ReplicaError` (a `RuntimeError`) with
prelude's messages. The function checks its arguments before running anything (`ValueError`):
`complex_image` or `phase` and `magnitude` together, `num_phase_split` of at least 2, `start` and
`end` not negative.

```python
import larmorx as lx

# fMRIPrep's call: a phase difference (radians) with its magnitude and brain mask
res = lx.fsl.prelude("phasediff_rad.nii.gz", "magnitude.nii.gz", mask="mask.nii.gz")
res.unwrapped            # lx.Image, float32, radians

# a complex image, the masks and labels returned, the linear ramps removed during unwrapping
res = lx.fsl.prelude(complex_image="complex.nii.gz", remove_ramps=True,
                     save_mask=True, save_labels=True)
res.mask, res.labels
```

Its result, `PreludeResult`, holds what `prelude` wrote, read back.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">unwrapped</span></code> | <code><span class="nw">Image</span></code> | The unwrapped phase in radians (<code><span class="nw">&#45;&#45;unwrap</span></code>, float32): one volume per processed volume (<code><span class="nw">start</span></code> to <code><span class="nw">end</span></code>), 0 outside the mask. |
| <code><span class="nw">mask</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">save&#95;mask&#61;True</span></code>: the mask each volume was unwrapped in (<code><span class="nw">&#45;&#45;savemask</span></code>, float32, 1 inside), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">labels</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">save&#95;labels&#61;True</span></code>: the regions' labels (<code><span class="nw">&#45;&#45;labels</span></code>, int32; 0 outside the mask), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">raw&#95;phase</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">save&#95;raw&#95;phase&#61;True</span></code>: the wrapped phase as prelude used it (<code><span class="nw">&#45;&#45;rawphase</span></code>: the input phase, every volume, rewrapped to [-pi, pi] where it lay outside), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">stdout</span></code> | <code><span class="nw">str</span></code> | prelude's standard output (its diagnostic messages with <code><span class="nw">verbose&#61;True</span></code>). |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `prelude` accepts (`crates/larmorx-fsl/src/cli/prelude.rs`) and the arguments of `lx.fsl.prelude` (`python/larmorx/fsl/prelude.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">prelude</span></code> option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;p</span></code>, <code><span class="nw">&#45;&#45;phase</span> <span class="nw">&#60;image&#62;</span></code> | <code><span class="nw">phase</span></code> (first argument) | <code><span class="nw">None</span></code> | the wrapped phase, radians; a range (maximum minus minimum) above 3 pi is refused (exit 255), values beyond [-pi, pi] are rewrapped first<span class="opt-help">FSL: “filename of raw phase input volume”</span> |
| <code><span class="nw">&#45;a</span></code>, <code><span class="nw">&#45;&#45;abs</span> <span class="nw">&#60;image&#62;</span></code> | <code><span class="nw">magnitude</span></code> (second argument) | <code><span class="nw">None</span></code> | the magnitude, for the mask; with <code><span class="nw">&#45;p</span></code> only<span class="opt-help">FSL: “filename of absolute input volume”</span> |
| <code><span class="nw">&#45;c</span></code>, <code><span class="nw">&#45;&#45;complex</span> <span class="nw">&#60;image&#62;</span></code> | <code><span class="nw">complex&#95;image</span></code> | <code><span class="nw">None</span></code> | a complex image instead of <code><span class="nw">&#45;p</span></code> and <code><span class="nw">&#45;a</span></code>: its phase and magnitude<span class="opt-help">FSL: “filename of complex phase input volume”</span> |
| <code><span class="nw">&#45;o</span></code>, <code><span class="nw">&#45;&#45;out</span></code>, <code><span class="nw">&#45;u</span></code>, <code><span class="nw">&#45;&#45;unwrap</span> <span class="nw">&#60;name&#62;</span></code> | the result |  | the unwrapped phase (compulsory): the result's <code><span class="nw">unwrapped</span></code><span class="opt-help">FSL: “filename for saving the unwrapped phase output”</span> |
| <code><span class="nw">&#45;m</span></code>, <code><span class="nw">&#45;&#45;mask</span> <span class="nw">&#60;image&#62;</span></code> | <code><span class="nw">mask</span></code> | <code><span class="nw">None</span></code> | the mask (thresholded at 0.5 unless <code><span class="nw">&#45;t</span></code> is given); its last volume serves the volumes beyond it<span class="opt-help">FSL: “filename of mask input volume”</span> |
| <code><span class="nw">&#45;t</span></code>, <code><span class="nw">&#45;&#45;thresh</span> <span class="nw">&#60;value&#62;</span></code> | <code><span class="nw">threshold</span></code> | <code><span class="nw">None</span></code> | the mask's threshold on the magnitude (default: 10 % of the way from the 2nd to the 98th percentile); the largest connected part above it is kept<span class="opt-help">FSL: “intensity threshold for masking”</span> |
| <code><span class="nw">&#45;n</span></code>, <code><span class="nw">&#45;&#45;numphasesplit</span> <span class="nw">&#60;n&#62;</span></code> | <code><span class="nw">num&#95;phase&#95;split</span></code> | <code><span class="nw">8</span></code> | the number of phase intervals the regions are first split into (at least 2)<span class="opt-help">FSL: “number of phase partitions to use”</span> |
| <code><span class="nw">&#45;s</span></code>, <code><span class="nw">&#45;&#45;slices</span></code> | <code><span class="nw">slices&#61;True</span></code> | <code><span class="nw">False</span></code> | labels and unwraps slice by slice, then joins the slices<span class="opt-help">FSL: “does all processing in 2D (slice at a time)”</span> |
| <code><span class="nw">&#45;&#45;labelslices</span></code> | <code><span class="nw">label&#95;slices&#61;True</span></code> | <code><span class="nw">False</span></code> | labels slice by slice (automatic when the image is larger than 64 voxels along x or y), unwraps in 3D<span class="opt-help">FSL: “does label processing in 2D (slice at a time)”</span> |
| <code><span class="nw">&#45;f</span></code>, <code><span class="nw">&#45;&#45;force3D</span></code> | <code><span class="nw">force&#95;3d&#61;True</span></code> | <code><span class="nw">False</span></code> | everything in 3D (overrides <code><span class="nw">&#45;s</span></code>, <code><span class="nw">&#45;&#45;labelslices</span></code> and the automatic 2D labels)<span class="opt-help">FSL: “forces all processing to be full 3D”</span> |
| <code><span class="nw">&#45;&#45;start&#61;&#60;n&#62;</span></code> | <code><span class="nw">start</span></code> | <code><span class="nw">None</span></code> | the first volume processed (from 0)<span class="opt-help">FSL: “first image number to process (default 0)”</span> |
| <code><span class="nw">&#45;&#45;end&#61;&#60;n&#62;</span></code> | <code><span class="nw">end</span></code> | <code><span class="nw">None</span></code> | the last volume processed (default: the last)<span class="opt-help">FSL: “final image number to process (default Inf)”</span> |
| <code><span class="nw">&#45;&#45;removeramps</span></code> | <code><span class="nw">remove&#95;ramps&#61;True</span></code> | <code><span class="nw">False</span></code> | removes the linear phase ramps before unwrapping and restores them after<span class="opt-help">FSL: “remove phase ramps during unwrapping”</span> |
| <code><span class="nw">&#45;&#45;savemask&#61;&#60;name&#62;</span></code> | <code><span class="nw">save&#95;mask&#61;True</span></code> | <code><span class="nw">False</span></code> | the mask used: the result's <code><span class="nw">mask</span></code><span class="opt-help">FSL: “filename for saving the mask volume”</span> |
| <code><span class="nw">&#45;l</span></code>, <code><span class="nw">&#45;&#45;labels</span> <span class="nw">&#60;name&#62;</span></code> | <code><span class="nw">save&#95;labels&#61;True</span></code> | <code><span class="nw">False</span></code> | the regions' labels (int32): the result's <code><span class="nw">labels</span></code><span class="opt-help">FSL: “filename for saving the area labels output”</span> |
| <code><span class="nw">&#45;r</span></code>, <code><span class="nw">&#45;&#45;rawphase</span> <span class="nw">&#60;name&#62;</span></code> | <code><span class="nw">save&#95;raw&#95;phase&#61;True</span></code> | <code><span class="nw">False</span></code> | the wrapped phase as prelude used it (rewrapped where it was outside [-pi, pi]): the result's <code><span class="nw">raw&#95;phase</span></code><span class="opt-help">FSL: “filename for saving the raw phase output”</span> |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> | <code><span class="nw">verbose&#61;True</span></code> | <code><span class="nw">False</span></code> | diagnostic messages: the result's <code><span class="nw">stdout</span></code><span class="opt-help">FSL: “switch on diagnostic messages”</span> |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | command line only |  | the usage (exit 1)<span class="opt-help">FSL: “display this message”</span> |
| <code><span class="nw">FSLOUTPUTTYPE</span></code> | NIfTI, read back |  | the output files' type; the function sets it and never reads the caller's FSL variables |
| <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | threads: the replica's for reading and writing the images; the clean room's also for the mask, the regions, the ramps and the slices of <code><span class="nw">&#45;s</span></code> (the merging itself is sequential: its order is the result); the same bits at any count |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl prelude ...`) and are arguments of `lx.fsl.prelude`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all): the replica's for reading and writing the images, the clean room's also for the mask, the regions, the ramps and the slices; the same bits at any count. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects corrected, or FSL's behaviour (<code><span class="nw">docs&#47;api&#47;fsl&#45;prelude&#46;md</span></code>, "Defects of the original, corrected by default"). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `phasediff.nii.gz` (a phase ramp along x, wrapped into [−pi, pi), on the head's grid), `magnitude.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# A wrapped phase difference (radians) and its magnitude, as fMRIPrep gives them.
res = lx.fsl.prelude("phasediff.nii.gz", "magnitude.nii.gz")
res.unwrapped.shape  # -> (40, 48, 40)
```

```bash
larmorx fsl prelude -p phasediff.nii.gz -a magnitude.nii.gz -o unwrapped
```

## Ports {#ports}

`prelude` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-prelude-replica](repo:docs/validation/fsl-prelude-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-prelude](repo:docs/validation/fsl-prelude.md) |

With `reproduce` both ports give FSL's result bit for bit. By default they agree bit for bit too,
except the phase of a complex image (`-c`): the clean room's arctangent is correctly rounded,
glibc's `atan2f` (FSL's, and the replica's) is not, so a few phases differ in their last bit
(GLIBC-07, named), and the unwrapped phase keeps FSL's whole turns.

- **The replica against FSL 6.0.7.23** (the record `fsl-prelude-replica`, 88 cases: 68 identical
  to FSL, 20 where both refuse alike): bit-identical exit status, messages and files on every
  option, output type and failure case; fMRIPrep 25.2.6's seven prelude calls on four of its runs
  (ds005454, ds002603, ds002422, ds001600) bit-identical to FSL and to fMRIPrep's own outputs.
  larmorx-nc's 15 cases and 4 failures of its cross-platform checks
  (`crates-nc/larmorx-nc-cli/tests/golden.rs`) run on every platform.
- **The clean room against FSL 6.0.7.23** ([its record](repo:docs/validation/fsl-prelude.md), 166 cases:
  138 within its thresholds, 28 refused alike): the replica's cases, the clean room standing in
  for the replica's program; its own cases (every option, image type, NaN input, failure and
  output type) with `reproduce` bit-identical to FSL (headers whole, the pair's extension bytes
  included) and by default bit-identical to the replica's default (GLIBC-07's phases by their
  whole turns); fMRIPrep's seven calls bit-identical to fMRIPrep's own outputs in both modes.
  Its cross-platform checks: `cli.fsl.prelude`, `cli.fsl.prelude.reproduce` and `py.fsl.prelude`
  (`tests/golden/registry.py`), on every platform. Findings:
  [fsl-prelude-original](repo:docs/findings/fsl-prelude-original.md).

**Speed.** The replica merges the regions with FSL's arithmetic in FSL's order, but keeps each
region's neighbours and the candidate merges ordered, instead of scanning every region for every
merge: fMRIPrep's call on ds005454-sub-16 (14,678 regions) takes 0.15 s against FSL's 6.5 s,
with the same bits. The clean room makes the same choices in the same order through an indexed
heap of the candidate merges and a weighted union-find of the regions' turns (each merge costs a
logarithm of the candidates and the neighbours of the region that joins), and runs the linear
parts (the mask, the regions, the ramps, reading and writing) on its threads: the same call
takes 0.069 s on one thread (97 times FSL's speed, 2.5 times the replica's), 0.053 s on 12;
ds002603's 0.135 s against FSL's 28.4 s; a 256 x 256 x 160 map of 153,000 regions 2.0 s (the
replica 9.4 s), with the same bits at every thread count
([benchmarks](repo:docs/benchmarks/fsl-prelude.md)).

FSL is distributed under the FSL Licence (non-commercial use only), so `prelude` has two ports,
a replica and a clean room, in different packages ([licensing](repo:docs/licensing.md)):

- **The replica** is bit-exact: `larmorx-nc fsl prelude`, in the package `larmorx-nc`
  (`crates-nc/`), under the FSL Licence's terms, run as a separate program.
- **The clean room** is `larmorx fsl prelude` in the main package (crate `larmorx-fsl`,
  Apache-2.0, written from `specs/prelude.md` without FSL's source:
  [PROVENANCE](repo:crates/larmorx-fsl/PROVENANCE.md)), run in this process and built for
  speed.

`implementation="auto"` runs the replica when `larmorx-nc` is installed (`pip install
larmorx-nc`), else the clean room; `"replica"` needs `larmorx-nc` (`ReplicaNotFoundError` without
it); `"clean-room"` (`"original"`, 0.1.0rc1's spelling, still works) runs the clean room. The
command line follows `--implementation` (before the family) or `LARMORX_IMPLEMENTATION` the same
way (exit 127 when the replica's program is asked for and not found).

## Evidence {#evidence}

How each of `prelude`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-prelude/).

## More in the repository {#more}

The API page [docs/api/fsl-prelude.md](repo:docs/api/fsl-prelude.md) holds what `prelude` shares with the page's other programs:

- [Defects of the original, corrected by default](repo:docs/api/fsl-prelude.md#defects-of-the-original-corrected-by-default)
- [History](repo:docs/api/fsl-prelude.md#history)
