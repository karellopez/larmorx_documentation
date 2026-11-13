---
title: "`midtrans`"
kicker: "Programs · FSL"
lede: "`midtrans` finds the transform from a template space to the \"middle\" of several transforms into that space."
description: "LARMORX reference for FSL 6.0.7.23 `midtrans`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl midtrans"
  python: "lx.fsl.midtrans"
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
    crates/larmorx-fsl/src/cli/midtrans.rs: "13276bf6cb0507f0"
    docs/api/fsl-flirt.md: "21d456bedacfd6a2"
    python/larmorx/fsl/flirt_more.py: "64de6a5439fd3ed6"
    validation/tools.toml: "f0750687390307f1"
---

## What it does {#what-it-does}

The middle is FSL's Procrustes average of the transforms, about the MNI origin or about
the centre of gravity of a template image (`--template`). With `--separate`, each transform
composed with it is written too.

## Command line {#command-line}

```text synopsis
larmorx fsl midtrans [options] transform1 transform2 ... transformN
```

Everything after `larmorx fsl midtrans` is the original's command line: the arguments of FSL 6.0.7.23's `midtrans`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl midtrans ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>midtrans</code>'s usage text, as the clean room prints it</summary>

```text
Part of FSL (ID: 2412.6-dirty)
midtrans 
Copyright(c) 2010, University of Oxford (Mark Jenkinson)

Usage: 
midtrans [options] transform1 transform2 ... transformN
  e.g. midtrans -o temp2mid.mat A2temp.mat B2temp.mat C2temp.mat
       midtrans -o C2mid.mat A2C.mat B2C.mat ident.mat

Optional arguments (You may optionally specify one or more of):
	-o,--out	output filename for matrix
	--template	input filename for template image (needed for fix origin)
	--separate	basename for output of separate matrices (final name includes a number; e.g. img2mid0001.mat)
	--debug	switch on debugging output
	-v,--verbose	switch on diagnostic messages
	-h,--help	display this message
```

</details>

## Python {#python}

```python
lx.fsl.midtrans(
    transforms: list[Any],
    *,
    template: Any = None,
    separate: str | None = None,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
) -> np.ndarray
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

FSL's `midtrans`: the 4 x 4 transform from the template space of `transforms` (4 x 4 arrays or files, at least two) to their "middle" (FSL's Procrustes average about the MNI origin, or about the centre of gravity of `template`). With `separate` (a path prefix) each transform composed with it is also written to `<separate>0001.mat` and so on.

`transforms` are 4 × 4 arrays or matrix files, at least two; `template` is a path or an `lx.Image`.
The result is the 4 × 4 transform from the template space to the middle.

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `midtrans` accepts (`crates/larmorx-fsl/src/cli/midtrans.rs`) and the arguments of `lx.fsl.midtrans` (`python/larmorx/fsl/flirt_more.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">midtrans</span></code> option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">transform1</span></code> <code><span class="nw">transform2</span></code> <code><span class="nw">&#46;&#46;&#46;</span></code> | <code><span class="nw">transforms</span></code> |  | at least two |
| <code><span class="nw">&#45;o</span></code>, <code><span class="nw">&#45;&#45;out</span></code> | the result |  | <span class="opt-help">FSL: “output filename for matrix”</span> |
| <code><span class="nw">&#45;&#45;template</span></code> | <code><span class="nw">template</span></code> | <code><span class="nw">None</span></code> | an image: the average about its centre of gravity (about the MNI origin without one)<span class="opt-help">FSL: “input filename for template image (needed for fix origin)”</span> |
| <code><span class="nw">&#45;&#45;separate</span></code> | <code><span class="nw">separate</span></code> | <code><span class="nw">None</span></code> | a basename: each transform composed with the middle, written to <code><span class="nw">&#60;basename&#62;0001&#46;mat</span></code> and on<span class="opt-help">FSL: “basename for output of separate matrices (final name includes a number; e.g. img2mid0001.mat)”</span> |
| <code><span class="nw">&#45;&#45;debug</span></code>, <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code>, <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | command line only |  | <code><span class="nw">&#45;v</span></code> and <code><span class="nw">&#45;&#45;debug</span></code> print every stage<span class="opt-help">FSL: “switch on debugging output”</span><span class="opt-help">FSL: “switch on diagnostic messages”</span><span class="opt-help">FSL: “display this message”</span> |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl midtrans ...`); `lx.fsl.midtrans` takes `implementation` and `upstream_defects` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;fsl&#46;midtrans</span></code> takes no <code><span class="nw">n&#95;threads</span></code>. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>). The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects corrected, or FSL's behaviour (<code><span class="nw">docs&#47;api&#47;fsl&#45;flirt&#46;md</span></code>, "Upstream defects"). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `A2temp.mat` (the identity as a 4 × 4 text matrix), `B2temp.mat` (the identity as a 4 × 4 text matrix), `C2temp.mat` (the identity as a 4 × 4 text matrix). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

mid = lx.fsl.midtrans(["A2temp.mat", "B2temp.mat", "C2temp.mat"])
mid.shape  # -> (4, 4)
```

```bash
larmorx fsl midtrans -o temp2mid.mat A2temp.mat B2temp.mat C2temp.mat
```

## Ports {#ports}

`midtrans` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-flirt-replica](repo:docs/validation/fsl-flirt-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-flirt](repo:docs/validation/fsl-flirt.md) |

Both ports are complete: every option, usage, message, exit status and failure case of
`specs/flirt.md` §15.5, with every stage that `-v` and `--debug` print. An error after the
arguments exits with status 1 (FSL exits 0: **FSL-78**, corrected by default and named). The clean
room uses a transform whose determinant is not finite (FSL's test is `|det| < 1e-6`), and refuses
transforms whose averages reach beyond double precision, such as a scale of 1e200 or a translation
of 1e300, with exit status 1 in both modes (**FSL-241**: FSL writes rows of NaN, or reports its
failed decomposition as a matrix-size error, and exits 0).

The replica's record holds 12 cases of `midtrans`: 8 identical to FSL, 4 where both refuse alike.
The clean room's holds 14: 8 within its thresholds, 4 refused alike, and the 2 of FSL-241.

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

How each of `midtrans`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-flirt/).

## More in the repository {#more}

The API page [docs/api/fsl-flirt.md](repo:docs/api/fsl-flirt.md) holds what `midtrans` shares with the page's other programs:

- [The clean room (part 1, 2026-11-02)](repo:docs/api/fsl-flirt.md#the-clean-room-part-1-2026-11-02)
- [Upstream defects (D13)](repo:docs/api/fsl-flirt.md#upstream-defects-d13)
- [Not yet](repo:docs/api/fsl-flirt.md#not-yet)
- [History](repo:docs/api/fsl-flirt.md#history)
