---
title: "`applytopup`"
kicker: "Programs · FSL"
description: "LARMORX reference for FSL 6.0.7.23 `applytopup`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl applytopup"
  python: "lx.fsl.applytopup"
  api: "docs/api/fsl-topup.md"
  evidence: "/evidence/fsl-topup/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "be80bfe4fac23290"
    crates/larmorx-fsl/src/cli/applytopup.rs: "6c753c57a27b935e"
    docs/api/fsl-topup.md: "5177b83d500b0c2f"
    python/larmorx/fsl/topup.py: "316784a1d5ebe0d4"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

`applytopup` corrects images with topup's result, by Jacobian modulation of each image or by the
least-squares restoration of pairs with opposite phase encodings.

## Command line {#command-line}

```text synopsis
larmorx fsl applytopup -in=topdn,botup --topup=mytu --inindex=1,2 --out=hifi
larmorx fsl applytopup -in=topdn --topup=mytu --inindex=1 --method=jac --interp=spline --out=hifi
```

Everything after `larmorx fsl applytopup` is the original's command line: the arguments of FSL 6.0.7.23's `applytopup`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl applytopup ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>applytopup</code>'s usage text, as the clean room prints it</summary>

```text
Part of FSL (ID: 2412.6-dirty)
applytopup (Version 1.0)
Copyright(c) 2009, University of Oxford (Jesper Andersson)

Usage: 
applytopup -in=topdn,botup --topup=mytu --inindex=1,2 --out=hifi
applytopup -in=topdn --topup=mytu --inindex=1 --method=jac --interp=spline --out=hifi


Compulsory arguments (You MUST set one or more of):
	-i,--imain	comma separated list of names of input image (to be corrected)
	-a,--datain	name of text file with PE directions/times
	-x,--inindex	comma separated list of indicies into --datain of the input image (to be corrected)
	-t,--topup	name of field/movements (from topup)
	-o,--out	basename for output (warped) image

Optional arguments (You may optionally specify one or more of):
	-m,--method	Use jacobian modulation (jac) or least-squares resampling (lsr), default=lsr.
	-n,--interp	interpolation method {trilinear,spline}, default=spline
	-d,--datatype	Force output data type [preserve char short int float double].
	-v,--verbose	switch on diagnostic messages
	-h,--help	display this message
```

</details>

## Python {#python}

```python
lx.fsl.applytopup(
    images: Any,
    acquisition: Any,
    indices: Sequence[int],
    topup_result: Any,
    *,
    method: Literal["lsr", "jac", "vb2D", "vb3D", "vb4D"] = "lsr",
    interp: Literal["spline", "trilinear"] = "spline",
    datatype: Literal["preserve", "char", "short", "int", "float", "double"] | None = None,
    verbose: bool = False,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
) -> ApplytopupResult
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

Correct `images` with topup's field (FSL's `applytopup`).

FSL's settings are the call's (CLAUDE.md rule 6): the outputs are NIfTI-1 read back, and no FSL
variable of the process reaches the program.

Its result, `ApplytopupResult`, holds what `applytopup` wrote.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">corrected</span></code> | <code><span class="nw">Image</span></code> | The corrected image (<code><span class="nw">&#45;&#45;out</span></code>). |
| <code><span class="nw">stdout</span></code> | <code><span class="nw">str</span></code> | applytopup's standard output (the <code><span class="nw">vb&#42;</span></code> methods print their iterations). |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `applytopup` accepts (`crates/larmorx-fsl/src/cli/applytopup.rs`) and the arguments of `lx.fsl.applytopup` (`python/larmorx/fsl/topup.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">applytopup</span></code> option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;i</span></code>, <code><span class="nw">&#45;&#45;imain</span></code> | <code><span class="nw">images</span></code> |  | one image or a list of them (3D or 4D, one grid)<span class="opt-help">FSL: “comma separated list of names of input image (to be corrected)”</span> |
| <code><span class="nw">&#45;a</span></code>, <code><span class="nw">&#45;&#45;datain</span></code> | <code><span class="nw">acquisition</span></code> |  | as topup's<span class="opt-help">FSL: “name of text file with PE directions/times”</span> |
| <code><span class="nw">&#45;x</span></code>, <code><span class="nw">&#45;&#45;inindex</span></code> | <code><span class="nw">indices</span></code> |  | each image's row of <code><span class="nw">acquisition</span></code> (1-based)<span class="opt-help">FSL: “comma separated list of indicies into --datain of the input image (to be corrected)”</span> |
| <code><span class="nw">&#45;t</span></code>, <code><span class="nw">&#45;&#45;topup</span></code> | <code><span class="nw">topup&#95;result</span></code> |  | a <code><span class="nw">TopupResult</span></code>, a field image in Hz, or the base name of topup's files (without extension)<span class="opt-help">FSL: “name of field/movements (from topup)”</span> |
| <code><span class="nw">&#45;o</span></code>, <code><span class="nw">&#45;&#45;out</span></code> | the result |  | the corrected image<span class="opt-help">FSL: “basename for output (warped) image”</span> |
| <code><span class="nw">&#45;m</span></code>, <code><span class="nw">&#45;&#45;method</span></code> | <code><span class="nw">method</span></code> | <code><span class="nw">&#34;lsr&#34;</span></code> | <code><span class="nw">&#34;lsr&#34;</span></code> (least-squares restoration of opposite phase encodings), <code><span class="nw">&#34;jac&#34;</span></code> (Jacobian modulation), <code><span class="nw">&#34;vb2D&#34;</span></code>, <code><span class="nw">&#34;vb3D&#34;</span></code>, <code><span class="nw">&#34;vb4D&#34;</span></code> (undocumented variational-Bayes restorations)<span class="opt-help">FSL: “Use jacobian modulation (jac) or least-squares resampling (lsr), default=lsr.”</span> |
| <code><span class="nw">&#45;n</span></code>, <code><span class="nw">&#45;&#45;interp</span></code> | <code><span class="nw">interp</span></code> | <code><span class="nw">&#34;spline&#34;</span></code> | <code><span class="nw">&#34;spline&#34;</span></code> (default) or <code><span class="nw">&#34;trilinear&#34;</span></code><span class="opt-help">FSL: “interpolation method {trilinear,spline}, default=spline”</span> |
| <code><span class="nw">&#45;d</span></code>, <code><span class="nw">&#45;&#45;datatype</span></code> | <code><span class="nw">datatype</span></code> | <code><span class="nw">None</span></code> | <code><span class="nw">&#34;preserve&#34;</span></code>, <code><span class="nw">&#34;char&#34;</span></code>, <code><span class="nw">&#34;short&#34;</span></code>, <code><span class="nw">&#34;int&#34;</span></code>, <code><span class="nw">&#34;float&#34;</span></code> (default), <code><span class="nw">&#34;double&#34;</span></code><span class="opt-help">FSL: “Force output data type [preserve char short int float double].”</span> |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> | <code><span class="nw">verbose&#61;True</span></code> | <code><span class="nw">False</span></code> | (applytopup prints nothing more)<span class="opt-help">FSL: “switch on diagnostic messages”</span> |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | command line only |  | <span class="opt-help">FSL: “display this message”</span> |
| <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | threads of the resampling; the results do not depend on it |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | as topup's |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl applytopup ...`) and are arguments of `lx.fsl.applytopup`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all); the results do not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects corrected, or FSL's behaviour (<code><span class="nw">docs&#47;api&#47;fsl&#45;topup&#46;md</span></code>, "Defects of the original, corrected by default"). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `b0.nii.gz` (a synthetic series of 4 such heads), `acqp.txt` (the phase encodings of four volumes, two along +y and two along −y, read out in 0.05 s). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

r = lx.fsl.topup("b0.nii.gz", "acqp.txt", warpres=20, subsamp=2, miter=2, estmov=False)
# Each volume corrected by Jacobian modulation, with topup's result.
c = lx.fsl.applytopup("b0.nii.gz", "acqp.txt", [1], r, method="jac")
c.corrected.shape  # -> (40, 48, 40, 4)
```

```bash
larmorx fsl topup --imain=b0 --datain=acqp.txt --warpres=20 --subsamp=2 --miter=2 --estmov=0 --out=tu
larmorx fsl applytopup --imain=b0 --datain=acqp.txt --inindex=1 --topup=tu --method=jac --out=b0_corrected
```

## Ports {#ports}

`applytopup` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-topup-replica](repo:docs/validation/fsl-topup-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-topup](repo:docs/validation/fsl-topup.md) |

Both ports are complete (`specs/topup.md` §2 to §10): applytopup's every method (`lsr`, `jac`,
`vb2D`, `vb3D`, `vb4D`; lines of 30, 32 and 96 voxels), data type and failure, each compared file
by file with FSL's. The replica's record holds 75 cases of `applytopup`: 48 identical to FSL, 25
where both refuse alike, 2 refused in both modes. The clean room's holds 75: 44 within its
thresholds, 25 refused alike, 6 expected divergences ([the records](repo:docs/api/fsl-topup.md#the-records) say why). The
clean room's `lsr` on ds005040's pair takes 0.13 s on one thread and 0.04 s on 14 (FSL 0.42 s, the
replica 3.47 s).

FSL is distributed under the FSL Licence (non-commercial use only), so each program has two
ports, a replica and a clean room, in different packages ([licensing](repo:docs/licensing.md)):

- **The replica** is bit-exact: `larmorx-nc fsl topup` and `fsl applytopup`, in the package
  `larmorx-nc` (`crates-nc/larmorx-nc-topup`), under the FSL Licence's terms, translated from
  FSL's source with the B-spline fields, sparse matrices, non-linear optimisers and warps of FSL's
  libraries.
- **The clean room** is in the main package (Apache-2.0, crate `larmorx-fsl`, module `topup`),
  written from [`specs/topup.md`](repo:specs/topup.md) without FSL's source.

`implementation="auto"` (the default) runs the replica when `larmorx-nc` is installed (`pip
install larmorx-nc`) and the clean room otherwise; `"replica"` needs `larmorx-nc` (otherwise
`ReplicaNotFoundError`); `"clean-room"` (`"original"`, 0.1.0rc1's spelling, still works) always
runs the clean room. The command line chooses alike (`--implementation` before the family, or
`LARMORX_IMPLEMENTATION`).

## Evidence {#evidence}

How each of `applytopup`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-topup/).

## More in the repository {#more}

The API page [docs/api/fsl-topup.md](repo:docs/api/fsl-topup.md) holds what `applytopup` shares with the page's other programs:

- [The records](repo:docs/api/fsl-topup.md#the-records)
- [FSL's settings files without FSL](repo:docs/api/fsl-topup.md#fsls-settings-files-without-fsl)
- [LARMORX's own settings](repo:docs/api/fsl-topup.md#larmorxs-own-settings)
- [File names on Windows](repo:docs/api/fsl-topup.md#file-names-on-windows)
- [The clean room](repo:docs/api/fsl-topup.md#the-clean-room)
- [Defects of the original, corrected by default](repo:docs/api/fsl-topup.md#defects-of-the-original-corrected-by-default)
- [Not yet](repo:docs/api/fsl-topup.md#not-yet)
- [History](repo:docs/api/fsl-topup.md#history)
