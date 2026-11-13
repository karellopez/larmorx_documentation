---
title: "`sdcflows`"
kicker: "Programs · sdcflows"
lede: "`sdcflows` finds the field-map estimators of a BIDS dataset (PEPOLAR, direct and fieldmap-less), runs their workflows and writes their derivatives: ``` larmorx sdcflows sdcflows <bids_dir> <output_dir> participant [options] ``` It is a Python program: the `larmorx` (or `lx`) command the Python package installs runs it (`python -m larmorx` too); the standalone Rust binary lists it and says so (exit status 127)."
description: "LARMORX reference for sdcflows 2.17.1 `sdcflows`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: sdcflows
  original: "sdcflows 2.17.1"
  software: "sdcflows"
  command: "larmorx sdcflows sdcflows"
  python: "lx.sdcflows.run_app"
  api: "docs/api/sdcflows-fieldmap.md"
  evidence: "/evidence/sdcflows-estimation/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "24c23485c8957683"
    docs/api/sdcflows-fieldmap.md: "f80fef53d3d8b3c6"
    python/larmorx/sdcflows/app.py: "09204dc892fed513"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

Every option of sdcflows' parser is there, through Python's own `argparse` as sdcflows uses it, so
the usage, help and error messages are argparse's of the Python that runs it (as sdcflows' are);
the program's name in them is `sdcflows`.

## Command line {#command-line}

```text synopsis
larmorx sdcflows sdcflows [-h] [-v]
                          [--participant-label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
                          [--session-label [SESSION_LABEL ...]]
                          [--bids-filter-file PATH]
                          [--bids-database-dir PATH]
                          [--bids-database-wipe] [--nprocs NPROCS]
                          [--omp-nthreads OMP_NTHREADS]
                          [--mem-gb MEMORY_GB] [--debug] [--pdb]
                          [--sloppy] [-w WORK_DIR] [-n] [--no-fmapless]
                          [--use-plugin USE_PLUGIN] [--notrack]
                          bids_dir output_dir {participant,group}
                          [{participant,group} ...]
```

Everything after `larmorx sdcflows sdcflows` is the original's command line: the arguments of sdcflows 2.17.1's `sdcflows`, as sdcflows takes them. LARMORX's own options stand between `larmorx` and the family `sdcflows`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        sdcflows sdcflows ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

## Python {#python}

```python
lx.sdcflows.run_app(
    argv: Sequence[str] | None = None,
    *,
    upstream_defects: UpstreamDefectsName | None = None,
    env: Mapping[str, str] | None = None,
) -> int
```

Where `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

Run sdcflows' command line with `argv` (its arguments, without the program's name; by default `sys.argv[1:]`) and return its exit status: 0, argparse's 2, 64 when no estimator was found (`os.EX_USAGE`), 1 for an error (its message on standard error). `upstream_defects` defaults to `LARMORX_UPSTREAM_DEFECTS` (else `"fix"`); `env` is the environment the run reads (by default `os.environ`: `OMP_NUM_THREADS`, `TEMPLATEFLOW_HOME`, `FSLDIR`, `LARMORX_IMPLEMENTATION`, `LARMORX_SDCFLOWS_LIBRARIES`).

Runs the program with `argv` (the arguments without the program's name) and returns its exit
status; `upstream_defects` defaults to `LARMORX_UPSTREAM_DEFECTS`, `env` is the environment it
reads (default `os.environ`). The Python functions under it:

| Python (`lx.sdcflows`) | sdcflows | Notes |
|---|---|---|
| `run_app(argv=None, *, upstream_defects=None, env=None)` → exit status | `sdcflows.cli.main:main` | `argv` without the program's name; `upstream_defects` defaults to `LARMORX_UPSTREAM_DEFECTS`; `env` the environment it reads (default `os.environ`) |
| `sdcflows_workflow(layout, *, output_dir, participant_label=None, work_dir=None, fmapless=True, sessions=None, bids_filters=None, omp_nthreads=1, sloppy=False, debug=False, logger=None, upstream_defects="fix", n_threads=1, **workflow_options)` → `SdcflowsWorkflow(subjects, estimators, workflows, output_dir, work_dir, upstream_defects, n_threads)` (`.all_estimators`, `.run()` → one `EstimatorRun` per estimator) | `init_sdcflows_wf` | the participants (`lx.niworkflows.collect_participants`), their estimators (`find_estimators`; a registry per participant: SDC-36), each one's workflow (`estimator_workflow`); `.run()` runs them in order with their derivatives, the first failure stops it (nipype's `stop_on_first_crash`); the app gives `sessions`, `bids_filters`, `sloppy`, `debug` (SDC-30 to SDC-32) and the libraries, implementations and `fsldir` as `workflow_options` |
| `larmorx.sdcflows.app.build_parser`, `parse_args`, `AppSettings` (`EnvironmentSettings`, `ExecutionSettings`, `WorkflowSettings`, `NipypeSettings`; `.get()`, `.dumps()`), `toml_dumps` | `cli/parser.py`'s `_parser`, `parse_args`; `config.py`'s sections, `get`, `dumps` | one settings object per run (no module-wide state) |
| `lx.niworkflows.collect_participants(bids_dir, participant_label=None, strict=False, bids_validate=True)`, `BIDSError`, `BIDSWarning` | niworkflows 1.15.4 `utils/bids.py` | |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `sdcflows` accepts (`python/larmorx/sdcflows/app.py`) and the arguments of `lx.sdcflows.run_app` (`python/larmorx/sdcflows/app.py`), whose defaults and descriptions are taken from it. Under each option, in grey, sdcflows's own help for it.

| <code><span class="nw">sdcflows</span></code> | Python (<code><span class="nw">run&#95;app</span></code>) | What (and <code><span class="nw">sdcflows&#95;workflow</span></code>'s argument) |
|---|---|---|
| <code><span class="nw">bids&#95;dir</span></code> | <code><span class="nw">argv</span></code> | the dataset (argparse's <code><span class="nw">Path</span> <span class="nw">does</span> <span class="nw">not</span> <span class="nw">exist&#58;</span> <span class="nw">&#60;&#46;&#46;&#46;&#62;&#46;</span></code> otherwise), indexed with the app's ignore patterns (only <code><span class="nw">sub&#45;&#60;label&#62;</span></code> folders, without <code><span class="nw">beh</span></code>, <code><span class="nw">pet</span></code>, <code><span class="nw">perf</span></code>, <code><span class="nw">meg</span></code>, <code><span class="nw">eeg</span></code>, <code><span class="nw">ieeg</span></code>, <code><span class="nw">micr</span></code>, <code><span class="nw">nirs</span></code>), without the BIDS validator; no <code><span class="nw">dataset&#95;description&#46;json</span></code>: pybids' <code><span class="nw">BIDSValidationError</span></code> (exit status 1) (<code><span class="nw">sdcflows&#95;workflow&#40;layout&#44;</span> <span class="nw">&#46;&#46;&#46;&#41;</span></code>) |
| <code><span class="nw">output&#95;dir</span></code> | <code><span class="nw">argv</span></code> | the derivatives in <code><span class="nw">output&#95;dir&#47;sdcflows&#47;sub&#45;&#60;label&#62;&#47;fmap&#47;</span></code> (as <code><span class="nw">init&#95;fmap&#95;derivatives&#95;wf</span></code> writes them, named by all the estimator's sources), and an empty <code><span class="nw">logs&#47;</span></code>; the same folder as <code><span class="nw">bids&#95;dir</span></code>: argparse's error with sdcflows' suggestion (<code><span class="nw">&#60;bids&#95;dir&#62;&#47;derivatives&#47;sdcflows&#95;2&#46;17&#46;1</span></code>) (<code><span class="nw">sdcflows&#95;workflow</span></code>'s <code><span class="nw">output&#95;dir&#61;</span></code>) |
| <code><span class="nw">analysis&#95;level</span></code> (<code><span class="nw">participant</span></code>, <code><span class="nw">group</span></code>, one or more) | <code><span class="nw">argv</span></code> | only <code><span class="nw">participant</span></code>; <code><span class="nw">group</span></code>: sdcflows' <code><span class="nw">ValueError&#58;</span> <span class="nw">Analysis</span> <span class="nw">level</span> <span class="nw">can</span> <span class="nw">only</span> <span class="nw">be</span> <span class="nw">&#39;participant&#39;</span></code> (exit status 1) |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | <code><span class="nw">argv</span></code> | the usage and the help (argparse's, exit status 0)<span class="opt-help">sdcflows: “show this help message and exit”</span> |
| <code><span class="nw">&#45;&#45;version</span></code> | <code><span class="nw">argv</span></code> | <code><span class="nw">SDCFlows</span> <span class="nw">2&#46;17&#46;1</span></code> |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> (repeated) | <code><span class="nw">argv</span></code> | the log level, 25 less 5 per <code><span class="nw">&#45;v</span></code> (10 from <code><span class="nw">&#45;vvv</span></code>): sdcflows' <code><span class="nw">cli</span></code> lines on standard output in its format (<code><span class="nw">&#60;yymmdd&#45;HH&#58;MM&#58;SS&#62;&#44;&#60;ms&#62;</span> <span class="nw">cli</span> <span class="nw">IMPORTANT&#58;</span></code> then the message: "Running SDCFlows 2.17.1: ...", "Finished all workload"), the search's debug lines at <code><span class="nw">&#45;vvv</span></code> (<code><span class="nw">sdcflows&#95;workflow</span></code>'s <code><span class="nw">logger&#61;</span></code>)<span class="opt-help">sdcflows: “Increases log verbosity for each occurrence, debug level is -vvv.”</span> |
| <code><span class="nw">&#45;&#45;participant&#45;label</span></code> | <code><span class="nw">argv</span></code> | labels with or without <code><span class="nw">sub&#45;</span></code>, sorted and unique; labels not in the dataset: argparse's error (sorted: SDC-34); the indexed folders are those whose name starts with a label's (sdcflows' pattern: <code><span class="nw">01</span></code> also indexes <code><span class="nw">sub&#45;010</span></code>) (<code><span class="nw">sdcflows&#95;workflow</span></code>'s <code><span class="nw">participant&#95;label&#61;</span></code>)<span class="opt-help">sdcflows: “A space delimited list of participant identifiers or a single identifier (the sub- prefix can be removed).”</span> |
| <code><span class="nw">&#45;&#45;session&#45;label</span></code> | <code><span class="nw">argv</span></code> | SDC-30 (<code><span class="nw">sdcflows&#95;workflow</span></code>'s <code><span class="nw">sessions&#61;</span></code>)<span class="opt-help">sdcflows: “Filter input dataset by session label.”</span> |
| <code><span class="nw">&#45;&#45;bids&#45;filter&#45;file</span> <span class="nw">PATH</span></code> | <code><span class="nw">argv</span></code> | SDC-31, SDC-33 (<code><span class="nw">sdcflows&#95;workflow</span></code>'s <code><span class="nw">bids&#95;filters&#61;</span></code> (the file's <code><span class="nw">fmap</span></code> entry))<span class="opt-help">sdcflows: “a JSON file describing custom BIDS input filter using pybids {&lt;suffix&gt;:{&lt;entity&gt;:&lt;filter&gt;,...},...} (https://github.com/bids-standard/pybids/blob/master/bids/layout/config/bids.json)”</span> |
| <code><span class="nw">&#45;&#45;bids&#45;database&#45;dir</span> <span class="nw">PATH</span></code> | <code><span class="nw">argv</span></code> | must exist (argparse's error); pybids' database is not read: the dataset is indexed again, in memory, and no database is written (sdcflows writes one in <code><span class="nw">output&#95;dir&#47;&#46;bids&#95;db</span></code> or <code><span class="nw">work&#95;dir&#47;&#46;bids&#95;db&#45;&#60;run&#62;</span></code>)<span class="opt-help">sdcflows: “Path to an existing PyBIDS database folder, for faster indexing (especially useful for large datasets).”</span> |
| <code><span class="nw">&#45;&#45;bids&#45;database&#45;wipe</span></code> | <code><span class="nw">argv</span></code> | recorded (no database)<span class="opt-help">sdcflows: “Wipe out previously existing BIDS indexing caches, forcing re-indexing.”</span> |
| <code><span class="nw">&#45;&#45;nprocs</span> <span class="nw">N</span></code> | <code><span class="nw">argv</span></code> | at least 1 (argparse's <code><span class="nw">Argument</span> <span class="nw">can&#39;t</span> <span class="nw">be</span> <span class="nw">less</span> <span class="nw">than</span> <span class="nw">one&#46;</span></code>; a non-integer: <code><span class="nw">invalid</span> <span class="nw">&#95;min&#95;one</span> <span class="nw">value</span></code>, SDC-34); recorded: the estimators run one after the other (nipype runs <code><span class="nw">N</span></code> processes at once; the results are the same); <code><span class="nw">1</span> <span class="nw">&#60;</span> <span class="nw">N</span> <span class="nw">&#60;</span> <span class="nw">&#45;&#45;omp&#45;nthreads</span></code>: sdcflows' warning "Per-process threads (--omp-nthreads=...) exceed total threads (--nthreads/--n_cpus=...)"<span class="opt-help">sdcflows: “Maximum number of simultaneously running parallel processes executed by *SDCFlows* (e.g., several instances of ANTs' registration). However, when `<code><span class="nw">&#45;&#45;nprocs</span></code><code><span class="nw">is</span> <span class="nw">greater</span> <span class="nw">or</span> <span class="nw">equal</span> <span class="nw">to</span> <span class="nw">the</span></code><code><span class="nw">&#45;&#45;omp&#45;nthreads</span></code><code><span class="nw">option&#44;</span> <span class="nw">it</span> <span class="nw">also</span> <span class="nw">sets</span> <span class="nw">the</span> <span class="nw">maximum</span> <span class="nw">number</span> <span class="nw">of</span> <span class="nw">threads</span> <span class="nw">that</span> <span class="nw">simultaneously</span> <span class="nw">running</span> <span class="nw">processes</span> <span class="nw">may</span> <span class="nw">aggregate</span> <span class="nw">&#40;meaning&#44;</span> <span class="nw">with</span></code><code><span class="nw">&#45;&#45;nprocs</span> <span class="nw">16</span> <span class="nw">&#45;&#45;omp&#45;nthreads</span> <span class="nw">8</span></code><code><span class="nw">a</span> <span class="nw">maximum</span> <span class="nw">of</span> <span class="nw">two</span> <span class="nw">8&#45;CPU&#45;threaded</span> <span class="nw">processes</span> <span class="nw">will</span> <span class="nw">be</span> <span class="nw">running</span> <span class="nw">at</span> <span class="nw">a</span> <span class="nw">given</span> <span class="nw">time&#41;&#46;</span> <span class="nw">Under</span> <span class="nw">this</span> <span class="nw">mode</span> <span class="nw">of</span> <span class="nw">operation&#44;</span></code><code><span class="nw">&#45;&#45;nprocs</span></code><code><span class="nw">sets</span> <span class="nw">the</span> <span class="nw">maximum</span> <span class="nw">number</span> <span class="nw">of</span> <span class="nw">processors</span> <span class="nw">that</span> <span class="nw">can</span> <span class="nw">be</span> <span class="nw">assigned</span> <span class="nw">work</span> <span class="nw">within</span> <span class="nw">an</span> <span class="nw">&#42;SDCFlows&#42;</span> <span class="nw">job&#44;</span> <span class="nw">which</span> <span class="nw">includes</span> <span class="nw">all</span> <span class="nw">the</span> <span class="nw">processors</span> <span class="nw">used</span> <span class="nw">by</span> <span class="nw">currently</span> <span class="nw">running</span> <span class="nw">single&#45;</span> <span class="nw">and</span> <span class="nw">multi&#45;threaded</span> <span class="nw">processes&#46;</span> <span class="nw">If</span></code><code><span class="nw">None</span></code>`, the number of CPUs available will be automatically assigned (which may not be what you want in, e.g., shared systems like a HPC cluster.”</span> |
| <code><span class="nw">&#45;&#45;omp&#45;nthreads</span> <span class="nw">N</span></code> | <code><span class="nw">argv</span></code> | each step's threads (default <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code>, else the CPUs) (<code><span class="nw">sdcflows&#95;workflow</span></code>'s <code><span class="nw">omp&#95;nthreads&#61;</span></code>, <code><span class="nw">n&#95;threads&#61;</span></code>)<span class="opt-help">sdcflows: “Maximum number of threads that multi-threaded processes executed by *SDCFlows* (e.g., ANTs' registration) can use. If `<code><span class="nw">None</span></code>`, the number of CPUs available will be automatically assigned (which may not be what you want in, e.g., shared systems like a HPC cluster.”</span> |
| <code><span class="nw">&#45;&#45;mem&#45;gb</span></code> | <code><span class="nw">argv</span></code> | sdcflows' units (<code><span class="nw">G</span></code> by default, <code><span class="nw">T</span></code>, <code><span class="nw">M</span></code>, <code><span class="nw">K</span></code>, <code><span class="nw">B</span></code>, powers of ten); recorded, nipype's memory limit has no counterpart; SDC-33<span class="opt-help">sdcflows: “Upper bound memory limit for SDCFlows processes.”</span> |
| <code><span class="nw">&#45;&#45;debug</span></code>, <code><span class="nw">&#45;&#45;sloppy</span></code> | <code><span class="nw">argv</span></code> | SDC-32 (<code><span class="nw">sdcflows&#95;workflow</span></code>'s <code><span class="nw">debug&#61;</span></code>, <code><span class="nw">sloppy&#61;</span></code>)<span class="opt-help">sdcflows: “Enable changes to processing to aid in debugging”</span><span class="opt-help">sdcflows: “Use sloppy mode for minimal footprint.”</span> |
| <code><span class="nw">&#45;&#45;pdb</span></code> | <code><span class="nw">argv</span></code> | an error prints Python's whole traceback (and a blank line), and opens <code><span class="nw">pdb</span></code> on it when standard input, output and error are terminals (niworkflows' <code><span class="nw">setup&#95;exceptionhook</span></code>); nipype's <code><span class="nw">Linear</span></code> plugin recorded<span class="opt-help">sdcflows: “Open Python debugger (pdb) on exceptions.”</span> |
| <code><span class="nw">&#45;w</span></code>, <code><span class="nw">&#45;&#45;work&#45;dir</span></code> | <code><span class="nw">argv</span></code> | default <code><span class="nw">&#46;&#47;work</span></code>: the nodes' files (<code><span class="nw">sdcflows&#95;wf&#47;wf&#95;&#60;id&#62;&#47;</span></code>, <code><span class="nw">sdcflows&#95;wf&#47;fmap&#95;derivatives&#95;&#60;id&#62;&#47;</span></code>) and the run's settings, <code><span class="nw">&#46;sdcflows&#46;&#60;8</span> <span class="nw">characters&#62;&#46;toml</span></code> (sdcflows' sections and keys, written as toml 0.10.2 writes them: <code><span class="nw">toml&#95;dumps</span></code>; <code><span class="nw">&#91;environment&#93;</span></code> without nipype's and TemplateFlow's versions, with <code><span class="nw">larmorx&#95;version</span></code>; <code><span class="nw">bids&#95;database&#95;dir</span></code> only when given); inside <code><span class="nw">bids&#95;dir</span></code>: argparse's error (<code><span class="nw">sdcflows&#95;workflow</span></code>'s <code><span class="nw">work&#95;dir&#61;</span></code>)<span class="opt-help">sdcflows: “Path where intermediate results should be stored.”</span> |
| <code><span class="nw">&#45;n</span></code>, <code><span class="nw">&#45;&#45;dry&#45;run</span></code> | <code><span class="nw">argv</span></code> | the estimators listed, as sdcflows lists them (each participant, each estimator, each source's phase-encoding direction and path), exit status 0<span class="opt-help">sdcflows: “only find estimable fieldmaps (that is, estimation is not triggered)”</span> |
| <code><span class="nw">&#45;&#45;no&#45;fmapless</span></code> | <code><span class="nw">argv</span></code> | no fieldmap-less estimators; with them (the default): SDC-29 (<code><span class="nw">sdcflows&#95;workflow</span></code>'s <code><span class="nw">fmapless&#61;False</span></code>)<span class="opt-help">sdcflows: “Allow fieldmap-less estimation”</span> |
| <code><span class="nw">&#45;&#45;use&#45;plugin</span> <span class="nw">FILE</span></code> | <code><span class="nw">argv</span></code> | SDC-35, SDC-33<span class="opt-help">sdcflows: “Nipype plugin configuration file.”</span> |
| <code><span class="nw">&#45;&#45;notrack</span></code> | <code><span class="nw">argv</span></code> | recorded; larmorx never sends usage information<span class="opt-help">sdcflows: “Opt-out of sending tracking information of this run to the NiPreps developers. This information helps to improve SDCFlows and provides an indicator of real world usage for obtaining funding.”</span> |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">fix</span></code> (default) or <code><span class="nw">reproduce</span></code> (D13) (<code><span class="nw">sdcflows&#95;workflow</span></code>'s <code><span class="nw">upstream&#95;defects&#61;</span></code>) |
| (larmorx's own) <code><span class="nw">&#45;&#45;implementation</span></code> (before the family) or <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> | <code><span class="nw">env</span></code> | <code><span class="nw">auto</span></code> (default), <code><span class="nw">replica</span></code>, <code><span class="nw">clean&#45;room</span></code> (<code><span class="nw">original</span></code>, 0.1.0rc1's spelling, still works): FSL's <code><span class="nw">prelude</span></code> and <code><span class="nw">topup</span></code>, AFNI's <code><span class="nw">3dvolreg</span></code> (<code><span class="nw">sdcflows&#95;workflow</span></code>'s <code><span class="nw">prelude&#95;implementation&#61;</span></code>, <code><span class="nw">topup&#95;implementation&#61;</span></code>, <code><span class="nw">volreg&#95;implementation&#61;</span></code>) |
| <code><span class="nw">LARMORX&#95;SDCFLOWS&#95;LIBRARIES</span></code> | <code><span class="nw">env</span></code> | <code><span class="nw">newest</span></code> (numpy 2.5.4, SciPy 1.18.1, LAPACK 3.12.1; default) or <code><span class="nw">shared</span></code> (numpy 2.3.5, SciPy 1.15.3, LAPACK 3.12.0) (<code><span class="nw">sdcflows&#95;workflow</span></code>'s <code><span class="nw">numpy&#95;version&#61;</span></code>, <code><span class="nw">scipy&#95;version&#61;</span></code>; nibabel's <code><span class="nw">set&#95;qform</span></code> LAPACK (<code><span class="nw">larmorx&#46;io&#46;nibabel&#95;header&#46;use&#95;lapack</span></code>, for the run)) |
| <code><span class="nw">FSLDIR</span></code> | <code><span class="nw">env</span></code> | FSL's topup configurations (decision D9: <code><span class="nw">topup&#95;config&#95;file</span></code>) (<code><span class="nw">sdcflows&#95;workflow</span></code>'s <code><span class="nw">fsldir&#61;</span></code>) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `sdcflows` on the command line (`larmorx --n-threads 4 sdcflows sdcflows ...`); `lx.sdcflows.run_app` takes `upstream_defects` as an argument, and the others are the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;sdcflows&#46;run&#95;app</span></code> takes no <code><span class="nw">n&#95;threads</span></code>. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>). The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;sdcflows&#46;run&#95;app</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;None</span></code> | The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `ds` (a BIDS dataset of one participant with two PEPOLAR images and a BOLD run (a folder)). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# The estimators of a dataset with two PEPOLAR images, listed without running them.
lx.sdcflows.run_app(["ds", "out", "participant", "--dry-run", "-w", "work"])  # -> 0
```

```bash
larmorx sdcflows sdcflows --version
larmorx sdcflows sdcflows ds out participant --dry-run -w work
```

## Ports {#ports}

`sdcflows` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [sdcflows-estimation](repo:docs/validation/sdcflows-estimation.md), [sdcflows-estimation-full](repo:docs/validation/sdcflows-estimation-full.md), [sdcflows-estimation-app-shared](repo:docs/validation/sdcflows-estimation-app-shared.md) |

**The replica: status `validated`** against sdcflows 2.17.1 (its records:
[sdcflows-estimation](repo:docs/validation/sdcflows-estimation.md), 2026-11-09, 19 cases;
[sdcflows-estimation-full](repo:docs/validation/sdcflows-estimation-full.md), 2026-11-09, 14 cases, the
BIDS app run whole on each of sdcflows 2.17.1's eight own runs among them;
[sdcflows-estimation-app-shared](repo:docs/validation/sdcflows-estimation-app-shared.md), 2026-11-09, 8
cases, the same eight runs on numpy 2.3.5 and SciPy 1.15.3: every case passes).

Checked (`validation/investigations/sdcflows-fieldmap-b/check_app.py`, sdcflows 2.17.1's own
program in its own process per run): the parser on 58 command lines, the settings file's text
(toml 0.10.2), `parse_args`' checks and folders in 16 runs, `--dry-run`'s listing on 57 datasets
and settings, the exit statuses, all identical with `reproduce` (the defaults as the corrections
above say); whole runs on ds005752's direct field map and ds001600's four estimators (sdcflows'
programs through the oracle cache, larmorx's replicas): all 25 derivative files byte for byte
(the [findings](repo:docs/findings/sdcflows-estimation.md)).

Not reproduced, on purpose: nipype (its plugins, scheduler, node messages and crash files),
pybids' database, the telemetry, the reports' figures (decision D7: larmorprepx's reports part).
sdcflows replaces Python's `warnings.warn` for the whole run, and its warnings go nowhere: the
ported libraries' warnings are hidden the same way, larmorx's notices of corrected or reproduced
defects (D13) are shown on standard error.

sdcflows' BIDS app, the `sdcflows` program, has one port, in `pip install larmorx` (a Python
program of the Python package, not of the standalone `larmorx` program): **the replica**
(`python/larmorx/sdcflows/app.py`; Apache-2.0), ported whole from sdcflows 2.17.1's
`cli/parser.py`, `cli/main.py`, `cli/workflow.py`, `config.py` and `workflows/fit/base.py`'s
`init_sdcflows_wf`. The nipype interfaces of the sections before have no program of their own
(nipype has no original arguments for them), as for the resampler.

## Evidence {#evidence}

How each of `sdcflows`'s ports was measured against sdcflows, case by case: [its evidence](/evidence/sdcflows-estimation/).

## More in the repository {#more}

The API page [docs/api/sdcflows-fieldmap.md](repo:docs/api/sdcflows-fieldmap.md) holds what `sdcflows` shares with the page's other programs:

- [Quick start](repo:docs/api/sdcflows-fieldmap.md#quick-start)
- [The B-spline grid and its weights](repo:docs/api/sdcflows-fieldmap.md#the-b-spline-grid-and-its-weights)
- [bspline_approx: BSplineApprox](repo:docs/api/sdcflows-fieldmap.md#bspline_approx-bsplineapprox)
- [The field given by its coefficients](repo:docs/api/sdcflows-fieldmap.md#the-field-given-by-its-coefficients)
- [The phase-difference preparation](repo:docs/api/sdcflows-fieldmap.md#the-phase-difference-preparation)
- [The brain-extraction, magnitude and field-map workflows (part B)](repo:docs/api/sdcflows-fieldmap.md#the-brain-extraction-magnitude-and-field-map-workflows-part-b)
- [A quick EPI mask: epi_mask (part B)](repo:docs/api/sdcflows-fieldmap.md#a-quick-epi-mask-epi_mask-part-b)
- [The PEPOLAR estimation (part B)](repo:docs/api/sdcflows-fieldmap.md#the-pepolar-estimation-part-b)
- [The PEPOLAR estimation with 3dQwarp: its Python steps (part B)](repo:docs/api/sdcflows-fieldmap.md#the-pepolar-estimation-with-3dqwarp-its-python-steps-part-b)
- [Unwarping an EPI with the coefficients: unwarp_workflow (part B)](repo:docs/api/sdcflows-fieldmap.md#unwarping-an-epi-with-the-coefficients-unwarp_workflow-part-b)
- [The field map's registration to the EPI (part B)](repo:docs/api/sdcflows-fieldmap.md#the-field-maps-registration-to-the-epi-part-b)
- [The fieldmap-less (SyN) preprocessing (part B)](repo:docs/api/sdcflows-fieldmap.md#the-fieldmap-less-syn-preprocessing-part-b)
- [The fieldmap-less (SyN) estimation (part B)](repo:docs/api/sdcflows-fieldmap.md#the-fieldmap-less-syn-estimation-part-b)
- [The estimators of a BIDS dataset (part B)](repo:docs/api/sdcflows-fieldmap.md#the-estimators-of-a-bids-dataset-part-b)
- [The estimators' workflows and their derivatives (part B)](repo:docs/api/sdcflows-fieldmap.md#the-estimators-workflows-and-their-derivatives-part-b)
- [Upstream defects (D13)](repo:docs/api/sdcflows-fieldmap.md#upstream-defects-d13)
- [Rust API](repo:docs/api/sdcflows-fieldmap.md#rust-api)
- [Differences and limits](repo:docs/api/sdcflows-fieldmap.md#differences-and-limits)
