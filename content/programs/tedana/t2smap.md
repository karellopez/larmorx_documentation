---
title: "`t2smap`"
kicker: "Programs · tedana"
description: "LARMORX reference for tedana 26.0.3 `t2smap`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: tedana
  original: "tedana 26.0.3"
  software: "tedana"
  command: "larmorx tedana t2smap"
  python: "lx.tedana.t2smap"
  api: "docs/api/tedana-t2smap.md"
  evidence: "/evidence/tedana-t2smap/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-gpl, licence: "GNU GPL version 3", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "bf883da07a0caa93"
    crates/larmorx-tedana/src/cli.rs: "ce00851fe6e9bc07"
    docs/api/tedana-t2smap.md: "26fcb5dca281c1d5"
    python/larmorx/tedana/t2smap.py: "b2d6b751ac619d49"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

`t2smap` estimates the T2* and S0 of multi-echo fMRI voxel by voxel and combines the echoes into
one series.

## Command line {#command-line}

```text synopsis
larmorx tedana t2smap [-h] -d FILE [FILE ...] -e TE [TE ...]
                      [--out-dir PATH] [--prefix PREFIX]
                      [--convention {orig,bids}] [--verbose]
                      [--overwrite] [--mask FILE]
                      [--masktype {dropout,decay,none} [{dropout,decay,none} ...]]
                      [--dummy-scans INT] [--exclude EXCLUDE]
                      [--fittype {loglin,curvefit}]
                      [--fitmode {all,ts}] [--combmode {t2s,paid}]
                      [--n-independent-echos INT] [--n-threads INT]
                      [--debug] [-v]
```

Everything after `larmorx tedana t2smap` is the original's command line: the arguments of tedana 26.0.3's `t2smap`, as tedana takes them. LARMORX's own options stand between `larmorx` and the family `tedana`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        tedana t2smap ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

## Python {#python}

```python
lx.tedana.t2smap(
    echoes: Any,
    echo_times: Sequence[float],
    *,
    mask: Any = None,
    masktype: MaskType | Sequence[MaskType] = "dropout",
    fittype: FitType = "loglin",
    fitmode: FitMode = "all",
    combmode: CombMode = "t2s",
    dummy_scans: int = 0,
    exclude: str | Sequence[int] | None = None,
    n_independent_echos: int | None = None,
    convention: Convention = "bids",
    prefix: str = "",
    verbose: bool = False,
    debug: bool = False,
    quiet: bool = False,
    out_dir: str | os.PathLike[str] | None = None,
    overwrite: bool = False,
    libraries: Libraries = "newest",
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
    n_threads: int = 1,
) -> T2smapResult
```

Where `MaskType` is one of `"dropout"`, `"decay"`, `"none"`; `FitType` is one of `"loglin"`, `"curvefit"`; `FitMode` is one of `"all"`, `"ts"`; `CombMode` is one of `"t2s"`, `"paid"`; `Convention` is one of `"bids"`, `"orig"`; `Libraries` is one of `"newest"`, `"shared"`; `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

tedana's `t2smap`: the T2* and S0 maps of the multi-echo series `echoes` (one image per echo, in ascending order of `echo_times`, `-d`; or one path of a z-concatenated file, the echoes stacked along the third axis, which tedana deprecates) and their optimal combination.

```python
import larmorx as lx

# fMRIPrep's call: three echoes, their times (seconds, or ms as fMRIPrep passes them), a mask
res = lx.tedana.t2smap(
    ["echo-1_bold.nii.gz", "echo-2_bold.nii.gz", "echo-3_bold.nii.gz"],
    [0.014, 0.02996, 0.04592],
    mask="brainmask_dilated.nii.gz",
    fittype="curvefit",
)
res.t2star          # lx.Image, the full T2* map in seconds (fMRIPrep's)
res.optcom          # lx.Image, the optimally combined series (fMRIPrep's)
res.adaptive_mask   # int32: the number of good echoes per voxel
res.fit_failures    # uint8: the voxels whose curve fit failed (they keep the log-linear estimate)
res.confounds["rmse_mean"]   # the fit's error per volume

# tedana's defaults (log-linear fit), the files kept, tedana's original names
res = lx.tedana.t2smap(echoes, tes, mask=mask, out_dir="derivatives/t2smap", convention="orig")
```

```bash
larmorx tedana t2smap -d echo-1.nii.gz echo-2.nii.gz echo-3.nii.gz -e 14.0 29.96 45.92 \
    --mask mask.nii.gz --fittype curvefit --out-dir t2smap
larmorx --implementation clean-room --n-threads 8 tedana t2smap -d echo-1.nii.gz \
    echo-2.nii.gz echo-3.nii.gz -e 14.0 29.96 45.92 --mask mask.nii.gz --out-dir t2smap-cr
```

Inputs are paths or in-memory images (an `lx.Image`, a nibabel image, an `(array, affine)` pair),
written as NIfTI-1 in their own data type to the call's temporary directory. The files are written
to a temporary directory and read back, unless `out_dir` is given (then they stay there, and
tedana refuses to overwrite an existing one unless `overwrite=True`). The result is a
`T2smapResult`: `t2star`, `s0`, `t2star_limited`, `s0_limited`, `optcom`, `adaptive_mask`,
`rmse` (images carrying `implementation`), `confounds` (the table's columns as float64 arrays,
NaN for tedana's `n/a`), `fit_failures`, `t2star_variance`, `s0_variance`,
`t2star_s0_covariance` (or `None`), `dataset_description`, `files` (tedana's registry: each
file's name by its description), `out_dir`, `log` (tedana's log, its standard error without
larmorx's notice lines) and `implementation` (the `larmorx-gpl` replica, or the clean room:
`Implementation(kind="clean-room", package="larmorx", ...)`). A run of the replica that fails
raises `ReplicaError` (a `RuntimeError`) with tedana's messages and exit status; one of the clean
room a `RuntimeError` with the same messages.

Its result, `T2smapResult`, holds what `t2smap` wrote, read back.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">t2star</span></code> | <code><span class="nw">Image</span></code> | The full T2* map in seconds (<code><span class="nw">T2starmap</span></code>): every voxel of the mask, from the echoes the adaptive mask keeps (at least two). fMRIPrep's T2* map. |
| <code><span class="nw">s0</span></code> | <code><span class="nw">Image</span></code> | The full S0 map (<code><span class="nw">S0map</span></code>). |
| <code><span class="nw">t2star&#95;limited</span></code> | <code><span class="nw">Image</span></code> | The limited maps (<code><span class="nw">desc&#45;limited&#95;T2starmap</span></code>, <code><span class="nw">desc&#45;limited&#95;S0map</span></code>): 0 where fewer than two echoes have good signal; the T2* map's outliers capped (above ten times its 99.5th percentile). |
| <code><span class="nw">s0&#95;limited</span></code> | <code><span class="nw">Image</span></code> | The limited maps (<code><span class="nw">desc&#45;limited&#95;T2starmap</span></code>, <code><span class="nw">desc&#45;limited&#95;S0map</span></code>): 0 where fewer than two echoes have good signal; the T2* map's outliers capped (above ten times its 99.5th percentile). |
| <code><span class="nw">optcom</span></code> | <code><span class="nw">Image</span></code> | The optimally combined series (<code><span class="nw">desc&#45;optcom&#95;bold</span></code>), every volume (the excluded ones too, not the dummy scans). fMRIPrep's combined BOLD series. |
| <code><span class="nw">adaptive&#95;mask</span></code> | <code><span class="nw">Image</span></code> | The adaptive mask (<code><span class="nw">desc&#45;adaptiveGoodSignal&#95;mask</span></code>, int32): per voxel the number of echoes with good signal, 0 outside the mask. |
| <code><span class="nw">rmse</span></code> | <code><span class="nw">Image</span></code> | The fit's root-mean-square error per voxel (<code><span class="nw">desc&#45;rmse&#95;statmap</span></code>). |
| <code><span class="nw">confounds</span></code> | <code><span class="nw">dict&#91;str&#44;</span> <span class="nw">np&#46;ndarray&#93;</span></code> | The fit's error per volume (<code><span class="nw">desc&#45;confounds&#95;timeseries&#46;tsv</span></code>): its columns (<code><span class="nw">rmse&#95;mean</span></code>, <code><span class="nw">rmse&#95;std</span></code>, <code><span class="nw">rmse&#95;min</span></code>, <code><span class="nw">rmse&#95;percentile02</span></code> ... <code><span class="nw">rmse&#95;max</span></code>) as float64 arrays, NaN where tedana writes <code><span class="nw">n&#47;a</span></code>. |
| <code><span class="nw">fit&#95;failures</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">fittype&#61;&#34;curvefit&#34;</span></code>: the voxels whose monoexponential fit failed (uint8; they keep the log-linear estimate), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">t2star&#95;variance</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">fittype&#61;&#34;curvefit&#34;</span></code> and <code><span class="nw">verbose&#61;True</span></code>: the fit's variances and covariance, else <code><span class="nw">None</span></code>. |
| <code><span class="nw">s0&#95;variance</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">fittype&#61;&#34;curvefit&#34;</span></code> and <code><span class="nw">verbose&#61;True</span></code>: the fit's variances and covariance, else <code><span class="nw">None</span></code>. |
| <code><span class="nw">t2star&#95;s0&#95;covariance</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">fittype&#61;&#34;curvefit&#34;</span></code> and <code><span class="nw">verbose&#61;True</span></code>: the fit's variances and covariance, else <code><span class="nw">None</span></code>. |
| <code><span class="nw">dataset&#95;description</span></code> | <code><span class="nw">dict&#91;str&#44;</span> <span class="nw">Any&#93;</span></code> | <code><span class="nw">dataset&#95;description&#46;json</span></code>. |
| <code><span class="nw">files</span></code> | <code><span class="nw">dict&#91;str&#44;</span> <span class="nw">str&#93;</span></code> | tedana's output registry: each file's name (relative to <code><span class="nw">out&#95;dir</span></code>) by tedana's description (<code><span class="nw">&#34;t2star</span> <span class="nw">img&#34;</span></code>, <code><span class="nw">&#34;combined</span> <span class="nw">img&#34;</span></code>, ...). |
| <code><span class="nw">out&#95;dir</span></code> | <code><span class="nw">str</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | Where the files are, when <code><span class="nw">out&#95;dir</span></code> was given (else they were removed after reading). |
| <code><span class="nw">log</span></code> | <code><span class="nw">str</span></code> | tedana's log (its standard error, without larmorx's notice lines). |
| <code><span class="nw">implementation</span></code> | <code><span class="nw">&#95;replica&#46;Implementation</span></code> | What computed them (<code><span class="nw">Implementation</span></code>: the <code><span class="nw">larmorx&#45;gpl</span></code> replica, or larmorx's clean room). |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `t2smap` accepts (`crates/larmorx-tedana/src/cli.rs`) and the arguments of `lx.tedana.t2smap` (`python/larmorx/tedana/t2smap.py`), whose defaults and descriptions are taken from it. Under each option, in grey, tedana's own help for it.

| <code><span class="nw">t2smap</span></code> | Python (<code><span class="nw">lx&#46;tedana&#46;t2smap&#40;&#46;&#46;&#46;&#41;</span></code>) | What |
|---|---|---|
| <code><span class="nw">&#45;d</span> <span class="nw">FILE</span> <span class="nw">&#91;FILE</span> <span class="nw">&#46;&#46;&#46;&#93;</span></code> | <code><span class="nw">echoes</span></code> (first argument) | the echoes' series, in ascending order of echo time; one file is a z-concatenated series (the echoes stacked along the third axis: tedana warns that it is deprecated, issue 1313). NIfTI-1 and -2 (<code><span class="nw">&#46;nii</span></code>, <code><span class="nw">&#46;nii&#46;gz</span></code>, pairs), ANALYZE and MGH; other formats nibabel reads (AFNI, MINC, PAR/REC) are refused with a clear message (a documented gap)<span class="opt-help">tedana: “Multi-echo dataset for analysis. A set of echo-specific files in ascending order. The TEs of the data should match the TEs listed in the -e argument.”</span> |
| <code><span class="nw">&#45;e</span> <span class="nw">TE</span> <span class="nw">&#91;TE</span> <span class="nw">&#46;&#46;&#46;&#93;</span></code> | <code><span class="nw">echo&#95;times</span></code> (second argument) | the echo times: seconds when all are below 1 (converted to ms, an INFO line), milliseconds when all are at least 1 (tedana's deprecation warning); otherwise tedana's ValueError<span class="opt-help">tedana: “Ascending echo times in seconds (per BIDS convention). E.g., 0.015 0.039 0.063. Millisecond values (e.g., 15.0 39.0 63.0) are still accepted but deprecated.”</span> |
| <code><span class="nw">&#45;&#45;out&#45;dir</span> <span class="nw">PATH</span></code> | <code><span class="nw">out&#95;dir&#61;None</span></code> | the output directory (created, one level); by default the wrapper's temporary directory<span class="opt-help">tedana: “Output directory.”</span> |
| <code><span class="nw">&#45;&#45;prefix</span> <span class="nw">PREFIX</span></code> | <code><span class="nw">prefix&#61;&#34;&#34;</span></code> | a prefix of every file name (<code><span class="nw">&#95;</span></code> appended unless it ends with one)<span class="opt-help">tedana: “Prefix for filenames generated.”</span> |
| <code><span class="nw">&#45;&#45;convention</span> <span class="nw">&#123;orig&#44;bids&#125;</span></code> | <code><span class="nw">convention&#61;&#34;bids&#34;</span></code> | the files' names: BIDS derivatives 1.5.0, or tedana's original ones (the API page's "Outputs")<span class="opt-help">tedana: “Filenaming convention. "bids" will use the latest BIDS derivatives version.”</span> |
| <code><span class="nw">&#45;&#45;verbose</span></code> | <code><span class="nw">verbose&#61;False</span></code> | with <code><span class="nw">curvefit</span></code>: also the fit's variance and covariance maps<span class="opt-help">tedana: “Generate intermediate and additional files.”</span> |
| <code><span class="nw">&#45;&#45;overwrite</span></code>, <code><span class="nw">&#45;f</span></code> | <code><span class="nw">overwrite&#61;False</span></code> | overwrite existing files (else an existing output stops the run: RuntimeError)<span class="opt-help">tedana: “Force overwriting of files.”</span> |
| <code><span class="nw">&#45;&#45;mask</span> <span class="nw">FILE</span></code> | <code><span class="nw">mask&#61;None</span></code> | the analysis mask (its voxels above 0); without one, nilearn's <code><span class="nw">compute&#95;epi&#95;mask</span></code> of the first echo (a warning: tedana recommends a mask)<span class="opt-help">tedana: “Binary mask of voxels to include in TE Dependent ANAlysis. Must be in the same space as <code><span class="nw">data</span></code>. If an explicit mask is not provided, then Nilearn's compute_epi_mask function will be used to derive a mask from the first echo's data. Providing a mask is recommended.”</span> |
| <code><span class="nw">&#45;&#45;masktype</span> <span class="nw">&#123;dropout&#44;decay&#44;none&#125;</span> <span class="nw">&#46;&#46;&#46;</span></code> | <code><span class="nw">masktype&#61;&#34;dropout&#34;</span></code> (one or several) | the adaptive mask's methods: <code><span class="nw">dropout</span></code> (an echo whose mean signal is below a third of a reference voxel's), <code><span class="nw">decay</span></code> (signal that stops decaying), <code><span class="nw">none</span></code><span class="opt-help">tedana: “Method(s) by which to define the adaptive mask. The adaptive mask starts with the mask from '--mask', when provided. It identifies voxels that have good data in all vs a subset of echoes. "dropout" removes voxels with much lower voxels than other voxels within each echo. "decay" removes voxels where the raw signal does not decay across echoes. Users can specify one, both, or neither of the models.”</span> |
| <code><span class="nw">&#45;&#45;dummy&#45;scans</span> <span class="nw">INT</span></code> | <code><span class="nw">dummy&#95;scans&#61;0</span></code> | volumes removed from the start (also from the combined series)<span class="opt-help">tedana: “Number of dummy scans to remove from the beginning of the data.”</span> |
| <code><span class="nw">&#45;&#45;exclude</span> <span class="nw">EXCLUDE</span></code> | <code><span class="nw">exclude&#61;None</span></code> (tedana's text, <code><span class="nw">&#34;0&#44;5&#58;10&#44;15&#34;</span></code>, or volume indices) | volumes left out of the adaptive mask and the fit, kept in the combination (0-based, ranges end-exclusive; not with <code><span class="nw">&#45;&#45;fitmode</span> <span class="nw">ts</span></code>)<span class="opt-help">tedana: “Volume indices to exclude from adaptive mask generation and T2* and S0 estimation, but which will be retained in the optimally combined data. Can be individual indices (e.g., '0,5,10'), ranges (e.g., '5:10'), or a mix of the two (e.g., '0,5:10,15'). Indices are 0-based. As in Python lists, ranges are start-inclusive and end-exclusive (for example, '0:5' includes the first [0] through fifth [4] timepoints). Default is to not exclude any volumes.”</span> |
| <code><span class="nw">&#45;&#45;fittype</span> <span class="nw">&#123;loglin&#44;curvefit&#125;</span></code> | <code><span class="nw">fittype&#61;&#34;loglin&#34;</span></code> | the fit: log-linear least squares, or the monoexponential curve fit (fMRIPrep's)<span class="opt-help">tedana: “Desired T2*/S0 fitting method. "loglin" means that a linear model is fit to the log of the data. "curvefit" means that a more computationally demanding monoexponential model is fit to the raw data.”</span> |
| <code><span class="nw">&#45;&#45;fitmode</span> <span class="nw">&#123;all&#44;ts&#125;</span></code> | <code><span class="nw">fitmode&#61;&#34;all&#34;</span></code> | one fit per voxel over all volumes, or one per voxel and volume (4D maps)<span class="opt-help">tedana: “Monoexponential model fitting scheme. "all" means that the model is fit, per voxel, across all timepoints. "ts" means that the model is fit, per voxel and per timepoint.”</span> |
| <code><span class="nw">&#45;&#45;combmode</span> <span class="nw">&#123;t2s&#44;paid&#125;</span></code> | <code><span class="nw">combmode&#61;&#34;t2s&#34;</span></code> | the combination's weights: TE · exp(-TE / T2*), or PAID's temporal SNR<span class="opt-help">tedana: “Combination scheme for TEs: "t2s" (Posse 1999), "paid" (Poser)”</span> |
| <code><span class="nw">&#45;&#45;n&#45;independent&#45;echos</span> <span class="nw">INT</span></code> | <code><span class="nw">n&#95;independent&#95;echos&#61;None</span></code> | the number of independent echoes (EPTI): only tedana's warnings change<span class="opt-help">tedana: “Number of independent echoes to use in goodness of fit metrics (fstat). Primarily used for EPTI acquisitions, which have dependency across echoes. If not provided, number of echoes will be used.”</span> |
| <code><span class="nw">&#45;&#45;n&#45;threads</span> <span class="nw">INT</span></code> | <code><span class="nw">n&#95;threads&#61;1</span></code> (0: all logical CPUs, passed as -1) | threads; tedana's limit for its BLAS and its curve-fit processes. On the command line, when it is not given, larmorx's own <code><span class="nw">&#45;&#45;n&#45;threads</span></code> before the family applies (<code><span class="nw">larmorx</span> <span class="nw">&#45;&#45;n&#45;threads</span> <span class="nw">4</span> <span class="nw">tedana</span> <span class="nw">t2smap</span> <span class="nw">&#46;&#46;&#46;</span></code>; else <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code>, else every logical CPU), not tedana's default of 1. The replica's results never depend on it (it gives tedana's one-thread results; tedana's own log-linear maps change with BLAS threads in a few voxels' last bits), nor the clean room's (the same files at any count)<span class="opt-help">tedana: “Number of threads to use. Used by threadpoolctl to set the parameter outside of the workflow function. Higher numbers of threads tend to slow down performance on typical datasets.”</span> |
| <code><span class="nw">&#45;&#45;debug</span></code> | <code><span class="nw">debug&#61;False</span></code> | the log at DEBUG level (the help's TSV log file is never written: tedana's, kept)<span class="opt-help">tedana: “Logs in the terminal will have increased verbosity, and will also be written into a TSV file in the output directory.”</span> |
| <code><span class="nw">&#45;&#45;quiet</span></code> (hidden) | <code><span class="nw">quiet&#61;False</span></code> | the log at WARNING level |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | - | the usage (argparse's, exit 0)<span class="opt-help">tedana: “show this help message and exit”</span> |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;&#45;version</span></code> | - | <code><span class="nw">t2smap</span> <span class="nw">v26&#46;0&#46;3</span></code> (exit 0)<span class="opt-help">tedana: “show program's version number and exit”</span> |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;reproduce&#34;</span></code> gives tedana's files: bit for bit by the replica (its defects and its maths), and by the clean room with tedana's defects exactly and its fitted numbers within the spec's thresholds (§17.3; exactly at TED-46's voxels) |
| <code><span class="nw">LARMORX&#95;TEDANA&#95;LIBRARIES</span></code> | <code><span class="nw">libraries&#61;&#34;newest&#34;</span></code> | the numpy and SciPy whose arithmetic is reproduced: <code><span class="nw">newest</span></code> (numpy 2.5.4, SciPy 1.18.1) or <code><span class="nw">shared</span></code> (numpy 2.3.5, SciPy 1.15.3); the curve fit's last bits differ between them |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `tedana` on the command line (`larmorx --n-threads 4 tedana t2smap ...`) and are arguments of `lx.tedana.t2smap`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `echo-1.nii.gz` (the first echo of a synthetic multi-echo series: 8 heads of 40 × 48 × 40 voxels of 4 mm), `echo-2.nii.gz` (the second echo: the first times 0.6), `echo-3.nii.gz` (the third echo: the first times 0.36), `mask.nii.gz` (the synthetic head's brain as a mask (1 inside, 0 outside)). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# Three echoes 15 ms apart and a mask: the T2* map and the combined series.
res = lx.tedana.t2smap(
    ["echo-1.nii.gz", "echo-2.nii.gz", "echo-3.nii.gz"], [0.015, 0.030, 0.045], mask="mask.nii.gz"
)
res.t2star.shape  # -> (40, 48, 40)
res.optcom.shape  # -> (40, 48, 40, 8)
```

```bash
larmorx tedana t2smap -d echo-1.nii.gz echo-2.nii.gz echo-3.nii.gz -e 15 30 45 --mask mask.nii.gz --out-dir t2smap
larmorx tedana t2smap -d echo-1.nii.gz echo-2.nii.gz echo-3.nii.gz -e 15 30 45 --mask mask.nii.gz --fittype curvefit --convention orig --out-dir t2smap-curvefit
```

## Ports {#ports}

`t2smap` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;gpl</span></code> | GNU GPL version 3 | experimental | `tedana-t2smap-replica` |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [tedana-t2smap-original](repo:docs/validation/tedana-t2smap-original.md) |

**The replica: status `experimental`**, against tedana 26.0.3 (its record,
`tedana-t2smap-replica`, 2026-11-12, in both library environments):
102 cases, 62 bit-identical (every output file, header, log line and Python warning, the chain of
tracebacks, the exit status and the last error line), 40 rejected by both alike, 0 failures:
fMRIPrep's four multi-echo calls, every option and path, ANALYZE and MGH inputs and the failure
cases of every defect.

**The clean room: status `experimental`**, against tedana 26.0.3 in `reproduce` and the replica's
default by default (its [record](repo:docs/validation/tedana-t2smap-original.md), 2026-11-12, the full
tier): 125 cases, 124 pass, 1 expected divergence (a chaotic curve-fit regime: SciPy's own
floating-point warnings inside its steps), 0 failures, by the spec's thresholds (§17.3): every
option, the readers, TED-46's saturated voxels, thread invariance at 1, 4 and 8 threads, and
fMRIPrep's six multi-echo calls.

tedana is licensed under the GNU LGPL version 2.1, so `t2smap` has two ports
([licensing](repo:docs/licensing.md)):
- **the replica** (2026-11-08), `larmorx-gpl tedana t2smap` (package `larmorx-gpl`, under the GNU
  GPL version 3 only: tedana's LGPL-2.1 converted under its section 3; its provenance in
  `crates-gpl/larmorx-gpl-tedana/PROVENANCE.md`), bit-exact, run as a separate program;
- **the clean room**, `crates/larmorx-tedana` in the main package (Apache-2.0, written from
  `specs/t2smap.md` by implementers who never read tedana's source or the replica's code,
  2026-11-11; [PROVENANCE](repo:crates/larmorx-tedana/PROVENANCE.md)), built for speed: the
  log-linear fit per voxel in closed form, its own trust-region curve fit on the per-echo means,
  deterministic threads (the same files at any `--n-threads`), every option, message, exit status
  and defect of the spec; run in this process by `lx.tedana.t2smap` and `larmorx tedana t2smap`
  since 2026-11-12 (its own binding, `larmorx._core.tedana_t2smap_cleanroom(args, env, cwd)`:
  tedana's arguments, an environment table, the directory; `(exit status, standard output,
  standard error)`, serves the validation tools). Its `reproduce` gives tedana's defects exactly
  and its fitted numbers within the spec's thresholds (§17.3), not bit for bit: the replica is
  the exact one (but at TED-46's voxels of equal observations, whose values are tedana's
  rounding noise: there `reproduce` computes them with the main package's exact ports of numpy's
  `lstsq` and SciPy's `curve_fit`, since 2026-11-12).

`implementation="auto"` (the default) runs the replica when `larmorx-gpl` is installed (`pip
install larmorx-gpl`, or `pip install "larmorx[all]"`), else the clean room; `"replica"` runs the
replica or raises `ReplicaNotFoundError` with that command; `"clean-room"` (`"original"`,
0.1.0rc1's spelling, still works, with a `DeprecationWarning`) runs the clean room. The command
line does the same (`--implementation` before the family, or `LARMORX_IMPLEMENTATION`; `replica`
without the program exits 127 with the command that installs it): `larmorx --implementation
clean-room tedana t2smap -d ... -e ...`. The program is found through `LARMORX_GPL_BIN`, then the
Python environment's scripts directory, then `PATH`.

## Evidence {#evidence}

How each of `t2smap`'s ports was measured against tedana, case by case: [its evidence](/evidence/tedana-t2smap/).

## More in the repository {#more}

The API page [docs/api/tedana-t2smap.md](repo:docs/api/tedana-t2smap.md) holds what `t2smap` shares with the page's other programs:

- [Outputs](repo:docs/api/tedana-t2smap.md#outputs)
- [Upstream defects](repo:docs/api/tedana-t2smap.md#upstream-defects)
- [Validation](repo:docs/api/tedana-t2smap.md#validation)
