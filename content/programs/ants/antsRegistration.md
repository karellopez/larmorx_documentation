---
title: "`antsRegistration`"
kicker: "Programs · ANTs and ITK"
lede: "`antsRegistration` registers one image to another, stage by stage."
description: "LARMORX reference for ANTs 2.6.5 `antsRegistration`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: ants
  original: "ANTs 2.6.5"
  software: "ANTs"
  command: "larmorx ants antsRegistration"
  python: "lx.ants.registration"
  api: "docs/api/ants-registration.md"
  evidence: "/evidence/ants-registration/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-ants/src/cli/registration.rs: "e5e300a8bf806882"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "bf883da07a0caa93"
    docs/api/ants-registration.md: "1cf0f05a0c8da9f8"
    python/larmorx/ants/registration.py: "1aad07a617402e3c"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

It runs **linear stages** (`Translation`, `Rigid`, `Similarity`, `Affine`,
`CompositeAffine`), **SyN stages** (`SyN[gradientStep,updateFieldVariance,totalFieldVariance]`,
[SyN stages](repo:docs/api/ants-registration.md#syn-stages)), the **B-spline and displacement-field
stages** (`BSplineSyN`, `GaussianDisplacementField`, `BSplineDisplacementField`, `BSpline`,
[B-spline and displacement-field stages](repo:docs/api/ants-registration.md#b-spline-and-displacement-field-stages))
and the **velocity-field stages** (`Exponential`, `BSplineExponential`,
`TimeVaryingVelocityField`, `TimeVaryingBSplineVelocityField`;
[Velocity-field stages](repo:docs/api/ants-registration.md#velocity-field-stages)): every transform `antsRegistration` has,
in 2, 3 and 4 dimensions, double and float
(`--float 1`), with every image metric (`Mattes`/`MI`, `MI2`, `MeanSquares`, `CC`, `GC`, and
`Demons`, which needs a displacement field: it fails in a linear stage as in ANTs) and every
point-set metric (`ICP`, `PSE`, `JHCT`, `IGDM`; [Point-set metrics](repo:docs/api/ants-registration.md#point-set-metrics)),
several metrics per stage, sampling, masks, multi-resolution shrinking and smoothing, the
gradient filter, winsorizing and histogram matching, initial transforms (files, displacement
fields and composites holding them, `[fixed,moving,feature]`), `--initialize-transforms-per-stage`,
`--restore-state` and `--save-state`, `--print-similarity-measure-interval` and
`--write-interval-volumes`. larmorx refuses nothing ANTs accepts, except MINC transform files
and the crashes and hangs listed in the [register](repo:docs/api/upstream-defects.md).

## Command line {#command-line}

```text synopsis
larmorx ants antsRegistration ...
```

Everything after `larmorx ants antsRegistration` is the original's command line: the arguments of ANTs 2.6.5's `antsRegistration`, as ANTs takes them. LARMORX's own options stand between `larmorx` and the family `ants`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        ants antsRegistration ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

## Python {#python}

```python
lx.ants.registration(
    stages: RegistrationStage | Sequence[RegistrationStage],
    *,
    dimension: int | None = None,
    initial_moving_transforms: Sequence[Any] = (),
    initial_fixed_transforms: Sequence[Any] = (),
    restore_state: Any = None,
    winsorize: tuple[float, float] | None = None,
    use_histogram_matching: bool = False,
    collapse_output_transforms: bool = True,
    write_composite_transform: bool = False,
    initialize_transforms_per_stage: bool = False,
    warped: bool = False,
    inverse_warped: bool = False,
    interpolation: str = "Linear",
    precision: Precision = "float64",
    random_seed: int | None = None,
    print_similarity_measure_interval: int = 0,
    n_threads: int = 1,
    upstream_defects: UpstreamDefectsName = "fix",
) -> RegistrationResult
```

Where `Precision` is one of `"float64"`, `"float32"`; `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

Register the moving images to the fixed ones in linear, SyN, B-spline and displacement-field stages, as `antsRegistration` (ANTs v2.6.5) does.

Returns a `RegistrationResult`: `transforms` and `inverse_transforms` (as `ItkTransform` lists,
ready for `lx.ants.apply_transforms`), `files` (each output file's transforms, by the name
antsRegistration gives it), `warped` and `inverse_warped` (with those arguments), `iterations`
(every iteration's stage, level, number and metric value, from the `DIAGNOSTIC` lines) and
`log`.

```python
import larmorx as lx

stage1 = lx.ants.RegistrationStage(
    transform="Rigid", gradient_step=0.1,
    metrics=lx.ants.RegistrationMetric("Mattes", "fixed.nii.gz", "moving.nii.gz",
                                       bins=32, sampling="Regular", sampling_percentage=0.25),
    iterations=[1000, 500, 250], shrink_factors=[4, 2, 1], smoothing_sigmas=[2, 1, 0],
)
stage2 = lx.ants.RegistrationStage(
    transform="Affine", gradient_step=0.1,
    metrics=lx.ants.RegistrationMetric("Mattes", "fixed.nii.gz", "moving.nii.gz",
                                       sampling="Regular", sampling_percentage=0.25),
    iterations=[1000, 500, 250], shrink_factors=[4, 2, 1], smoothing_sigmas=[2, 1, 0],
)
res = lx.ants.registration(
    [stage1, stage2],
    initial_moving_transforms=[lx.ants.AlignCenters("fixed.nii.gz", "moving.nii.gz", "moments")],
    winsorize=(0.005, 0.995), use_histogram_matching=True,
    warped=True, random_seed=42,
)
res.files["0GenericAffine.mat"]                 # the collapsed affine, as ITK transforms
warped = lx.ants.apply_transforms("moving.nii.gz", "fixed.nii.gz", res.transforms)
[(it.stage, it.level, it.iteration, it.value) for it in res.iterations]
```

Its result, `RegistrationResult`, holds what `antsRegistration` wrote.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">transforms</span></code> | <code><span class="nw">list&#91;list&#91;ItkTransform&#93;&#93;</span></code> |  |
| <code><span class="nw">inverse&#95;transforms</span></code> | <code><span class="nw">list&#91;list&#91;ItkTransform&#93;&#93;</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">files</span></code> | <code><span class="nw">dict&#91;str&#44;</span> <span class="nw">list&#91;ItkTransform&#93;&#93;</span></code> |  |
| <code><span class="nw">warped</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">inverse&#95;warped</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">iterations</span></code> | <code><span class="nw">list&#91;RegistrationIteration&#93;</span></code> |  |
| <code><span class="nw">log</span></code> | <code><span class="nw">str</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `antsRegistration` accepts (`crates/larmorx-ants/src/cli/registration.rs`) and the arguments of `lx.ants.registration` (`python/larmorx/ants/registration.py`), whose defaults and descriptions are taken from it. Under each option, in grey, ANTs's own help for it.

| ANTs option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;d</span> <span class="nw">2&#47;3&#47;4</span></code>, <code><span class="nw">&#45;&#45;dimensionality</span></code> | <code><span class="nw">dimension</span></code> | <code><span class="nw">None</span></code> | default: the first fixed image's<span class="opt-help">ANTs: “This option forces the image to be treated as a specified-dimensional image.  If not specified, we try to infer the dimensionality from the input image.”</span> |
| <code><span class="nw">&#45;o</span> <span class="nw">&#91;prefix&#44;warped&#44;inverse&#93;</span></code>, <code><span class="nw">&#45;&#45;output</span></code> | <code><span class="nw">warped&#61;True</span></code>, <code><span class="nw">inverse&#95;warped&#61;True</span></code> | <code><span class="nw">warped&#61;False</span></code>, <code><span class="nw">inverse&#95;warped&#61;False</span></code> | the result's <code><span class="nw">files</span></code>, <code><span class="nw">transforms</span></code>, <code><span class="nw">warped</span></code> and <code><span class="nw">inverse&#95;warped</span></code>; Python writes the transforms to a temporary directory and reads them back; the warped images stay in memory<span class="opt-help">ANTs: “Specify the output transform prefix (output format is .nii.gz ). Optionally, one can choose to warp the moving image to the fixed space and, if the inverse transform exists, one can also output the warped fixed image.  Note that only the images specified in the first metric call are warped.  Use antsApplyTransforms to warp other images using the resultant transform(s). When a composite transform is not specified, linear transforms are specified with a '.mat' suffix and displacement fields with a 'Warp.nii.gz' suffix (and 'InverseWarp.nii.gz', when applicable.  In addition, for velocity-based transforms, the full velocity field is written to file ('VelocityField.nii.gz') as long as the collapse transforms flag is turned off ('-z 0').”</span> |
| <code><span class="nw">&#45;t</span></code>, <code><span class="nw">&#45;m</span></code>, <code><span class="nw">&#45;c</span></code>, <code><span class="nw">&#45;f</span></code>, <code><span class="nw">&#45;s</span></code>, <code><span class="nw">&#45;x</span></code>, <code><span class="nw">&#45;g</span></code> (one stage each) | <code><span class="nw">stages</span></code> |  | a list of <code><span class="nw">lx&#46;ants&#46;RegistrationStage</span></code>, one per <code><span class="nw">&#45;t</span></code>, each with its metrics (<code><span class="nw">lx&#46;ants&#46;RegistrationMetric</span></code>, <code><span class="nw">PointSetMetric</span></code>, <code><span class="nw">IntensityPointSetMetric</span></code>), convergence, shrink factors, smoothing sigmas, masks and restrictions<span class="opt-help">ANTs: “Several transform options are available.  The gradientStep or learningRate characterizes the gradient descent optimization and is scaled appropriately for each transform using the shift scales estimator.  Subsequent parameters are transform-specific and can be determined from the usage. For the B-spline transforms one can also specify the smoothing in terms of spline distance (i.e. knot spacing). ”</span><span class="opt-help">ANTs: “These image metrics are available--- CC:  ANTS neighborhood cross correlation, MI:  Mutual information, Demons: (Thirion), MeanSquares, and GC: Global Correlation. The "metricWeight" variable is used to modulate the per stage weighting of the metrics.  The metrics can also employ a sampling strategy defined by a sampling percentage. The sampling strategy defaults to 'None' (aka a dense sampling of one sample per voxel), otherwise it defines a point set over which to optimize the metric. The point set can be on a regular lattice or a random lattice of points slightly perturbed to minimize aliasing artifacts. samplingPercentage defines the fraction of points to select from the domain. useGradientFilter specifies whether a smoothingfilter is applied when estimating the metric gradient.In addition, three point set metrics are available:  Euclidean (ICP), Point-set expectation (PSE), and Jensen-Havrda-Charvet-Tsallis (JHCT).”</span><span class="opt-help">ANTs: “Convergence is determined from the number of iterations per level and is determined by fitting a line to the normalized energy profile of the last N iterations (where N is specified by the window size) and determining the slope which is then compared with the convergence threshold.”</span><span class="opt-help">ANTs: “Specify the shrink factor for the virtual domain (typically the fixed image) at each level.”</span><span class="opt-help">ANTs: “Specify the sigma of gaussian smoothing at each level.  Units are given in terms of voxels ('vox') or physical spacing ('mm'). Example usage is '4x2x1mm' and '4x2x1vox' where no units implies voxel spacing.”</span><span class="opt-help">ANTs: “Image masks to limit voxels considered by the metric. Two options are allowed for mask specification:  1) Either the user specifies a single mask to be used for all stages or 2) the user specifies a mask for each stage.  With the latter one can select to which stages masks are applied by supplying valid file names.  If the file does not exist, a mask will not be used for that stage.  Note that we handle the fixed and moving masks separately to enforce this constraint.”</span><span class="opt-help">ANTs: “This option allows the user to restrict the optimization of the displacement field, translation, rigid or affine transform on a per-component basis.  For example, if one wants to limit the deformation or rotation of 3-D volume to the first two dimensions, this is possible by specifying a weight vector of '1x1x0' for a deformation field or  '1x1x0x1x1x0' for a rigid transformation. Low-dimensional restriction only works if there are no preceding transformations.All stages up to and including the desired stage must have this option specified,even if they should not be restricted (in which case specify 1x1x1...)”</span> |
| <code><span class="nw">&#45;t</span> <span class="nw">Rigid&#91;step&#93;</span></code>, <code><span class="nw">&#45;&#45;transform</span></code> | <code><span class="nw">RegistrationStage&#40;transform&#61;&#34;Rigid&#34;&#44;</span> <span class="nw">gradient&#95;step&#61;step&#41;</span></code> |  | <code><span class="nw">Translation</span></code>, <code><span class="nw">Rigid</span></code>, <code><span class="nw">Similarity</span></code>, <code><span class="nw">Affine</span></code>, <code><span class="nw">CompositeAffine</span></code><span class="opt-help">ANTs: “Several transform options are available.  The gradientStep or learningRate characterizes the gradient descent optimization and is scaled appropriately for each transform using the shift scales estimator.  Subsequent parameters are transform-specific and can be determined from the usage. For the B-spline transforms one can also specify the smoothing in terms of spline distance (i.e. knot spacing). ”</span> |
| <code><span class="nw">&#45;t</span> <span class="nw">SyN&#91;step&#44;update&#44;total&#93;</span></code> | <code><span class="nw">RegistrationStage&#40;transform&#61;&#34;SyN&#34;&#44;</span> <span class="nw">gradient&#95;step&#61;step&#44;</span> <span class="nw">update&#95;field&#95;variance&#61;update&#44;</span> <span class="nw">total&#95;field&#95;variance&#61;total&#41;</span></code> |  | variances in voxels², default 3 and 0<span class="opt-help">ANTs: “Several transform options are available.  The gradientStep or learningRate characterizes the gradient descent optimization and is scaled appropriately for each transform using the shift scales estimator.  Subsequent parameters are transform-specific and can be determined from the usage. For the B-spline transforms one can also specify the smoothing in terms of spline distance (i.e. knot spacing). ”</span> |
| <code><span class="nw">&#45;t</span> <span class="nw">BSplineSyN&#91;step&#44;updateMesh&#44;totalMesh&#44;order&#93;</span></code> | <code><span class="nw">RegistrationStage&#40;transform&#61;&#34;BSplineSyN&#34;&#44;</span> <span class="nw">gradient&#95;step&#61;step&#44;</span> <span class="nw">mesh&#95;size&#61;updateMesh&#44;</span> <span class="nw">total&#95;mesh&#95;size&#61;totalMesh&#44;</span> <span class="nw">spline&#95;order&#61;order&#41;</span></code> |  | meshes per axis at the base level (<code><span class="nw">&#40;2&#44;</span> <span class="nw">2&#44;</span> <span class="nw">2&#41;</span></code>, <code><span class="nw">2x2x2</span></code>), or one knot spacing in mm (<code><span class="nw">26</span></code>); total mesh default 0 (no smoothing), order 3<span class="opt-help">ANTs: “Several transform options are available.  The gradientStep or learningRate characterizes the gradient descent optimization and is scaled appropriately for each transform using the shift scales estimator.  Subsequent parameters are transform-specific and can be determined from the usage. For the B-spline transforms one can also specify the smoothing in terms of spline distance (i.e. knot spacing). ”</span> |
| <code><span class="nw">&#45;t</span> <span class="nw">GaussianDisplacementField&#91;step&#44;update&#44;total&#93;</span></code> | <code><span class="nw">RegistrationStage&#40;transform&#61;&#34;GaussianDisplacementField&#34;&#44;</span> <span class="nw">gradient&#95;step&#61;step&#44;</span> <span class="nw">update&#95;field&#95;variance&#61;update&#44;</span> <span class="nw">total&#95;field&#95;variance&#61;total&#41;</span></code> |  | both variances required on the command line<span class="opt-help">ANTs: “Several transform options are available.  The gradientStep or learningRate characterizes the gradient descent optimization and is scaled appropriately for each transform using the shift scales estimator.  Subsequent parameters are transform-specific and can be determined from the usage. For the B-spline transforms one can also specify the smoothing in terms of spline distance (i.e. knot spacing). ”</span> |
| <code><span class="nw">&#45;t</span> <span class="nw">BSplineDisplacementField&#91;step&#44;updateMesh&#44;totalMesh&#44;order&#93;</span></code> | <code><span class="nw">RegistrationStage&#40;transform&#61;&#34;BSplineDisplacementField&#34;&#44;</span> <span class="nw">gradient&#95;step&#61;step&#44;</span> <span class="nw">mesh&#95;size&#61;&#44;</span> <span class="nw">total&#95;mesh&#95;size&#61;&#44;</span> <span class="nw">spline&#95;order&#61;&#41;</span></code> |  | the meshes at the base level, doubled at each level (ANTs doubles them already at the base level, ANTS-78: give twice the mesh, or <code><span class="nw">reproduce</span></code>, for its result)<span class="opt-help">ANTs: “Several transform options are available.  The gradientStep or learningRate characterizes the gradient descent optimization and is scaled appropriately for each transform using the shift scales estimator.  Subsequent parameters are transform-specific and can be determined from the usage. For the B-spline transforms one can also specify the smoothing in terms of spline distance (i.e. knot spacing). ”</span> |
| <code><span class="nw">&#45;t</span> <span class="nw">BSpline&#91;step&#44;mesh&#93;</span></code> | <code><span class="nw">RegistrationStage&#40;transform&#61;&#34;BSpline&#34;&#44;</span> <span class="nw">gradient&#95;step&#61;step&#44;</span> <span class="nw">mesh&#95;size&#61;mesh&#41;</span></code> |  | a cubic B-spline transform; the mesh (or knot spacing) at the base level, doubled at each level<span class="opt-help">ANTs: “Several transform options are available.  The gradientStep or learningRate characterizes the gradient descent optimization and is scaled appropriately for each transform using the shift scales estimator.  Subsequent parameters are transform-specific and can be determined from the usage. For the B-spline transforms one can also specify the smoothing in terms of spline distance (i.e. knot spacing). ”</span> |
| <code><span class="nw">&#45;t</span> <span class="nw">Exponential&#91;step&#44;update&#44;velocity&#44;steps&#93;</span></code> | <code><span class="nw">RegistrationStage&#40;transform&#61;&#34;Exponential&#34;&#44;</span> <span class="nw">gradient&#95;step&#61;step&#44;</span> <span class="nw">update&#95;field&#95;variance&#61;update&#44;</span> <span class="nw">velocity&#95;field&#95;variance&#61;velocity&#44;</span> <span class="nw">integration&#95;steps&#61;steps&#41;</span></code> |  | <code><span class="nw">Exp</span></code> is the short name; <code><span class="nw">steps</span></code> 0 or left out (<code><span class="nw">None</span></code>): automatic; the sigmas <code><span class="nw">&#45;s</span></code> in the units given (ANTs: mm, ANTS-80)<span class="opt-help">ANTs: “Several transform options are available.  The gradientStep or learningRate characterizes the gradient descent optimization and is scaled appropriately for each transform using the shift scales estimator.  Subsequent parameters are transform-specific and can be determined from the usage. For the B-spline transforms one can also specify the smoothing in terms of spline distance (i.e. knot spacing). ”</span> |
| <code><span class="nw">&#45;t</span> <span class="nw">BSplineExponential&#91;step&#44;updateMesh&#44;velocityMesh&#44;steps&#44;order&#93;</span></code> | <code><span class="nw">RegistrationStage&#40;transform&#61;&#34;BSplineExponential&#34;&#44;</span> <span class="nw">gradient&#95;step&#61;step&#44;</span> <span class="nw">mesh&#95;size&#61;updateMesh&#44;</span> <span class="nw">total&#95;mesh&#95;size&#61;velocityMesh&#44;</span> <span class="nw">integration&#95;steps&#61;steps&#44;</span> <span class="nw">spline&#95;order&#61;order&#41;</span></code> |  | meshes or knot spacings, at the base level (ANTS-78)<span class="opt-help">ANTs: “Several transform options are available.  The gradientStep or learningRate characterizes the gradient descent optimization and is scaled appropriately for each transform using the shift scales estimator.  Subsequent parameters are transform-specific and can be determined from the usage. For the B-spline transforms one can also specify the smoothing in terms of spline distance (i.e. knot spacing). ”</span> |
| <code><span class="nw">&#45;t</span> <span class="nw">TimeVaryingVelocityField&#91;step&#44;timeIndices&#44;update&#44;updateTime&#44;total&#44;totalTime&#93;</span></code> | <code><span class="nw">RegistrationStage&#40;transform&#61;&#34;TimeVaryingVelocityField&#34;&#44;</span> <span class="nw">gradient&#95;step&#61;step&#44;</span> <span class="nw">number&#95;of&#95;time&#95;indices&#61;&#44;</span> <span class="nw">update&#95;field&#95;variance&#61;&#44;</span> <span class="nw">update&#95;field&#95;time&#95;variance&#61;&#44;</span> <span class="nw">total&#95;field&#95;variance&#61;&#44;</span> <span class="nw">total&#95;field&#95;time&#95;variance&#61;&#41;</span></code> |  | <code><span class="nw">tvf</span></code> is the short name; all six parameters required<span class="opt-help">ANTs: “Several transform options are available.  The gradientStep or learningRate characterizes the gradient descent optimization and is scaled appropriately for each transform using the shift scales estimator.  Subsequent parameters are transform-specific and can be determined from the usage. For the B-spline transforms one can also specify the smoothing in terms of spline distance (i.e. knot spacing). ”</span> |
| <code><span class="nw">&#45;t</span> <span class="nw">TimeVaryingBSplineVelocityField&#91;step&#44;mesh&#44;samples&#44;order&#93;</span></code> | <code><span class="nw">RegistrationStage&#40;transform&#61;&#34;TimeVaryingBSplineVelocityField&#34;&#44;</span> <span class="nw">gradient&#95;step&#61;step&#44;</span> <span class="nw">mesh&#95;size&#61;mesh&#44;</span> <span class="nw">number&#95;of&#95;time&#95;point&#95;samples&#61;samples&#44;</span> <span class="nw">spline&#95;order&#61;order&#41;</span></code> |  | the mesh has one size per axis and one for time (<code><span class="nw">4x4x4x2</span></code>)<span class="opt-help">ANTs: “Several transform options are available.  The gradientStep or learningRate characterizes the gradient descent optimization and is scaled appropriately for each transform using the shift scales estimator.  Subsequent parameters are transform-specific and can be determined from the usage. For the B-spline transforms one can also specify the smoothing in terms of spline distance (i.e. knot spacing). ”</span> |
| <code><span class="nw">&#45;m</span> <span class="nw">ICP&#91;f&#44;m&#44;w&#44;p&#44;boundary&#93;</span></code> | <code><span class="nw">PointSetMetric&#40;&#34;ICP&#34;&#44;</span> <span class="nw">f&#44;</span> <span class="nw">m&#44;</span> <span class="nw">weight&#61;w&#44;</span> <span class="nw">sampling&#95;percentage&#61;p&#44;</span> <span class="nw">boundary&#95;points&#95;only&#61;boundary&#41;</span></code> |  | <code><span class="nw">f</span></code>, <code><span class="nw">m</span></code>: a label image, a <code><span class="nw">&#46;txt</span></code> or <code><span class="nw">&#46;vtk</span></code> point set, or <code><span class="nw">&#40;points&#44;</span> <span class="nw">labels&#41;</span></code> arrays<span class="opt-help">ANTs: “These image metrics are available--- CC:  ANTS neighborhood cross correlation, MI:  Mutual information, Demons: (Thirion), MeanSquares, and GC: Global Correlation. The "metricWeight" variable is used to modulate the per stage weighting of the metrics.  The metrics can also employ a sampling strategy defined by a sampling percentage. The sampling strategy defaults to 'None' (aka a dense sampling of one sample per voxel), otherwise it defines a point set over which to optimize the metric. The point set can be on a regular lattice or a random lattice of points slightly perturbed to minimize aliasing artifacts. samplingPercentage defines the fraction of points to select from the domain. useGradientFilter specifies whether a smoothingfilter is applied when estimating the metric gradient.In addition, three point set metrics are available:  Euclidean (ICP), Point-set expectation (PSE), and Jensen-Havrda-Charvet-Tsallis (JHCT).”</span> |
| <code><span class="nw">&#45;m</span> <span class="nw">PSE&#91;f&#44;m&#44;w&#44;p&#44;boundary&#44;sigma&#44;k&#93;</span></code> | <code><span class="nw">PointSetMetric&#40;&#34;PSE&#34;&#44;</span> <span class="nw">&#46;&#46;&#46;&#44;</span> <span class="nw">sigma&#61;sigma&#44;</span> <span class="nw">k&#95;neighborhood&#61;k&#41;</span></code> |  | <span class="opt-help">ANTs: “These image metrics are available--- CC:  ANTS neighborhood cross correlation, MI:  Mutual information, Demons: (Thirion), MeanSquares, and GC: Global Correlation. The "metricWeight" variable is used to modulate the per stage weighting of the metrics.  The metrics can also employ a sampling strategy defined by a sampling percentage. The sampling strategy defaults to 'None' (aka a dense sampling of one sample per voxel), otherwise it defines a point set over which to optimize the metric. The point set can be on a regular lattice or a random lattice of points slightly perturbed to minimize aliasing artifacts. samplingPercentage defines the fraction of points to select from the domain. useGradientFilter specifies whether a smoothingfilter is applied when estimating the metric gradient.In addition, three point set metrics are available:  Euclidean (ICP), Point-set expectation (PSE), and Jensen-Havrda-Charvet-Tsallis (JHCT).”</span> |
| <code><span class="nw">&#45;m</span> <span class="nw">JHCT&#91;f&#44;m&#44;w&#44;p&#44;boundary&#44;sigma&#44;k&#44;alpha&#44;aniso&#93;</span></code> | <code><span class="nw">PointSetMetric&#40;&#34;JHCT&#34;&#44;</span> <span class="nw">&#46;&#46;&#46;&#44;</span> <span class="nw">sigma&#61;&#44;</span> <span class="nw">k&#95;neighborhood&#61;&#44;</span> <span class="nw">alpha&#61;&#44;</span> <span class="nw">anisotropic&#95;covariances&#61;&#41;</span></code> |  | <span class="opt-help">ANTs: “These image metrics are available--- CC:  ANTS neighborhood cross correlation, MI:  Mutual information, Demons: (Thirion), MeanSquares, and GC: Global Correlation. The "metricWeight" variable is used to modulate the per stage weighting of the metrics.  The metrics can also employ a sampling strategy defined by a sampling percentage. The sampling strategy defaults to 'None' (aka a dense sampling of one sample per voxel), otherwise it defines a point set over which to optimize the metric. The point set can be on a regular lattice or a random lattice of points slightly perturbed to minimize aliasing artifacts. samplingPercentage defines the fraction of points to select from the domain. useGradientFilter specifies whether a smoothingfilter is applied when estimating the metric gradient.In addition, three point set metrics are available:  Euclidean (ICP), Point-set expectation (PSE), and Jensen-Havrda-Charvet-Tsallis (JHCT).”</span> |
| <code><span class="nw">&#45;m</span> <span class="nw">IGDM&#91;f&#44;m&#44;w&#44;fmask&#44;mmask&#44;radius&#44;isigma&#44;dsigma&#44;k&#44;gsigma&#93;</span></code> | <code><span class="nw">IntensityPointSetMetric&#40;f&#44;</span> <span class="nw">m&#44;</span> <span class="nw">fmask&#44;</span> <span class="nw">mmask&#44;</span> <span class="nw">weight&#61;&#44;</span> <span class="nw">neighborhood&#95;radius&#61;&#44;</span> <span class="nw">intensity&#95;sigma&#61;&#44;</span> <span class="nw">distance&#95;sigma&#61;&#44;</span> <span class="nw">k&#95;neighborhood&#61;&#44;</span> <span class="nw">gradient&#95;sigma&#61;&#41;</span></code> |  | sigmas of 0 are estimated (the distance sigma at least one voxel, ANTS-70); the <code><span class="nw">k</span></code> nearest points and Gaussian gradients of <code><span class="nw">gsigma</span></code> mm (ANTs uses neither, ANTS-67)<span class="opt-help">ANTs: “These image metrics are available--- CC:  ANTS neighborhood cross correlation, MI:  Mutual information, Demons: (Thirion), MeanSquares, and GC: Global Correlation. The "metricWeight" variable is used to modulate the per stage weighting of the metrics.  The metrics can also employ a sampling strategy defined by a sampling percentage. The sampling strategy defaults to 'None' (aka a dense sampling of one sample per voxel), otherwise it defines a point set over which to optimize the metric. The point set can be on a regular lattice or a random lattice of points slightly perturbed to minimize aliasing artifacts. samplingPercentage defines the fraction of points to select from the domain. useGradientFilter specifies whether a smoothingfilter is applied when estimating the metric gradient.In addition, three point set metrics are available:  Euclidean (ICP), Point-set expectation (PSE), and Jensen-Havrda-Charvet-Tsallis (JHCT).”</span> |
| <code><span class="nw">&#45;m</span> <span class="nw">Mattes&#91;f&#44;m&#44;w&#44;bins&#44;sampling&#44;p&#44;gf&#93;</span></code> | <code><span class="nw">RegistrationMetric&#40;&#34;Mattes&#34;&#44;</span> <span class="nw">f&#44;</span> <span class="nw">m&#44;</span> <span class="nw">weight&#61;w&#44;</span> <span class="nw">bins&#61;bins&#44;</span> <span class="nw">sampling&#61;&#46;&#46;&#46;&#44;</span> <span class="nw">sampling&#95;percentage&#61;p&#44;</span> <span class="nw">use&#95;gradient&#95;filter&#61;gf&#41;</span></code> |  | <code><span class="nw">MI</span></code> is ANTs' other name for Mattes; <code><span class="nw">MI2</span></code> the joint-histogram MI; <code><span class="nw">CC&#91;f&#44;m&#44;w&#44;radius&#44;&#46;&#46;&#46;&#93;</span></code>: <code><span class="nw">radius&#61;</span></code>; <code><span class="nw">MeanSquares</span></code>, <code><span class="nw">GC</span></code>, <code><span class="nw">Demons</span></code> have no parameter<span class="opt-help">ANTs: “These image metrics are available--- CC:  ANTS neighborhood cross correlation, MI:  Mutual information, Demons: (Thirion), MeanSquares, and GC: Global Correlation. The "metricWeight" variable is used to modulate the per stage weighting of the metrics.  The metrics can also employ a sampling strategy defined by a sampling percentage. The sampling strategy defaults to 'None' (aka a dense sampling of one sample per voxel), otherwise it defines a point set over which to optimize the metric. The point set can be on a regular lattice or a random lattice of points slightly perturbed to minimize aliasing artifacts. samplingPercentage defines the fraction of points to select from the domain. useGradientFilter specifies whether a smoothingfilter is applied when estimating the metric gradient.In addition, three point set metrics are available:  Euclidean (ICP), Point-set expectation (PSE), and Jensen-Havrda-Charvet-Tsallis (JHCT).”</span> |
| several <code><span class="nw">&#45;m</span></code> in a stage, <code><span class="nw">&#45;&#45;metric</span></code> | <code><span class="nw">RegistrationStage&#40;metrics&#61;&#91;&#46;&#46;&#46;&#93;&#41;</span></code> |  | the first metric's value; derivatives weighed by <code><span class="nw">weight</span></code> (normalised)<span class="opt-help">ANTs: “These image metrics are available--- CC:  ANTS neighborhood cross correlation, MI:  Mutual information, Demons: (Thirion), MeanSquares, and GC: Global Correlation. The "metricWeight" variable is used to modulate the per stage weighting of the metrics.  The metrics can also employ a sampling strategy defined by a sampling percentage. The sampling strategy defaults to 'None' (aka a dense sampling of one sample per voxel), otherwise it defines a point set over which to optimize the metric. The point set can be on a regular lattice or a random lattice of points slightly perturbed to minimize aliasing artifacts. samplingPercentage defines the fraction of points to select from the domain. useGradientFilter specifies whether a smoothingfilter is applied when estimating the metric gradient.In addition, three point set metrics are available:  Euclidean (ICP), Point-set expectation (PSE), and Jensen-Havrda-Charvet-Tsallis (JHCT).”</span> |
| <code><span class="nw">&#45;c</span> <span class="nw">&#91;10x5&#44;1e&#45;6&#44;10&#93;</span></code>, <code><span class="nw">&#45;&#45;convergence</span></code> | <code><span class="nw">RegistrationStage&#40;iterations&#61;&#91;10&#44;</span> <span class="nw">5&#93;&#44;</span> <span class="nw">convergence&#95;threshold&#61;1e&#45;6&#44;</span> <span class="nw">convergence&#95;window&#61;10&#41;</span></code> |  | a level stops when the window's convergence value is ≤ the threshold (negative when the metric rises: [findings](repo:docs/findings/ants-registration.md))<span class="opt-help">ANTs: “Convergence is determined from the number of iterations per level and is determined by fitting a line to the normalized energy profile of the last N iterations (where N is specified by the window size) and determining the slope which is then compared with the convergence threshold.”</span> |
| <code><span class="nw">&#45;f</span> <span class="nw">4x2x1</span></code>, <code><span class="nw">&#45;&#45;shrink&#45;factors</span></code> | <code><span class="nw">RegistrationStage&#40;shrink&#95;factors&#61;&#91;4&#44;</span> <span class="nw">2&#44;</span> <span class="nw">1&#93;&#41;</span></code> |  | per level; per axis as <code><span class="nw">CalculateShrinkFactorsPerDimension</span></code> chooses<span class="opt-help">ANTs: “Specify the shrink factor for the virtual domain (typically the fixed image) at each level.”</span> |
| <code><span class="nw">&#45;s</span> <span class="nw">2x1x0vox</span></code> / <code><span class="nw">mm</span></code>, <code><span class="nw">&#45;&#45;smoothing&#45;sigmas</span></code> | <code><span class="nw">RegistrationStage&#40;smoothing&#95;sigmas&#61;&#91;2&#44;</span> <span class="nw">1&#44;</span> <span class="nw">0&#93;&#44;</span> <span class="nw">sigmas&#95;in&#95;mm&#61;&#46;&#46;&#46;&#41;</span></code> |  | <span class="opt-help">ANTs: “Specify the sigma of gaussian smoothing at each level.  Units are given in terms of voxels ('vox') or physical spacing ('mm'). Example usage is '4x2x1mm' and '4x2x1vox' where no units implies voxel spacing.”</span> |
| <code><span class="nw">&#45;x</span> <span class="nw">mask</span></code> / <code><span class="nw">&#45;x</span> <span class="nw">&#91;fixed&#44;moving&#93;</span></code>, <code><span class="nw">&#45;&#45;masks</span></code> | <code><span class="nw">RegistrationStage&#46;masks&#61;mask</span></code> / <code><span class="nw">&#40;fixed&#44;</span> <span class="nw">moving&#41;</span></code> |  | <code><span class="nw">None</span></code> in the pair is ANTs' <code><span class="nw">NULL</span></code><span class="opt-help">ANTs: “Image masks to limit voxels considered by the metric. Two options are allowed for mask specification:  1) Either the user specifies a single mask to be used for all stages or 2) the user specifies a mask for each stage.  With the latter one can select to which stages masks are applied by supplying valid file names.  If the file does not exist, a mask will not be used for that stage.  Note that we handle the fixed and moving masks separately to enforce this constraint.”</span> |
| <code><span class="nw">&#45;g</span> <span class="nw">1x1x0x1x1x1</span></code>, <code><span class="nw">&#45;&#45;restrict&#45;deformation</span></code> | <code><span class="nw">RegistrationStage&#40;restrict&#95;deformation&#61;&#91;1&#44;</span> <span class="nw">1&#44;</span> <span class="nw">0&#44;</span> <span class="nw">1&#44;</span> <span class="nw">1&#44;</span> <span class="nw">1&#93;&#41;</span></code> |  | weights of the transform's parameters<span class="opt-help">ANTs: “This option allows the user to restrict the optimization of the displacement field, translation, rigid or affine transform on a per-component basis.  For example, if one wants to limit the deformation or rotation of 3-D volume to the first two dimensions, this is possible by specifying a weight vector of '1x1x0' for a deformation field or  '1x1x0x1x1x0' for a rigid transformation. Low-dimensional restriction only works if there are no preceding transformations.All stages up to and including the desired stage must have this option specified,even if they should not be restricted (in which case specify 1x1x1...)”</span> |
| <code><span class="nw">&#45;r</span> <span class="nw">file</span></code> / <code><span class="nw">&#45;r</span> <span class="nw">&#91;file&#44;1&#93;</span></code> / <code><span class="nw">&#45;r</span> <span class="nw">&#91;f&#44;m&#44;0&#47;1&#47;2&#93;</span></code>, <code><span class="nw">&#45;&#45;initial&#45;moving&#45;transform</span></code> | <code><span class="nw">initial&#95;moving&#95;transforms&#61;&#91;path</span> <span class="nw">or</span> <span class="nw">ItkTransforms&#44;</span> <span class="nw">&#40;t&#44;</span> <span class="nw">True&#41;&#44;</span> <span class="nw">AlignCenters&#40;f&#44;</span> <span class="nw">m&#44;</span> <span class="nw">&#34;geometry&#34;&#47;&#34;moments&#34;&#47;&#34;origins&#34;&#41;&#93;</span></code> | <code><span class="nw">&#40;&#41;</span></code> | a file whose last extension is not a transform file's (<code><span class="nw">&#46;nii&#46;gz</span></code>, ...) is a displacement field image; a composite may hold fields; a field has no inverse (<code><span class="nw">&#91;field&#44;1&#93;</span></code> fails)<span class="opt-help">ANTs: “Specify the initial moving transform(s) which get immediately incorporated into the composite transform.  The order of the transforms is stack-esque in that the last transform specified on the command line is the first to be applied.  In addition to initialization with ITK transforms, the user can perform an initial translation alignment by specifying the fixed and moving images and selecting an initialization feature.  These features include using the geometric center of the images (=0), the image intensities (=1), or the origin of the images (=2).”</span> |
| <code><span class="nw">&#45;q</span> <span class="nw">&#46;&#46;&#46;</span></code>, <code><span class="nw">&#45;&#45;initial&#45;fixed&#45;transform</span></code> | <code><span class="nw">initial&#95;fixed&#95;transforms&#61;</span></code> | <code><span class="nw">&#40;&#41;</span></code> | <span class="opt-help">ANTs: “Specify the initial fixed transform(s) which get immediately incorporated into the composite transform.  The order of the transforms is stack-esque in that the last transform specified on the command line is the first to be applied.  In addition to initialization with ITK transforms, the user can perform an initial translation alignment by specifying the fixed and moving images and selecting an initialization feature.  These features include using the geometric center of the images (=0), the image intensities (=1), or the origin of the images (=2).”</span> |
| <code><span class="nw">&#45;k</span> <span class="nw">state</span></code>, <code><span class="nw">&#45;&#45;restore&#45;state</span></code> | <code><span class="nw">restore&#95;state&#61;</span></code> | <code><span class="nw">None</span></code> | <span class="opt-help">ANTs: “Specify the initial state of the registration which get immediately used to directly initialize the registration process. The flag is mutually exclusive with other intialization flags.If this flag is used, none of the initial-moving-transform and initial-fixed-transform cannot be used.”</span> |
| <code><span class="nw">&#45;j</span> <span class="nw">state</span></code>, <code><span class="nw">&#45;&#45;save&#45;state</span></code> | (command line only) |  | only on the command line (<code><span class="nw">&#45;&#45;save&#45;state</span></code>, needs <code><span class="nw">&#45;a</span> <span class="nw">1</span></code>): after a SyN stage, the composite before it and SyN's fixed-to-middle and moving-to-middle fields, each followed by its inverse; after linear stages every transform (ANTS-50, ANTS-74)<span class="opt-help">ANTs: “Specify the output file for the current state of the registration. The state file is written to an hdf5 composite file. It is specially usefull if we want to save the current state of a SyN registration to the disk, so we can load and restore that later to continue the next registration process directly started from the last saved state. The output file of this flag is the same as the write-composite-transform, unless the last transform is a SyN transform. In that case, the inverse displacement field of the SyN transform is also added to the output composite transform. Again notice that this file cannot be treated as a transform, and restore-state option must be used to load the written file by this flag.”</span> |
| <code><span class="nw">&#45;w</span> <span class="nw">&#91;0&#46;005&#44;0&#46;995&#93;</span></code>, <code><span class="nw">&#45;&#45;winsorize&#45;image&#45;intensities</span></code> | <code><span class="nw">winsorize&#61;&#40;0&#46;005&#44;</span> <span class="nw">0&#46;995&#41;</span></code> | <code><span class="nw">None</span></code> | <span class="opt-help">ANTs: “Winsorize data based on specified quantiles.”</span> |
| <code><span class="nw">&#45;u</span> <span class="nw">1</span></code>, <code><span class="nw">&#45;&#45;use&#45;histogram&#45;matching</span></code> | <code><span class="nw">use&#95;histogram&#95;matching&#61;True</span></code> | <code><span class="nw">False</span></code> | <span class="opt-help">ANTs: “Histogram match the images before registration.”</span> |
| <code><span class="nw">&#45;z</span> <span class="nw">0&#47;1</span></code>, <code><span class="nw">&#45;&#45;collapse&#45;output&#45;transforms</span></code> | <code><span class="nw">collapse&#95;output&#95;transforms&#61;</span></code> | <code><span class="nw">True</span></code> | default 1<span class="opt-help">ANTs: “Collapse output transforms. Specifically, enabling this option combines all adjacent transforms wherepossible.  All adjacent linear transforms are written to disk in the forman itk affine transform (called xxxGenericAffine.mat).  Similarly, all adjacent displacement field transforms are combined when written to disk (e.g. xxxWarp.nii.gz and xxxInverseWarp.nii.gz (if available)).Also, an output composite transform including the collapsed transforms is written to the disk (called outputCollapsed(Inverse)Composite).”</span> |
| <code><span class="nw">&#45;a</span> <span class="nw">1</span></code>, <code><span class="nw">&#45;&#45;write&#45;composite&#45;transform</span></code> | <code><span class="nw">write&#95;composite&#95;transform&#61;True</span></code> | <code><span class="nw">False</span></code> | <code><span class="nw">Composite&#46;h5</span></code>, <code><span class="nw">InverseComposite&#46;h5</span></code> (fields stored forward; the inverse composite holds the inverse fields)<span class="opt-help">ANTs: “Boolean specifying whether or not the composite transform (and its inverse, if it exists) should be written to an hdf5 composite file.  This is false by default so that only the transform for each stage is written to file.”</span> |
| <code><span class="nw">&#45;i</span> <span class="nw">1</span></code>, <code><span class="nw">&#45;&#45;initialize&#45;transforms&#45;per&#45;stage</span></code> | <code><span class="nw">initialize&#95;transforms&#95;per&#95;stage&#61;True</span></code> | <code><span class="nw">False</span></code> | needs <code><span class="nw">&#45;a</span> <span class="nw">1</span></code> and <code><span class="nw">&#45;z</span> <span class="nw">0</span></code><span class="opt-help">ANTs: “Initialize linear transforms from the previous stage. By enabling this option, the current linear stage transform is directly intialized from the previous stage's linear transform; this allows multiple linear stages to be run where each stage directly updates the estimated linear transform from the previous stage. (e.g. Translation -&gt; Rigid -&gt; Affine).”</span> |
| <code><span class="nw">&#45;n</span> <span class="nw">Linear</span></code>, <code><span class="nw">&#45;&#45;interpolation</span></code> | <code><span class="nw">interpolation&#61;&#34;Linear&#34;</span></code> | <code><span class="nw">&#34;Linear&#34;</span></code> | the warped images' interpolator, as <code><span class="nw">antsApplyTransforms</span> <span class="nw">&#45;n</span></code>, in every dimension<span class="opt-help">ANTs: “Several interpolation options are available in ITK. These have all been made available.  Currently the interpolator choice is only used to warp (and possibly inverse warp) the final output image(s).”</span> |
| <code><span class="nw">&#45;&#45;float</span> <span class="nw">1</span></code> | <code><span class="nw">precision&#61;&#34;float32&#34;</span></code> | <code><span class="nw">&#34;float64&#34;</span></code> | ANTs' single-precision pipeline<span class="opt-help">ANTs: “Use 'float' instead of 'double' for computations.”</span> |
| <code><span class="nw">&#45;&#45;random&#45;seed</span> <span class="nw">N</span></code> / <code><span class="nw">ANTS&#95;RANDOM&#95;SEED</span></code> | <code><span class="nw">random&#95;seed&#61;N</span></code> | <code><span class="nw">None</span></code> | without one: ANTs from the clock, larmorx 121212<span class="opt-help">ANTs: “Use a fixed seed for random number generation. By default, the system clock is used to initialize the seeding. The fixed seed can be any nonzero int value.”</span> |
| <code><span class="nw">&#45;p</span> <span class="nw">N</span></code>, <code><span class="nw">&#45;&#45;print&#45;similarity&#45;measure&#45;interval</span></code> | <code><span class="nw">print&#95;similarity&#95;measure&#95;interval&#61;N</span></code> | <code><span class="nw">0</span></code> | each of the result's <code><span class="nw">iterations</span></code> gets its <code><span class="nw">full&#95;scale&#95;value</span></code><span class="opt-help">ANTs: “Prints out the CC similarity metric measure between the full-size input fixed and the transformed moving images at each iteration a value of 0 (the default) indicates that the full scale computation should not take placeany value greater than 0 represents the interval of full scale metric computation.”</span> |
| <code><span class="nw">&#45;&#45;write&#45;interval&#45;volumes</span> <span class="nw">N</span></code> | (command line only) |  | <span class="opt-help">ANTs: “Writes out the output volume at each iteration. It helps to present the registration process as a short movie a value of 0 (the default) indicates that this option should not take placeany value greater than 0 represents the interval between the iterations which outputs are written to the disk.”</span> |
| <code><span class="nw">&#45;v</span> <span class="nw">1</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> | the result |  | its <code><span class="nw">log</span></code> and <code><span class="nw">iterations</span></code>: Python always runs verbose and parses the <code><span class="nw">DIAGNOSTIC</span></code> lines<span class="opt-help">ANTs: “Verbose output.”</span> |
| <code><span class="nw">&#45;&#45;minc</span> <span class="nw">1</span></code> | – |  | MINC transforms: not supported yet<span class="opt-help">ANTs: “Use MINC file formats for transformations.”</span> |
| <code><span class="nw">&#45;&#45;version</span></code> | (command line only) |  | the version line<span class="opt-help">ANTs: “Get Version Information.”</span> |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | (command line only) |  | ANTs' short and long help<span class="opt-help">ANTs: “Print the help menu (short version).”</span><span class="opt-help">ANTs: “Print the help menu.  Will also print values used on the current command line call.”</span> |
| <code><span class="nw">ITK&#95;GLOBAL&#95;DEFAULT&#95;NUMBER&#95;OF&#95;THREADS</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | the result does not depend on it |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects&#61;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | ANTS-49, -50, -51, ITK-18; the point-set metrics' ANTS-61 to -63, -65 to -68, -70, ITK-22 to -24, -26, -28, -29; SyN's ANTS-71, -73, -74, ITK-30 to -33; the B-spline and field stages' ANTS-75, -76, -78, ITK-35, -42; the velocity-field stages' ANTS-79 to -81, ITK-36 to -41 ([upstream defects](repo:docs/api/upstream-defects.md)) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `ants` on the command line (`larmorx --n-threads 4 ants antsRegistration ...`); `lx.ants.registration` takes `n_threads` and `upstream_defects` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;registration</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `fixed.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `moving.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# A rigid stage with Mattes on a quarter of the voxels, two levels, a fixed seed.
stage = lx.ants.RegistrationStage(
    transform="Rigid", gradient_step=0.1,
    metrics=lx.ants.RegistrationMetric("Mattes", "fixed.nii.gz", "moving.nii.gz",
                                       bins=32, sampling="Regular", sampling_percentage=0.25),
    iterations=[20, 10], shrink_factors=[2, 1], smoothing_sigmas=[1, 0],
)
res = lx.ants.registration([stage], random_seed=42)
res.files["0GenericAffine.mat"][0].name  # -> 'AffineTransform_double_3_3'
```

```bash
larmorx ants antsRegistration -d 3 -o [out_,out_warped.nii.gz] -t Rigid[0.1] -m Mattes[fixed.nii.gz,moving.nii.gz,1,32,Regular,0.25] -c [20x10,1e-6,10] -f 2x1 -s 1x0vox --random-seed 42
```

## Ports {#ports}

`antsRegistration` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [ants-registration](repo:docs/validation/ants-registration.md) |

**The replica: status `validated`** against antsRegistration itself (its
[record](repo:docs/validation/ants-registration.md), standard tier, 2026-10-28, and the full tier's
records): every compared case identical to ANTs 2.6.5 at one thread with the same seed (exit
status, standard output with every `DIAGNOSTIC` line, standard error, every file), most against
the unmodified binary, the rest once glibc's `exp`/`log`/`sin`/`cos` are replaced by CORE-MATH's
correctly rounded ones, which larmorx uses (CLAUDE.md rule 5).

| Tier | Cases | Identical to the unmodified ANTs | Identical with CORE-MATH | Rejected by both | Expected divergences | Failures |
|---|---|---|---|---|---|---|
| standard (2026-10-28) | 513 | 355 | 44 | 93 | 21 | 0 |
| full ([record](repo:docs/validation/ants-registration-full.md), A5 part 2's run, 2026-10-21) | 441 | 278 | 68 | 77 | 18 | 0 |
| full, A5 part 3's cases ([record](repo:docs/validation/ants-registration-velocity-full.md), 2026-10-23) | 124 | 77 | 26 | 16 | 5 | 0 |

The cases cover every transform in 2D, 3D and 4D, double and float, every metric and sampling,
masks, the initial transforms and their files, every output and interpolator, every
command-line check and message, fMRIPrep 25.2.6's own command lines of four oracle nodes, and
(full tier) the linear stages of sMRIPrep's brain extraction and template registration in all
five oracle runs, and (A4 part 4) the point-set metrics: each metric alone and with the
others and image metrics, label images (with boundary points), text and VTK point sets
(ASCII, binary, without scalars), in-memory points, 2D, 3D and 4D, double and float, initial
transforms, several levels and stages, and every message, failure and crash; and (A5 part 1)
SyN stages with each metric, several metrics, masks, sampling, 2D, 3D and 4D, double and float,
the collapse and every output, displacement fields among the initial transforms, saved and
restored states, the point-set metrics in tangent space, and sMRIPrep's two SyN registrations.
The expected divergences: no seed (ANTs from the clock), ANTS-51's crash, `--version`, three of
ANTS-45's silent failures, MINC transforms (refused), a point set's random fraction (ANTs seeds
it from the clock, ANTS-64), IGDM's value for neighbourhoods of more than one voxel (ANTs reads
before its arrays, ANTS-66), a text point set ANTs reads forever (ANTS-69), four linear stages
after a displacement field (ANTs seeds their voxel sample from the clock, ANTS-72); A5 part 2
added ANTS-77's two B-spline meshes (a size of 0, fewer sizes than dimensions: ANTs fails on
garbage, larmorx refuses); A5 part 3 added three samplings of the velocity-field stages (ANTs
seeds them from the clock, ANTS-82), an affine stage after a velocity field (ANTS-72) and a
time-varying B-spline mesh of 0 (ANTS-77). The velocity-field stages, an expected divergence
while larmorx refused them (`syn/exponential`), are compared since A5 part 3.

ANTs' own result moves with its thread count, from about 1e-13 in a transform parameter on the
phantoms to 1.7 in the standard record's 36 cases at 2, 4 and 8 threads (the full account:
[How the records grew](repo:docs/api/ants-registration.md#how-the-records-grew)); larmorx gives the one-thread result at any
thread count.

**On the data panel** ([record](repo:docs/validation/ants-registration-panel.md), 2026-10-27): every
antsRegistration node of the fourteen finished fMRIPrep oracle runs, each replayed from its node
with its inputs and fMRIPrep's seed (the BOLD references' registrations to the template, the
field maps' coregistrations, sMRIPrep's brain extraction at full size: 3.5-year-old, glioma,
stroke, strong motion, 1.5 T, 7 T, multiband-8 and multi-echo among them), and the template
registrations on every third voxel: **71 of 71 cases identical to ANTs 2.6.5 at one thread, 16 as
built and 55 more with CORE-MATH** (warped images, transforms, standard output). The template
registration's inputs, which niworkflows writes for itself and nipype does not keep, are made
again exactly from each node's recorded inputs; its fourteen whole-size runs (about 2.4 hours of
ANTs at one thread each, as built and with CORE-MATH) are left for a larger machine. sMRIPrep's
brain extraction of the 7 T head at full size: ANTs 2884 MiB and 2431 s at one thread, larmorx
2394 MiB and 1165 s, its four files identical.

`antsRegistration` has one port, in `pip install larmorx`: **the replica** (Rust
`larmorx_ants::registration::helper::RegistrationHelper` and the crate `larmorx-registration`;
Apache-2.0), translated from ANTs 2.6.5's `antsRegistration` on ITK 5.4.5's v4 registration
framework (Apache-2.0). **Results do not depend on threads.** ANTs' do (its metrics sum per work
unit); larmorx always gives ANTs' one-thread result. **Without a seed ANTs is not repeatable**
(its sampling is seeded from the clock); larmorx then uses a fixed seed (121212).

## Evidence {#evidence}

How each of `antsRegistration`'s ports was measured against ANTs, case by case: [its evidence](/evidence/ants-registration/).

## More in the repository {#more}

The API page [docs/api/ants-registration.md](repo:docs/api/ants-registration.md) holds what `antsRegistration` shares with the page's other programs:

- [How the records grew](repo:docs/api/ants-registration.md#how-the-records-grew)
- [SyN stages](repo:docs/api/ants-registration.md#syn-stages)
- [B-spline and displacement-field stages](repo:docs/api/ants-registration.md#b-spline-and-displacement-field-stages)
- [Velocity-field stages](repo:docs/api/ants-registration.md#velocity-field-stages)
- [Point-set metrics](repo:docs/api/ants-registration.md#point-set-metrics)
- [Not supported yet](repo:docs/api/ants-registration.md#not-supported-yet)
