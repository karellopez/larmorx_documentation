---
title: "`3dUnifize`"
kicker: "Programs · AFNI"
description: "LARMORX reference for AFNI 26.3.05 `3dUnifize`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: afni
  original: "AFNI 26.3.05"
  software: "AFNI"
  command: "larmorx afni 3dUnifize"
  python: "lx.afni.unifize"
  api: "docs/api/afni-unifize.md"
  evidence: "/evidence/afni-unifize/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0 AND CC-BY-4.0", status: "validated"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-afni/src/cli/unifize.rs: "13006a3d0f104de6"
    crates/larmorx-afni/src/settings.rs: "8b2560253b92f512"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "91be42d24bb3ba2b"
    docs/api/afni-unifize.md: "80ea9d66456c2ad6"
    python/larmorx/afni/unifize.py: "72dc6b79d7e2617c"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

`3dUnifize` makes the white-matter intensity of a T1-weighted volume uniform across space and
scales it to about 1000 (or, with `-T2`, of a T2-weighted one; with `-EPI`, of an EPI series).

## Command line {#command-line}

```text synopsis
larmorx afni 3dUnifize [options] dataset
```

Everything after `larmorx afni 3dUnifize` is the original's command line: the arguments of AFNI 26.3.05's `3dUnifize`, as AFNI takes them. LARMORX's own options stand between `larmorx` and the family `afni`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        afni 3dUnifize ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>3dUnifize</code>'s usage text, as the clean room prints it</summary>

```text
Usage: 3dUnifize [options] dataset   (larmorx, clean-room re-implementation of AFNI 3dUnifize)

Makes the white-matter intensity of a T1-weighted NIfTI volume uniform (about 1000): at each
voxel, the mean of the automasked values between two percentiles in a ball around it estimates
the local white-matter intensity, which divides the image.

Options:
  -prefix pp      the output (NIfTI: .nii or .nii.gz)
  -input dd       the dataset (also -inset; or the first argument after the options)
  -T2             invert the contrast first and back after; twice: no inversion back
  -T2up uu        the upper percentile of the inversion, 90 to 100 [98.5]
  -GM             also scale the grey matter
  -Urad rr        the ball's radius in voxels, 5 to 99 [18.3]
  -rbt R b t      radius and percentiles [18.3 70 80] (also -param)
  -clfrac cc      the automask's clip level fraction, 0.1 to 0.9 [0.2] (also -mfrac)
  -ssave ss       save the scale factors
  -amsave aa      save the automasked input
  -noduplo        never work on a half-size copy (also -nodouble)
  -EPI            an EPI series: the scaling of its median volume applied to every volume
  -nosquash       do not squash values above 1300 (also -oink)
  -quiet          no progress messages
  -verb           the automask's messages too

AFNI's global options may stand anywhere: -overwrite, -Dname=value, -ok_1D_text, -skip_afnirc.
```

</details>

## Python {#python}

```python
lx.afni.unifize(
    image: Any,
    *,
    t2: int | bool = False,
    t2_percentile: float = 98.5,
    gm: bool = False,
    radius: float = 18.3,
    percentiles: Sequence[float] = (70.0, 80.0),
    clfrac: float = 0.2,
    duplo: bool = True,
    epi: bool = False,
    squash: bool = True,
    save_scale: bool = False,
    save_automask: bool = False,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
    afni_settings: Mapping[str, str] | None = None,
) -> UnifizeResult
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

The image with its white-matter intensity uniformized, as AFNI's `3dUnifize` makes it.

Returns an `UnifizeResult`: `image` (float32; with `epi=True` every volume), `scale` (with
`save_scale=True`) and `automasked` (with `save_automask=True`). `lx.afni.fmriprep_unifize_options()`
gives fMRIPrep's arguments. The arguments are checked before anything runs (`ValueError`, with
3dUnifize's ranges); with the clean room, AFNI's fatal errors (no automask) are `ValueError`s too.

```python
import larmorx as lx

# As fMRIPrep's BOLD reference workflow calls 3dUnifize (-clfrac 0.2 -rbt 18.3 65.0 90.0 -T2).
uni = lx.afni.unifize("boldref_brain_masked.nii.gz", **lx.afni.fmriprep_unifize_options())
uni.image   # float32, white matter about 1000

# A T1w, with the scale factors.
r = lx.afni.unifize("sub-01_T1w.nii.gz", save_scale=True, n_threads=6)
```

Its result, `UnifizeResult`, holds what `unifize` computed.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">image</span></code> | <code><span class="nw">Image</span></code> | The unifized image, float32 (white matter about 1000); with <code><span class="nw">epi&#61;True</span></code> every volume. |
| <code><span class="nw">scale</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">save&#95;scale&#61;True</span></code>: the white-matter scale factor of each voxel (<code><span class="nw">&#45;ssave</span></code>). |
| <code><span class="nw">automasked</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">save&#95;automask&#61;True</span></code>: the input inside its automask (<code><span class="nw">&#45;amsave</span></code>). |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `3dUnifize` accepts (`crates/larmorx-afni/src/cli/unifize.rs`) and the arguments of `lx.afni.unifize` (`python/larmorx/afni/unifize.py`), whose defaults and descriptions are taken from it. Under each option, in grey, its line of the usage text the clean room prints, in the clean room's own words.

| AFNI option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;prefix</span> <span class="nw">p</span></code> | the result |  | its <code><span class="nw">image</span></code>; NIfTI only; AFNI's default <code><span class="nw">Unifized</span></code> is its own format, refused<span class="opt-help">The clean room's usage: “the output (NIfTI: .nii or .nii.gz)”</span> |
| <code><span class="nw">&#45;input</span> <span class="nw">d</span></code>, <code><span class="nw">&#45;inset</span> <span class="nw">d</span></code>, or the last argument | <code><span class="nw">image</span></code> |  | A path to a NIfTI file (read with AFNI's rules), or an in-memory image. Only the first volume of a 4D image is processed, unless <code><span class="nw">epi&#61;True</span></code>.<span class="opt-help">The clean room's usage: “the dataset (also -inset; or the first argument after the options)”</span> |
| <code><span class="nw">&#45;T2</span></code> | <code><span class="nw">t2&#61;True</span></code> (or 1) | <code><span class="nw">False</span></code> | invert the contrast, unifize, invert back<span class="opt-help">The clean room's usage: “invert the contrast first and back after; twice: no inversion back”</span> |
| <code><span class="nw">&#45;T2</span> <span class="nw">&#45;T2</span></code> | <code><span class="nw">t2&#61;2</span></code> | <code><span class="nw">False</span></code> | no inversion back; bright edges clipped<span class="opt-help">The clean room's usage: “invert the contrast first and back after; twice: no inversion back”</span> |
| <code><span class="nw">&#45;T2</span></code> three or more times | – |  | AFNI neither inverts back nor clips edges: refused by default (AFNI-48)<span class="opt-help">The clean room's usage: “invert the contrast first and back after; twice: no inversion back”</span> |
| <code><span class="nw">&#45;T2up</span> <span class="nw">u</span></code> | <code><span class="nw">t2&#95;percentile</span></code> | <code><span class="nw">98&#46;5</span></code> | 90 to 100; near 100 see AFNI-45<span class="opt-help">The clean room's usage: “the upper percentile of the inversion, 90 to 100 [98.5]”</span> |
| <code><span class="nw">&#45;GM</span></code> | <code><span class="nw">gm&#61;True</span></code> | <code><span class="nw">False</span></code> | grey-matter scaling (not with <code><span class="nw">&#45;EPI</span></code>)<span class="opt-help">The clean room's usage: “also scale the grey matter”</span> |
| <code><span class="nw">&#45;Urad</span> <span class="nw">R</span></code>, <code><span class="nw">&#45;rbt</span> <span class="nw">R</span> <span class="nw">b</span> <span class="nw">t</span></code>, <code><span class="nw">&#45;param</span> <span class="nw">R</span> <span class="nw">b</span> <span class="nw">t</span></code> | <code><span class="nw">radius</span></code>, <code><span class="nw">percentiles&#61;&#40;b&#44;</span> <span class="nw">t&#41;</span></code> | <code><span class="nw">radius&#61;18&#46;3</span></code>, <code><span class="nw">percentiles&#61;&#40;70&#46;0&#44;</span> <span class="nw">80&#46;0&#41;</span></code> | 5 ≤ R ≤ 99, 30 ≤ b ≤ 80, b < t ≤ 90<span class="opt-help">The clean room's usage: “the ball's radius in voxels, 5 to 99 [18.3]”</span><span class="opt-help">The clean room's usage: “R b t      radius and percentiles [18.3 70 80] (also -param)”</span> |
| <code><span class="nw">&#45;clfrac</span> <span class="nw">c</span></code>, <code><span class="nw">&#45;mfrac</span> <span class="nw">c</span></code> | <code><span class="nw">clfrac</span></code> | <code><span class="nw">0&#46;2</span></code> | the automask's clip level fraction (default 0.2; AFNI's help says 0.1, AFNI-49)<span class="opt-help">The clean room's usage: “the automask's clip level fraction, 0.1 to 0.9 [0.2] (also -mfrac)”</span> |
| <code><span class="nw">&#45;noduplo</span></code>, <code><span class="nw">&#45;nodouble</span></code> | <code><span class="nw">duplo&#61;False</span></code> | <code><span class="nw">True</span></code> | the half-size copy is only used above a million voxels<span class="opt-help">The clean room's usage: “never work on a half-size copy (also -nodouble)”</span> |
| <code><span class="nw">&#45;EPI</span></code> | <code><span class="nw">epi&#61;True</span></code> | <code><span class="nw">False</span></code> | implies <code><span class="nw">&#45;T2</span></code> (once, whatever <code><span class="nw">&#45;T2</span></code> gave) and <code><span class="nw">&#45;noduplo</span></code>, turns off <code><span class="nw">&#45;GM</span></code>, sets the radius from the voxel size<span class="opt-help">The clean room's usage: “an EPI series: the scaling of its median volume applied to every volume”</span> |
| <code><span class="nw">&#45;nosquash</span></code>, <code><span class="nw">&#45;oink</span></code> | <code><span class="nw">squash&#61;False</span></code> | <code><span class="nw">True</span></code> | <code><span class="nw">False</span></code> is <code><span class="nw">&#45;nosquash</span></code>.<span class="opt-help">The clean room's usage: “do not squash values above 1300 (also -oink)”</span> |
| <code><span class="nw">&#45;ssave</span> <span class="nw">s</span></code>, <code><span class="nw">&#45;amsave</span> <span class="nw">a</span></code> | <code><span class="nw">save&#95;scale</span></code>, <code><span class="nw">save&#95;automask</span></code> | <code><span class="nw">save&#95;scale&#61;False</span></code>, <code><span class="nw">save&#95;automask&#61;False</span></code> | the result's <code><span class="nw">scale</span></code> and <code><span class="nw">automasked</span></code><span class="opt-help">The clean room's usage: “save the scale factors”</span><span class="opt-help">The clean room's usage: “save the automasked input”</span> |
| <code><span class="nw">&#45;quiet</span></code>, <code><span class="nw">&#45;verb</span></code> | (always quiet) |  | warnings become Python warnings<span class="opt-help">The clean room's usage: “no progress messages”</span><span class="opt-help">The clean room's usage: “the automask's messages too”</span> |
| <code><span class="nw">&#45;useall</span></code> | – |  | disabled in AFNI 25.2.09 and 26.3.05 (a warning) |
| <code><span class="nw">&#45;overwrite</span></code>, <code><span class="nw">&#45;Dname&#61;value</span></code>, <code><span class="nw">&#45;ok&#95;1D&#95;text</span></code>, <code><span class="nw">&#45;skip&#95;afnirc</span></code>; <code><span class="nw">AFNI&#95;&#42;</span></code> | <code><span class="nw">afni&#95;settings</span></code> | <code><span class="nw">None</span></code> | AFNI's global options, anywhere on the command line, and AFNI's variables, as for 3dAutomask |
| <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | the result does not depend on it, in AFNI or larmorx |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `afni` on the command line (`larmorx --n-threads 4 afni 3dUnifize ...`) and are arguments of `lx.afni.unifize`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all); the result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | As for <code><span class="nw">automask</span></code>. <code><span class="nw">t2&#61;3</span></code> (<code><span class="nw">&#45;T2</span></code> three times, AFNI-48) is not accepted. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | As for <code><span class="nw">automask</span></code>. <code><span class="nw">t2&#61;3</span></code> (<code><span class="nw">&#45;T2</span></code> three times, AFNI-48) is not accepted. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `ref.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# As fMRIPrep's BOLD reference workflow calls 3dUnifize (-clfrac 0.2 -rbt 18.3 65.0 90.0 -T2).
uni = lx.afni.unifize("ref.nii.gz", **lx.afni.fmriprep_unifize_options())
uni.image.data.dtype  # -> dtype('float32')
```

```bash
larmorx afni 3dUnifize -clfrac 0.2 -rbt 18.3 65.0 90.0 -prefix uni.nii.gz -T2 -input ref.nii.gz
```

## Ports {#ports}

`3dUnifize` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 AND CC-BY-4.0 | validated | [afni-unifize-replica](repo:docs/validation/afni-unifize-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | validated | [afni-unifize](repo:docs/validation/afni-unifize.md) |

Both are `validated` against AFNI 26.3.05 itself (the clean room against AFNI 25.2.09 until
2026-10-29), each in a standard comparison of 2026-10-30:

- **The replica** ([its record](repo:docs/validation/afni-unifize-replica.md)): 127 cases, 106 within
  its thresholds, 19 rejected by both alike, 2 expected divergences (AFNI's default prefix, its
  own format, which LARMORX refuses; a slab where AFNI reads memory it never wrote, AFNI-47);
  every one of the 97 compared cases that write an output is AFNI's bit for bit (data and NIfTI
  header), with AFNI's exit status and messages.
- **The clean room** ([its record](repo:docs/validation/afni-unifize.md)): 129 cases, none failing: 108
  within its thresholds, 19 rejected by both alike, the same 2 expected divergences (GLIBC-05's 5
  cases since 2026-10-30). AFNI's exit status and messages in every case; in 44 of the 99
  compared cases that write outputs every output is AFNI's, bit for bit (data and NIfTI header);
  in the other 55 the headers are AFNI's and some squashed values differ in their last bit (at
  most 8.7e-8 of the largest value; the threshold is 1e-5), because AFNI's `tanhf` is glibc's and
  the clean room's is correctly rounded: AFNI run with CORE-MATH's correctly rounded functions
  preloaded gives the clean room's bytes in all 55. fMRIPrep's own outputs of 22 BOLD references
  of fMRIPrep's runs: 1 bit for bit, the other 21 AFNI's output with the same last-bit
  differences. Its result does not depend on the thread count (nor does AFNI's: 1 and 6 threads,
  and fMRIPrep's build, give AFNI's bytes).

`3dUnifize` has two ports, both in `pip install larmorx`:

- **The replica** is bit-exact, translated from AFNI's source (`crates/larmorx-afni-replica`;
  Apache-2.0, with CC BY 4.0's attribution for the code of the Medical College of Wisconsin,
  which AFNI 26.3.05 releases under CC BY 4.0 ([NOTICE](repo:NOTICE),
  [licensing](repo:docs/licensing.md)); with fdlibm's `tanhf` as glibc 2.35 runs it; until 2026-10-29
  the separate GPL package `larmorx-gpl`).
- **The clean room** (`crates/larmorx-afni`, Apache-2.0) is built for speed and written from
  [`specs/3dUnifize.md`](repo:specs/3dUnifize.md) and black-box runs of AFNI only
  ([PROVENANCE](repo:crates/larmorx-afni/PROVENANCE.md)).

`implementation="auto"` (the default, and `larmorx afni 3dUnifize`) runs the replica, in the same
process; `"replica"` or `"clean-room"` (`"original"`, 0.1.0rc1's spelling, still works)
(`--implementation` before the family, or `LARMORX_IMPLEMENTATION`) forces one. Each image's
`implementation` names the one that ran.

## Evidence {#evidence}

How each of `3dUnifize`'s ports was measured against AFNI, case by case: [its evidence](/evidence/afni-unifize/).

## More in the repository {#more}

The API page [docs/api/afni-unifize.md](repo:docs/api/afni-unifize.md) holds what `3dUnifize` shares with the page's other programs:

- [-EPI's radius and the cube root's last bit](repo:docs/api/afni-unifize.md#-epis-radius-and-the-cube-roots-last-bit)
- [Upstream defects (D13)](repo:docs/api/afni-unifize.md#upstream-defects-d13)
- [Deliberate differences](repo:docs/api/afni-unifize.md#deliberate-differences)
- [Known last-bit differences](repo:docs/api/afni-unifize.md#known-last-bit-differences)
- [Speed](repo:docs/api/afni-unifize.md#speed)
- [Rust](repo:docs/api/afni-unifize.md#rust)
