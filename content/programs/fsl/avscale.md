---
title: "`avscale`"
kicker: "Programs · FSL"
lede: "`avscale` decomposes a FLIRT matrix."
description: "LARMORX reference for FSL 6.0.7.23 `avscale`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl avscale"
  python: "lx.fsl.avscale"
  api: "docs/api/fsl-flirt.md"
  evidence: "/evidence/fsl-flirt/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "fa776d2ea0a17487"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "34429cb924a382b4"
    crates/larmorx-fsl/src/cli/avscale.rs: "5dea0b58ae04b62c"
    docs/api/fsl-flirt.md: "7d546a158684c299"
    python/larmorx/fsl/flirt_tools.py: "3a8443985d099472"
    validation/tools.toml: "f0750687390307f1"
---

## What it does {#what-it-does}

It prints the rotation-and-translation matrix, the angles
and translations (about the volume's centre of gravity), the scales, skews and their average,
the determinant and left-right order, the half transforms (the matrix's square root) and, with
`--inverteddies`, the eddy-current inversion's matrices.

## Command line {#command-line}

```text synopsis
larmorx fsl avscale [--allparams/--inverteddies] matrixfile [non-reference-volume]
```

Everything after `larmorx fsl avscale` is the original's command line: the arguments of FSL 6.0.7.23's `avscale`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl avscale ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>avscale</code>'s usage text, as the clean room prints it</summary>

```text
Usage: avscale [--allparams/--inverteddies] matrixfile [non-reference-volume]
```

</details>

## Python {#python}

```python
lx.fsl.avscale(
    matrix: Any,
    volume: Any = None,
    *,
    all_params: bool = False,
    inverted_eddies: bool = False,
    implementation: ImplementationName = "auto",
) -> AvscaleResult
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`).

FSL's `avscale`: `matrix` (4 x 4 array or file) decomposed, its translations about the centre of gravity of `volume` (a path or `Image`; the origin without one). `all_params` also returns the rotation angles and translations; `inverted_eddies` the eddy-current inversion (the two options are exclusive, as on the command line).

`matrix` is a 4 × 4 array or a matrix file, `volume` a path or an `lx.Image`. The result, an
`AvscaleResult`, holds what the program prints, parsed (FSL prints 6 decimals or 6 significant
digits, and so does it).

Its result, `AvscaleResult`, holds `avscale`'s decomposition of `matrix` (`matrix = rotation * skew * scale`, the rotation's angles about x, y, z in radians and the translation about `centre`), as it prints them (6 decimals): the rotation-and-translation matrix, the angles and translations (`all_params`), scales, skews, their average, the determinant, whether the left-right order is kept, and the two half transforms; with `inverted_eddies` the check matrix and the inverted eddy-current matrix. `stdout` is the program's text.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">rotation&#95;translation</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">rotations</span></code> | <code><span class="nw">np&#46;ndarray</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">translations</span></code> | <code><span class="nw">np&#46;ndarray</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">scales</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">skews</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">average&#95;scale</span></code> | <code><span class="nw">float</span></code> |  |
| <code><span class="nw">determinant</span></code> | <code><span class="nw">float</span></code> |  |
| <code><span class="nw">left&#95;right&#95;preserved</span></code> | <code><span class="nw">bool</span></code> |  |
| <code><span class="nw">forward&#95;half</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">backward&#95;half</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">matrix&#95;check</span></code> | <code><span class="nw">np&#46;ndarray</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">inverted&#95;eddy</span></code> | <code><span class="nw">np&#46;ndarray</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">stdout</span></code> | <code><span class="nw">str</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `avscale` accepts (`crates/larmorx-fsl/src/cli/avscale.rs`) and the arguments of `lx.fsl.avscale` (`python/larmorx/fsl/flirt_tools.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">avscale</span></code> option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">matrixfile</span></code> <code><span class="nw">&#91;non&#45;reference&#45;volume&#93;</span></code> | <code><span class="nw">matrix</span></code>, <code><span class="nw">volume</span></code> | <code><span class="nw">volume&#61;None</span></code> |  |
| <code><span class="nw">&#45;&#45;allparams</span></code> | <code><span class="nw">all&#95;params&#61;True</span></code> | <code><span class="nw">False</span></code> | also the rotation angles and translations |
| <code><span class="nw">&#45;&#45;inverteddies</span></code> | <code><span class="nw">inverted&#95;eddies&#61;True</span></code> | <code><span class="nw">False</span></code> | the eddy-current inversion; exclusive with <code><span class="nw">&#45;&#45;allparams</span></code> |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl avscale ...`); `lx.fsl.avscale` takes `implementation` as an argument, and the others are the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;fsl&#46;avscale</span></code> takes no <code><span class="nw">n&#95;threads</span></code>. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>). The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;fsl&#46;avscale</span></code> takes no <code><span class="nw">upstream&#95;defects</span></code>. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `bold2t1.mat` (the identity as a 4 × 4 text matrix), `boldref.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

d = lx.fsl.avscale("bold2t1.mat", "boldref.nii.gz", all_params=True)
d.scales, d.rotations, d.determinant, d.forward_half
```

```bash
larmorx fsl avscale --allparams bold2t1.mat boldref.nii.gz
```

## Ports {#ports}

`avscale` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-flirt-replica](repo:docs/validation/fsl-flirt-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-flirt](repo:docs/validation/fsl-flirt.md) |

Both ports are complete: every option, usage, message, exit status and failure case of
`specs/flirt.md` §15.1 to §15.4 (where FSL aborts, the same lines and exit status 1). The clean
room's record holds 66 cases of `avscale`, the coordinate programs, `rmsdiff` and `makerot`: 39
identical to FSL in every byte of text and file, 27 more where both refuse or abort alike. One
more matrix of the findings (a reflection's `--inverteddies` check) differs in the sign of a 1e-10
residual. A matrix of 4 rows that is not 4 × 4, where FSL aborts at a determinant, an inverse or a
product, is refused (FSL prints part of its output first).

FSL's licence allows non-commercial use only, so each of FLIRT's programs has two ports, a
replica and a clean room, in different packages ([licensing](repo:docs/licensing.md) says what each
package holds):

- **The replica** is translated from FSL's source. The package `larmorx-nc` holds it (`crates-nc/`),
  under the FSL Licence's terms, and `larmorx` runs it as a separate program, `larmorx-nc fsl
  <program>`, when `larmorx-nc` is installed (`pip install larmorx-nc`).
- **The clean room** is written from [`specs/flirt.md`](repo:specs/flirt.md) by an implementer who
  never read FSL's source or the replica. It is part of `larmorx`, under Apache-2.0
  (`crates/larmorx-fsl`, with its [PROVENANCE](repo:crates/larmorx-fsl/PROVENANCE.md), section
  "FLIRT"), and runs on the main package's clean-room registration engine, shared with
  `lx.mri.hmc`.

`implementation="auto"` runs the replica when `larmorx-nc` is installed, and the clean room
otherwise. `"replica"` and `"clean-room"` choose one (`"original"`, 0.1.0rc1's spelling of
`"clean-room"`, still works); `"clean-room"` runs the clean room in this process. On the command
line, `--implementation auto|replica|clean-room` before the family chooses alike, from the next
release; in 0.1.0rc1 the variable `LARMORX_IMPLEMENTATION` chooses (`original` for the clean
room).

## Evidence {#evidence}

How each of `avscale`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-flirt/).

## More in the repository {#more}

The API page [docs/api/fsl-flirt.md](repo:docs/api/fsl-flirt.md) holds what `avscale` shares with the page's other programs:

- [FLIRT's other programs and scripts (part 3)](repo:docs/api/fsl-flirt.md#flirts-other-programs-and-scripts-part-3)
- [The clean-room original (part 1, 2026-11-02)](repo:docs/api/fsl-flirt.md#the-clean-room-original-part-1-2026-11-02)
- [Upstream defects (D13)](repo:docs/api/fsl-flirt.md#upstream-defects-d13)
- [Not yet](repo:docs/api/fsl-flirt.md#not-yet)
- [History](repo:docs/api/fsl-flirt.md#history)
