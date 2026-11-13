---
title: "`3dvolreg`"
kicker: "Programs · AFNI"
lede: "`3dvolreg` registers every volume of a series to a base volume with a rigid-body (6-parameter) transform."
description: "LARMORX reference for AFNI 26.3.05 `3dvolreg`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: afni
  original: "AFNI 26.3.05"
  software: "AFNI"
  command: "larmorx afni 3dvolreg"
  python: "lx.afni.volreg"
  api: "docs/api/afni-volreg.md"
  evidence: "/evidence/afni-volreg/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0 AND CC-BY-4.0", status: "validated"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-afni/src/cli/volreg.rs: "71fd54692bc1ce7b"
    crates/larmorx-afni/src/settings.rs: "8b2560253b92f512"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "91be42d24bb3ba2b"
    docs/api/afni-volreg.md: "2c9bfa921b2e2503"
    python/larmorx/afni/volreg.py: "2c8280722dd9d4c4"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

fMRIPrep runs it for its BOLD reference (niworkflows' `RobustAverage`: up to 20
volumes aligned before their median, `-Fourier -twopass -zpad 4`, once per run and per 4D
sbref) and sdcflows' PEPOLAR estimator for its reference averages.

## Command line {#command-line}

```text synopsis
larmorx afni 3dvolreg [options] dataset
```

Everything after `larmorx afni 3dvolreg` is the original's command line: the arguments of AFNI 26.3.05's `3dvolreg`, as AFNI takes them. LARMORX's own options stand between `larmorx` and the family `afni`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        afni 3dvolreg ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>3dvolreg</code>'s usage text, as the clean room prints it</summary>

```text
Usage: 3dvolreg [options] dataset   (larmorx: clean-room original of AFNI 26.3.05's 3dvolreg)

Registers each 3D sub-brick of the input dataset to the base brick (rigid body, 6
parameters), by iterated linearised weighted least squares, as AFNI's 3dvolreg does. The
dataset and the outputs are NIfTI files.

Options (before the dataset):
  -verbose             print progress reports (twice: lots of output)
  -Fourier -heptic -quintic -cubic -linear
                       interpolation for the estimation (default -heptic)
  -final mode          final interpolation: NN cubic quintic heptic Fourier linear
  -clipit / -noclip    clip each output to its input's range (default on)
  -zpad n              zero padding around the edges during rotations (default 4)
  -prefix fname        output (.nii or .nii.gz); NULL writes no dataset
  -float               write the output as float
  -base n | -base dset the n'th sub-brick of the input, or sub-brick 0 of another dataset
  -dfile f             save n, roll, pitch, yaw, dS, dL, dP, rmsold, rmsnew
  -1Dfile f            save roll, pitch, yaw, dS, dL, dP
  -1Dmatrix_save ff    save the base-to-input matrices (ff, or ff.aff12.1D)
  -rotcom              print the 3drotate fragments
  -maxdisp / -nomaxdisp  report the maximum displacement in the automask (default on)
  -maxdisp1D mm        also write it per sub-brick to mm (and its change to mm_delt)
  -savedisp sss        save the displacements of every voxel (sss_DX, sss_DY, sss_DZ)
  -maxite m  -x_thresh x  -rot_thresh r  -delta d  -params m x r d
  -weight 'wset[n]'    the weight brick
  -wtinp               sub-brick 0 of the input as the weight
  -edging ee | ee%     the weight's zeroed edge (default 5%, or AFNI_VOLREG_EDGING)
  -twopass  -twoblur bb  -sinit  -coarse del num  -coarserot  -nocoarserot
                       two passes: a coarse search on blurred bricks first
  -tshift ii           slice-time correct the input first (ignoring ii time points)
  -rotparent rset  -gridparent gset  -twodup
  -input dset / -source dset   the dataset, given as an option

AFNI's global options (anywhere on the command line):
  -overwrite      replace an existing output (AFNI_DECONFLICT=OVERWRITE)
  -Dname=value    set AFNI's environment variable 'name' for this run
  -skip_afnirc    accepted (no .afnirc file is read)
```

</details>

## Python {#python}

```python
lx.afni.volreg(
    image: Any,
    *,
    base: int | Any = 0,
    interpolation: Literal["Fourier", "heptic", "quintic", "cubic", "linear"] = "heptic",
    final: Literal["Fourier", "heptic", "quintic", "cubic", "linear", "NN"] | None = None,
    clip: bool = True,
    zpad: int = 4,
    twopass: bool = False,
    twoblur: float = 2.0,
    coarse: tuple[int, int] = (10, 2),
    coarse_rotation: bool = True,
    sinit: bool = True,
    weight: Any = None,
    weight_index: int = 0,
    weight_input: bool = False,
    edging: float | str | None = None,
    max_iterations: int = 23,
    x_threshold: float = 0.01,
    rot_threshold: float = 0.02,
    delta: float = 0.70,
    tshift: int | None = None,
    float_output: bool = False,
    maxdisp: bool = True,
    save_displacements: bool = False,
    rotparent: str | os.PathLike[str] | None = None,
    gridparent: str | os.PathLike[str] | None = None,
    twodup: bool = False,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
    afni_settings: Mapping[str, str] | None = None,
) -> VolregResult
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

Registers every volume of a series to a base volume, as AFNI's `3dvolreg` does.

Returns a `VolregResult`: `registered`, `parameters`, `matrices`, `rms` (`-dfile`'s rmsold and
rmsnew), `max_displacement` and `max_delta_displacement` (with `maxdisp=True`), `displacements`
(with `save_displacements=True`: the x, y and z displacement series). `lx.afni.fmriprep_volreg_options()`
gives fMRIPrep's arguments. The arguments are checked before anything runs (`ValueError`);
AFNI's fatal errors (a base with fewer than 100 non-zero voxels, mismatched grids, ...) are
`larmorx.ReplicaError`s with AFNI's message from the replica, `ValueError`s with it from the
clean room.

```python
import larmorx as lx

# As fMRIPrep's RobustAverage calls 3dvolreg (-Fourier -twopass -zpad 4).
r = lx.afni.volreg("bold_sliced.nii.gz", **lx.afni.fmriprep_volreg_options())
r.registered          # the registered series (an lx.Image)
r.parameters          # (n, 6): roll, pitch, yaw (deg), dS, dL, dP (mm), as -1Dfile
r.matrices            # (n, 12): -1Dmatrix_save's rows (base to input, DICOM)
r.max_displacement    # (n,): -maxdisp1D

# The default heptic registration to volume 3, with the displacement datasets.
r = lx.afni.volreg(series, base=3, save_displacements=True, n_threads=6)
```

Its result, `VolregResult`, holds what `volreg` computed (one row per volume).

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">registered</span></code> | <code><span class="nw">Image</span></code> | The registered series, on the input's grid (or <code><span class="nw">gridparent</span></code>'s), in the input's storage type (float32 with <code><span class="nw">float&#95;output&#61;True</span></code> or a scaled input). |
| <code><span class="nw">parameters</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | <code><span class="nw">&#40;n&#44;</span> <span class="nw">6&#41;</span></code> float64: roll, pitch, yaw (degrees, about the I, R and A axes) and dS, dL, dP (mm), as <code><span class="nw">&#45;1Dfile</span></code> writes them (4 decimals). |
| <code><span class="nw">matrices</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | <code><span class="nw">&#40;n&#44;</span> <span class="nw">12&#41;</span></code> float64: each volume's affine, base to input in DICOM coordinates, row by row (<code><span class="nw">&#45;1Dmatrix&#95;save</span></code>, 6 significant digits): the matrix fMRIPrep reads. |
| <code><span class="nw">rms</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | <code><span class="nw">&#40;n&#44;</span> <span class="nw">2&#41;</span></code> float64: the root mean square difference from the base before and after registration (<code><span class="nw">&#45;dfile</span></code>'s last two columns; 0 with <code><span class="nw">rotparent</span></code>). |
| <code><span class="nw">max&#95;displacement</span></code> | <code><span class="nw">np&#46;ndarray</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | <code><span class="nw">&#40;n&#44;&#41;</span></code> float64: the largest displacement of the automask's boundary voxels, and its largest change from the previous volume (mm, <code><span class="nw">&#45;maxdisp1D</span></code>, 3 decimals); <code><span class="nw">None</span></code> with <code><span class="nw">maxdisp&#61;False</span></code> or no automask. |
| <code><span class="nw">max&#95;delta&#95;displacement</span></code> | <code><span class="nw">np&#46;ndarray</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | <code><span class="nw">&#40;n&#44;&#41;</span></code> float64: the largest displacement of the automask's boundary voxels, and its largest change from the previous volume (mm, <code><span class="nw">&#45;maxdisp1D</span></code>, 3 decimals); <code><span class="nw">None</span></code> with <code><span class="nw">maxdisp&#61;False</span></code> or no automask. |
| <code><span class="nw">displacements</span></code> | <code><span class="nw">tuple&#91;Image&#44;</span> <span class="nw">Image&#44;</span> <span class="nw">Image&#93;</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">save&#95;displacements&#61;True</span></code>: each voxel's displacement along the dataset's x, y and z axes (mm, float32 series, <code><span class="nw">&#45;savedisp</span></code>); else <code><span class="nw">None</span></code>. |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `3dvolreg` accepts (`crates/larmorx-afni/src/cli/volreg.rs`) and the arguments of `lx.afni.volreg` (`python/larmorx/afni/volreg.py`), whose defaults and descriptions are taken from it. Under each option, in grey, its line of the usage text the clean room prints, in the clean room's own words.

| AFNI option | Python | Default | Notes |
|---|---|---|---|
| the last word (<code><span class="nw">dataset</span></code>), <code><span class="nw">&#45;input</span></code>, <code><span class="nw">&#45;source</span></code> | <code><span class="nw">image</span></code> |  | NIfTI-1/2 (<code><span class="nw">&#46;nii</span></code>, <code><span class="nw">&#46;nii&#46;gz</span></code>) or an in-memory image; sub-brick selectors (<code><span class="nw">dset&#91;&#46;&#46;&#46;&#93;</span></code>) are refused, as by every larmorx AFNI tool<span class="opt-help">The clean room's usage: “the dataset, given as an option”</span> |
| <code><span class="nw">&#45;base</span> <span class="nw">n</span></code>, <code><span class="nw">&#45;base</span> <span class="nw">dset</span></code> | <code><span class="nw">base</span></code> (int, path or image) | <code><span class="nw">0</span></code> | an external base's first volume (AFNI warns when it has more)<span class="opt-help">The clean room's usage: “the n'th sub-brick of the input, or sub-brick 0 of another dataset”</span> |
| <code><span class="nw">&#45;Fourier</span></code>, <code><span class="nw">&#45;heptic</span></code> (default), <code><span class="nw">&#45;quintic</span></code>, <code><span class="nw">&#45;cubic</span></code>, <code><span class="nw">&#45;linear</span></code> | <code><span class="nw">interpolation</span></code> | <code><span class="nw">&#34;heptic&#34;</span></code> | also <code><span class="nw">&#45;fourier</span></code>, <code><span class="nw">&#45;Heptic</span></code>, ... (4 letters)<span class="opt-help">The clean room's usage: “interpolation for the estimation (default -heptic)”</span> |
| <code><span class="nw">&#45;final</span> <span class="nw">mode</span></code> | <code><span class="nw">final</span></code> | <code><span class="nw">None</span></code> | <code><span class="nw">NN</span></code>, <code><span class="nw">linear</span></code>, <code><span class="nw">cubic</span></code>, <code><span class="nw">quintic</span></code>, <code><span class="nw">heptic</span></code>, <code><span class="nw">Fourier</span></code><span class="opt-help">The clean room's usage: “final interpolation: NN cubic quintic heptic Fourier linear”</span> |
| <code><span class="nw">&#45;clipit</span></code> (default), <code><span class="nw">&#45;noclip</span></code> | <code><span class="nw">clip</span></code> | <code><span class="nw">True</span></code> | <code><span class="nw">&#45;clipit</span></code> prints AFNI's notice<span class="opt-help">The clean room's usage: “clip each output to its input's range (default on)”</span> |
| <code><span class="nw">&#45;zpad</span> <span class="nw">n</span></code> | <code><span class="nw">zpad</span></code> | <code><span class="nw">4</span></code> | default 4; <code><span class="nw">AFNI&#95;ROTA&#95;ZPAD</span></code> is never read (AFNI's help says otherwise: kept, rule C)<span class="opt-help">The clean room's usage: “zero padding around the edges during rotations (default 4)”</span> |
| <code><span class="nw">&#45;prefix</span> <span class="nw">p</span></code> | the result |  | its <code><span class="nw">registered</span></code>; <code><span class="nw">&#46;nii</span></code>/<code><span class="nw">&#46;nii&#46;gz</span></code> only; <code><span class="nw">NULL</span></code> writes nothing<span class="opt-help">The clean room's usage: “output (.nii or .nii.gz); NULL writes no dataset”</span> |
| <code><span class="nw">&#45;float</span></code> | <code><span class="nw">float&#95;output</span></code> | <code><span class="nw">False</span></code> | a scaled input is always written as float, as in AFNI<span class="opt-help">The clean room's usage: “write the output as float”</span> |
| <code><span class="nw">&#45;1Dfile</span></code>, <code><span class="nw">&#45;dfile</span></code>, <code><span class="nw">&#45;1Dmatrix&#95;save</span></code> | the result |  | its <code><span class="nw">parameters</span></code>, <code><span class="nw">rms</span></code> and <code><span class="nw">matrices</span></code>; <code><span class="nw">&#45;1Dmatrix&#95;save</span> <span class="nw">ff</span></code> writes <code><span class="nw">ff&#46;aff12&#46;1D</span></code> unless <code><span class="nw">ff</span></code> ends in <code><span class="nw">&#46;1D</span></code><span class="opt-help">The clean room's usage: “save roll, pitch, yaw, dS, dL, dP”</span><span class="opt-help">The clean room's usage: “save n, roll, pitch, yaw, dS, dL, dP, rmsold, rmsnew”</span><span class="opt-help">The clean room's usage: “save the base-to-input matrices (ff, or ff.aff12.1D)”</span> |
| <code><span class="nw">&#45;maxdisp</span></code> (default), <code><span class="nw">&#45;nomaxdisp</span></code>, <code><span class="nw">&#45;maxdisp1D</span> <span class="nw">mm</span></code> | <code><span class="nw">maxdisp</span></code> | <code><span class="nw">True</span></code> | the result's <code><span class="nw">max&#95;displacement</span></code> and <code><span class="nw">max&#95;delta&#95;displacement</span></code>; the delta goes to <code><span class="nw">mm&#95;delt</span></code> (with <code><span class="nw">&#45;maxdisp1D</span> <span class="nw">&#45;</span></code>: the file <code><span class="nw">&#45;&#95;delt</span></code>, as AFNI's help says: kept, rule C)<span class="opt-help">The clean room's usage: “report the maximum displacement in the automask (default on)”</span><span class="opt-help">The clean room's usage: “also write it per sub-brick to mm (and its change to mm_delt)”</span> |
| <code><span class="nw">&#45;savedisp</span> <span class="nw">sss</span></code>, <code><span class="nw">&#45;SAVEDISP</span> <span class="nw">sss</span></code> | <code><span class="nw">save&#95;displacements</span></code> | <code><span class="nw">False</span></code> | the result's <code><span class="nw">displacements</span></code>; <code><span class="nw">&#45;SAVEDISP</span></code> (command line only): 19 normalised datasets; names must end in <code><span class="nw">&#46;nii</span></code>/<code><span class="nw">&#46;nii&#46;gz</span></code><span class="opt-help">The clean room's usage: “save the displacements of every voxel (sss_DX, sss_DY, sss_DZ)”</span> |
| <code><span class="nw">&#45;rotcom</span></code> | (command line only) |  | the <code><span class="nw">3drotate</span></code> fragments on standard output<span class="opt-help">The clean room's usage: “print the 3drotate fragments”</span> |
| <code><span class="nw">&#45;twopass</span></code>, <code><span class="nw">&#45;twoblur</span> <span class="nw">bb</span></code>, <code><span class="nw">&#45;twodup</span></code>, <code><span class="nw">&#45;sinit</span></code>, <code><span class="nw">&#45;coarse</span> <span class="nw">del</span> <span class="nw">num</span></code> | <code><span class="nw">twopass</span></code>, <code><span class="nw">twoblur</span></code>, <code><span class="nw">twodup</span></code>, <code><span class="nw">sinit&#61;False</span></code>, <code><span class="nw">coarse</span></code> | <code><span class="nw">twopass&#61;False</span></code>, <code><span class="nw">twoblur&#61;2&#46;0</span></code>, <code><span class="nw">twodup&#61;False</span></code>, <code><span class="nw">sinit&#61;True</span></code>, <code><span class="nw">coarse&#61;&#40;10&#44;</span> <span class="nw">2&#41;</span></code> | <code><span class="nw">&#45;twopass</span></code> raises a <code><span class="nw">&#45;maxite</span></code> below 10 to 66<span class="opt-help">The clean room's usage: “two passes: a coarse search on blurred bricks first”</span> |
| <code><span class="nw">&#45;coarserot</span></code> (default), <code><span class="nw">&#45;nocoarserot</span></code> | <code><span class="nw">coarse&#95;rotation</span></code> | <code><span class="nw">True</span></code> | AFNI-86: AFNI reads <code><span class="nw">&#45;nocoarserot</span></code> as <code><span class="nw">&#45;noclip</span></code> (<code><span class="nw">reproduce</span></code>)<span class="opt-help">The clean room's usage: “two passes: a coarse search on blurred bricks first”</span> |
| <code><span class="nw">&#45;weight</span> <span class="nw">&#39;wset&#91;n&#93;&#39;</span></code>, <code><span class="nw">&#45;wtinp</span></code>, <code><span class="nw">&#45;wtrim</span></code> | <code><span class="nw">weight</span></code>, <code><span class="nw">weight&#95;index</span></code>, <code><span class="nw">weight&#95;input</span></code> | <code><span class="nw">weight&#61;None</span></code>, <code><span class="nw">weight&#95;index&#61;0</span></code>, <code><span class="nw">weight&#95;input&#61;False</span></code> | <code><span class="nw">&#45;wtrim</span></code> is always on (AFNI's notice)<span class="opt-help">The clean room's usage: “the weight brick”</span><span class="opt-help">The clean room's usage: “sub-brick 0 of the input as the weight”</span> |
| <code><span class="nw">&#45;edging</span> <span class="nw">ee</span></code>, <code><span class="nw">&#45;edging</span> <span class="nw">ee&#37;</span></code> | <code><span class="nw">edging</span></code> | <code><span class="nw">None</span></code> | default 5%, or <code><span class="nw">AFNI&#95;VOLREG&#95;EDGING</span></code><span class="opt-help">The clean room's usage: “the weight's zeroed edge (default 5%, or AFNI_VOLREG_EDGING)”</span> |
| <code><span class="nw">&#45;maxite</span></code>, <code><span class="nw">&#45;x&#95;thresh</span></code>, <code><span class="nw">&#45;rot&#95;thresh</span></code>, <code><span class="nw">&#45;delta</span></code>, <code><span class="nw">&#45;params</span> <span class="nw">m</span> <span class="nw">x</span> <span class="nw">r</span> <span class="nw">d</span></code> | <code><span class="nw">max&#95;iterations</span></code>, <code><span class="nw">x&#95;threshold</span></code>, <code><span class="nw">rot&#95;threshold</span></code>, <code><span class="nw">delta</span></code> | <code><span class="nw">max&#95;iterations&#61;23</span></code>, <code><span class="nw">x&#95;threshold&#61;0&#46;01</span></code>, <code><span class="nw">rot&#95;threshold&#61;0&#46;02</span></code>, <code><span class="nw">delta&#61;0&#46;70</span></code> | non-positive values are ignored by <code><span class="nw">&#45;maxite</span></code> etc. (the wrapper refuses them) |
| <code><span class="nw">&#45;tshift</span> <span class="nw">ii</span></code> | <code><span class="nw">tshift</span></code> | <code><span class="nw">None</span></code> | 3dTshift's default (Fourier, the trend restored) before registering<span class="opt-help">The clean room's usage: “slice-time correct the input first (ignoring ii time points)”</span> |
| <code><span class="nw">&#45;rotparent</span> <span class="nw">rset</span></code>, <code><span class="nw">&#45;gridparent</span> <span class="nw">gset</span></code> | <code><span class="nw">rotparent</span></code>, <code><span class="nw">gridparent</span></code> (paths) | <code><span class="nw">rotparent&#61;None</span></code>, <code><span class="nw">gridparent&#61;None</span></code> | the rotparent must be an output of AFNI's own 3dvolreg (larmorx writes no <code><span class="nw">VOLREG&#95;&#42;</span></code> attributes) |
| <code><span class="nw">&#45;verbose</span></code> (twice: more) | (command line only) |  | the CPU times are printed as 0<span class="opt-help">The clean room's usage: “print progress reports (twice: lots of output)”</span> |
| <code><span class="nw">&#45;&#64;</span></code> | (command line only) |  | the arguments from standard input |
| <code><span class="nw">&#45;overwrite</span></code>, <code><span class="nw">&#45;Dname&#61;value</span></code>, <code><span class="nw">&#45;ok&#95;1D&#95;text</span></code>, <code><span class="nw">&#45;skip&#95;afnirc</span></code> | <code><span class="nw">afni&#95;settings</span></code> | <code><span class="nw">None</span></code> | AFNI's global options, anywhere on the command line; in Python AFNI's variables, as for 3dTshift<span class="opt-help">The clean room's usage: “replace an existing output (AFNI_DECONFLICT=OVERWRITE)”</span><span class="opt-help">The clean room's usage: “accepted (no .afnirc file is read)”</span> |
| <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | the result does not depend on it (AFNI's 3dvolreg is single-threaded on this path; the clean room runs the work inside each volume in parallel) |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | <code><span class="nw">fix</span></code> (default) or <code><span class="nw">reproduce</span></code> |
| <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> | <code><span class="nw">implementation</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> | <code><span class="nw">auto</span></code>, <code><span class="nw">replica</span></code> or <code><span class="nw">clean&#45;room</span></code> (<code><span class="nw">&#45;&#45;implementation</span></code> before the family) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `afni` on the command line (`larmorx --n-threads 4 afni 3dvolreg ...`) and are arguments of `lx.afni.volreg`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all); the result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default) and <code><span class="nw">&#34;replica&#34;</span></code>: the bit-exact replica; <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works): the clean room. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code> (AFNI's output); a <code><span class="nw">UpstreamDefectWarning</span></code> names each defect that changed the result. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `bold.nii.gz` (a synthetic series of 4 such heads). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# As fMRIPrep's RobustAverage calls 3dvolreg (-Fourier -twopass -zpad 4).
r = lx.afni.volreg("bold.nii.gz", **lx.afni.fmriprep_volreg_options())
r.parameters.shape  # -> (4, 6)
```

```bash
larmorx afni 3dvolreg -Fourier -twopass -zpad 4 -1Dfile mc.1D -1Dmatrix_save mc.aff12.1D -maxdisp1D md.1D -prefix reg.nii.gz bold.nii.gz
```

## Ports {#ports}

`3dvolreg` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 AND CC-BY-4.0 | validated | [afni-volreg-replica](repo:docs/validation/afni-volreg-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [afni-volreg-original](repo:docs/validation/afni-volreg-original.md) |

- **The replica: status `validated`**, bit-identical with AFNI 26.3.05 in every compared case of
  its record ([afni-volreg-replica](repo:docs/validation/afni-volreg-replica.md), 2026-11-07, the
  standard tier through the oracle-output cache: 190 cases, 158 pass, 30 rejected by both alike,
  2 expected divergences; all 137 compared cases that write outputs give AFNI's bytes, data and
  NIfTI header, and the messages of the 180 cases that ran both programs are AFNI's byte for
  byte): every option, data type, orientation, message and failure case; fMRIPrep's
  RobustAverage call on the BOLD references of 6 oracle runs (single-band, two volumes,
  multiband with 160 × 160 × 96 voxels, multi-echo, multiband 8 stored as uint16, Philips
  float32; 7 more in the full tier) and on sdcflows' PEPOLAR reference averages of 2, whose
  medians are fMRIPrep's own `gen_avg` and `ref_average` outputs byte for byte; AFNI 25.2.09
  identical on every case. Random testing: a trial and two checks of the final build
  (`validation/difftest/triage.toml`: the trial's 39,751 random cases agree once its findings
  were fixed; the final build's checks ran 22,539 cases without a difference, whose notices
  without a visible change made AFNI-99's notice exact, then 20,824, every one agreeing).
- **The clean room: status `experimental`** (2026-11-08), held to `specs/3dvolreg.md` §14.3's
  thresholds, not to AFNI's bits (the shear decomposition's exact ties:
  [The clean room](repo:docs/api/afni-volreg.md#the-clean-room)), in its record
  ([afni-volreg-original](repo:docs/validation/afni-volreg-original.md), the standard tier from a clean
  commit: 251 cases, 185 pass, 63 refused alike with the same messages (every error, AFNI-88,
  -89, -90, -94, -96 included), 3 expected divergences (larmorx refuses AFNI's .HEAD/.BRIK
  format, twice, and AFNI-96's short attribute, rule B), none failing: every option, data type,
  orientation, message and failure case; fMRIPrep's RobustAverage call on 8 BOLD references of
  6 oracle runs and sdcflows' 2 PEPOLAR averages, whose inputs re-made in fMRIPrep's image give
  fMRIPrep's own medians from AFNI's volumes byte for byte: the clean room's medians within
  0.115 of the limit their volumes imply (ds000256's high-motion child run; 0.0016 or less on
  the others), its registered volumes within 0.68 of each volume's limit (the same run, as
  AFNI's own tie variants), `-final NN` within the nearest-neighbour rule, `-SAVEDISP`'s
  nineteen datasets bit for bit on AFNI's raw displacements; 417 of 1,096 `-1Dfile` lines
  identical with AFNI's; the default held to the replica's default by the same thresholds,
  with the defects named the same; every byte the same at 1, 2, 5 and 14 threads), and a
  random-testing trial (21,710 cases, 11,385 agreeing; a seeded sample of 1,200 of the
  differences judged again with the final build: 67 agree, 860 within 3 times the clean room's
  own spread under the ties, 268 runaways whose structure agrees, 5 explained; triaged in
  `validation/difftest/triage.toml`; [findings](repo:docs/findings/afni-volreg-clean-room.md)).

`3dvolreg` has two ports, both in `pip install larmorx`:

- **The replica** is bit-exact, translated from AFNI's source (`crates/larmorx-afni-replica`;
  Apache-2.0, with CC BY 4.0's attribution for the code of the Medical College of Wisconsin,
  which AFNI 26.3.05 releases under CC BY 4.0 ([NOTICE](repo:NOTICE),
  [licensing](repo:docs/licensing.md)), and the NIH's public-domain files).
- **The clean room** (`crates/larmorx-afni/src/volreg/`, Apache-2.0) is built for speed and
  written from [`specs/3dvolreg.md`](repo:specs/3dvolreg.md) by an agent that never read AFNI's
  source or the replica ([The clean room](repo:docs/api/afni-volreg.md#the-clean-room) says how it is built and why its
  numbers differ from AFNI's in the last digits).

`implementation="auto"` (the default, and `larmorx afni 3dvolreg`) and `"replica"` run the
replica, in the same process; `"clean-room"` (`"original"`, 0.1.0rc1's spelling, still works)
(`--implementation clean-room` before the family, or `LARMORX_IMPLEMENTATION`) runs the clean
room, also in the same process. Each image of the result names the one that ran in its
`implementation`.

## Evidence {#evidence}

How each of `3dvolreg`'s ports was measured against AFNI, case by case: [its evidence](/evidence/afni-volreg/).

## More in the repository {#more}

The API page [docs/api/afni-volreg.md](repo:docs/api/afni-volreg.md) holds what `3dvolreg` shares with the page's other programs:

- [Upstream defects](repo:docs/api/afni-volreg.md#upstream-defects)
- [Differences from AFNI shared with every larmorx AFNI tool](repo:docs/api/afni-volreg.md#differences-from-afni-shared-with-every-larmorx-afni-tool)
- [The clean room](repo:docs/api/afni-volreg.md#the-clean-room)
- [Speed](repo:docs/api/afni-volreg.md#speed)
