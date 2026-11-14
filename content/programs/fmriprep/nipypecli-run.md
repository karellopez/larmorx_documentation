---
title: "`nipypecli run`"
kicker: "Programs · fMRIPrep"
lede: "`nipypecli run` lists a module's interfaces, prints an interface's help, and runs one interface from the shell, in the current folder."
description: "LARMORX reference for nipype 1.12.0 `nipypecli run`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fmriprep
  original: "nipype 1.12.0"
  software: "nipype"
  command: "larmorx nipype run"
  python: "lx.nipype.run"
  api: "docs/api/nipype-run.md"
  evidence: "/evidence/confounds/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "bf883da07a0caa93"
    docs/api/nipype-run.md: "50047e270afff29e"
    python/larmorx/nipype/_run.py: "1257e62ec85512cb"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

larmorx's gives the same arguments, listing, help, printed
inputs and outputs, files, messages and exit statuses as nipype's own command line (nipype 1.12.0
with niworkflows 1.15.4 and fMRIPrep 25.2.7, the newest releases), checked case by case against
it, for the modules of fMRIPrep's confound estimation:
| Module | Interfaces larmorx runs | Listed, not run |
|---|---|---|
| `nipype.algorithms.confounds` | `ACompCor`, `CompCor`, `TCompCor`, `ComputeDVARS`, `FramewiseDisplacement`, `NonSteadyStateDetector`, `TSNR` | `BaseInterface`, `SimpleInterface` (nipype's base classes) |
| `niworkflows.interfaces.confounds` | `ExpandModel`, `SpikeRegressors`, `NormalizeMotionParams`, `FSLMotionParams`, `FSLRMSDeviation`, `FramewiseDisplacement` | `SimpleInterface` |
| `niworkflows.interfaces.images` | `SignalExtraction`, `RegridToZooms` | `Conform`, `TemplateDimensions` (not ported), `IntraModalMerge`, `RobustAverage` (ported, below), `SimpleInterface` |
| `niworkflows.interfaces.morphology` | `BinaryDilation`, `BinarySubtraction` | `SimpleInterface` |
| `niworkflows.interfaces.nibabel` | `ApplyMask`, `Binarize`, `IntensityClip`, `MergeSeries`, `ReorientImage`, `RegridToZooms`, `GenerateSamplingReference` | `BinaryDilation` (nibabel's, deprecated by niworkflows), `DemeanImage`, `FilledImageLike`, `MapLabels`, `MergeROIs`, `SplitSeries`, `SimpleInterface` |
| `niworkflows.interfaces.utility` | `AddTSVHeader`, `DictMerge`, `TSV2JSON` | `JoinTSVColumns`, `KeySelect` (nipype cannot instantiate it without fields), `BaseInterface`, `SimpleInterface` |
| `niworkflows.interfaces.bold` | `NonsteadyStatesDetector` | `SimpleInterface` |
| `niworkflows.interfaces.patches` | `RobustACompCor`, `RobustTCompCor` | `FreeSurferSource` |
| `fmriprep.interfaces.confounds` | `aCompCorMasks`, `FSLMotionParams`, `FSLRMSDeviation`, `FramewiseDisplacement`, `FilterDropped`, `RenameACompCor`, `GatherConfounds` | `FMRISummary` (a report: with larmorprepx's reports), `SimpleInterface` |

37 interfaces of the 61 these modules hold. Each runs through the larmorx function that ports it
(the confounds' [docs/api/confounds.md](repo:docs/api/confounds.md), niworkflows' helpers
[docs/api/niworkflows-helpers.md](repo:docs/api/niworkflows-helpers.md)), with the newest libraries' arithmetic
(numpy 2.5.4, SciPy 1.18.1, pandas 3.0.6). An interface that is listed but not run prints its
help as nipype does; running it is an error (`error: larmorx has not ported ...`, exit status 1).
`IntraModalMerge` and `RobustAverage` are ported (`lx.niworkflows.intra_modal_merge`,
`robust_average`) but not run here yet: they run FSL's `mcflirt` and AFNI's `3dvolreg` as
programs whose messages nipype relays through its log, line by line, which larmorx's ports in this
process do not print (a follow-up).

## Command line {#command-line}

```text synopsis
larmorx nipype run [--list] <module> [<Interface> [inputs]]
```

Everything after `larmorx nipype run` is the original's command line: the arguments of nipype 1.12.0's `nipypecli run`, as nipype takes them. LARMORX's own options stand between `larmorx` and the family `fmriprep`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        nipype run ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

## Python {#python}

```python
lx.nipype.run(
    argv: Sequence[str] | None = None,
    *,
    prog: str = "larmorx nipype run",
    upstream_defects: str | None = None,
    n_threads: int | None = None,
    env: Mapping[str, str] | None = None,
) -> int
```

`nipypecli run` with `argv` (its arguments: `[--list] <module> [<Interface> [inputs]]`; by default `sys.argv[1:]`) and return its exit status: 0, 2 for a usage error (click's or argparse's), 1 for an error (nipype's traceback as its first and last lines on standard error). The interface runs in the current folder, which receives its files. `prog` is the command's name in its messages (nipype's `nipypecli run`); `upstream_defects` defaults to `LARMORX_UPSTREAM_DEFECTS` (else `"fix"`), `n_threads` to `OMP_NUM_THREADS` (else every logical CPU; the results do not depend on it); `env` is the environment read (by default `os.environ`).

Runs `nipypecli run` with `argv` (the arguments after `run`; by default `sys.argv[1:]`) and
returns its exit status: 0, 2 for a usage error (click's or argparse's), 1 for an error. It
writes to `sys.stdout` and `sys.stderr`, and the interface's files to the current folder.

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `nipypecli run` accepts (`python/larmorx/nipype/_run.py`) and the arguments of `lx.nipype.run` (`python/larmorx/nipype/_run.py`), whose defaults and descriptions are taken from it. Under each option, in grey, nipype's own help for it.

| nipype's option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;&#45;list</span></code> | <code><span class="nw">argv</span></code> | <code><span class="nw">None</span></code> | <code><span class="nw">Available</span> <span class="nw">Interfaces&#58;</span></code> and the names of the interface classes in the module's namespace, sorted (those it imports included), four blanks before each; the same as the module alone |
| (the module, the interface and its inputs) | <code><span class="nw">argv</span></code> | <code><span class="nw">None</span></code> | the module alone lists its interfaces, an interface alone prints its help; its inputs: the mandatory inputs positional, in name order (lists with one or more values), the others <code><span class="nw">&#45;&#45;name</span> <span class="nw">value</span></code> (lists with zero or more), booleans <code><span class="nw">&#45;&#45;name</span></code> (they set true) |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | <code><span class="nw">argv</span></code> | <code><span class="nw">None</span></code> | a flag the command never reads (click's): <code><span class="nw">run</span> <span class="nw">&#60;module&#62;</span> <span class="nw">&#60;Interface&#62;</span> <span class="nw">&#45;h</span></code> prints the help because the flag leaves no input; <code><span class="nw">&#45;&#45;</span></code> passes <code><span class="nw">&#45;h</span></code> to argparse |
| (the command's name) | <code><span class="nw">prog</span></code> | <code><span class="nw">&#34;larmorx</span> <span class="nw">nipype</span> <span class="nw">run&#34;</span></code> | the name in the messages (nipype's is <code><span class="nw">nipypecli</span> <span class="nw">run</span></code>) |
| (the environment) | <code><span class="nw">env</span></code> | <code><span class="nw">None</span></code> | the environment read (default <code><span class="nw">os&#46;environ</span></code>) |
| <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">None</span></code> | the threads of larmorx's computations (the results do not depend on them); default every logical CPU |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">None</span></code> | <code><span class="nw">fix</span></code> (the default) or <code><span class="nw">reproduce</span></code>: D13's mode, which also chooses how the command line itself behaves ([The defects of nipype's command line](repo:docs/api/nipype-run.md#the-defects-of-nipypes-command-line)) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fmriprep` on the command line (`larmorx --n-threads 4 nipype run ...`); `lx.nipype.run` takes `n_threads` and `upstream_defects` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;None</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">None</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;nipype&#46;run</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;None</span></code> | The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `bold.nii.gz` (a synthetic series of 4 such heads). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# nipype's TSNR on a series: the mean, the standard deviation and their ratio, in this folder.
lx.nipype.run(["nipype.algorithms.confounds", "TSNR", "bold.nii.gz"])  # -> 0
```

```bash
larmorx nipype run --list nipype.algorithms.confounds
larmorx nipype run nipype.algorithms.confounds TSNR bold.nii.gz
```

## Ports {#ports}

`nipypecli run` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | experimental | [confounds-nipype](repo:docs/validation/confounds-nipype.md) |

**The replica: status `experimental`**, checked against nipype's own `nipypecli run`
(`validation/investigations/confounds/check_nipype_cli.py`, the newest environment; finding
[confounds-nipype-cli.md](repo:docs/findings/confounds-nipype-cli.md)): the exit status, standard
output, standard error and every file written, byte for byte, with `reproduce`, and with the
default (identical but where a correction applies: then against nipype's interface run through its
Python API on the same inputs); the click layer, all 61 helps at two widths, argparse's and traits'
errors, every interface larmorx runs with its options, and fMRIPrep's real calls of the confounds
nodes of three reference runs (single-band, multiband with 280 volumes, multi-echo): 226 of 226
cases, 51 real calls among them (15 of which nipype's command line refuses: PIPE-81, PIPE-82); the
parity suite `confounds-nipype` runs the check as its cases `cli-quick-e1` and `cli-full-e1`
(the record [confounds-nipype](repo:docs/validation/confounds-nipype.md), standard tier, 2026-11-13: 25 of 25
cases, `cli-quick-e1` among them, 18 of 18 checks). The
golden case `cli.nipype.run`; `tests/python/test_nipype_run.py`.

`nipypecli run` has one port, in `pip install larmorx` (a Python program of the Python package,
not of the standalone `larmorx` program): **the replica** (`python/larmorx/nipype/`;
Apache-2.0 AND BSD-3-Clause), ported from nipype 1.12.0's `scripts/cli.py` and the parts of nipype
it runs, with niworkflows 1.15.4 and fMRIPrep 25.2.7's interfaces (the newest releases).

## Evidence {#evidence}

How each of `nipypecli run`'s ports was measured against nipype, case by case: [its evidence](/evidence/confounds/).

## More in the repository {#more}

The API page [docs/api/nipype-run.md](repo:docs/api/nipype-run.md) holds what `nipypecli run` shares with the page's other programs:

- [The command line](repo:docs/api/nipype-run.md#the-command-line)
- [The defects of nipype's command line](repo:docs/api/nipype-run.md#the-defects-of-nipypes-command-line)
- [The other Python functions](repo:docs/api/nipype-run.md#the-other-python-functions)
- [How it is built and checked](repo:docs/api/nipype-run.md#how-it-is-built-and-checked)
