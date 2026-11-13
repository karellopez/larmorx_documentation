---
title: "`convert_xfm`"
kicker: "Programs · FSL"
lede: "`convert_xfm` is FLIRT's matrix tool: it inverts a 4 × 4 matrix (`-inverse`), composes two (`-concat`) and gives a matrix another's scales and skews (`-fixscaleskew`)."
description: "LARMORX reference for FSL 6.0.7.23 `convert_xfm`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl convert_xfm"
  python: "lx.fsl.convert_xfm"
  api: "docs/api/fsl-flirt.md"
  evidence: "/evidence/fsl-flirt/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "24c23485c8957683"
    crates/larmorx-fsl/src/cli/convert_xfm.rs: "04725ca060b5ef97"
    docs/api/fsl-flirt.md: "abc8e4a5001ff9ef"
    python/larmorx/fsl/flirt.py: "185eb1b0aa54582c"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

It applies
`-fixscaleskew` first, then `-concat` (that matrix times the input), then `-inverse`, and writes
the result (`-omat`).

## Command line {#command-line}

```text synopsis
larmorx fsl convert_xfm [options] <input-matrix-filename>
```

Everything after `larmorx fsl convert_xfm` is the original's command line: the arguments of FSL 6.0.7.23's `convert_xfm`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl convert_xfm ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>convert_xfm</code>'s usage text, as the clean room prints it</summary>

```text
convert_xfm (Version 2.1)
Tool for manipulating FSL transformation matrices
Copyright(c) 1999-2007, University of Oxford (Mark Jenkinson)

Usage: convert_xfm [options] <input-matrix-filename>
  e.g. convert_xfm -omat <outmat> -inverse <inmat>
       convert_xfm -omat <outmat_AtoC> -concat <mat_BtoC> <mat_AtoB>

  Available options are:
        -omat <matrix-filename>            (4x4 ascii format)
        -concat <second-matrix-filename>
        -fixscaleskew <second-matrix-filename>
        -inverse                           (Reference image must be the one originally used)
        -help
```

</details>

## Python {#python}

```python
lx.fsl.convert_xfm(
    matrix: Any,
    *,
    concat: Any = None,
    fix_scale_skew: Any = None,
    inverse: bool = False,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
) -> np.ndarray
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`).

FSL's `convert_xfm`: `matrix` (4 x 4 array or file) with `fix_scale_skew`'s scales and skews, then `concat @ matrix`, then inverted; returned as a 4 x 4 array (as FSL writes it: 10 significant digits).

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `convert_xfm` accepts (`crates/larmorx-fsl/src/cli/convert_xfm.rs`) and the arguments of `lx.fsl.convert_xfm` (`python/larmorx/fsl/flirt.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">convert&#95;xfm</span></code> option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#60;input&#45;matrix&#45;filename&#62;</span></code> | <code><span class="nw">matrix</span></code> |  | a 4 × 4 array or a matrix file |
| <code><span class="nw">&#45;omat</span></code> | the result |  | <span class="opt-help">FSL: “(4x4 ascii format)”</span> |
| <code><span class="nw">&#45;concat</span></code> | <code><span class="nw">concat</span></code> | <code><span class="nw">None</span></code> |  |
| <code><span class="nw">&#45;fixscaleskew</span></code> | <code><span class="nw">fix&#95;scale&#95;skew</span></code> | <code><span class="nw">None</span></code> |  |
| <code><span class="nw">&#45;inverse</span></code> | <code><span class="nw">inverse&#61;True</span></code> | <code><span class="nw">False</span></code> | <span class="opt-help">FSL: “(Reference image must be the one originally used)”</span> |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;verbose</span></code>, <code><span class="nw">&#45;help</span></code> | command line only |  |  |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl convert_xfm ...`); `lx.fsl.convert_xfm` takes `n_threads` and `implementation` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all), given to the program as <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code>; the result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;fsl&#46;convert&#95;xfm</span></code> takes no <code><span class="nw">upstream&#95;defects</span></code>. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `epi2t1.mat` (the identity as a 4 × 4 text matrix). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# The inverse of a FLIRT matrix.
inv = lx.fsl.convert_xfm("epi2t1.mat", inverse=True)
inv.shape  # -> (4, 4)
```

```bash
larmorx fsl convert_xfm -omat t12epi.mat -inverse epi2t1.mat
```

## Ports {#ports}

`convert_xfm` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-flirt-replica](repo:docs/validation/fsl-flirt-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-flirt](repo:docs/validation/fsl-flirt.md) |

Both ports are complete. The replica is translated from FSL 6.0.7.23's source, giving FSL's results
byte for byte. In the
clean room, `convert_xfm`'s messages are FSL's, and `-fixscaleskew` aborts where its decomposition
does not solve (a zero scale or a non-finite entry), as `avscale` does.

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

How each of `convert_xfm`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-flirt/).

## More in the repository {#more}

The API page [docs/api/fsl-flirt.md](repo:docs/api/fsl-flirt.md) holds what `convert_xfm` shares with the page's other programs:

- [The clean room (part 1, 2026-11-02)](repo:docs/api/fsl-flirt.md#the-clean-room-part-1-2026-11-02)
- [Defects of the original, corrected by default](repo:docs/api/fsl-flirt.md#defects-of-the-original-corrected-by-default)
- [Not yet](repo:docs/api/fsl-flirt.md#not-yet)
- [History](repo:docs/api/fsl-flirt.md#history)
