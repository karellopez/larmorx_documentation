---
title: "`avscale`"
kicker: "Programs · FSL"
lede: "`avscale` takes a FLIRT matrix apart: its rotation and translation, angles, scales, skews, determinant and half transforms."
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
    crates/larmorx-core/src/defects.rs: "035dcd92e164879c"
    crates/larmorx-fsl/src/cli/avscale.rs: "5dea0b58ae04b62c"
    docs/api/fsl-flirt.md: "7fe0febecf4edaee"
    python/larmorx/fsl/flirt_tools.py: "dd92d42ca083679f"
    validation/tools.toml: "f0750687390307f1"
---

## What it does {#what-it-does}

The angles and translations are about the volume's centre of
gravity, the half transforms are the matrix's square root, and the scales' average and the
left-right order come with them; with `--inverteddies` it also prints the eddy-current
inversion's matrices.

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

Its result, `AvscaleResult`, holds `avscale`'s decomposition of `matrix` (`matrix = rotation * skew * scale`), as it prints them (6 decimals, or 6 significant digits where FSL prints those).

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">rotation&#95;translation</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | The rotation-and-translation matrix (4 x 4). |
| <code><span class="nw">rotations</span></code> | <code><span class="nw">np&#46;ndarray</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The rotation's angles about x, y and z, in radians (<code><span class="nw">all&#95;params</span></code>; else <code><span class="nw">None</span></code>). |
| <code><span class="nw">translations</span></code> | <code><span class="nw">np&#46;ndarray</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The translation about the centre of gravity of <code><span class="nw">volume</span></code>, or about the origin without one (<code><span class="nw">all&#95;params</span></code>; else <code><span class="nw">None</span></code>). |
| <code><span class="nw">scales</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | The scales along x, y and z. |
| <code><span class="nw">skews</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | The skews. |
| <code><span class="nw">average&#95;scale</span></code> | <code><span class="nw">float</span></code> | The scales' average. |
| <code><span class="nw">determinant</span></code> | <code><span class="nw">float</span></code> | The matrix's determinant. |
| <code><span class="nw">left&#95;right&#95;preserved</span></code> | <code><span class="nw">bool</span></code> | Whether the left-right order is kept. |
| <code><span class="nw">forward&#95;half</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | The forward half transform (the matrix's square root). |
| <code><span class="nw">backward&#95;half</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | The backward half transform. |
| <code><span class="nw">matrix&#95;check</span></code> | <code><span class="nw">np&#46;ndarray</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The check matrix (<code><span class="nw">inverted&#95;eddies</span></code>; else <code><span class="nw">None</span></code>). |
| <code><span class="nw">inverted&#95;eddy</span></code> | <code><span class="nw">np&#46;ndarray</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The inverted eddy-current matrix (<code><span class="nw">inverted&#95;eddies</span></code>; else <code><span class="nw">None</span></code>). |
| <code><span class="nw">stdout</span></code> | <code><span class="nw">str</span></code> | The program's text. |

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

Both ports are complete (`specs/flirt.md` §15.1); where FSL aborts, they print the same lines and
exit with status 1. A matrix of 4 rows that is not 4 × 4, where FSL aborts at a determinant, an
inverse or a product, is refused (FSL prints part of its output first). One more matrix, from
random testing (a reflection's `--inverteddies` check), differs in the sign of a 1e-10 residual.

The replica's record holds 9 cases of `avscale`: 5 identical to FSL, 4 where both refuse or abort
alike. The clean room's holds 9: 5 identical to FSL in every byte of text and file, 4 where both
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

How each of `avscale`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-flirt/).

## More in the repository {#more}

The API page [docs/api/fsl-flirt.md](repo:docs/api/fsl-flirt.md) holds what `avscale` shares with the page's other programs:

- [The clean room (part 1, 2026-11-02)](repo:docs/api/fsl-flirt.md#the-clean-room-part-1-2026-11-02)
- [Defects of the original, corrected by default](repo:docs/api/fsl-flirt.md#defects-of-the-original-corrected-by-default)
- [Not yet](repo:docs/api/fsl-flirt.md#not-yet)
- [History](repo:docs/api/fsl-flirt.md#history)
