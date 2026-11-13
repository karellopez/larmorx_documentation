---
title: "`3dAutomask`"
kicker: "Programs · AFNI"
description: "LARMORX reference for AFNI 26.3.05 `3dAutomask`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: afni
  original: "AFNI 26.3.05"
  software: "AFNI"
  command: "larmorx afni 3dAutomask"
  python: "lx.afni.automask"
  api: "docs/api/afni-automask.md"
  evidence: "/evidence/afni-automask/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0 AND CC-BY-4.0", status: "validated"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-afni/src/cli/automask.rs: "b2304a19276b469c"
    crates/larmorx-afni/src/settings.rs: "8b2560253b92f512"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "035dcd92e164879c"
    docs/api/afni-automask.md: "5ea70d6aa84dab74"
    python/larmorx/afni/automask.py: "4bf4fd465a0d0a8b"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

`3dAutomask` makes a brain mask from an EPI series or a skull-stripped anatomical image.

## Command line {#command-line}

```text synopsis
larmorx afni 3dAutomask [options] dataset
```

Everything after `larmorx afni 3dAutomask` is the original's command line: the arguments of AFNI 26.3.05's `3dAutomask`, as AFNI takes them. LARMORX's own options stand between `larmorx` and the family `afni`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        afni 3dAutomask ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>3dAutomask</code>'s usage text, as the clean room prints it</summary>

```text
Usage: 3dAutomask [options] dataset   (larmorx, clean-room re-implementation of AFNI 3dAutomask)

Makes a brain mask (1 inside, 0 outside) from an EPI time series or a skull-stripped anatomical
NIfTI dataset: a clip level that varies gradually across the image, the largest connected
cluster, peeled and restored, its holes filled.

Options (they must come before the dataset):
  -prefix ppp        the mask (NIfTI: .nii or .nii.gz)
  -apply_prefix ppp  the input with every voxel outside the mask 0
  -depth ppp         how many erosions remove each mask voxel
  -clfrac cc         clip level fraction, 0.1 to 0.9 [0.5] (also -mfrac)
  -nograd            one clip level for the whole image
  -peels pp          peel and restore the mask pp times [1]; 0 turns it off
  -nbhrs nn          neighbours (of 18) a voxel needs not to be peeled, 6 to 26 [17]
  -NN1 -NN2 -NN3     neighbourhood of -dilate, -erode and -depth [NN2]; also sets -nbhrs
  -eclip             remove exterior voxels below the clip level
  -dilate nd         dilate the mask nd times
  -erode ne          erode the mask ne times
  -SI hh             clear everything more than hh mm inferior to the most superior voxel
  -q                 no progress messages

AFNI's global options may stand anywhere: -overwrite, -Dname=value, -ok_1D_text, -skip_afnirc.
```

</details>

## Python {#python}

```python
lx.afni.automask(
    image: Any,
    *,
    clfrac: float = 0.5,
    gradual: bool = True,
    peels: int = 1,
    neighbours: int = 17,
    nn: Literal[1, 2, 3] | None = None,
    exterior_clip: bool = False,
    dilate: int = 0,
    erode: int = 0,
    si: float | None = None,
    apply: bool = False,
    depth: bool = False,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
    afni_settings: Mapping[str, str] | None = None,
) -> AutomaskResult
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

A brain mask, as AFNI's `3dAutomask` makes it.

Returns an `AutomaskResult`: `mask` (uint8, 3D; 2D for a plane), `masked` (with `apply=True`;
the input's storage type, its values as `lx.load` reads them) and `depth` (with `depth=True`;
int16). `image` is a path (read with AFNI's NIfTI rules) or an in-memory image (2D, 3D or 4D;
uint8, int16 and float32 kept, other types float32). The arguments are checked before anything
runs (`ValueError`); with the clean room, AFNI's fatal errors (no mask of a plane smaller than
16 × 16, an empty mask) are `ValueError`s too. AFNI's variables are settings of the call
(`afni_settings`, as for [`lx.afni.tshift`](repo:docs/api/afni-tshift.md#afnis-settings-in-python)); the
process environment is never read.

```python
import larmorx as lx

# As fMRIPrep calls 3dAutomask on its unifized BOLD reference.
r = lx.afni.automask("uni_xform.nii.gz", dilate=1, apply=True)
r.mask      # uint8, 1 inside the brain
r.masked    # the input, 0 outside the mask
r.mask.implementation   # Implementation(kind='replica', package='larmorx', ...)
```

Its result, `AutomaskResult`, holds what `automask` computed.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">mask</span></code> | <code><span class="nw">Image</span></code> | The brain mask: uint8, 1 inside and 0 outside, on the input's grid (3D). |
| <code><span class="nw">masked</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">apply&#61;True</span></code>: the input with every voxel outside the mask 0, in the input's storage type (<code><span class="nw">&#45;apply&#95;prefix</span></code>); else <code><span class="nw">None</span></code>. |
| <code><span class="nw">depth</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">depth&#61;True</span></code>: int16, how many erosions it takes to reach each mask voxel (<code><span class="nw">&#45;depth</span></code>); else <code><span class="nw">None</span></code>. |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `3dAutomask` accepts (`crates/larmorx-afni/src/cli/automask.rs`) and the arguments of `lx.afni.automask` (`python/larmorx/afni/automask.py`), whose defaults and descriptions are taken from it. Under each option, in grey, its line of the usage text the clean room prints, in the clean room's own words.

| AFNI option | Python | Default | Notes |
|---|---|---|---|
| the last word (<code><span class="nw">dataset</span></code>) | <code><span class="nw">image</span></code> |  | the input: a path, or an in-memory image in Python |
| <code><span class="nw">&#45;prefix</span> <span class="nw">p</span></code> | the result |  | its <code><span class="nw">mask</span></code>; the command line writes NIfTI only (<code><span class="nw">&#46;nii</span></code>, <code><span class="nw">&#46;nii&#46;gz</span></code>); AFNI's default <code><span class="nw">automask</span></code> is its own format, refused<span class="opt-help">The clean room's usage: “the mask (NIfTI: .nii or .nii.gz)”</span> |
| <code><span class="nw">&#45;apply&#95;prefix</span> <span class="nw">p</span></code> | <code><span class="nw">apply&#61;True</span></code> | <code><span class="nw">False</span></code> | the result's <code><span class="nw">masked</span></code>; alone (no <code><span class="nw">&#45;prefix</span></code>) it is the only output<span class="opt-help">The clean room's usage: “the input with every voxel outside the mask 0”</span> |
| <code><span class="nw">&#45;depth</span> <span class="nw">p</span></code> | <code><span class="nw">depth&#61;True</span></code> | <code><span class="nw">False</span></code> | the result's <code><span class="nw">depth</span></code>, from the mask before <code><span class="nw">&#45;dilate</span></code>, <code><span class="nw">&#45;erode</span></code> and <code><span class="nw">&#45;SI</span></code><span class="opt-help">The clean room's usage: “how many erosions remove each mask voxel”</span> |
| <code><span class="nw">&#45;clfrac</span> <span class="nw">c</span></code>, <code><span class="nw">&#45;mfrac</span> <span class="nw">c</span></code> | <code><span class="nw">clfrac</span></code> | <code><span class="nw">0&#46;5</span></code> | 0.1 to 0.9<span class="opt-help">The clean room's usage: “clip level fraction, 0.1 to 0.9 [0.5] (also -mfrac)”</span> |
| <code><span class="nw">&#45;nograd</span></code> | <code><span class="nw">gradual&#61;False</span></code> | <code><span class="nw">True</span></code> | any option starting with <code><span class="nw">&#45;nogr</span></code><span class="opt-help">The clean room's usage: “one clip level for the whole image”</span> |
| <code><span class="nw">&#45;peels</span> <span class="nw">p</span></code> | <code><span class="nw">peels</span></code> | <code><span class="nw">1</span></code> | 0 turns the peeling off (AFNI-43; AFNI peels once)<span class="opt-help">The clean room's usage: “peel and restore the mask pp times [1]; 0 turns it off”</span> |
| <code><span class="nw">&#45;nbhrs</span> <span class="nw">n</span></code> | <code><span class="nw">neighbours</span></code> | <code><span class="nw">17</span></code> | 6 to 26 (19 to 26 act as 18); outside it an error by default (AFNI-41)<span class="opt-help">The clean room's usage: “neighbours (of 18) a voxel needs not to be peeled, 6 to 26 [17]”</span> |
| <code><span class="nw">&#45;NN1</span></code>, <code><span class="nw">&#45;NN2</span></code>, <code><span class="nw">&#45;NN3</span></code> | <code><span class="nw">nn&#61;1</span></code>, <code><span class="nw">2</span></code>, <code><span class="nw">3</span></code> | <code><span class="nw">None</span></code> | also set <code><span class="nw">neighbours</span></code> to 6, 18, 26 (AFNI-42, kept)<span class="opt-help">The clean room's usage: “-NN2 -NN3     neighbourhood of -dilate, -erode and -depth [NN2]; also sets -nbhrs”</span> |
| <code><span class="nw">&#45;eclip</span></code> | <code><span class="nw">exterior&#95;clip&#61;True</span></code> | <code><span class="nw">False</span></code> | <code><span class="nw">&#45;eclip</span></code>: remove exterior voxels below the clip level.<span class="opt-help">The clean room's usage: “remove exterior voxels below the clip level”</span> |
| <code><span class="nw">&#45;dilate</span> <span class="nw">nd</span></code>, <code><span class="nw">&#45;erode</span> <span class="nw">ne</span></code> | <code><span class="nw">dilate</span></code>, <code><span class="nw">erode</span></code> | <code><span class="nw">dilate&#61;0</span></code>, <code><span class="nw">erode&#61;0</span></code> | dilations need 3 neighbours; each is followed by filling holes<span class="opt-help">The clean room's usage: “dilate the mask nd times”</span><span class="opt-help">The clean room's usage: “erode the mask ne times”</span> |
| <code><span class="nw">&#45;SI</span> <span class="nw">hh</span></code> | <code><span class="nw">si</span></code> | <code><span class="nw">None</span></code> | millimetres, along the superior axis<span class="opt-help">The clean room's usage: “clear everything more than hh mm inferior to the most superior voxel”</span> |
| <code><span class="nw">&#45;q</span></code> | (always) |  | the Python wrapper runs quietly; its warnings become Python warnings<span class="opt-help">The clean room's usage: “no progress messages”</span> |
| <code><span class="nw">&#45;overwrite</span></code>, <code><span class="nw">&#45;Dname&#61;value</span></code>, <code><span class="nw">&#45;ok&#95;1D&#95;text</span></code>, <code><span class="nw">&#45;skip&#95;afnirc</span></code> | <code><span class="nw">afni&#95;settings</span></code> | <code><span class="nw">None</span></code> | AFNI's global options, anywhere on the command line |
| <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | the result does not depend on it (AFNI's 3dAutomask is single-threaded; the clean room runs its passes in parallel) |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | <code><span class="nw">fix</span></code> (default) or <code><span class="nw">reproduce</span></code> |
| <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> | <code><span class="nw">implementation</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> | <code><span class="nw">auto</span></code>, <code><span class="nw">replica</span></code> or <code><span class="nw">clean&#45;room</span></code> (<code><span class="nw">&#45;&#45;implementation</span></code> before the family) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `afni` on the command line (`larmorx --n-threads 4 afni 3dAutomask ...`) and are arguments of `lx.afni.automask`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all); the result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default) and <code><span class="nw">&#34;replica&#34;</span></code>: the bit-exact replica; <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works): the clean room. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code> (AFNI's output); a <code><span class="nw">UpstreamDefectWarning</span></code> names each defect that changed the result. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `uni_xform.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# As fMRIPrep calls 3dAutomask on its unifized BOLD reference.
r = lx.afni.automask("uni_xform.nii.gz", dilate=1, apply=True)
r.mask.data.dtype  # -> dtype('uint8')
```

```bash
larmorx afni 3dAutomask -apply_prefix uni_xform_masked.nii.gz -dilate 1 -prefix uni_xform_mask.nii.gz uni_xform.nii.gz
```

## Ports {#ports}

`3dAutomask` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 AND CC-BY-4.0 | validated | [afni-automask-replica](repo:docs/validation/afni-automask-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | validated | [afni-automask](repo:docs/validation/afni-automask.md) |

Both are `validated` against AFNI 26.3.05 itself (the clean room against AFNI 25.2.09 until
2026-10-29), each in a standard comparison of 2026-10-30:

- **The replica** ([its record](repo:docs/validation/afni-automask-replica.md)): 125 cases, 105 within its
  thresholds, 19 rejected by both alike, 1 expected divergence (AFNI's default prefix, its own
  format, which LARMORX refuses); every one of the 101 compared cases that write an output is
  AFNI's bit for bit (data and NIfTI header), with AFNI's exit status and messages.
- **The clean room** ([its record](repo:docs/validation/afni-automask.md)): 130 cases, 110 within its
  thresholds, 19 rejected by both alike, the same expected divergence. Of the 106 compared cases
  that write an output, 92 are AFNI's bit for bit (data and NIfTI header), with AFNI's exit
  status and messages; the other 14, fMRIPrep's calls on BOLD references of the data panel, have
  AFNI's data and a header that differs only where AFNI reads its own header extension of the
  input (AFNI-10). fMRIPrep's masks of all 22 BOLD references in the record: AFNI's data, bit for
  bit.

`3dAutomask` has two ports, both in `pip install larmorx`:

- **The replica** is bit-exact, translated from AFNI's source (`crates/larmorx-afni-replica`;
  Apache-2.0, with CC BY 4.0's attribution for the code of the Medical College of Wisconsin,
  which AFNI 26.3.05 releases under CC BY 4.0 ([NOTICE](repo:NOTICE),
  [licensing](repo:docs/licensing.md)); until 2026-10-29 the separate GPL package `larmorx-gpl`).
- **The clean room** (`crates/larmorx-afni`, Apache-2.0) is built for speed and written from
  [`specs/3dAutomask.md`](repo:specs/3dAutomask.md) and black-box runs of AFNI only
  ([PROVENANCE](repo:crates/larmorx-afni/PROVENANCE.md)).

`implementation="auto"` (the default, and `larmorx afni 3dAutomask`) runs the replica, in the
same process; `implementation="replica"` or `"clean-room"` (`"original"`, 0.1.0rc1's spelling,
still works) (`--implementation` on the command line, or `LARMORX_IMPLEMENTATION`) forces one.
Each image's `implementation` names the one that ran.

## Evidence {#evidence}

How each of `3dAutomask`'s ports was measured against AFNI, case by case: [its evidence](/evidence/afni-automask/).

## More in the repository {#more}

The API page [docs/api/afni-automask.md](repo:docs/api/afni-automask.md) holds what `3dAutomask` shares with the page's other programs:

- [Upstream defects (D13)](repo:docs/api/afni-automask.md#upstream-defects-d13)
- [Deliberate differences](repo:docs/api/afni-automask.md#deliberate-differences)
- [Known last-bit differences](repo:docs/api/afni-automask.md#known-last-bit-differences)
- [Speed](repo:docs/api/afni-automask.md#speed)
- [Rust](repo:docs/api/afni-automask.md#rust)
