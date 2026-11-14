---
title: "`topup`"
kicker: "Programs · FSL"
description: "LARMORX reference for FSL 6.0.7.23 `topup`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl topup"
  python: "lx.fsl.topup"
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
    crates/larmorx-fsl/src/cli/topup.rs: "adf22853a599c595"
    docs/api/fsl-topup.md: "5177b83d500b0c2f"
    python/larmorx/fsl/topup.py: "316784a1d5ebe0d4"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

`topup` estimates the off-resonance field (Hz) that displaces echo-planar images along their phase
encoding, from two or more images acquired with different phase encodings (typically "blip up"
and "blip down"), with each image's rigid-body movement if asked.

## Command line {#command-line}

```text synopsis
larmorx fsl topup --imain=<some 4D image> --datain=<text file> --config=<text file with parameters> --out=my_topup_results
```

Everything after `larmorx fsl topup` is the original's command line: the arguments of FSL 6.0.7.23's `topup`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl topup ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>topup</code>'s usage text, as the clean room prints it</summary>

```text
Part of FSL (ID: 2412.6-dirty)
topup

Usage: 
topup --imain=<some 4D image> --datain=<text file> --config=<text file with parameters> --out=my_topup_results


Compulsory arguments (You MUST set one or more of):
	--imain		name of 4D file with images

Optional arguments (You may optionally specify one or more of):
	--datain	name of text file with PE directions/times
	--acqp		alternative way to specify text file with PE directions/times
	--out		base-name of output files (spline coefficients (Hz) and movement parameters)
	--fout		name of image file with field (Hz)
	--iout		name of 4D image file with unwarped images
	--featout		base-name of output for export to FEAT
	--logout	Name of log-file
	--warpres	(approximate) resolution (in mm) of warp basis for the different sub-sampling levels, default 10
	--subsamp	sub-sampling scheme, default 1
	--fwhm		FWHM (in mm) of gaussian smoothing kernel, default 8
	--config	Name of config file specifying command line arguments
	--miter		Max # of non-linear iterations, default 5
	--lambda	Weight of regularisation, default depending on --ssqlambda and --regmod switches. See user documetation.
	--ssqlambda	If set (=1), lambda is weighted by current ssq, default 1
	--regmod	Model for regularisation of warp-field [membrane_energy bending_energy], default bending_energy
	--estmov	Estimate movements if set, default 1 (true)
	--minmet	Minimisation method 0=Levenberg-Marquardt, 1=Scaled Conjugate Gradient, default 0 (LM)
	--splineorder	Order of spline, 2->Qadratic spline, 3->Cubic spline. Default=3
	--numprec	Precision for representing Hessian, double or float. Default double
	--interp	Image interpolation model, linear or spline. Default spline
	--scale		If set (=1), the images are individually scaled to a common mean, default 0 (false)
	--regrid		If set (=1), the calculations are done in a different grid, default 1 (true)
	--nthr		Number of threads to use (cannot be greater than numbers of hardware cores), default 1
	-h,--help	display help info
	-v,--verbose	Print diagonostic information while running
	-h,--help	display help info
```

</details>

## Python {#python}

```python
lx.fsl.topup(
    images: Any,
    acquisition: Any,
    *,
    config: str | os.PathLike[str] | None = None,
    fsldir: str | os.PathLike[str] | None = None,
    warpres: float | Sequence[float] | None = None,
    subsamp: int | Sequence[int] | None = None,
    fwhm: float | Sequence[float] | None = None,
    miter: int | Sequence[int] | None = None,
    lambda_: float | Sequence[float] | None = None,
    ssqlambda: bool | None = None,
    regmod: Regularisation | None = None,
    estmov: bool | Sequence[bool] | None = None,
    minmet: Minimiser | Sequence[Minimiser] | None = None,
    splineorder: int | None = None,
    numprec: Literal["double", "float"] | None = None,
    interp: Literal["spline", "linear"] | None = None,
    scale: bool | None = None,
    regrid: bool | None = None,
    field: bool = True,
    corrected: bool = False,
    feat: bool = False,
    displacement_fields: bool = False,
    rigid_body_matrices: bool = False,
    jacobians: bool = False,
    verbose: bool = False,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
) -> TopupResult
```

Where `Regularisation` is one of `"bending_energy"`, `"membrane_energy"`; `Minimiser` is one of `"LM"`, `"SCG"`; `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

Estimate the susceptibility-induced field of `images` (FSL's `topup`).

`None` (the default of every estimation setting) leaves the option out, so the configuration
file, or topup's own default, sets it; a value given wins over the configuration, as on topup's
command line. FSL's settings are the call's (CLAUDE.md rule 6): the outputs are NIfTI-1 read
back, and no FSL variable of the process reaches the program.

```python
import larmorx as lx

# fMRIPrep's call (sdcflows' PEPOLAR estimation):
# topup --config=b02b0.cnf --datain=<encfile> --imain=<pair> --out=<base> --iout --fout
#       --jacout --logout --rbmout --dfout
acq = [[0, 1, 0, 0.0138], [0, -1, 0, 0.0138]]   # phase-encoding vector and read-out time (s)
r = lx.fsl.topup(
    "b0_pair.nii.gz", acq, config="sdcflows/data/flirtsch/b02b0.cnf",
    corrected=True, jacobians=True, rigid_body_matrices=True, displacement_fields=True,
)
field_hz = r.field                     # lx.Image on the input's grid
up_corrected = r.corrected.data[..., 0]
```

Its result, `TopupResult`, holds what `topup` wrote, read back.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">coefficients</span></code> | <code><span class="nw">Image</span></code> | The field's B-spline coefficients in Hz (<code><span class="nw">&#45;&#45;out</span></code>'s <code><span class="nw">&#95;fieldcoef</span></code>: an image of the coefficients' grid whose voxel sizes are the knot spacings in voxels, whose intent holds the spline order and the field's voxel sizes, and whose translation the field's size). <code><span class="nw">applytopup</span></code> reads it with <code><span class="nw">movement&#95;parameters</span></code>. |
| <code><span class="nw">movement&#95;parameters</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | Each image's rigid-body movement relative to the first (<code><span class="nw">&#95;movpar&#46;txt</span></code>): one row per image, three translations (mm) then three rotations (radians) about the field of view's centre. |
| <code><span class="nw">field</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">field&#61;True</span></code>: the field in Hz on the input's grid (<code><span class="nw">&#45;&#45;fout</span></code>), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">corrected</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">corrected&#61;True</span></code>: the images corrected by Jacobian modulation (<code><span class="nw">&#45;&#45;iout</span></code>, 4D) and their mean over the voxels every image sees (<code><span class="nw">&#45;&#45;iout</span></code>'s <code><span class="nw">&#95;mean</span></code>), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">corrected&#95;mean</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">corrected&#61;True</span></code>: the images corrected by Jacobian modulation (<code><span class="nw">&#45;&#45;iout</span></code>, 4D) and their mean over the voxels every image sees (<code><span class="nw">&#45;&#45;iout</span></code>'s <code><span class="nw">&#95;mean</span></code>), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">feat&#95;fieldmap&#95;rads</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">feat&#61;True</span></code>: the field in rad/s and the mean corrected image (<code><span class="nw">&#45;&#45;featout</span></code>'s <code><span class="nw">&#95;fieldmap&#95;rads</span></code> and <code><span class="nw">&#95;fieldmap&#95;mag</span></code>), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">feat&#95;fieldmap&#95;mag</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">feat&#61;True</span></code>: the field in rad/s and the mean corrected image (<code><span class="nw">&#45;&#45;featout</span></code>'s <code><span class="nw">&#95;fieldmap&#95;rads</span></code> and <code><span class="nw">&#95;fieldmap&#95;mag</span></code>), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">displacement&#95;fields</span></code> | <code><span class="nw">tuple&#91;Image&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">displacement&#95;fields&#61;True</span></code>: one 4D image per input image, its displacement in mm along x, y and z (<code><span class="nw">&#45;&#45;dfout</span></code>), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">rigid&#95;body&#95;matrices</span></code> | <code><span class="nw">tuple&#91;np&#46;ndarray&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">rigid&#95;body&#95;matrices&#61;True</span></code>: one 4 x 4 matrix per image (<code><span class="nw">&#45;&#45;rbmout</span></code>), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">jacobians</span></code> | <code><span class="nw">tuple&#91;Image&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | With <code><span class="nw">jacobians&#61;True</span></code>: each image's Jacobian determinant (<code><span class="nw">&#45;&#45;jacout</span></code>), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">log</span></code> | <code><span class="nw">str</span></code> | The log file's text (<code><span class="nw">&#45;&#45;logout</span></code>: the settings of every level). |
| <code><span class="nw">stdout</span></code> | <code><span class="nw">str</span></code> | topup's standard output (its progress with <code><span class="nw">verbose&#61;True</span></code>). |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `topup` accepts (`crates/larmorx-fsl/src/cli/topup.rs`) and the arguments of `lx.fsl.topup` (`python/larmorx/fsl/topup.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">topup</span></code> option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;&#45;imain</span></code> | <code><span class="nw">images</span></code> |  | the 4D image of the volumes (path or <code><span class="nw">lx&#46;Image</span></code>)<span class="opt-help">FSL: “name of 4D file with images”</span> |
| <code><span class="nw">&#45;&#45;datain</span></code>, <code><span class="nw">&#45;&#45;acqp</span></code> | <code><span class="nw">acquisition</span></code> |  | per volume the phase-encoding vector (3 numbers, voxel axes) and the read-out time (s): a file, or an array of shape <code><span class="nw">&#40;n&#44;</span> <span class="nw">4&#41;</span></code><span class="opt-help">FSL: “name of text file with PE directions/times”</span><span class="opt-help">FSL: “alternative way to specify text file with PE directions/times”</span> |
| <code><span class="nw">&#45;&#45;config</span></code> | <code><span class="nw">config</span></code> | <code><span class="nw">None</span></code> | a configuration file, or the name of one of FSL's: the six FSL ships (<code><span class="nw">&#34;b02b0&#34;</span></code>, <code><span class="nw">&#34;b02b0&#95;1&#34;</span></code>, <code><span class="nw">&#34;b02b0&#95;2&#34;</span></code>, <code><span class="nw">&#34;b02b0&#95;4&#34;</span></code>, <code><span class="nw">&#34;b02b0&#95;7T&#34;</span></code>, <code><span class="nw">&#34;test&#95;acqp&#34;</span></code>, with or without <code><span class="nw">&#46;cnf</span></code>) need nothing more ([LARMORX's own settings](repo:docs/api/fsl-topup.md#larmorxs-own-settings)); any other needs <code><span class="nw">fsldir</span></code><span class="opt-help">FSL: “Name of config file specifying command line arguments”</span> |
| <code><span class="nw">FSLDIR</span></code> | <code><span class="nw">fsldir</span></code> | <code><span class="nw">None</span></code> | the FSL installation whose <code><span class="nw">etc&#47;flirtsch</span></code> holds FSL's configurations (only for a <code><span class="nw">config</span></code> given by name; its file wins over LARMORX's own settings of the same name) |
| <code><span class="nw">&#45;&#45;warpres</span></code> | <code><span class="nw">warpres</span></code> | <code><span class="nw">None</span></code> | knot spacing (mm), one value or one per level; 10<span class="opt-help">FSL: “(approximate) resolution (in mm) of warp basis for the different sub-sampling levels, default 10”</span> |
| <code><span class="nw">&#45;&#45;subsamp</span></code> | <code><span class="nw">subsamp</span></code> | <code><span class="nw">None</span></code> | subsampling factor per level; 1<span class="opt-help">FSL: “sub-sampling scheme, default 1”</span> |
| <code><span class="nw">&#45;&#45;fwhm</span></code> | <code><span class="nw">fwhm</span></code> | <code><span class="nw">None</span></code> | Gaussian smoothing (mm) per level; 8<span class="opt-help">FSL: “FWHM (in mm) of gaussian smoothing kernel, default 8”</span> |
| <code><span class="nw">&#45;&#45;miter</span></code> | <code><span class="nw">miter</span></code> | <code><span class="nw">None</span></code> | iterations per level; 5<span class="opt-help">FSL: “Max # of non-linear iterations, default 5”</span> |
| <code><span class="nw">&#45;&#45;lambda</span></code> | <code><span class="nw">lambda&#95;</span></code> | <code><span class="nw">None</span></code> | regularisation weight per level; 0<span class="opt-help">FSL: “Weight of regularisation, default depending on --ssqlambda and --regmod switches. See user documetation.”</span> |
| <code><span class="nw">&#45;&#45;ssqlambda</span></code> | <code><span class="nw">ssqlambda</span></code> | <code><span class="nw">None</span></code> | the weight times the current sum of squared differences; on<span class="opt-help">FSL: “If set (=1), lambda is weighted by current ssq, default 1”</span> |
| <code><span class="nw">&#45;&#45;regmod</span></code> | <code><span class="nw">regmod</span></code> | <code><span class="nw">None</span></code> | <code><span class="nw">&#34;bending&#95;energy&#34;</span></code> (default) or <code><span class="nw">&#34;membrane&#95;energy&#34;</span></code><span class="opt-help">FSL: “Model for regularisation of warp-field [membrane_energy bending_energy], default bending_energy”</span> |
| <code><span class="nw">&#45;&#45;estmov</span></code> | <code><span class="nw">estmov</span></code> | <code><span class="nw">None</span></code> | estimate the movements, per level; on<span class="opt-help">FSL: “Estimate movements if set, default 1 (true)”</span> |
| <code><span class="nw">&#45;&#45;minmet</span></code> | <code><span class="nw">minmet</span></code> | <code><span class="nw">None</span></code> | <code><span class="nw">&#34;LM&#34;</span></code> (Levenberg-Marquardt, default) or <code><span class="nw">&#34;SCG&#34;</span></code> (scaled conjugate gradients), per level<span class="opt-help">FSL: “Minimisation method 0=Levenberg-Marquardt, 1=Scaled Conjugate Gradient, default 0 (LM)”</span> |
| <code><span class="nw">&#45;&#45;splineorder</span></code> | <code><span class="nw">splineorder</span></code> | <code><span class="nw">None</span></code> | 2 (quadratic) or 3 (cubic, default)<span class="opt-help">FSL: “Order of spline, 2-&gt;Qadratic spline, 3-&gt;Cubic spline. Default=3”</span> |
| <code><span class="nw">&#45;&#45;numprec</span></code> | <code><span class="nw">numprec</span></code> | <code><span class="nw">None</span></code> | the Hessian's precision: <code><span class="nw">&#34;double&#34;</span></code> (default) or <code><span class="nw">&#34;float&#34;</span></code><span class="opt-help">FSL: “Precision for representing Hessian, double or float. Default double”</span> |
| <code><span class="nw">&#45;&#45;interp</span></code> | <code><span class="nw">interp</span></code> | <code><span class="nw">None</span></code> | <code><span class="nw">&#34;spline&#34;</span></code> (default) or <code><span class="nw">&#34;linear&#34;</span></code><span class="opt-help">FSL: “Image interpolation model, linear or spline. Default spline”</span> |
| <code><span class="nw">&#45;&#45;scale</span></code> | <code><span class="nw">scale</span></code> | <code><span class="nw">None</span></code> | each volume scaled to a mean of 100 by itself; off<span class="opt-help">FSL: “If set (=1), the images are individually scaled to a common mean, default 0 (false)”</span> |
| <code><span class="nw">&#45;&#45;regrid</span></code> | <code><span class="nw">regrid</span></code> | <code><span class="nw">None</span></code> | work on a grid of <code><span class="nw">n</span> <span class="nw">&#43;</span> <span class="nw">s&#95;max</span></code> voxels per axis; on<span class="opt-help">FSL: “If set (=1), the calculations are done in a different grid, default 1 (true)”</span> |
| <code><span class="nw">&#45;&#45;out</span></code> | the result |  | the base name of the coefficients (<code><span class="nw">&#95;fieldcoef</span></code>) and the movements (<code><span class="nw">&#95;movpar&#46;txt</span></code>)<span class="opt-help">FSL: “base-name of output files (spline coefficients (Hz) and movement parameters)”</span> |
| <code><span class="nw">&#45;&#45;fout</span></code> | <code><span class="nw">field</span></code> | <code><span class="nw">True</span></code> | the field in Hz<span class="opt-help">FSL: “name of image file with field (Hz)”</span> |
| <code><span class="nw">&#45;&#45;iout</span></code> | <code><span class="nw">corrected</span></code> | <code><span class="nw">False</span></code> | the corrected volumes and their mean (<code><span class="nw">&#95;mean</span></code>)<span class="opt-help">FSL: “name of 4D image file with unwarped images”</span> |
| <code><span class="nw">&#45;&#45;featout</span></code> | <code><span class="nw">feat</span></code> | <code><span class="nw">False</span></code> | the field in rad/s and the corrected mean, for FEAT<span class="opt-help">FSL: “base-name of output for export to FEAT”</span> |
| <code><span class="nw">&#45;&#45;dfout</span></code> | <code><span class="nw">displacement&#95;fields</span></code> | <code><span class="nw">False</span></code> | each volume's displacement field (mm) |
| <code><span class="nw">&#45;&#45;rbmout</span></code> | <code><span class="nw">rigid&#95;body&#95;matrices</span></code> | <code><span class="nw">False</span></code> | each volume's rigid-body matrix |
| <code><span class="nw">&#45;&#45;jacout</span></code> | <code><span class="nw">jacobians</span></code> | <code><span class="nw">False</span></code> | each volume's Jacobian determinant |
| <code><span class="nw">&#45;&#45;logout</span></code> | the result |  | the log's text: the result's <code><span class="nw">log</span></code><span class="opt-help">FSL: “Name of log-file”</span> |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> | <code><span class="nw">verbose&#61;True</span></code> | <code><span class="nw">False</span></code> | the cost of every evaluation, in the result's <code><span class="nw">stdout</span></code><span class="opt-help">FSL: “Print diagonostic information while running”</span> |
| <code><span class="nw">&#45;&#45;nthr</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | threads; the results are FSL's one-thread results at any count (FSL-116). On the command line without <code><span class="nw">&#45;&#45;nthr</span></code> (nor in the configuration), the replica takes LARMORX's own <code><span class="nw">&#45;&#45;n&#45;threads</span></code> (else <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code>, else every logical CPU)<span class="opt-help">FSL: “Number of threads to use (cannot be greater than numbers of hardware cores), default 1”</span> |
| <code><span class="nw">&#45;&#45;debug</span></code>, <code><span class="nw">&#45;&#45;trace</span></code>, <code><span class="nw">&#45;&#45;profile</span></code> | command line only |  | the hidden debugging options |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | command line only |  | <span class="opt-help">FSL: “display help info”</span> |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects as FSL has them |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl topup ...`) and are arguments of `lx.fsl.topup`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all); the results do not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects corrected, or FSL's behaviour (<code><span class="nw">docs&#47;api&#47;fsl&#45;topup&#46;md</span></code>, "Defects of the original, corrected by default"). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `b0.nii.gz` (a synthetic series of 4 such heads), `acqp.txt` (the phase encodings of four volumes, two along +y and two along −y, read out in 0.05 s). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# One level of a coarse field, without movements: a quick estimate.
r = lx.fsl.topup("b0.nii.gz", "acqp.txt", warpres=20, subsamp=2, miter=2, estmov=False)
r.field.shape  # -> (40, 48, 40)
```

```bash
larmorx fsl topup --imain=b0 --datain=acqp.txt --warpres=20 --subsamp=2 --miter=2 --estmov=0 --out=tu --fout=field
```

## Ports {#ports}

`topup` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-topup-replica](repo:docs/validation/fsl-topup-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-topup](repo:docs/validation/fsl-topup.md) |

Both ports are complete (`specs/topup.md` §2 to §10): every option of topup (precision,
interpolation, both regularisers, spline orders, scaling, regridding, the minimisers per level,
the movements, FSL's shipped configurations, x and y and oblique phase encodings, four volumes, a
zero read-out time, `--debug`, `--trace`, `--profile`), every message, exit status and failure
case, each compared file by file with FSL's. fMRIPrep's topup call: bit-identical in the
replica in two of fMRIPrep's runs (ds005040 and ds001600: every file topup writes); in the clean
room, ds001600 within the thresholds, ds005040 within FSL's own band of a last-bit change (the
field's p99 0.61 Hz against FSL at `--nthr=4`'s 0.64).

The replica's record holds 102 cases of `topup`: 59 identical to FSL, 42 where both refuse
alike, 1 refused in both modes. The clean room's holds 112: 62 within its thresholds, 42 refused
alike, 8 expected divergences ([the records](repo:docs/api/fsl-topup.md#the-records) say why). The clean room is built for
speed: fMRIPrep's call on ds005040 takes 2.8 s on one thread and 0.8 s on 14 (FSL 32.6 s, the
replica 29.7 s), on ds001600 7.7 s and 2.0 s (FSL 77.4 s, the replica 71.4 s).

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

How each of `topup`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-topup/).

## More in the repository {#more}

The API page [docs/api/fsl-topup.md](repo:docs/api/fsl-topup.md) holds what `topup` shares with the page's other programs:

- [The records](repo:docs/api/fsl-topup.md#the-records)
- [FSL's settings files without FSL](repo:docs/api/fsl-topup.md#fsls-settings-files-without-fsl)
- [LARMORX's own settings](repo:docs/api/fsl-topup.md#larmorxs-own-settings)
- [File names on Windows](repo:docs/api/fsl-topup.md#file-names-on-windows)
- [The clean room](repo:docs/api/fsl-topup.md#the-clean-room)
- [Defects of the original, corrected by default](repo:docs/api/fsl-topup.md#defects-of-the-original-corrected-by-default)
- [Not yet](repo:docs/api/fsl-topup.md#not-yet)
- [History](repo:docs/api/fsl-topup.md#history)
