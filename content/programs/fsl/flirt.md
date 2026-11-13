---
title: "`flirt`"
kicker: "Programs · FSL"
lede: "`flirt` registers one image to another with an affine transform, with every cost function and boundary-based registration (BBR)."
description: "LARMORX reference for FSL 6.0.7.23 `flirt`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl flirt"
  python: "lx.fsl.flirt"
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
    crates/larmorx-fsl/src/cli/flirt.rs: "30a6569fa6aec523"
    crates/larmorx-fsl/src/flirt/mod.rs: "97b905a9b8cc9c3a"
    docs/api/fsl-flirt.md: "7d546a158684c299"
    python/larmorx/fsl/flirt.py: "31c67a2bf18f6789"
    validation/tools.toml: "f0750687390307f1"
---

## What it does {#what-it-does}

It finds a transform of 6, 7, 9 or 12 degrees of freedom, or
applies a given matrix (`-applyxfm`, `-applyisoxfm`), and writes the 4 × 4 matrix from the
input's FSL millimetres to the reference's (`-omat`) and, on request, the input resampled onto the
reference's grid (`-out`).

## Command line {#command-line}

```text synopsis
larmorx fsl flirt [options] -in <inputvol> -ref <refvol> -out <outputvol>
larmorx fsl flirt [options] -in <inputvol> -ref <refvol> -omat <outputmatrix>
larmorx fsl flirt [options] -in <inputvol> -ref <refvol> -applyxfm -init <matrix> -out <outputvol>
```

Everything after `larmorx fsl flirt` is the original's command line: the arguments of FSL 6.0.7.23's `flirt`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl flirt ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>flirt</code>'s usage text, as the clean room prints it</summary>

```text
FLIRT version 6.0

Usage: flirt [options] -in <inputvol> -ref <refvol> -out <outputvol>
       flirt [options] -in <inputvol> -ref <refvol> -omat <outputmatrix>
       flirt [options] -in <inputvol> -ref <refvol> -applyxfm -init <matrix> -out <outputvol>

  Available options are:
        -in  <inputvol>                    (no default)
        -ref <refvol>                      (no default)
        -init <matrix-filname>             (input 4x4 affine matrix)
        -omat <matrix-filename>            (output in 4x4 ascii format)
        -out, -o <outputvol>               (default is none)
        -datatype {char,short,int,float,double}                    (force output data type)
        -cost {mutualinfo,corratio,normcorr,normmi,leastsq,labeldiff,bbr}        (default is corratio)
        -searchcost {mutualinfo,corratio,normcorr,normmi,leastsq,labeldiff,bbr}  (default is corratio)
        -usesqform                         (initialise using appropriate sform or qform)
        -displayinit                       (display initial matrix)
        -anglerep {quaternion,euler}       (default is euler)
        -interp {trilinear,nearestneighbour,sinc,spline}  (final interpolation: def - trilinear)
        -sincwidth <full-width in voxels>  (default is 7)
        -sincwindow {rectangular,hanning,blackman}
        -bins <number of histogram bins>   (default is 256)
        -dof  <number of transform dofs>   (default is 12)
        -noresample                        (do not change input sampling)
        -forcescaling                      (force rescaling even for low-res images)
        -minsampling <vox_dim>             (set minimum voxel dimension for sampling (in mm))
        -applyxfm                          (applies transform (no optimisation) - requires -init)
        -applyisoxfm <scale>               (as applyxfm but forces isotropic resampling)
        -paddingsize <number of voxels>    (for applyxfm: interpolates outside image by size)
        -searchrx <min_angle> <max_angle>  (angles in degrees: default is -90 90)
        -searchry <min_angle> <max_angle>  (angles in degrees: default is -90 90)
        -searchrz <min_angle> <max_angle>  (angles in degrees: default is -90 90)
        -nosearch                          (sets all angular search ranges to 0 0)
        -coarsesearch <delta_angle>        (angle in degrees: default is 60)
        -finesearch <delta_angle>          (angle in degrees: default is 18)
        -schedule <schedule-file>          (replaces default schedule)
        -refweight <volume>                (use weights for reference volume)
        -inweight <volume>                 (use weights for input volume)
        -wmseg <volume>                    (white matter segmentation volume needed by BBR cost function)
        -wmcoords <text matrix>            (white matter boundary coordinates for BBR cost function)
        -wmnorms <text matrix>             (white matter boundary normals for BBR cost function)
        -fieldmap <volume>                 (fieldmap image in rads/s - must be already registered to the reference image)
        -fieldmapmask <volume>             (mask for fieldmap image)
        -pedir <index>                     (phase encode direction of EPI - 1/2/3=x/y/z & -1/-2/-3=-x/-y/-z)
        -echospacing <value>               (value of EPI echo spacing - units of seconds)
        -bbrtype <value>                   (type of bbr cost function: signed [default], global_abs, local_abs)
        -bbrslope <value>                  (value of bbr slope)
        -setbackground <value>             (use specified background value for points outside FOV)
        -noclamp                           (do not use intensity clamping)
        -noresampblur                      (do not use blurring on downsampling)
        -2D                                (use 2D rigid body mode - ignores dof)
        -verbose <num>                     (0 is least and default)
        -v                                 (same as -verbose 1)
        -i                                 (pauses at each stage: default is off)
        -version                           (prints version number)
        -help
```

</details>

## Python {#python}

```python
lx.fsl.flirt(
    in_image: Any,
    ref_image: Any,
    *,
    init: Any = None,
    dof: int = 12,
    cost: Cost = "corratio",
    search_cost: Cost = "corratio",
    bins: int = 256,
    interp: Interpolation = "trilinear",
    sinc_width: int = 7,
    sinc_window: SincWindow = "hanning",
    search_rx: tuple[float, float] = (-90.0, 90.0),
    search_ry: tuple[float, float] = (-90.0, 90.0),
    search_rz: tuple[float, float] = (-90.0, 90.0),
    no_search: bool = False,
    coarse_search: float = 60.0,
    fine_search: float = 18.0,
    schedule: str | os.PathLike[str] | None = None,
    apply_xfm: bool = False,
    apply_isoxfm: float | None = None,
    use_sqform: bool = False,
    out: bool = True,
    datatype: DataType | None = None,
    ref_weight: Any = None,
    in_weight: Any = None,
    wm_seg: Any = None,
    wm_coords: Any = None,
    wm_norms: Any = None,
    fieldmap: Any = None,
    fieldmap_mask: Any = None,
    pe_dir: int | None = None,
    echo_spacing: float = 0.0005,
    bbr_type: BbrType = "signed",
    bbr_slope: float = -0.5,
    padding_size: float = 0.0,
    background: float | None = None,
    no_resample: bool = False,
    no_clamp: bool = False,
    no_resample_blur: bool = False,
    force_scaling: bool = False,
    min_sampling: float | None = None,
    base_scale: float | None = None,
    two_d: bool = False,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
) -> FlirtResult
```

Where `Cost` is one of `"corratio"`, `"mutualinfo"`, `"normcorr"`, `"normmi"`, `"leastsq"`, `"labeldiff"`, `"bbr"`, `"woods"`; `Interpolation` is one of `"trilinear"`, `"nearestneighbour"`, `"sinc"`, `"spline"`; `SincWindow` is one of `"rectangular"`, `"hanning"`, `"blackman"`; `DataType` is one of `"char"`, `"short"`, `"int"`, `"float"`, `"double"`; `BbrType` is one of `"signed"`, `"global_abs"`, `"local_abs"`; `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

Register `in_image` to `ref_image` (FSL's `flirt`), or apply `init` with `apply_xfm`/`apply_isoxfm`.

Images are paths or `lx.Image` objects. `init` is a 4 × 4 matrix (an array or a `.mat` file),
`schedule` a schedule file. The result's `matrix` maps the input's FSL millimetres to the
reference's, as `-omat` writes it; its `image` is the input on the reference's grid (`None`
unless `out`); its `stdout` holds FLIRT's verbose lines and a schedule's `print`.

fMRIPrep's boundary-based registration of a BOLD reference to the T1w (no FreeSurfer), with
FSL's `bbr.sch` (in `$FSLDIR/etc/flirtsch`):

```python
r = lx.fsl.flirt(
    "boldref.nii.gz", "T1w_brain.nii.gz",
    init="init.mat", cost="bbr", search_cost="bbr", dof=6, base_scale=1,
    schedule="/path/to/fsl/etc/flirtsch/bbr.sch", wm_seg="wm_mask.nii.gz",
)
r.matrix     # 4 x 4, input FSL mm -> reference FSL mm (as -omat writes it)
r.image      # the BOLD reference on the T1w's grid
```

Its result, `FlirtResult`, holds what `flirt` computed: the 4 x 4 matrix (input FSL mm to reference FSL mm), the input resampled onto the reference's grid (`None` unless `out` was asked for), and FLIRT's standard output (its verbose lines, a schedule's `print`).

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">matrix</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">image</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">stdout</span></code> | <code><span class="nw">str</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `flirt` accepts (`crates/larmorx-fsl/src/cli/flirt.rs`) and the arguments of `lx.fsl.flirt` (`python/larmorx/fsl/flirt.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| FLIRT option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;in</span></code>, <code><span class="nw">&#45;ref</span></code> | <code><span class="nw">in&#95;image</span></code>, <code><span class="nw">ref&#95;image</span></code> |  | paths or <code><span class="nw">lx&#46;Image</span></code><span class="opt-help">FSL: “(no default)”</span><span class="opt-help">FSL: “(no default)”</span> |
| <code><span class="nw">&#45;out</span></code>, <code><span class="nw">&#45;omat</span></code> | <code><span class="nw">out&#61;True</span></code> (the image), the matrix always | <code><span class="nw">True</span></code> | returned in <code><span class="nw">FlirtResult</span></code>; <code><span class="nw">&#45;o</span></code> is <code><span class="nw">&#45;out</span></code><span class="opt-help">FSL: “(default is none)”</span><span class="opt-help">FSL: “(output in 4x4 ascii format)”</span> |
| <code><span class="nw">&#45;init</span></code> | <code><span class="nw">init</span></code> | <code><span class="nw">None</span></code> | a 4 x 4 array or a <code><span class="nw">&#46;mat</span></code> file<span class="opt-help">FSL: “(input 4x4 affine matrix)”</span> |
| <code><span class="nw">&#45;applyxfm</span></code>, <code><span class="nw">&#45;applyisoxfm</span> <span class="nw">s</span></code> | <code><span class="nw">apply&#95;xfm&#61;True</span></code>, <code><span class="nw">apply&#95;isoxfm&#61;s</span></code> | <code><span class="nw">apply&#95;xfm&#61;False</span></code>, <code><span class="nw">apply&#95;isoxfm&#61;None</span></code> | need <code><span class="nw">init</span></code> (or <code><span class="nw">use&#95;sqform</span></code>)<span class="opt-help">FSL: “(applies transform (no optimisation) - requires -init)”</span><span class="opt-help">FSL: “(as applyxfm but forces isotropic resampling)”</span> |
| <code><span class="nw">&#45;usesqform</span></code> | <code><span class="nw">use&#95;sqform</span></code> | <code><span class="nw">False</span></code> | <span class="opt-help">FSL: “(initialise using appropriate sform or qform)”</span> |
| <code><span class="nw">&#45;dof</span> <span class="nw">6&#47;7&#47;9&#47;12</span></code> | <code><span class="nw">dof</span></code> | <code><span class="nw">12</span></code> | <span class="opt-help">FSL: “(default is 12)”</span> |
| <code><span class="nw">&#45;cost</span></code>, <code><span class="nw">&#45;searchcost</span></code> | <code><span class="nw">cost</span></code>, <code><span class="nw">search&#95;cost</span></code> | <code><span class="nw">cost&#61;&#34;corratio&#34;</span></code>, <code><span class="nw">search&#95;cost&#61;&#34;corratio&#34;</span></code> | <code><span class="nw">corratio</span></code> (default), <code><span class="nw">mutualinfo</span></code>, <code><span class="nw">normmi</span></code>, <code><span class="nw">normcorr</span></code>, <code><span class="nw">leastsq</span></code>, <code><span class="nw">labeldiff</span></code>, <code><span class="nw">bbr</span></code>, <code><span class="nw">woods</span></code><span class="opt-help">FSL: “(default is corratio)”</span><span class="opt-help">FSL: “(default is corratio)”</span> |
| <code><span class="nw">&#45;bins</span></code> | <code><span class="nw">bins</span></code> | <code><span class="nw">256</span></code> | 256<span class="opt-help">FSL: “(default is 256)”</span> |
| <code><span class="nw">&#45;interp</span></code> | <code><span class="nw">interp</span></code> | <code><span class="nw">&#34;trilinear&#34;</span></code> | <code><span class="nw">trilinear</span></code>, <code><span class="nw">nearestneighbour</span></code>, <code><span class="nw">sinc</span></code>, <code><span class="nw">spline</span></code><span class="opt-help">FSL: “(final interpolation: def - trilinear)”</span> |
| <code><span class="nw">&#45;sincwidth</span></code>, <code><span class="nw">&#45;sincwindow</span></code> | <code><span class="nw">sinc&#95;width</span></code>, <code><span class="nw">sinc&#95;window</span></code> | <code><span class="nw">sinc&#95;width&#61;7</span></code>, <code><span class="nw">sinc&#95;window&#61;&#34;hanning&#34;</span></code> | 7, <code><span class="nw">hanning</span></code><span class="opt-help">FSL: “(default is 7)”</span> |
| <code><span class="nw">&#45;searchrx</span> <span class="nw">a</span> <span class="nw">b</span></code>, <code><span class="nw">&#45;searchry</span> <span class="nw">a</span> <span class="nw">b</span></code>, <code><span class="nw">&#45;searchrz</span> <span class="nw">a</span> <span class="nw">b</span></code>, <code><span class="nw">&#45;nosearch</span></code> | <code><span class="nw">search&#95;rx</span></code>, <code><span class="nw">search&#95;ry</span></code>, <code><span class="nw">search&#95;rz</span></code>, <code><span class="nw">no&#95;search</span></code> | <code><span class="nw">search&#95;rx&#61;&#40;&#45;90&#46;0&#44;</span> <span class="nw">90&#46;0&#41;</span></code>, <code><span class="nw">search&#95;ry&#61;&#40;&#45;90&#46;0&#44;</span> <span class="nw">90&#46;0&#41;</span></code>, <code><span class="nw">search&#95;rz&#61;&#40;&#45;90&#46;0&#44;</span> <span class="nw">90&#46;0&#41;</span></code>, <code><span class="nw">no&#95;search&#61;False</span></code> | degrees<span class="opt-help">FSL: “(angles in degrees: default is -90 90)”</span><span class="opt-help">FSL: “(angles in degrees: default is -90 90)”</span><span class="opt-help">FSL: “(angles in degrees: default is -90 90)”</span><span class="opt-help">FSL: “(sets all angular search ranges to 0 0)”</span> |
| <code><span class="nw">&#45;coarsesearch</span></code>, <code><span class="nw">&#45;finesearch</span></code> | <code><span class="nw">coarse&#95;search</span></code>, <code><span class="nw">fine&#95;search</span></code> | <code><span class="nw">coarse&#95;search&#61;60&#46;0</span></code>, <code><span class="nw">fine&#95;search&#61;18&#46;0</span></code> | 60, 18 degrees<span class="opt-help">FSL: “(angle in degrees: default is 60)”</span><span class="opt-help">FSL: “(angle in degrees: default is 18)”</span> |
| <code><span class="nw">&#45;schedule</span></code> | <code><span class="nw">schedule</span></code> | <code><span class="nw">None</span></code> | a schedule file<span class="opt-help">FSL: “(replaces default schedule)”</span> |
| <code><span class="nw">&#45;datatype</span></code> | <code><span class="nw">datatype</span></code> | <code><span class="nw">None</span></code> | <code><span class="nw">char</span></code>, <code><span class="nw">short</span></code>, <code><span class="nw">int</span></code>, <code><span class="nw">float</span></code>, <code><span class="nw">double</span></code><span class="opt-help">FSL: “(force output data type)”</span> |
| <code><span class="nw">&#45;refweight</span></code>, <code><span class="nw">&#45;inweight</span></code> | <code><span class="nw">ref&#95;weight</span></code>, <code><span class="nw">in&#95;weight</span></code> | <code><span class="nw">ref&#95;weight&#61;None</span></code>, <code><span class="nw">in&#95;weight&#61;None</span></code> | <span class="opt-help">FSL: “(use weights for reference volume)”</span><span class="opt-help">FSL: “(use weights for input volume)”</span> |
| <code><span class="nw">&#45;wmseg</span></code>, <code><span class="nw">&#45;wmcoords</span></code>, <code><span class="nw">&#45;wmnorms</span></code> | <code><span class="nw">wm&#95;seg</span></code>, <code><span class="nw">wm&#95;coords</span></code>, <code><span class="nw">wm&#95;norms</span></code> | <code><span class="nw">wm&#95;seg&#61;None</span></code>, <code><span class="nw">wm&#95;coords&#61;None</span></code>, <code><span class="nw">wm&#95;norms&#61;None</span></code> | BBR's boundary<span class="opt-help">FSL: “(white matter segmentation volume needed by BBR cost function)”</span><span class="opt-help">FSL: “(white matter boundary coordinates for BBR cost function)”</span><span class="opt-help">FSL: “(white matter boundary normals for BBR cost function)”</span> |
| <code><span class="nw">&#45;fieldmap</span></code>, <code><span class="nw">&#45;fieldmapmask</span></code>, <code><span class="nw">&#45;pedir</span></code>, <code><span class="nw">&#45;echospacing</span></code> | <code><span class="nw">fieldmap</span></code>, <code><span class="nw">fieldmap&#95;mask</span></code>, <code><span class="nw">pe&#95;dir</span></code>, <code><span class="nw">echo&#95;spacing</span></code> | <code><span class="nw">fieldmap&#61;None</span></code>, <code><span class="nw">fieldmap&#95;mask&#61;None</span></code>, <code><span class="nw">pe&#95;dir&#61;None</span></code>, <code><span class="nw">echo&#95;spacing&#61;0&#46;0005</span></code> | BBR with a field map<span class="opt-help">FSL: “(fieldmap image in rads/s - must be already registered to the reference image)”</span><span class="opt-help">FSL: “(mask for fieldmap image)”</span><span class="opt-help">FSL: “(phase encode direction of EPI - 1/2/3=x/y/z &amp; -1/-2/-3=-x/-y/-z)”</span><span class="opt-help">FSL: “(value of EPI echo spacing - units of seconds)”</span> |
| <code><span class="nw">&#45;bbrtype</span></code>, <code><span class="nw">&#45;bbrslope</span></code> | <code><span class="nw">bbr&#95;type</span></code>, <code><span class="nw">bbr&#95;slope</span></code> | <code><span class="nw">bbr&#95;type&#61;&#34;signed&#34;</span></code>, <code><span class="nw">bbr&#95;slope&#61;&#45;0&#46;5</span></code> | <code><span class="nw">signed</span></code>, <code><span class="nw">global&#95;abs</span></code>, <code><span class="nw">local&#95;abs</span></code>; −0.5<span class="opt-help">FSL: “(type of bbr cost function: signed [default], global_abs, local_abs)”</span><span class="opt-help">FSL: “(value of bbr slope)”</span> |
| <code><span class="nw">&#45;paddingsize</span></code>, <code><span class="nw">&#45;setbackground</span></code> | <code><span class="nw">padding&#95;size</span></code>, <code><span class="nw">background</span></code> | <code><span class="nw">padding&#95;size&#61;0&#46;0</span></code>, <code><span class="nw">background&#61;None</span></code> | <span class="opt-help">FSL: “(for applyxfm: interpolates outside image by size)”</span><span class="opt-help">FSL: “(use specified background value for points outside FOV)”</span> |
| <code><span class="nw">&#45;noresample</span></code>, <code><span class="nw">&#45;noclamp</span></code>, <code><span class="nw">&#45;noresampblur</span></code>, <code><span class="nw">&#45;forcescaling</span></code> | <code><span class="nw">no&#95;resample</span></code>, <code><span class="nw">no&#95;clamp</span></code>, <code><span class="nw">no&#95;resample&#95;blur</span></code>, <code><span class="nw">force&#95;scaling</span></code> | <code><span class="nw">no&#95;resample&#61;False</span></code>, <code><span class="nw">no&#95;clamp&#61;False</span></code>, <code><span class="nw">no&#95;resample&#95;blur&#61;False</span></code>, <code><span class="nw">force&#95;scaling&#61;False</span></code> | <span class="opt-help">FSL: “(do not change input sampling)”</span><span class="opt-help">FSL: “(do not use intensity clamping)”</span><span class="opt-help">FSL: “(do not use blurring on downsampling)”</span><span class="opt-help">FSL: “(force rescaling even for low-res images)”</span> |
| <code><span class="nw">&#45;minsampling</span></code>, <code><span class="nw">&#45;basescale</span></code> | <code><span class="nw">min&#95;sampling</span></code>, <code><span class="nw">base&#95;scale</span></code> | <code><span class="nw">min&#95;sampling&#61;None</span></code>, <code><span class="nw">base&#95;scale&#61;None</span></code> | <span class="opt-help">FSL: “(set minimum voxel dimension for sampling (in mm))”</span> |
| <code><span class="nw">&#45;2D</span></code> | <code><span class="nw">two&#95;d</span></code> | <code><span class="nw">False</span></code> | <span class="opt-help">FSL: “(use 2D rigid body mode - ignores dof)”</span> |
| <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;verbose</span></code>, <code><span class="nw">&#45;printinit</span></code>, <code><span class="nw">&#45;displayinit</span></code>, <code><span class="nw">&#45;debugsave</span></code>, <code><span class="nw">&#45;debug</span></code>, <code><span class="nw">&#45;i</span></code>, <code><span class="nw">&#45;help</span></code>, <code><span class="nw">&#45;version</span></code>, <code><span class="nw">&#45;anglerep</span></code>, <code><span class="nw">&#45;applynonisoxfm</span></code>, <code><span class="nw">&#45;nosave</span></code> | command line only |  | <code><span class="nw">&#45;anglerep</span> <span class="nw">quaternion</span></code> since part 2<span class="opt-help">FSL: “(same as -verbose 1)”</span><span class="opt-help">FSL: “(0 is least and default)”</span><span class="opt-help">FSL: “(display initial matrix)”</span><span class="opt-help">FSL: “(pauses at each stage: default is off)”</span><span class="opt-help">FSL: “(prints version number)”</span><span class="opt-help">FSL: “(default is euler)”</span> |
| <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | the results do not depend on it |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | <code><span class="nw">fix</span></code> (default) or <code><span class="nw">reproduce</span></code> |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl flirt ...`) and are arguments of `lx.fsl.flirt`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all); the results do not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects corrected, or FSL's behaviour (<code><span class="nw">docs&#47;api&#47;fsl&#45;flirt&#46;md</span></code>, "Upstream defects"). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `epi.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `T1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# A default 12-dof registration.
r = lx.fsl.flirt("epi.nii.gz", "T1w.nii.gz")
r.matrix.shape  # -> (4, 4)

# The same call, the clean room chosen, without the resampled image.
c = lx.fsl.flirt("epi.nii.gz", "T1w.nii.gz", out=False, implementation="clean-room")
c.image is None  # -> True
```

```bash
larmorx fsl flirt -in epi.nii.gz -ref T1w.nii.gz -omat epi2t1.mat -out epi2t1.nii.gz
```

## Ports {#ports}

`flirt` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-flirt-replica](repo:docs/validation/fsl-flirt-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-flirt](repo:docs/validation/fsl-flirt.md) |

The replica's record, against FSL 6.0.7.23 itself on the standard tier, holds fMRIPrep's
boundary-based calls on three oracle runs (ds005040, ds003592, ds000228), bit-identical, their
matrices also identical as text to fMRIPrep's own (its container's FSL); every cost function,
search option, schedule FSL ships, `-applyxfm` 3D and 4D with every interpolation and data type,
the BBR variants and the command line's errors. The clean room is within the thresholds in 238 of the 240
compared cases of its record, which holds FLIRT's fourteen programs; the 2 it misses are two
weighted registrations whose paths part at their costs' last bits. fMRIPrep's three boundary-based
calls are within 0.1 mm of FSL's matrices at the 95th percentile over the brain (0.053, 0.011 and
0.030 mm), their images' correlation with FSL's 0.9993 to 0.99996.

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

How each of `flirt`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-flirt/).

## More in the repository {#more}

The API page [docs/api/fsl-flirt.md](repo:docs/api/fsl-flirt.md) holds what `flirt` shares with the page's other programs:

- [FLIRT's other programs and scripts (part 3)](repo:docs/api/fsl-flirt.md#flirts-other-programs-and-scripts-part-3)
- [The clean-room original (part 1, 2026-11-02)](repo:docs/api/fsl-flirt.md#the-clean-room-original-part-1-2026-11-02)
- [Upstream defects (D13)](repo:docs/api/fsl-flirt.md#upstream-defects-d13)
- [Not yet](repo:docs/api/fsl-flirt.md#not-yet)
- [History](repo:docs/api/fsl-flirt.md#history)
