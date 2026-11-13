---
title: "`mcflirt`"
kicker: "Programs · FSL"
lede: "`mcflirt` corrects head motion in a 4D series."
description: "LARMORX reference for FSL 6.0.7.23 `mcflirt`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl mcflirt"
  python: "lx.mri.hmc"
  api: "docs/api/mri-hmc.md"
  evidence: "/evidence/mri-hmc/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "validated"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "24c23485c8957683"
    crates/larmorx-mri/src/cli/hmc.rs: "486b20a2279d91a5"
    docs/api/mri-hmc.md: "560a8f6e78e479d9"
    python/larmorx/mri/hmc.py: "29062ad607ecde1c"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

It registers every volume to the reference with a rigid-body transform (or up to 12 degrees
of freedom with `dof`) by mcflirt's schedule: one sweep of line searches on the reference
sampled every 8 mm, then every 4 mm, then 4 mm with an eight times tighter tolerance; each
volume's first search starts from its predecessor's result. The cost is mcflirt's normalised
correlation. It then resamples the series with the transforms. mcflirt's defects are corrected
by default; `upstream_defects="reproduce"` gives mcflirt's matrices
([Defects of the original](repo:docs/api/mri-hmc.md#defects-of-the-original-corrected-by-default)).

## Command line {#command-line}

```text synopsis
larmorx fsl mcflirt -in <infile> [options]
```

Everything after `larmorx fsl mcflirt` is the original's command line: the arguments of FSL 6.0.7.23's `mcflirt`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl mcflirt ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>mcflirt</code>'s usage text, as the clean room prints it</summary>

```text
Usage: larmorx mri hmc -in <infile> [options]
  Head-motion correction (larmorx, clean-room; accepts mcflirt-style options)

  Available options are:
        -out, -o <outfile>               (default is infile_mcf)
        -cost {mutualinfo,woods,corratio,normcorr,normmi,leastsquares}        (default is normcorr)
        -bins <number of histogram bins>   (default is 256)
        -dof  <number of transform dofs>   (default is 6)
        -refvol <number of reference volume> (default is no_vols/2)- registers to (n+1)th volume in series
        -reffile, -r <filename>            use a separate 3d image file as the target for registration (overrides refvol option)
        -scaling <num>                             (accepted and ignored)
        -smooth <num>                      (1.0 is default - controls smoothing in cost function)
        -rotation <num>                    specify scaling factor for rotation optimization tolerances
        -verbose <num>                     (0 is least and default)
        -stages <number of search levels>  (default is 3 - specify 4 for final sinc interpolation)
        -fov <num>                         (default is 20mm - specify size of field of view when padding 2d volume)
        -2d                                Force padding of volume
        -sinc_final                        (applies final transformations using sinc interpolation)
        -spline_final                      (applies final transformations using spline interpolation)
        -nn_final                          (applies final transformations using Nearest Neighbour interpolation)
        -init <filename>                   (initial transform matrix to apply to all vols)
        -meanvol                           register timeseries to mean volume (overrides refvol and reffile options)
        -stats                             produce variance and std. dev. images
        -mats                              save transformation matricies in subdirectory outfilename.mat
        -plots                             save transformation parameters in file outputfilename.par
        -report                            report progress to screen
        -help

  Output images use the extension of FSLOUTPUTTYPE (default NIFTI_GZ). Threads: OMP_NUM_THREADS
  (default: all logical CPUs); the results do not depend on it.
```

</details>

## Python {#python}

```python
lx.mri.hmc(
    bold: Any,
    *,
    reference: Any = None,
    ref_index: int | None = None,
    mean: bool = False,
    stages: int = 3,
    final: Final = "trilinear",
    dof: int = 6,
    cost: Cost = "normcorr",
    smooth: float = 1.0,
    rotation: float = 1.0,
    bins: int = 256,
    fudge: bool = False,
    in_plane: Literal["auto", "always", "never"] = "auto",
    fov: int = 20,
    init: np.ndarray | None = None,
    resample: bool = True,
    n_threads: int = 1,
    upstream_defects: UpstreamDefectsName = "fix",
    normcorr_count: NormCorrCount = "mcflirt",
    implementation: ImplementationName = "auto",
) -> HmcResult
```

Where `Final` is one of `"trilinear"`, `"sinc"`, `"spline"`, `"nearest"`; `Cost` is one of `"normcorr"`, `"leastsquares"`, `"corratio"`, `"woods"`, `"mutualinfo"`, `"normmi"`; `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`; `NormCorrCount` is one of `"mcflirt"`, `"weights"`; `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`).

Correct head motion in a 4D series (`mcflirt`'s algorithm).

`bold` is a path (read with mcflirt's rules, below) or an in-memory image (`lx.Image`, nibabel
image, `(array, affine)`); `reference` likewise. The result, an `HmcResult`, also writes
mcflirt's files: `save_mats(directory)` and `save_par(path)`, and `save_itk(path)` writes `itk`
as fMRIPrep's `mat2itk.txt`; `affine_series` wraps `affines` as `lx.transforms.AffineSeries`. Its
`implementation` is `lx.Implementation("clean-room", "larmorx", ...)` or the replica's
(`"replica"`, `"larmorx-nc"`, its version, `"LicenseRef-FSL"`, its program).
`lx.mri.read_mats(directory)` reads an mcflirt-style `.mat` directory into an `(N, 4, 4)` array.

**Reading.** As mcflirt: values become float32 (`scl_slope`/`scl_inter` applied when they ask
for it), voxel sizes come from `pixdim`, and images whose sform (or qform) has a positive
determinant have their x axis reversed in memory, so the matrices refer to "radiological"
order. Obliquity does not matter: the estimation works in voxel coordinates. The world
transforms (`affines`, `itk`) undo all of this.

**Threads.** `n_threads` (0 = all logical CPUs). The first stage is a chain within each sweep,
so its volumes run one after another with each cost evaluation's slices in parallel; the later
stages run the volumes in parallel. The result does not depend on the thread count.

```python
import larmorx as lx

# fMRIPrep's head-motion step: the HMC reference, the matrices only.
hmc = lx.mri.hmc("sub-01_task-rest_bold.nii.gz", reference="hmc_boldref.nii.gz",
                 resample=False, n_threads=8)
hmc.matrices          # (N, 4, 4) FSL matrices, as mcflirt's MAT_* files
hmc.affines           # (N, 4, 4) RAS transforms, reference -> volume (nitransforms)
hmc.save_itk("mat2itk.txt")       # fMRIPrep's ITKLinearTransformArray (LPS)
hmc.fd                # Power's framewise displacement (radius 50 mm)

# Everything mcflirt writes
res = lx.mri.hmc("bold.nii.gz")   # reference: volume N // 2
res.image.save("bold_mcf.nii.gz")
res.save_mats("bold_mcf.mat"); res.save_par("bold_mcf.par")

# One-shot resampling with the motion (fMRIPrep's way)
lx.transforms.resample_series(..., transforms=[res.affine_series, ...])
```

Its result, `HmcResult`, holds the result of `hmc`.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">matrices</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | <code><span class="nw">&#40;N&#44;</span> <span class="nw">4&#44;</span> <span class="nw">4&#41;</span></code>: one matrix per volume in <code><span class="nw">mcflirt</span></code>'s <code><span class="nw">&#46;mat</span></code> convention, mapping the volume's FSL-mm coordinates (voxel index times voxel size, x reversed for images whose affine has a positive determinant) to the reference's. |
| <code><span class="nw">affines</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | <code><span class="nw">&#40;N&#44;</span> <span class="nw">4&#44;</span> <span class="nw">4&#41;</span></code>: the same motion in RAS world coordinates, mapping reference points to the volume's points (nitransforms' <code><span class="nw">LinearTransformsMapping</span></code> convention, as fMRIPrep stores head motion). <code><span class="nw">affine&#95;series</span></code> wraps them for <code><span class="nw">resample&#95;series</span></code>. |
| <code><span class="nw">itk</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | <code><span class="nw">&#40;N&#44;</span> <span class="nw">4&#44;</span> <span class="nw">4&#41;</span></code>: <code><span class="nw">affines</span></code> in LPS (ITK and ANTs). |
| <code><span class="nw">params</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | <code><span class="nw">&#40;N&#44;</span> <span class="nw">6&#41;</span></code>: <code><span class="nw">rx</span> <span class="nw">ry</span> <span class="nw">rz</span> <span class="nw">tx</span> <span class="nw">ty</span> <span class="nw">tz</span></code> (radians, mm) about the reference's intensity-weighted centre, as <code><span class="nw">mcflirt</span> <span class="nw">&#45;plots</span></code> writes them. |
| <code><span class="nw">rms&#95;abs</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | <code><span class="nw">mcflirt</span></code>'s RMS displacements (radius 80 mm): from the reference (<code><span class="nw">N</span></code>) and from the previous volume (<code><span class="nw">N</span> <span class="nw">&#45;</span> <span class="nw">1</span></code>). |
| <code><span class="nw">rms&#95;rel</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | <code><span class="nw">mcflirt</span></code>'s RMS displacements (radius 80 mm): from the reference (<code><span class="nw">N</span></code>) and from the previous volume (<code><span class="nw">N</span> <span class="nw">&#45;</span> <span class="nw">1</span></code>). |
| <code><span class="nw">fd</span></code> | <code><span class="nw">np&#46;ndarray</span></code> | Power's framewise displacement from <code><span class="nw">params</span></code> (radius 50 mm; 0 for the first volume). |
| <code><span class="nw">reference&#95;index</span></code> | <code><span class="nw">int</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The reference volume of the series, or <code><span class="nw">None</span></code> (a separate reference or the mean). |
| <code><span class="nw">in&#95;plane</span></code> | <code><span class="nw">bool</span></code> | Whether the in-plane mode for thin slabs was used (only <code><span class="nw">rz</span></code>, <code><span class="nw">tx</span></code>, <code><span class="nw">ty</span></code> move). |
| <code><span class="nw">image</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The corrected series (float32) when <code><span class="nw">resample</span></code> was asked for, else <code><span class="nw">None</span></code>. |
| <code><span class="nw">mean</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> | The mean volume of <code><span class="nw">mean&#61;True</span></code> (the first pass's corrected mean), else <code><span class="nw">None</span></code>. |
| <code><span class="nw">implementation</span></code> | <code><span class="nw">&#95;replica&#46;Implementation</span></code> | The implementation that computed the result: larmorx's clean room, or the <code><span class="nw">larmorx&#45;nc</span></code> replica with its version (<code><span class="nw">Implementation</span></code>). |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `mcflirt` accepts (`crates/larmorx-mri/src/cli/hmc.rs`) and the arguments of `lx.mri.hmc` (`python/larmorx/mri/hmc.py`), whose defaults and descriptions are taken from it. Under each option, in grey, its line of the usage text the clean room prints, in the clean room's own words.

| <code><span class="nw">mcflirt</span></code> option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;in</span></code> (or a bare argument) | <code><span class="nw">bold</span></code> |  | the series |
| <code><span class="nw">&#45;out</span></code>, <code><span class="nw">&#45;o</span></code> | command line only |  | the outputs' names<span class="opt-help">The clean room's usage: “(default is infile_mcf)”</span> |
| <code><span class="nw">&#45;reffile</span></code>, <code><span class="nw">&#45;r</span></code> | <code><span class="nw">reference</span></code> | <code><span class="nw">None</span></code> | a separate reference volume: the first volume of a 4D file, with mcflirt's warning<span class="opt-help">The clean room's usage: “use a separate 3d image file as the target for registration (overrides refvol option)”</span> |
| <code><span class="nw">&#45;refvol</span></code> | <code><span class="nw">ref&#95;index</span></code> | <code><span class="nw">None</span></code> | <code><span class="nw">&#45;1</span></code>: the default <code><span class="nw">N&#47;2</span></code><span class="opt-help">The clean room's usage: “(default is no_vols/2)- registers to (n+1)th volume in series”</span> |
| <code><span class="nw">&#45;meanvol</span></code> | <code><span class="nw">mean&#61;True</span></code> | <code><span class="nw">False</span></code> | Register to the mean of the series after a first registration (<code><span class="nw">&#45;meanvol</span></code>) to <code><span class="nw">reference</span></code> if given, else to volume <code><span class="nw">ref&#95;index</span></code>.<span class="opt-help">The clean room's usage: “register timeseries to mean volume (overrides refvol and reffile options)”</span> |
| <code><span class="nw">&#45;stages</span></code> | <code><span class="nw">stages</span></code> | <code><span class="nw">3</span></code> | 1 to 4; 4 adds the sinc stage<span class="opt-help">The clean room's usage: “(default is 3 - specify 4 for final sinc interpolation)”</span> |
| <code><span class="nw">&#45;mats</span></code>, <code><span class="nw">&#45;plots</span></code>, <code><span class="nw">&#45;rmsrel</span></code>, <code><span class="nw">&#45;rmsabs</span></code> | the result: <code><span class="nw">HmcResult&#46;matrices</span></code>, <code><span class="nw">&#46;params</span></code>, <code><span class="nw">&#46;rms&#95;rel</span></code>, <code><span class="nw">&#46;rms&#95;abs</span></code> |  | the same files and text formats; through the replica, Python returns the files' values (matrices to 6 decimals, parameters and RMS to 6 significant digits)<span class="opt-help">The clean room's usage: “save transformation matricies in subdirectory outfilename.mat”</span><span class="opt-help">The clean room's usage: “save transformation parameters in file outputfilename.par”</span> |
| <code><span class="nw">&#45;stats</span></code> | command line only |  | <code><span class="nw">&#95;meanvol</span></code>, <code><span class="nw">&#95;variance</span></code>, <code><span class="nw">&#95;sigma</span></code>; every slice, named after <code><span class="nw">&#45;out</span></code> without its extension; mcflirt's end slices at 0 and names with <code><span class="nw">reproduce</span></code> (FSL-08), in both ports<span class="opt-help">The clean room's usage: “produce variance and std. dev. images”</span> |
| <code><span class="nw">&#45;sinc&#95;final</span></code>, <code><span class="nw">&#45;spline&#95;final</span></code>, <code><span class="nw">&#45;nn&#95;final</span></code> | <code><span class="nw">final&#61;&#34;sinc&#34;</span></code>, <code><span class="nw">&#34;spline&#34;</span></code>, <code><span class="nw">&#34;nearest&#34;</span></code> | <code><span class="nw">&#34;trilinear&#34;</span></code> | The final interpolation: one of <code><span class="nw">INTERPOLATIONS</span></code>.<span class="opt-help">The clean room's usage: “(applies final transformations using sinc interpolation)”</span><span class="opt-help">The clean room's usage: “(applies final transformations using spline interpolation)”</span><span class="opt-help">The clean room's usage: “(applies final transformations using Nearest Neighbour interpolation)”</span> |
| <code><span class="nw">&#45;dof</span></code> | <code><span class="nw">dof</span></code> | <code><span class="nw">6</span></code> | 6 to 12; the command line clamps with mcflirt's message<span class="opt-help">The clean room's usage: “(default is 6)”</span> |
| <code><span class="nw">&#45;cost</span></code> | <code><span class="nw">cost</span></code> | <code><span class="nw">&#34;normcorr&#34;</span></code> | the clean room: <code><span class="nw">normcorr</span></code> (its count's running total takes each point's weight as the point is visited, since 2026-11-07), <code><span class="nw">mutualinfo</span></code>, <code><span class="nw">normmi</span></code> (exactly as the spec's appendix B: mcflirt's evaluated matrices, evaluation by evaluation); <code><span class="nw">corratio</span></code>, <code><span class="nw">woods</span></code> (FLIRT's, since 2026-11-02), <code><span class="nw">leastsquares</span></code> (FLIRT's <code><span class="nw">leastsq</span></code>: three single-precision levels, since 2026-11-07); the replica: every cost, bit-identical<span class="opt-help">The clean room's usage: “(default is normcorr)”</span> |
| <code><span class="nw">&#45;bins</span></code> | <code><span class="nw">bins</span></code> | <code><span class="nw">256</span></code> | below 8 with a histogram cost: refused by default (FSL-21)<span class="opt-help">The clean room's usage: “(default is 256)”</span> |
| <code><span class="nw">&#45;smooth</span></code> | <code><span class="nw">smooth</span></code> | <code><span class="nw">1&#46;0</span></code> | 0: unweighted, Pearson's correlation<span class="opt-help">The clean room's usage: “(1.0 is default - controls smoothing in cost function)”</span> |
| <code><span class="nw">&#45;rotation</span></code> | <code><span class="nw">rotation</span></code> | <code><span class="nw">1&#46;0</span></code> | Divides the rotation tolerances (<code><span class="nw">&#45;rotation</span></code>).<span class="opt-help">The clean room's usage: “specify scaling factor for rotation optimization tolerances”</span> |
| <code><span class="nw">&#45;fudge</span></code> | <code><span class="nw">fudge&#61;True</span></code> | <code><span class="nw">False</span></code> | also makes the first stage fully parallel, in both ports |
| <code><span class="nw">&#45;2d</span></code>, <code><span class="nw">&#45;fov</span></code> | <code><span class="nw">in&#95;plane&#61;&#34;always&#34;</span></code>, <code><span class="nw">fov</span></code> | <code><span class="nw">in&#95;plane&#61;&#34;auto&#34;</span></code>, <code><span class="nw">fov&#61;20</span></code> | <code><span class="nw">in&#95;plane&#61;&#34;never&#34;</span></code> is LARMORX's own: under <code><span class="nw">&#34;auto&#34;</span></code> the clean room runs it<span class="opt-help">The clean room's usage: “Force padding of volume”</span><span class="opt-help">The clean room's usage: “(default is 20mm - specify size of field of view when padding 2d volume)”</span> |
| <code><span class="nw">&#45;init</span></code> | <code><span class="nw">init</span></code> | <code><span class="nw">None</span></code> | final resampling only, as mcflirt<span class="opt-help">The clean room's usage: “(initial transform matrix to apply to all vols)”</span> |
| <code><span class="nw">&#45;scaling</span></code>, <code><span class="nw">&#45;hist</span></code>, <code><span class="nw">&#45;v</span></code>, <code><span class="nw">&#45;verbose</span></code>, <code><span class="nw">&#45;report</span></code> | command line only |  | accepted; <code><span class="nw">&#45;scaling</span></code> and <code><span class="nw">&#45;hist</span></code> have no effect (in mcflirt either; a warning says so, FSL-05); the clean room's <code><span class="nw">&#45;report</span></code> prints progress messages (not mcflirt's exact text); the replica prints mcflirt's messages to the byte (<code><span class="nw">&#45;verbose</span> <span class="nw">20</span></code> prints every evaluated matrix)<span class="opt-help">The clean room's usage: “(accepted and ignored)”</span><span class="opt-help">The clean room's usage: “(0 is least and default)”</span><span class="opt-help">The clean room's usage: “report progress to screen”</span> |
| <code><span class="nw">&#45;gdt</span></code> | command line only |  | not supported by the clean room (exit 1); the replica refuses it by default, and with <code><span class="nw">reproduce</span></code> registers the gradient images as mcflirt does (FSL-04) |
| <code><span class="nw">&#45;help</span></code> | command line only |  | the usage, exit 0; without arguments: exit 1 (<code><span class="nw">&#45;help</span></code> alone exits 0; mcflirt's exit 1 with <code><span class="nw">reproduce</span></code>, FSL-07); the same in both ports |
| (none: mcflirt always resamples) | <code><span class="nw">resample&#61;False</span></code> | <code><span class="nw">True</span></code> | the matrices only, as fMRIPrep needs; it saves no time with the replica |
| (none) | <code><span class="nw">normcorr&#95;count&#61;&#34;mcflirt&#34;</span></code> | <code><span class="nw">&#34;mcflirt&#34;</span></code> | <code><span class="nw">&#34;weights&#34;</span></code>: the corrected correlation count (FSL-02), opt-in ([The correlation count](repo:docs/api/mri-hmc.md#the-correlation-count-fsl-02)); the clean room's only (the replica counts as mcflirt; under <code><span class="nw">&#34;auto&#34;</span></code> the clean room runs it) |
| <code><span class="nw">FSLOUTPUTTYPE</span></code> | command line only |  | the output format ([Output types and file names](/programs/fsl/mcflirt/#output-types-and-file-names)) |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | mcflirt's defects corrected (default) or reproduced; the replica's <code><span class="nw">reproduce</span></code> gives mcflirt's bytes |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl mcflirt ...`) and are arguments of `lx.mri.hmc`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Worker threads (0 = all logical CPUs). The result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the bit-exact replica when the <code><span class="nw">larmorx&#45;nc</span></code> package is installed (FSL Licence: non-commercial use only; <code><span class="nw">pip</span> <span class="nw">install</span> <span class="nw">larmorx&#45;nc</span></code>), else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works) force one. The replica runs <code><span class="nw">mcflirt</span></code>'s command line as a separate program on files in a temporary directory and returns <code><span class="nw">mcflirt</span></code>'s outputs as written (the matrices with 6 decimals, the parameters and RMS values with 6 significant digits, the corrected series as float32 from the file in the input's data type). Options with no command-line equivalent (<code><span class="nw">in&#95;plane&#61;&#34;never&#34;</span></code>, <code><span class="nw">normcorr&#95;count&#61;&#34;weights&#34;</span></code>) run the clean room under <code><span class="nw">&#34;auto&#34;</span></code> and are an error with <code><span class="nw">&#34;replica&#34;</span></code>. <code><span class="nw">resample&#61;False</span></code> saves no time with the replica (<code><span class="nw">mcflirt</span></code> always resamples); the series is then not returned. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) corrects mcflirt's defects: the last volume of the series starts its first stage from its predecessor's result like every other volume (FSL-01), the in-plane mode pads the first stage's grid once (FSL-03), and NaN or infinite voxels are left out of the centre of mass and the cost instead of making the matrix NaN (FSL-14). <code><span class="nw">&#34;reproduce&#34;</span></code> gives mcflirt's matrices. A <code><span class="nw">UpstreamDefectWarning</span></code> names each defect that changed the result (or would have been corrected). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `bold.nii.gz` (a synthetic series of 4 such heads), `ref.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# fMRIPrep's way: a separate reference, the matrices only.
hmc = lx.mri.hmc("bold.nii.gz", reference="ref.nii.gz", resample=False)
hmc.matrices.shape  # -> (4, 4, 4)
hmc.image is None  # -> True
```

```bash
larmorx fsl mcflirt -in bold.nii.gz -reffile ref.nii.gz -mats -plots -rmsrel -rmsabs
larmorx mri hmc -in bold.nii.gz -out bold_mcf -meanvol
```

## Output types and file names

`FSLOUTPUTTYPE` chooses the output format as for mcflirt 6.0.7.23 (`NIFTI`, `NIFTI2`, the pair
types `NIFTI_PAIR` and `NIFTI2_PAIR`, each also `_GZ`, `_ZST` and `_BZ2`: gzip, zstd and bzip2,
pure Rust); an unknown value prints FSL's message (`ERROR:: Unrecognised value (…) of environment
variable FSLOUTPUTTYPE` and the legal values) and exits 1 before any work. Inputs are read by
their content (gzip, zstd, bzip2 or uncompressed), whatever their names, and a name without an
image extension is completed as FSL completes it (`.nii.gz`, `.nii`, `.hdr`, `.hdr.gz`,
`.nii.zst`, `.hdr.zst`, `.nii.bz2`, `.hdr.bz2`; two matches or none are FSL's errors), also by
the Python API. The CLI's threads come from `OMP_NUM_THREADS` (default: all).

## Ports {#ports}

`mcflirt` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | validated | [fsl-mcflirt-replica](repo:docs/validation/fsl-mcflirt-replica.md), [fsl-mcflirt-replica-full](repo:docs/validation/fsl-mcflirt-replica-full.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [mri-hmc](repo:docs/validation/mri-hmc.md) |

**The replica** against mcflirt 6.0.7.23 itself ([its record](repo:docs/validation/fsl-mcflirt-replica.md),
the standard comparison, 2026-11-02): 205 of 205 compared cases bit-identical (every file, the
exit status and both streams, the replica in `reproduce` mode), 32 where both end with the same
error. Against FSL 6.0.7.17 before the version update ([its full record](repo:docs/validation/fsl-mcflirt-replica-full.md),
2026-10-25): 137 of the 137 recorded mcflirt runs, with the same messages and exit status where
both fail (12 of them), fMRIPrep's own mcflirt calls on the 12 fMRIPrep runs with BOLD series (22
of 22, the data panel's included; fMRIPrep's 4,517 matrices are identical too) and 35 edge cases:
173 of 173 compared cases bit-identical, 21 rejected alike.

**The clean room** against mcflirt 6.0.7.23 ([its record](repo:docs/validation/mri-hmc.md), the
standard comparison, 2026-11-11): every recorded run of mcflirt replayed and compared, 170
cases: 145 within the thresholds, 21 rejected by both alike, 4 expected divergences (each with
its reason in the record), 0 failures. On fMRIPrep's command the matrices differ from mcflirt's
by less than mcflirt differs from itself when its input is perturbed slightly (half an intensity
unit of noise, the volume order reversed): for nine real runs, the 95th percentile of the matrix
RMS deviation is **0.0151–0.0274 mm** (mcflirt's own band: 0.0164–0.1014 mm), on each run at or
below mcflirt's own. On every run with `-mats` (116) the worst 95th percentile is 0.1186 mm (the
thresholds: 0.1 mm, or mcflirt's band where wider, as on 26 runs). The differences are explained
under [Agreement with mcflirt](repo:docs/api/mri-hmc.md#agreement-with-mcflirt).

FSL is distributed under the FSL Licence (non-commercial use only), so `mcflirt` has two ports, a
replica and a clean room, in different packages ([licensing](repo:docs/licensing.md)):

- **The replica** is bit-exact: `larmorx-nc fsl mcflirt`, in the package `larmorx-nc`
  (`crates-nc/`), under the FSL Licence's terms, translated from mcflirt's source (fsl-mcflirt
  2111.0 and the libraries it uses). It gives mcflirt's output files byte for byte
  ([The replica](repo:docs/api/mri-hmc.md#the-replica)).
- **The clean room** is in the main package (Apache-2.0, crate `larmorx-mri`), written from the
  behaviour spec [`specs/mcflirt.md`](repo:specs/mcflirt.md), the published papers, `mcflirt
  -help` and black-box runs of FSL's program, without FSL's source
  ([PROVENANCE](repo:crates/larmorx-mri/PROVENANCE.md)). It is named by what it does, `mri
  hmc`, not after the program it is compatible with (decision D4).

Both follow mcflirt 6.0.7.23 and are compared with it; the clean room follows its `-sinc_final`
and `-nn_final` (FSL-59), its zstd and bzip2 output types, its reading of files by content and
its names (FSL-60), and computes `-cost mutualinfo` and `normmi` exactly as the spec's appendix B
describes them (2026-10-29).

`implementation="auto"` (the default) runs the replica when `larmorx-nc` is installed, else the
clean room; `"replica"` or `"clean-room"` (`"original"`, 0.1.0rc1's spelling, still works) force
one. The command line chooses alike (`--implementation` before the family, or
`LARMORX_IMPLEMENTATION`).

## Evidence {#evidence}

How each of `mcflirt`'s ports was measured against FSL, case by case: [its evidence](/evidence/mri-hmc/).

## More in the repository {#more}

The API page [docs/api/mri-hmc.md](repo:docs/api/mri-hmc.md) holds what `mcflirt` shares with the page's other programs:

- [The replica](repo:docs/api/mri-hmc.md#the-replica)
- [Differences by design](repo:docs/api/mri-hmc.md#differences-by-design)
- [Defects of the original, corrected by default](repo:docs/api/mri-hmc.md#defects-of-the-original-corrected-by-default)
- [Agreement with mcflirt](repo:docs/api/mri-hmc.md#agreement-with-mcflirt)
- [Performance](repo:docs/api/mri-hmc.md#performance)
- [History](repo:docs/api/mri-hmc.md#history)
