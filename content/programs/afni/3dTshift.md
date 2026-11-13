---
title: "`3dTshift`"
kicker: "Programs · AFNI"
lede: "`3dTshift` corrects slice timing: it aligns every slice of a 4D series to one time origin."
description: "LARMORX reference for AFNI 26.3.05 `3dTshift`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: afni
  original: "AFNI 26.3.05"
  software: "AFNI"
  command: "larmorx afni 3dTshift"
  python: "lx.afni.tshift"
  api: "docs/api/afni-tshift.md"
  evidence: "/evidence/afni-tshift/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0 AND CC-BY-4.0", status: "validated"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-afni/src/cli/tshift.rs: "ed663773458414fa"
    crates/larmorx-afni/src/settings.rs: "8b2560253b92f512"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "035dcd92e164879c"
    docs/api/afni-tshift.md: "3e7ceb5513115003"
    python/larmorx/afni/tshift.py: "109d8c664b0d6d2f"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

Each
voxel's time series is detrended (a least-squares line), shifted in time so that its slice
refers to `tzero`, clipped to its own range, and given its trend back. The output at time point
`n` estimates the signal at `n·TR + tzero`.

## Command line {#command-line}

```text synopsis
larmorx afni 3dTshift [options] dataset
```

Everything after `larmorx afni 3dTshift` is the original's command line: the arguments of AFNI 26.3.05's `3dTshift`, as AFNI takes them. LARMORX's own options stand between `larmorx` and the family `afni`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        afni 3dTshift ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>3dTshift</code>'s usage text, as the clean room prints it</summary>

```text
Usage: 3dTshift [options] dataset   (larmorx, clean-room re-implementation of AFNI 3dTshift)

Shifts voxel time series so that all slices are aligned to the same temporal origin:
detrend -> interpolate -> retrend. The dataset is a 4D NIfTI file.

Options (they must come before the dataset):
  -verbose        print progress messages
  -TR ddd         use ddd as the TR (suffix s or ms; ms switches every time to milliseconds)
  -tzero zzz      align each slice to time offset zzz (default: the mean slice offset)
  -slice nnn      align each slice to the offset of slice nnn (wins over -tzero)
  -prefix ppp     output file name: must end in .nii or .nii.gz; an existing file is an error
                  unless -overwrite or AFNI_DECONFLICT says otherwise
  -ignore ii      leave the first ii time points out of the detrending and shifting
  -rlt            do not add the trend back after shifting
  -rlt+           add back only the intercept of the trend
  -no_detrend     remove (and restore) only the mean; needs a non-Fourier method before it
  -Fourier -linear -cubic -quintic -heptic -wsinc5 -wsinc9
                  interpolation method (default -Fourier)
  -tpattern ttt   slice timing: alt+z altplus alt+z2 alt-z altminus alt-z2 seq+z seqplus
                  seq-z seqminus zero simult, or @file / '@1D: ...' with one offset per slice
                  (default: the slice timing in the NIfTI header)

AFNI's global options may stand anywhere: -overwrite, -Dname=value (sets one of AFNI's
environment variables for this run), -ok_1D_text, -skip_afnirc.
```

</details>

## Python {#python}

```python
lx.afni.tshift(
    image: Any,
    *,
    slice_times: Sequence[float] | str,
    tr: float | None = None,
    tzero: float | None = None,
    slice: int | None = None,
    ignore: int = 0,
    method: Method = "fourier",
    restore: RestoreName = "trend",
    detrend: bool = True,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
    afni_settings: Mapping[str, str] | None = None,
) -> Image
```

Where `Method` is one of `"fourier"`, `"linear"`, `"cubic"`, `"quintic"`, `"heptic"`, `"wsinc5"`, `"wsinc9"`; `RestoreName` is one of `"trend"`, `"none"`, `"intercept"`; `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

Align every slice of a 4D image to one time origin (AFNI's `3dTshift`).

Returns an `lx.Image` with the header `3dTshift` writes: `pixdim[4]` = TR (seconds),
`toffset` = `tzero`, no slice timing, millimetres and seconds. Data keep AFNI's storage type
(`uint8`, `int16` or `float32`); when the output has a brick factor (`scl_slope`), the data
are the scaled values, as `lx.load` returns them. `img.implementation` says which port computed
it.

**Files and in-memory images.** Paths are read with AFNI's rules
([How AFNI reads and writes NIfTI](repo:docs/api/afni-tshift.md#how-afni-reads-and-writes-nifti-reproduced)), which is what
makes the result match AFNI. In-memory images (`lx.Image`, nibabel images, `(array, affine)`)
keep `uint8`, `int16` and `float32` data and convert other types to `float32`; `tr` is required
when they have no NIfTI header.

`lx.afni.fmriprep_slice_timing(slice_timing, slice_encoding_direction)` gives the slice times
and `tzero` fMRIPrep passes: `SliceTiming` reversed when the direction ends in `-`, and
`round(min + 0.5·(max − min), 3)`.

```python
import json
import larmorx as lx

# As fMRIPrep calls 3dTshift: SliceTiming from the BIDS sidecar, tzero mid-acquisition.
meta = json.load(open("sub-01_task-rest_bold.json"))
times, t0 = lx.afni.fmriprep_slice_timing(meta["SliceTiming"], meta.get("SliceEncodingDirection"))
stc = lx.afni.tshift(
    "sub-01_task-rest_bold.nii.gz",
    slice_times=times,
    tzero=t0,
    tr=meta["RepetitionTime"],
    n_threads=8,
)
stc.save("sub-01_task-rest_desc-stc_bold.nii.gz")

# A named pattern and another method
img = lx.afni.tshift("bold.nii.gz", slice_times="alt+z", method="heptic")
```

Its result, `Image`, holds a voxel array placed in world space by an affine.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">data</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">affine</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">header</span></code> | <code><span class="nw">NiftiHeader</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">implementation</span></code> | <code><span class="nw">Implementation</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `3dTshift` accepts (`crates/larmorx-afni/src/cli/tshift.rs`) and the arguments of `lx.afni.tshift` (`python/larmorx/afni/tshift.py`), whose defaults and descriptions are taken from it. Under each option, in grey, its line of the usage text the clean room prints, in the clean room's own words.

| AFNI option | Python | Default | Notes |
|---|---|---|---|
| the last word (<code><span class="nw">dataset</span></code>) | <code><span class="nw">image</span></code> |  | the input: a 4D NIfTI path, or in Python an <code><span class="nw">lx&#46;Image</span></code>, a nibabel image or <code><span class="nw">&#40;array&#44;</span> <span class="nw">affine&#41;</span></code> |
| <code><span class="nw">&#45;prefix</span> <span class="nw">ppp</span></code> | the result |  | the returned image (its <code><span class="nw">&#46;save&#40;path&#41;</span></code> writes it); the command line needs <code><span class="nw">&#46;nii</span></code> or <code><span class="nw">&#46;nii&#46;gz</span></code> and refuses an existing file<span class="opt-help">The clean room's usage: “output file name: must end in .nii or .nii.gz; an existing file is an error unless -overwrite or AFNI_DECONFLICT says otherwise”</span> |
| <code><span class="nw">&#45;tpattern</span> <span class="nw">alt&#43;z</span></code> (and <code><span class="nw">altplus</span></code>, <code><span class="nw">alt&#43;z2</span></code>, <code><span class="nw">alt&#45;z</span></code>, <code><span class="nw">altminus</span></code>, <code><span class="nw">alt&#45;z2</span></code>, <code><span class="nw">seq&#43;z</span></code>, <code><span class="nw">seqplus</span></code>, <code><span class="nw">seq&#45;z</span></code>, <code><span class="nw">seqminus</span></code>, <code><span class="nw">zero</span></code>, <code><span class="nw">simult</span></code>) | <code><span class="nw">slice&#95;times&#61;&#34;alt&#43;z&#34;</span></code> |  | case-sensitive, except <code><span class="nw">zero</span></code> and <code><span class="nw">simult</span></code><span class="opt-help">The clean room's usage: “slice timing: alt+z altplus alt+z2 alt-z altminus alt-z2 seq+z seqplus seq-z seqminus zero simult, or @file / '@1D: ...' with one offset per slice (default: the slice timing in the NIfTI header)”</span> |
| <code><span class="nw">&#45;tpattern</span> <span class="nw">&#64;file</span></code>, <code><span class="nw">&#45;tpattern</span> <span class="nw">&#39;&#64;1D&#58;</span> <span class="nw">&#46;&#46;&#46;&#39;</span></code> | <code><span class="nw">slice&#95;times&#61;&#91;&#46;&#46;&#46;&#93;</span></code> (seconds) |  | values must lie in <code><span class="nw">&#91;0&#44;</span> <span class="nw">TR&#93;</span></code>; the file is AFNI 1D text ([Behaviour found by black-box runs](repo:docs/api/afni-tshift.md#behaviour-found-by-black-box-runs))<span class="opt-help">The clean room's usage: “slice timing: alt+z altplus alt+z2 alt-z altminus alt-z2 seq+z seqplus seq-z seqminus zero simult, or @file / '@1D: ...' with one offset per slice (default: the slice timing in the NIfTI header)”</span> |
| (no <code><span class="nw">&#45;tpattern</span></code>) | – |  | the command line uses the header's slice timing, or copies the input when there is none |
| <code><span class="nw">&#45;TR</span> <span class="nw">2s</span></code>, <code><span class="nw">&#45;TR</span> <span class="nw">2000ms</span></code> | <code><span class="nw">tr&#61;2&#46;0</span></code> | <code><span class="nw">None</span></code> | default: the header's TR (ms and µs converted), 1 s if not positive<span class="opt-help">The clean room's usage: “use ddd as the TR (suffix s or ms; ms switches every time to milliseconds)”</span> |
| <code><span class="nw">&#45;tzero</span> <span class="nw">z</span></code> | <code><span class="nw">tzero&#61;z</span></code> | <code><span class="nw">None</span></code> | default: the mean slice time; must be ≥ 0<span class="opt-help">The clean room's usage: “align each slice to time offset zzz (default: the mean slice offset)”</span> |
| <code><span class="nw">&#45;slice</span> <span class="nw">k</span></code> | <code><span class="nw">slice&#61;k</span></code> | <code><span class="nw">None</span></code> | wins over <code><span class="nw">tzero</span></code><span class="opt-help">The clean room's usage: “align each slice to the offset of slice nnn (wins over -tzero)”</span> |
| <code><span class="nw">&#45;ignore</span> <span class="nw">n</span></code> | <code><span class="nw">ignore&#61;n</span></code> | <code><span class="nw">0</span></code> | at most nt − 5<span class="opt-help">The clean room's usage: “leave the first ii time points out of the detrending and shifting”</span> |
| <code><span class="nw">&#45;Fourier</span></code> <code><span class="nw">&#45;linear</span></code> <code><span class="nw">&#45;cubic</span></code> <code><span class="nw">&#45;quintic</span></code> <code><span class="nw">&#45;heptic</span></code> <code><span class="nw">&#45;wsinc5</span></code> <code><span class="nw">&#45;wsinc9</span></code> | <code><span class="nw">method&#61;&#34;fourier&#34;</span></code> (default), <code><span class="nw">&#34;linear&#34;</span></code>, … | <code><span class="nw">&#34;fourier&#34;</span></code> | the command line compares 4 characters (<code><span class="nw">&#45;cub</span></code>), 7 for <code><span class="nw">&#45;wsinc5&#47;9</span></code> (any case)<span class="opt-help">The clean room's usage: “interpolation method (default -Fourier)”</span> |
| <code><span class="nw">&#45;rlt</span></code> / <code><span class="nw">&#45;rlt&#43;</span></code> | <code><span class="nw">restore&#61;&#34;none&#34;</span></code> / <code><span class="nw">&#34;intercept&#34;</span></code> | <code><span class="nw">&#34;trend&#34;</span></code> | <code><span class="nw">&#45;rlt&#43;</span></code> adds back the fitted intercept, not the mean<span class="opt-help">The clean room's usage: “do not add the trend back after shifting”</span><span class="opt-help">The clean room's usage: “add back only the intercept of the trend”</span> |
| <code><span class="nw">&#45;no&#95;detrend</span></code> | <code><span class="nw">detrend&#61;False</span></code> | <code><span class="nw">True</span></code> | every voxel's mean removed and restored, in both modes, as AFNI 26.3.05 does (AFNI 25.2.09's voxel pairs: AFNI-05, in [Upstream defects](repo:docs/api/afni-tshift.md#upstream-defects-d13))<span class="opt-help">The clean room's usage: “remove (and restore) only the mean; needs a non-Fourier method before it”</span> |
| <code><span class="nw">&#45;verbose</span></code> | – |  | progress on standard error; its first line names the port that runs<span class="opt-help">The clean room's usage: “print progress messages”</span> |
| <code><span class="nw">&#45;voxshift</span> <span class="nw">dset</span></code> | – |  | not supported |
| <code><span class="nw">&#45;Dname&#61;value</span></code>; AFNI's environment variables | <code><span class="nw">afni&#95;settings&#61;&#123;&#34;AFNI&#95;NIFTI&#95;PRIORITY&#34;&#58;</span> <span class="nw">&#34;Q&#34;&#125;</span></code> | <code><span class="nw">None</span></code> | the command line reads the process environment, as AFNI does, and <code><span class="nw">&#45;D</span></code> sets a variable for the run; Python never reads the environment ([AFNI's settings in Python](repo:docs/api/afni-tshift.md#afnis-settings-in-python)) |
| <code><span class="nw">&#45;overwrite</span></code>, <code><span class="nw">&#45;ok&#95;1D&#95;text</span></code>, <code><span class="nw">&#45;skip&#95;afnirc</span></code> | – |  | AFNI's global options, anywhere on the command line; the Python API writes no output file and its own slice-time file |
| <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> | <code><span class="nw">n&#95;threads&#61;1</span></code> (0 = all CPUs) | <code><span class="nw">1</span></code> | AFNI is single-threaded; the result does not depend on the thread count |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | AFNI's defects corrected (default) or reproduced (<code><span class="nw">reproduce</span></code>; [Upstream defects](repo:docs/api/afni-tshift.md#upstream-defects-d13), [upstream-defects.md](repo:docs/api/upstream-defects.md)) |
| <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> | <code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> | <code><span class="nw">auto</span></code>, <code><span class="nw">replica</span></code> or <code><span class="nw">clean&#45;room</span></code> (<code><span class="nw">&#45;&#45;implementation</span></code> before the family) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `afni` on the command line (`larmorx --n-threads 4 afni 3dTshift ...`) and are arguments of `lx.afni.tshift`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Worker threads (0 = all). The result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default) and <code><span class="nw">&#34;replica&#34;</span></code>: the bit-exact replica (part of larmorx, run in this process on temporary NIfTI files, with the arguments AFNI's program takes); <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works): the clean room. The two differ only in the last bits of some values (<code><span class="nw">docs&#47;validation&#47;afni&#45;tshift&#46;md</span></code>). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) corrects AFNI's defects (AFNI-01, -02, -07, -16, and with <code><span class="nw">afni&#95;settings</span></code> AFNI-23); <code><span class="nw">&#34;reproduce&#34;</span></code> gives AFNI's output. A <code><span class="nw">UpstreamDefectWarning</span></code> names each defect that changed the result (or, reproduced, would have been corrected). The replica receives the choice as <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code>. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `bold.nii.gz` (a synthetic series of 8 heads of 40 × 48 × 40 voxels of 4 mm), `slice_timing.1D` (the times of 40 slices acquired interleaved within 2 s, on one line, as fMRIPrep writes them). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# As fMRIPrep calls 3dTshift: the run's SliceTiming, tzero in the middle of the acquisition.
slice_timing = [float(t) for t in open("slice_timing.1D").read().split()]
times, t0 = lx.afni.fmriprep_slice_timing(slice_timing)
t0  # -> 0.975
stc = lx.afni.tshift("bold.nii.gz", slice_times=times, tzero=t0, tr=2.0)
stc.data.shape  # -> (40, 48, 40, 8)
```

```bash
larmorx afni 3dTshift -ignore 0 -tzero 0.975 -TR 2.0s -tpattern @slice_timing.1D -prefix bold_stc.nii.gz bold.nii.gz
```

## Ports {#ports}

`3dTshift` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 AND CC-BY-4.0 | validated | [afni-tshift-replica](repo:docs/validation/afni-tshift-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | validated | [afni-tshift](repo:docs/validation/afni-tshift.md) |

Both are `validated` against AFNI 26.3.05 itself (the clean room against AFNI 25.2.09 until
2026-10-29), on the same 317 cases of the standard tier: every file of `larmorx-testdata`'s
`synthetic/tshift/` (every FFT length class, every data type AFNI reads, edge content); every
method, option and `-tpattern` form, slice timing from NIfTI headers, the copies of the input,
AFNI's defects (D13) and 21 error cases; 20 runs on real BOLD data (ds000210 multi-echo,
ds001600, ds003345, ds005454 multiband with 96 slices, ds006010, ds006736), called as fMRIPrep
calls 3dTshift; and 60 cases of AFNI's global options and environment variables. In both
records 282 cases pass, 32 are rejected by both alike and 3 are expected divergences (AFNI's own
output format and `-voxshift`, which larmorx does not support, and a dataset of one row, which
AFNI writes as a text file with a random identifier, AFNI-20).

- **The replica** ([its record](repo:docs/validation/afni-tshift-replica.md), 2026-11-13): all 282
  compared cases are AFNI's output data bit for bit (the Fourier method's 147 and the other
  methods' and copies' 135); in the 63 cases of AFNI's global options, variables and failed
  writes, the exit status and both output streams are AFNI's byte for byte too (AFNI's version
  banner and larmorx's own lines set aside).
- **The clean room** ([its record](repo:docs/validation/afni-tshift.md), 2026-11-04): 180 of the 282
  compared cases are AFNI's output data bit for bit. The Lagrange and weighted-sinc methods and
  the copies give the same bytes as AFNI in 133 of 135; the Fourier method (the default) in 47
  of 147, because AFNI's FFT is float32 and the clean room's is double. The outputs that differ
  do so in the last float32 bits, by at most 3.7e-7 of AFNI's largest value (5.6e-8 on the real
  runs); integer outputs by at most 1. In every compared case the header fields are AFNI's and
  the geometry agrees to 1e-6 mm; in the 63 cases of AFNI's global options, variables and failed
  writes, the exit status and both output streams are AFNI's byte for byte (AFNI's version
  banner and larmorx's own lines set aside). The known last-bit differences are listed in
  [Known last-bit differences](repo:docs/api/afni-tshift.md#known-last-bit-differences).

In both records the Python call gives the command line's output bit for bit (data and header) on
the 194 passing cases it can express, 149 of 149 from an image in memory, and on the 28 cases of
AFNI's variables and global options it can express, with `afni_settings`.

`3dTshift` has two ports, both in `pip install larmorx`:

- **The replica** is bit-exact, translated from AFNI's own source
  (`crates/larmorx-afni-replica`; Apache-2.0, with CC BY 4.0's attribution for the code of the
  Medical College of Wisconsin, which AFNI 26.3.05 releases under CC BY 4.0
  ([NOTICE](repo:NOTICE), [licensing](repo:docs/licensing.md)); until 2026-10-29 the separate GPL
  program `larmorx-gpl`), with AFNI's float32 FFT and glibc 2.35's `sinf`/`cosf` translated from
  Arm's Optimized Routines (MIT), proved equal to glibc's on every input. With
  `LARMORX_UPSTREAM_DEFECTS=reproduce` it gives AFNI's output bytes on every compared parity
  case.
- **The clean room** (`crates/larmorx-afni`, Apache-2.0) is built for speed. AFNI's 3dTshift
  was GPL-2 code until AFNI 26.3.05, so larmorx wrote it without AFNI's source code: from the
  behaviour spec [`specs/3dTshift.md`](repo:specs/3dTshift.md), AFNI's help text and black-box
  runs of the AFNI binary ([PROVENANCE](repo:crates/larmorx-afni/PROVENANCE.md)).

Both take the same arguments, follow the same conventions (NIfTI output only, an existing output
is an error) and correct the same AFNI defects by default
([Upstream defects](repo:docs/api/afni-tshift.md#upstream-defects-d13)). `implementation="auto"` (the default, and
`larmorx afni 3dTshift`) runs the replica, in the same process; `implementation="replica"` or
`"clean-room"` (`"original"`, 0.1.0rc1's spelling, still works) (`--implementation` before the
family, or `LARMORX_IMPLEMENTATION`) forces one. Each image's `implementation` names the one that
ran.

## Evidence {#evidence}

How each of `3dTshift`'s ports was measured against AFNI, case by case: [its evidence](/evidence/afni-tshift/).

## More in the repository {#more}

The API page [docs/api/afni-tshift.md](repo:docs/api/afni-tshift.md) holds what `3dTshift` shares with the page's other programs:

- [Choosing the implementation](repo:docs/api/afni-tshift.md#choosing-the-implementation)
- [How AFNI reads and writes NIfTI (reproduced)](repo:docs/api/afni-tshift.md#how-afni-reads-and-writes-nifti-reproduced)
- [Upstream defects (D13)](repo:docs/api/afni-tshift.md#upstream-defects-d13)
- [AFNI's global options and environment variables](repo:docs/api/afni-tshift.md#afnis-global-options-and-environment-variables)
- [AFNI's settings in Python](repo:docs/api/afni-tshift.md#afnis-settings-in-python)
- [Behaviour found by black-box runs](repo:docs/api/afni-tshift.md#behaviour-found-by-black-box-runs)
- [Deliberate differences](repo:docs/api/afni-tshift.md#deliberate-differences)
- [Known last-bit differences](repo:docs/api/afni-tshift.md#known-last-bit-differences)
- [Rust](repo:docs/api/afni-tshift.md#rust)
