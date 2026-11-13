---
title: "`rmsdiff`"
kicker: "Programs · FSL"
description: "LARMORX reference for FSL 6.0.7.23 `rmsdiff`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl rmsdiff"
  python: "lx.fsl.rmsdiff"
  api: "docs/api/fsl-flirt.md"
  evidence: "/evidence/fsl-flirt/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "fa776d2ea0a17487"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "035dcd92e164879c"
    crates/larmorx-fsl/src/cli/rmsdiff.rs: "29e761efbef30f51"
    docs/api/fsl-flirt.md: "7fe0febecf4edaee"
    python/larmorx/fsl/flirt_tools.py: "dd92d42ca083679f"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

`rmsdiff` measures how far apart two FLIRT matrices are: the RMS deviation in millimetres over 80
mm about the reference's centre of gravity or, with a mask, the largest and the RMS displacement
over the mask's voxels.

## Command line {#command-line}

```text synopsis
larmorx fsl rmsdiff matrixfile1 matrixfile2 refvol [mask]
```

Everything after `larmorx fsl rmsdiff` is the original's command line: the arguments of FSL 6.0.7.23's `rmsdiff`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl rmsdiff ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>rmsdiff</code>'s usage text, as the clean room prints it</summary>

```text
Usage: rmsdiff matrixfile1 matrixfile2 refvol [mask]
        Outputs rms deviation between matrices (in mm)
```

</details>

## Python {#python}

```python
lx.fsl.rmsdiff(
    matrix1: Any,
    matrix2: Any,
    ref: Any,
    mask: Any = None,
    *,
    implementation: ImplementationName = "auto",
) -> float | tuple[float, float]
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`).

FSL's `rmsdiff`: the RMS deviation (mm) between two matrices (4 x 4 arrays or files) over a sphere of radius 80 mm about `ref`'s centre of gravity; with `mask`, the largest and the RMS displacement over the mask's voxels, as `(largest, rms)`.

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `rmsdiff` accepts (`crates/larmorx-fsl/src/cli/rmsdiff.rs`) and the arguments of `lx.fsl.rmsdiff` (`python/larmorx/fsl/flirt_tools.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">rmsdiff</span></code> arguments | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">matrixfile1</span></code> <code><span class="nw">matrixfile2</span></code> <code><span class="nw">refvol</span></code> <code><span class="nw">&#91;mask&#93;</span></code> | <code><span class="nw">matrix1</span></code>, <code><span class="nw">matrix2</span></code>, <code><span class="nw">ref</span></code>, <code><span class="nw">mask</span></code> | <code><span class="nw">mask&#61;None</span></code> |  |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl rmsdiff ...`); `lx.fsl.rmsdiff` takes `implementation` as an argument, and the others are the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;fsl&#46;rmsdiff</span></code> takes no <code><span class="nw">n&#95;threads</span></code>. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>). The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;fsl&#46;rmsdiff</span></code> takes no <code><span class="nw">upstream&#95;defects</span></code>. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `a.mat` (the identity as a 4 × 4 text matrix), `b.mat` (the identity as a 4 × 4 text matrix), `boldref.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

d = lx.fsl.rmsdiff("a.mat", "b.mat", "boldref.nii.gz")
```

```bash
larmorx fsl rmsdiff a.mat b.mat boldref.nii.gz
```

## Ports {#ports}

`rmsdiff` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-flirt-replica](repo:docs/validation/fsl-flirt-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-flirt](repo:docs/validation/fsl-flirt.md) |

Both ports are complete (`specs/flirt.md` §15.3). Where FSL aborts, they print the same lines and
exit with status 1.

The replica's record holds 7 cases of `rmsdiff`: 4 identical to FSL, 3 where both refuse or abort
alike. The clean room's holds 7: 4 identical to FSL in every byte of text and file, 3 where both
refuse or abort alike.

FSL's licence allows non-commercial use only, so each of FLIRT's programs has two ports, a
replica and a clean room, in different packages ([licensing](repo:docs/licensing.md) says what each
package holds):

- **The replica** is translated from FSL's source. The package `larmorx-nc` holds it (`crates-nc/`),
  under the FSL Licence's terms, and `larmorx` runs it as a separate program, `larmorx-nc fsl
  <program>`, when `larmorx-nc` is installed (`pip install larmorx-nc`).
- **The clean room** is written from [`specs/flirt.md`](repo:specs/flirt.md) by an implementer who
  never read FSL's source or the replica. It is part of `larmorx`, under Apache-2.0
  (`crates/larmorx-fsl`, with its [PROVENANCE](repo:crates/larmorx-fsl/PROVENANCE.md), section
  "FLIRT"), and runs on LARMORX's clean-room registration engine, the head-motion correction's
  (`lx.mri.hmc`).

`implementation="auto"` runs the replica when `larmorx-nc` is installed, and the clean room
otherwise. `"replica"` and `"clean-room"` choose one (`"original"`, 0.1.0rc1's spelling of
`"clean-room"`, still works); `"clean-room"` runs the clean room in this process. On the command
line, `--implementation auto|replica|clean-room` before the family chooses alike, from the next
release; in 0.1.0rc1 the variable `LARMORX_IMPLEMENTATION` chooses (`original` for the clean
room).

## Evidence {#evidence}

How each of `rmsdiff`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-flirt/).

## More in the repository {#more}

The API page [docs/api/fsl-flirt.md](repo:docs/api/fsl-flirt.md) holds what `rmsdiff` shares with the page's other programs:

- [The clean room (part 1, 2026-11-02)](repo:docs/api/fsl-flirt.md#the-clean-room-part-1-2026-11-02)
- [Defects of the original, corrected by default](repo:docs/api/fsl-flirt.md#defects-of-the-original-corrected-by-default)
- [Not yet](repo:docs/api/fsl-flirt.md#not-yet)
- [History](repo:docs/api/fsl-flirt.md#history)
