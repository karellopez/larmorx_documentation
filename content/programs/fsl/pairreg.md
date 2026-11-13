---
title: "`pairreg`"
kicker: "Programs · FSL"
lede: "`pairreg` is a script that registers one brain to another and refines the result with the two heads' skulls."
description: "LARMORX reference for FSL 6.0.7.23 `pairreg`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl pairreg"
  python: "lx.fsl.pairreg"
  api: "docs/api/fsl-flirt.md"
  evidence: "/evidence/fsl-flirt/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "035dcd92e164879c"
    crates/larmorx-fsl/src/cli/pairreg.rs: "c3ccbcb23f7dc04e"
    docs/api/fsl-flirt.md: "abc8e4a5001ff9ef"
    python/larmorx/fsl/flirt_more.py: "e26d92e30bf57c9f"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

It runs FLIRT three times, with FSL's schedules `pairreg1.sch` to `pairreg3.sch`:
the brains first, then the skulls, then the brains again; `brain1` and `skull1` are the references.

## Command line {#command-line}

```text synopsis
larmorx fsl pairreg brain1 brain2 skull1 skull2 outputmatrix [extra flirt args]
```

Everything after `larmorx fsl pairreg` is the original's command line: the arguments of FSL 6.0.7.23's `pairreg`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl pairreg ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>pairreg</code>'s usage text, as the clean room prints it</summary>

```text
Usage: pairreg brain1 brain2 skull1 skull2 outputmatrix [extra flirt args]

  NB: brain1 and skull1 are used as -ref arguments internally
```

</details>

## Python {#python}

```python
lx.fsl.pairreg(
    brain1: str | os.PathLike,
    brain2: str | os.PathLike,
    skull1: str | os.PathLike,
    skull2: str | os.PathLike,
    *,
    flirt_args: list[str] | None = None,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
) -> np.ndarray
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

FSL's `pairreg`: the matrix from `brain2` to `brain1` (`brain1` and `skull1` the references), found with the brains, refined with the skulls and finished with the brains (three FLIRT runs with FSL's `pairreg1.sch` to `pairreg3.sch` schedules, which the clean room carries: no `$FSLDIR` needed); `flirt_args` are passed to every FLIRT run.

The images are paths; `flirt_args` is a list of FLIRT's options. The result is the 4 × 4 matrix
from `brain2` to `brain1`.

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `pairreg` accepts (`crates/larmorx-fsl/src/cli/pairreg.rs`) and the arguments of `lx.fsl.pairreg` (`python/larmorx/fsl/flirt_more.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">pairreg</span></code> arguments | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">brain1</span></code> <code><span class="nw">brain2</span></code> <code><span class="nw">skull1</span></code> <code><span class="nw">skull2</span></code> | <code><span class="nw">brain1</span></code>, <code><span class="nw">brain2</span></code>, <code><span class="nw">skull1</span></code>, <code><span class="nw">skull2</span></code> |  | <code><span class="nw">brain1</span></code> and <code><span class="nw">skull1</span></code> the references |
| <code><span class="nw">outputmatrix</span></code> | the result |  |  |
| <code><span class="nw">&#91;extra</span> <span class="nw">flirt</span> <span class="nw">args&#93;</span></code> | <code><span class="nw">flirt&#95;args</span></code> | <code><span class="nw">None</span></code> | passed to every FLIRT run |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl pairreg ...`) and are arguments of `lx.fsl.pairreg`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all), given to the program as <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code>; the result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects corrected, or FSL's behaviour (<code><span class="nw">docs&#47;api&#47;fsl&#45;flirt&#46;md</span></code>, "Defects of the original, corrected by default"). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `b1_brain.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `b2_brain.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `b1.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `b2.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

pair = lx.fsl.pairreg("b1_brain.nii.gz", "b2_brain.nii.gz", "b1.nii.gz", "b2.nii.gz")
pair.shape  # -> (4, 4)
```

```bash
larmorx fsl pairreg b1_brain.nii.gz b2_brain.nii.gz b1.nii.gz b2.nii.gz b2_to_b1.mat
```

## Ports {#ports}

`pairreg` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-flirt-replica](repo:docs/validation/fsl-flirt-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-flirt](repo:docs/validation/fsl-flirt.md) |

Both ports are complete (`specs/flirt.md` §15.8). The clean room runs its own `flirt` three times and one `convert_xfm -fixscaleskew`, in
this process, and carries FSL's three schedules itself: it needs no `$FSLDIR`. `-v` echoes FSL's
lines, and a step that aborts is followed by the shell's `Aborted` line. Arguments that the
script's shell would split or expand are refused.

The replica's record holds 3 cases of `pairreg`: 2 identical to FSL, 1 where both refuse alike.
The clean room's holds 5: 4 within its thresholds, 1 refused alike.

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

How each of `pairreg`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-flirt/).

## More in the repository {#more}

The API page [docs/api/fsl-flirt.md](repo:docs/api/fsl-flirt.md) holds what `pairreg` shares with the page's other programs:

- [The clean room (part 1, 2026-11-02)](repo:docs/api/fsl-flirt.md#the-clean-room-part-1-2026-11-02)
- [Defects of the original, corrected by default](repo:docs/api/fsl-flirt.md#defects-of-the-original-corrected-by-default)
- [Not yet](repo:docs/api/fsl-flirt.md#not-yet)
- [History](repo:docs/api/fsl-flirt.md#history)
