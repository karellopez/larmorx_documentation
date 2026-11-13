---
title: "`makerot`"
kicker: "Programs · FSL"
description: "LARMORX reference for FSL 6.0.7.23 `makerot`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl makerot"
  python: "lx.fsl.makerot"
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
    crates/larmorx-fsl/src/cli/makerot.rs: "35208189e514b135"
    docs/api/fsl-flirt.md: "abc8e4a5001ff9ef"
    python/larmorx/fsl/flirt_tools.py: "a0b788dabe4a5b66"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

`makerot` writes the 4 × 4 matrix of a rotation by `theta` degrees about an axis through a centre
(or through the centre of an image).

## Command line {#command-line}

```text synopsis
larmorx fsl makerot [options] --theta=angle
```

Everything after `larmorx fsl makerot` is the original's command line: the arguments of FSL 6.0.7.23's `makerot`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl makerot ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>makerot</code>'s usage text, as the clean room prints it</summary>

```text
Part of FSL (ID: 2412.6-dirty)
makerot 
Copyright(c) 2003, University of Oxford (Mark Jenkinson)

Usage: 
makerot [options] --theta=angle

Compulsory arguments (You MUST set one or more of):
	-t,--theta	angle of rotation (in degrees)

Optional arguments (You may optionally specify one or more of):
	-a,--axis <ax,ay,az>	unnormalised axis vector (comma separated)
	--cov	image filename used for centre of volume
	-c,--centre <cx,cy,cz>	centre of rotation in mm (comma separated)
	-o,--out	output filename for matrix
	-v,--verbose	switch on diagnostic messages
	-h,--help	display this message
```

</details>

## Python {#python}

```python
lx.fsl.makerot(
    theta: float,
    axis: Any = None,
    centre: Any = None,
    *,
    cov: Any = None,
    n_threads: int = 1,
    upstream_defects: UpstreamDefectsName = "fix",
    implementation: ImplementationName = "auto",
) -> np.ndarray
```

Where `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`; `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`).

FSL's `makerot`: the 4 x 4 matrix of a rotation by `theta` degrees about `axis` (three values of any length, z by default) through `centre` (mm, the origin by default), or through the centre of the image `cov` (half its extent in mm). The axis is divided by its length (FSL divides by the square root of it, FSL-76; `upstream_defects="reproduce"` gives FSL's matrix); an axis or centre of other than three values is an error here (FSL-77 is about the command line, where one word holds them).

The result is a 4 × 4 array.

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `makerot` accepts (`crates/larmorx-fsl/src/cli/makerot.rs`) and the arguments of `lx.fsl.makerot` (`python/larmorx/fsl/flirt_tools.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">makerot</span></code> option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;t</span></code>, <code><span class="nw">&#45;&#45;theta</span></code> | <code><span class="nw">theta</span></code> |  | degrees<span class="opt-help">FSL: “angle of rotation (in degrees)”</span> |
| <code><span class="nw">&#45;a</span></code>, <code><span class="nw">&#45;&#45;axis</span></code> | <code><span class="nw">axis</span></code> | <code><span class="nw">None</span></code> | three values; divided by its length (FSL by its square root: **FSL-76**, corrected by default)<span class="opt-help">FSL: “unnormalised axis vector (comma separated)”</span> |
| <code><span class="nw">&#45;c</span></code>, <code><span class="nw">&#45;&#45;centre</span></code> | <code><span class="nw">centre</span></code> | <code><span class="nw">None</span></code> | three values<span class="opt-help">FSL: “centre of rotation in mm (comma separated)”</span> |
| <code><span class="nw">&#45;&#45;cov</span></code> | <code><span class="nw">cov</span></code> | <code><span class="nw">None</span></code> | an image: the rotation's centre is its centre<span class="opt-help">FSL: “image filename used for centre of volume”</span> |
| <code><span class="nw">&#45;o</span></code>, <code><span class="nw">&#45;&#45;out</span></code> | the result |  | <span class="opt-help">FSL: “output filename for matrix”</span> |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code>, <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | command line only |  | <span class="opt-help">FSL: “switch on diagnostic messages”</span><span class="opt-help">FSL: “display this message”</span> |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl makerot ...`) and are arguments of `lx.fsl.makerot`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all), given to the program as <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code>; the result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects corrected, or FSL's behaviour (<code><span class="nw">docs&#47;api&#47;fsl&#45;flirt&#46;md</span></code>, "Defects of the original, corrected by default"). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder. The command lines run as `python -m larmorx`.

```python
import larmorx as lx

r = lx.fsl.makerot(30, axis=(1, 2, 3), centre=(4, 5, 6))
r.shape  # -> (4, 4)
```

```bash
larmorx fsl makerot -t 30 -a 1,2,3 -c 4,5,6 -o rot.mat
```

## Ports {#ports}

`makerot` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-flirt-replica](repo:docs/validation/fsl-flirt-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-flirt](repo:docs/validation/fsl-flirt.md) |

Both ports are complete (`specs/flirt.md` §15.4): FSL-76 corrected by default (FSL's matrix with
`reproduce`, named), FSL-77 refused by default (FSL's reading with `reproduce`, named in both
modes). Where FSL aborts, they print the same lines and exit with status 1.

The replica's record holds 14 cases of `makerot`: 8 identical to FSL, 6 where both refuse or abort
alike. The clean room's holds 14: 8 identical to FSL in every byte of text and file, 6 where both
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

How each of `makerot`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-flirt/).

## More in the repository {#more}

The API page [docs/api/fsl-flirt.md](repo:docs/api/fsl-flirt.md) holds what `makerot` shares with the page's other programs:

- [The clean room (part 1, 2026-11-02)](repo:docs/api/fsl-flirt.md#the-clean-room-part-1-2026-11-02)
- [Defects of the original, corrected by default](repo:docs/api/fsl-flirt.md#defects-of-the-original-corrected-by-default)
- [Not yet](repo:docs/api/fsl-flirt.md#not-yet)
- [History](repo:docs/api/fsl-flirt.md#history)
