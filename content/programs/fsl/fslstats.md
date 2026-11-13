---
title: "`fslstats`"
kicker: "Programs · FSL"
lede: "`fslstats` prints statistics of an image, per volume, per label or as JSON."
description: "LARMORX reference for FSL 6.0.7.23 `fslstats`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl fslstats"
  python: "lx.fsl.fslstats"
  api: "docs/api/fsl-stats.md"
  evidence: "/evidence/fsl-stats/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "fa776d2ea0a17487"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "035dcd92e164879c"
    crates/larmorx-fsl/src/cli/fslstats.rs: "9e71fb588889a84f"
    crates/larmorx-fsl/src/cli/fslstats_usage.txt: "767247972f6fb604"
    docs/api/fsl-stats.md: "77d2b6321f5663d3"
    python/larmorx/fsl/stats.py: "c0bdd2ec5179513e"
    validation/tools.toml: "f0750687390307f1"
---

## What it does {#what-it-does}

Its options apply in
order: thresholds, masks, absolute values and a difference image change what the later options
see; the others print the mean, standard deviation, minimum and maximum, robust range,
percentiles, entropy, voxel count and volume, centre of gravity, the extremes' coordinates, the
bounding box of the nonzero voxels or a histogram. With `-t` it prints one line per volume, with
`-K` one per label of an index image, with `-json` everything as JSON.

**Order matters**: `-k` replaces the masks the thresholds made, as a later threshold replaces
`-k`'s, so `fslstats img -M -l 10 -M` reports the nonzero mean, applies a threshold, then reports
the new nonzero mean.

## Command line {#command-line}

```text synopsis
larmorx fsl fslstats [preoptions] <input> [options]
```

Everything after `larmorx fsl fslstats` is the original's command line: the arguments of FSL 6.0.7.23's `fslstats`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl fslstats ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>fslstats</code>'s usage text, as the clean room prints it</summary>

```text
Usage: fslstats [preoptions] <input> [options]

preoption -json: output in JSON format to standard out
preoption -t will give a separate output line for each 3D volume of a 4D timeseries
preoption -K < indexMask > will generate seperate n submasks from indexMask, for indexvalues 1..n where n is the maximum index value in indexMask, and generate statistics for each submask
Note - options are applied in order, e.g. -M -l 10 -M will report the non-zero mean, apply a threshold and then report the new nonzero mean

-l <lthresh> : set lower threshold
-u <uthresh> : set upper threshold
-r           : output <robust min intensity> <robust max intensity>
-R           : output <min intensity> <max intensity>
-e           : output mean entropy ; mean(-i*ln(i))
-E           : output mean entropy (of nonzero voxels)
-v           : output <voxels> <volume>
-V           : output <voxels> <volume> (for nonzero voxels)
-m           : output mean
-M           : output mean (for nonzero voxels)
-s           : output standard deviation
-S           : output standard deviation (for nonzero voxels)
-w           : output smallest ROI <xmin> <xsize> <ymin> <ysize> <zmin> <zsize> <tmin> <tsize> containing nonzero voxels
-x           : output co-ordinates of maximum voxel
-X           : output co-ordinates of minimum voxel
-c           : output centre-of-gravity (cog) in mm coordinates
-C           : output centre-of-gravity (cog) in voxel coordinates
-p <n>       : output nth percentile (n between 0 and 100)
-P <n>       : output nth percentile (for nonzero voxels)
-a           : use absolute values of all image intensities
-n           : treat NaN or Inf as zero for subsequent stats
-k <mask>    : use the specified image (filename) for masking - overrides lower and upper thresholds
-d <image>   : take the difference between the base image and the image specified here
-h <nbins>   : output a histogram (for the thresholded/masked voxels only) with nbins
-H <nbins> <min> <max>   : output a histogram (for the thresholded/masked voxels only) with nbins and histogram limits of min and max
Note - thresholds are not inclusive ie lthresh<allowed<uthresh
```

</details>

## Python {#python}

```python
lx.fsl.fslstats(
    image: Any,
    *options: Any,
    timeseries: bool = False,
    index_mask: Any = None,
    json: bool = False,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
) -> str
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

Run fslstats' `options` on `image`, as `fslstats [-t] [-K <index_mask>] [-json] <image> <options...>` does, and return its standard output.

- `image`, `index_mask` and the image operands (`-k`, `-d`) are `lx.Image`s, nibabel images,
  `(array, affine)` pairs or paths (in-memory images written for the program in their own data
  type); options are fslstats' own words, numbers passed as their shortest round-trip text.
- **The program runs in the caller's working directory**: relative names are read there.
- **Numbers**: the text output has six decimals (`%.6f`), as nipype reads it for fMRIPrep;
  `json=True` gives each number at full precision (a decimal that reads back to the same double,
  as nlohmann/json writes it; NaN and the infinities as `null`).
- FSL's environment variables are settings of the call, never read from the process. FSL's
  fslstats runs on one thread; the clean room runs on `n_threads`, with the same results at any
  count.
- Errors: `ValueError` for invalid arguments, `larmorx.ReplicaError` when the replica fails (its
  message in the error, without the usage text), `RuntimeError` when the clean room does,
  `larmorx.ReplicaNotFoundError` without `larmorx-nc`.
- The typed wrappers (`lx.fsl.image_mean` and the others in the options table) choose the voxels
  in a fixed order ([The typed wrappers](repo:docs/api/fsl-stats.md#the-typed-wrappers)); for another order call
  `fslstats()`.

```python
import larmorx as lx

# fMRIPrep's goodvoxels mask: fslstats <cov_ribbon> -M, then -S (the nonzero voxels)
m = lx.fsl.image_mean("cov_ribbon.nii.gz", nonzero=True)
s = lx.fsl.image_std("cov_ribbon.nii.gz", nonzero=True)
upper = m + 0.5 * s

# BET's script: the centre of gravity, in voxels, of the voxels above a threshold
cog = lx.fsl.centre_of_gravity("t1w.nii.gz", lower=0.001, voxels=True)

# per volume, per label, in a mask
means = lx.fsl.image_mean("bold.nii.gz", per_volume=True)            # shape (n_volumes,)
by_label = lx.fsl.image_mean("t1w.nii.gz", labels="labels.nii.gz")   # shape (n_labels,)

# any option list, in fslstats' own words; JSON for full precision
text = lx.fsl.fslstats("t1w.nii.gz", "-M", "-l", 10, "-M")
doc = lx.fsl.fslstats("t1w.nii.gz", "-r", "-p", 50, json=True)
```

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `fslstats` accepts (`crates/larmorx-fsl/src/cli/fslstats.rs`) and the arguments of `lx.fsl.fslstats` (`python/larmorx/fsl/stats.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">fslstats</span></code> option | Python | Default | Notes |
|---|---|---|---|
| the first word after the preoptions | <code><span class="nw">image</span></code> |  | the image |
| <code><span class="nw">&#45;t</span></code> | <code><span class="nw">timeseries&#61;True</span></code> | <code><span class="nw">False</span></code> | one line per volume<span class="opt-help">FSL: “will give a separate output line for each 3D volume of a 4D timeseries”</span> |
| <code><span class="nw">&#45;K</span></code> | <code><span class="nw">index&#95;mask</span></code> | <code><span class="nw">None</span></code> | one line per label 1..n of the 3D label image<span class="opt-help">FSL: “will generate seperate n submasks from indexMask, for indexvalues 1..n where n is the maximum index value in indexMask, and generate statistics for each submask”</span> |
| <code><span class="nw">&#45;json</span></code> | <code><span class="nw">json&#61;True</span></code> | <code><span class="nw">False</span></code> | the numbers in JSON, at full precision; NaN and the infinities as <code><span class="nw">null</span></code><span class="opt-help">FSL: “output in JSON format to standard out”</span> |
| <code><span class="nw">&#45;l</span></code>, <code><span class="nw">&#45;u</span></code> | <code><span class="nw">options</span></code> |  | the voxels strictly between (the typed wrappers' <code><span class="nw">lower&#61;</span></code>, <code><span class="nw">upper&#61;</span></code>)<span class="opt-help">FSL: “set lower threshold”</span><span class="opt-help">FSL: “set upper threshold”</span> |
| <code><span class="nw">&#45;k</span></code> | <code><span class="nw">options</span></code> |  | the voxels where the mask is above 0.5 (it overrides thresholds, as a later threshold overrides it; the typed wrappers' <code><span class="nw">mask&#61;</span></code>)<span class="opt-help">FSL: “use the specified image (filename) for masking - overrides lower and upper thresholds”</span> |
| <code><span class="nw">&#45;d</span></code> | <code><span class="nw">options</span></code> |  | the image minus this one first (the typed wrappers' <code><span class="nw">difference&#61;</span></code>)<span class="opt-help">FSL: “take the difference between the base image and the image specified here”</span> |
| <code><span class="nw">&#45;a</span></code> | <code><span class="nw">options</span></code> |  | absolute values first (the typed wrappers' <code><span class="nw">absolute&#61;True</span></code>)<span class="opt-help">FSL: “use absolute values of all image intensities”</span> |
| <code><span class="nw">&#45;n</span></code> | <code><span class="nw">options</span></code> |  | NaN and infinities as 0 first (the typed wrappers' <code><span class="nw">nan&#95;as&#95;zero&#61;True</span></code>)<span class="opt-help">FSL: “treat NaN or Inf as zero for subsequent stats”</span> |
| <code><span class="nw">&#45;m</span></code>, <code><span class="nw">&#45;M</span></code> | <code><span class="nw">options</span></code>; <code><span class="nw">lx&#46;fsl&#46;image&#95;mean&#40;image&#44;</span> <span class="nw">nonzero&#61;False&#41;</span></code> |  | the mean (of the nonzero voxels)<span class="opt-help">FSL: “output mean”</span><span class="opt-help">FSL: “output mean (for nonzero voxels)”</span> |
| <code><span class="nw">&#45;s</span></code>, <code><span class="nw">&#45;S</span></code> | <code><span class="nw">options</span></code>; <code><span class="nw">lx&#46;fsl&#46;image&#95;std&#40;image&#44;</span> <span class="nw">nonzero&#61;False&#41;</span></code> |  | the standard deviation (of the nonzero voxels)<span class="opt-help">FSL: “output standard deviation”</span><span class="opt-help">FSL: “output standard deviation (for nonzero voxels)”</span> |
| <code><span class="nw">&#45;p</span></code>, <code><span class="nw">&#45;P</span></code> | <code><span class="nw">options</span></code>; <code><span class="nw">lx&#46;fsl&#46;image&#95;percentile&#40;image&#44;</span> <span class="nw">percent&#44;</span> <span class="nw">nonzero&#61;False&#41;</span></code> |  | the percentile, <code><span class="nw">percent</span></code> in [0, 100]<span class="opt-help">FSL: “output nth percentile (n between 0 and 100)”</span><span class="opt-help">FSL: “output nth percentile (for nonzero voxels)”</span> |
| <code><span class="nw">&#45;R</span></code>, <code><span class="nw">&#45;r</span></code> | <code><span class="nw">options</span></code>; <code><span class="nw">lx&#46;fsl&#46;image&#95;range&#40;image&#44;</span> <span class="nw">robust&#61;False&#41;</span></code> |  | <code><span class="nw">&#91;min&#44;</span> <span class="nw">max&#93;</span></code>, or the robust range (FSL's 2 %-98 % histogram limits)<span class="opt-help">FSL: “output &lt;min intensity&gt; &lt;max intensity&gt;”</span><span class="opt-help">FSL: “output &lt;robust min intensity&gt; &lt;robust max intensity&gt;”</span> |
| <code><span class="nw">&#45;e</span></code>, <code><span class="nw">&#45;E</span></code> | <code><span class="nw">options</span></code>; <code><span class="nw">lx&#46;fsl&#46;image&#95;entropy&#40;image&#44;</span> <span class="nw">nonzero&#61;False&#41;</span></code> |  | the mean entropy of the intensities' histogram<span class="opt-help">FSL: “output mean entropy ; mean(-i*ln(i))”</span><span class="opt-help">FSL: “output mean entropy (of nonzero voxels)”</span> |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;V</span></code> | <code><span class="nw">options</span></code>; <code><span class="nw">lx&#46;fsl&#46;image&#95;volume&#40;image&#44;</span> <span class="nw">nonzero&#61;False&#41;</span></code> |  | <code><span class="nw">&#91;voxels&#44;</span> <span class="nw">mm&#179;&#93;</span></code><span class="opt-help">FSL: “output &lt;voxels&gt; &lt;volume&gt;”</span><span class="opt-help">FSL: “output &lt;voxels&gt; &lt;volume&gt; (for nonzero voxels)”</span> |
| <code><span class="nw">&#45;c</span></code>, <code><span class="nw">&#45;C</span></code> | <code><span class="nw">options</span></code>; <code><span class="nw">lx&#46;fsl&#46;centre&#95;of&#95;gravity&#40;image&#44;</span> <span class="nw">voxels&#61;False&#41;</span></code> |  | <code><span class="nw">&#91;x&#44;</span> <span class="nw">y&#44;</span> <span class="nw">z&#93;</span></code> in mm, or in voxel coordinates<span class="opt-help">FSL: “output centre-of-gravity (cog) in mm coordinates”</span><span class="opt-help">FSL: “output centre-of-gravity (cog) in voxel coordinates”</span> |
| <code><span class="nw">&#45;x</span></code>, <code><span class="nw">&#45;X</span></code> | <code><span class="nw">options</span></code>; <code><span class="nw">lx&#46;fsl&#46;extremum&#95;position&#40;image&#44;</span> <span class="nw">minimum&#61;False&#41;</span></code> |  | the voxel coordinates of the maximum (minimum)<span class="opt-help">FSL: “output co-ordinates of maximum voxel”</span><span class="opt-help">FSL: “output co-ordinates of minimum voxel”</span> |
| <code><span class="nw">&#45;w</span></code> | <code><span class="nw">options</span></code>; <code><span class="nw">lx&#46;fsl&#46;bounding&#95;roi&#40;image&#41;</span></code> |  | <code><span class="nw">&#91;xmin&#44;</span> <span class="nw">xsize&#44;</span> <span class="nw">ymin&#44;</span> <span class="nw">ysize&#44;</span> <span class="nw">zmin&#44;</span> <span class="nw">zsize&#44;</span> <span class="nw">tmin&#44;</span> <span class="nw">tsize&#93;</span></code> of the nonzero voxels, as <code><span class="nw">lx&#46;fsl&#46;roi</span></code> takes a region<span class="opt-help">FSL: “output smallest ROI &lt;xmin&gt; &lt;xsize&gt; &lt;ymin&gt; &lt;ysize&gt; &lt;zmin&gt; &lt;zsize&gt; &lt;tmin&gt; &lt;tsize&gt; containing nonzero voxels”</span> |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;H</span></code> | <code><span class="nw">options</span></code>; <code><span class="nw">lx&#46;fsl&#46;image&#95;histogram&#40;image&#44;</span> <span class="nw">bins&#44;</span> <span class="nw">limits&#61;None&#41;</span></code> |  | the counts in <code><span class="nw">bins</span></code> bins over the image's range (<code><span class="nw">&#45;h</span></code>) or <code><span class="nw">limits</span></code> (<code><span class="nw">&#45;H</span></code>)<span class="opt-help">FSL: “output a histogram (for the thresholded/masked voxels only) with nbins”</span><span class="opt-help">FSL: “output a histogram (for the thresholded/masked voxels only) with nbins and histogram limits of min and max”</span> |
| <code><span class="nw">&#45;D</span></code> | <code><span class="nw">options</span></code> |  | (hidden in FSL's usage) the sum of every value, masks ignored (<code><span class="nw">specs&#47;fslstats&#46;md</span></code> §5.2) |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects as FSL has them |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl fslstats ...`) and are arguments of `lx.fsl.fslstats`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all) for writing in-memory images, and the clean room's own; the same results at any count. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects corrected, or FSL's behaviour (<code><span class="nw">docs&#47;api&#47;fsl&#45;stats&#46;md</span></code>, "Defects of the original, corrected by default"). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `t1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `bold.nii.gz` (a synthetic series of 4 such heads). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# BET's script: the centre of gravity, in voxels, of the voxels above a threshold
cog = lx.fsl.centre_of_gravity("t1w.nii.gz", lower=0.001, voxels=True)
len(cog)  # -> 3
# One mean per volume of a series.
lx.fsl.image_mean("bold.nii.gz", per_volume=True).shape  # -> (4,)
# Any option list, in fslstats' own words: the nonzero mean, then above a threshold.
lx.fsl.fslstats("t1w.nii.gz", "-M", "-l", 100, "-M")  # -> '124.499801 498.625669 \n'
```

```bash
larmorx fsl fslstats t1w.nii.gz -M -S
larmorx fsl fslstats -t bold.nii.gz -m
larmorx fsl fslstats -json t1w.nii.gz -r -p 50
```

## Ports {#ports}

`fslstats` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-stats-replica](repo:docs/validation/fsl-stats-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-stats](repo:docs/validation/fsl-stats.md) |

Both ports take every option, preoption (`-t`, `-K`, `-json`), message, exit status and failure
case of FSL's, and correct the defects FSL-181 to FSL-189.

**The replica** against FSL 6.0.7.23 itself ([its record](repo:docs/validation/fsl-stats-replica.md),
the standard comparison, 2026-11-03): 172 of 172 compared cases identical, their standard output,
standard error and exit status; 36 more rejected by both alike. Among them fMRIPrep's four
goodvoxels calls (`-M` and `-S` of the ribbon's coefficient of variation, before and after its
modulation) on ds005040's chain (the ribbon a stand-in: the segmentation's grey matter, as the
no-reconall runs have no FreeSurfer ribbon), BET's `-l 0.001 -C` on ds005040's T1w, the option
lists of FSL's own test script against its expected outputs, and random testing's permanent cases.

**The clean room** against FSL 6.0.7.23 ([its record](repo:docs/validation/fsl-stats.md), the standard
comparison, 2026-11-04, `specs/fslstats.md` §10's thresholds): 162 cases, 126 within the
thresholds, 36 rejected by both alike, 0 failures. 125 of the 126 are identical to FSL's (standard
output, standard error, exit status), fMRIPrep's four goodvoxels calls on ds005040's chain among
them; BET's `-l 0.001 -C` on ds005040's T1w is within §10's bound (its x 6.1e-8 relative from
FSL's).

FSL is distributed under the FSL Licence (non-commercial use only), so `fslstats` has two ports,
a replica and a clean room, in different packages ([licensing](repo:docs/licensing.md)):

- **The replica** is bit-exact: `larmorx-nc fsl fslstats`, in the package `larmorx-nc`, under the
  FSL Licence's terms, translated from FSL's source. The program is in `crates-nc/larmorx-nc-core`,
  because BET's script runs it, with its command line in `crates-nc/larmorx-nc-avwutils`.
- **The clean room** is in the main package (Apache-2.0, crate `larmorx-fsl`, its
  `cli::fslstats`), written from [`specs/fslstats.md`](repo:specs/fslstats.md), FSL's
  documentation and black-box runs of FSL's program
  ([PROVENANCE](repo:crates/larmorx-fsl/PROVENANCE.md)).

`implementation="auto"` (the default) runs the replica when `larmorx-nc` is installed, the clean
room otherwise; `"replica"` needs `larmorx-nc` (otherwise `ReplicaNotFoundError`); `"clean-room"`
(`"original"`, 0.1.0rc1's spelling, still works) runs the clean room in this process on
`n_threads` threads (its results the same at any count; a failure raises `RuntimeError` with its
messages). The command line chooses alike (`--implementation` before the family, or
`LARMORX_IMPLEMENTATION`).

## Evidence {#evidence}

How each of `fslstats`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-stats/).

## More in the repository {#more}

The API page [docs/api/fsl-stats.md](repo:docs/api/fsl-stats.md) holds what `fslstats` shares with the page's other programs:

- [The typed wrappers](repo:docs/api/fsl-stats.md#the-typed-wrappers)
- [The records](repo:docs/api/fsl-stats.md#the-records)
- [File names on Windows](repo:docs/api/fsl-stats.md#file-names-on-windows)
- [Defects of the original, corrected by default](repo:docs/api/fsl-stats.md#defects-of-the-original-corrected-by-default)
- [Not yet](repo:docs/api/fsl-stats.md#not-yet)
- [History](repo:docs/api/fsl-stats.md#history)
