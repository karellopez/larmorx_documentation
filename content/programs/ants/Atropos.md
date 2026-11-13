---
title: "`Atropos`"
kicker: "Programs · ANTs and ITK"
lede: "`Atropos` segments an image into tissue classes by a finite mixture model with a Markov random field prior."
description: "LARMORX reference for ANTs 2.6.5 `Atropos`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: ants
  original: "ANTs 2.6.5"
  software: "ANTs"
  command: "larmorx ants Atropos"
  python: "lx.ants.atropos"
  api: "docs/api/ants-atropos.md"
  evidence: "/evidence/ants-atropos/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-ants/src/cli/atropos.rs: "d579dba919dfc29b"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "91be42d24bb3ba2b"
    docs/api/ants-atropos.md: "fed4e36f33548aa9"
    python/larmorx/ants/atropos.py: "738a7e61bdbeccb5"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

The method is Avants et al.'s (*An open source multivariate framework for n-tissue
segmentation with evaluation on public data*, Neuroinformatics 9:381-400, 2011); sMRIPrep runs it
once per subject, in its brain extraction (`atropos_wf`): K-means with three classes, Gaussian
likelihoods, MRF 0.1, three iterations, the fixed seed.

## Command line {#command-line}

```text synopsis
larmorx ants Atropos ...
```

Everything after `larmorx ants Atropos` is the original's command line: the arguments of ANTs 2.6.5's `Atropos`, as ANTs takes them. LARMORX's own options stand between `larmorx` and the family `ants`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        ants Atropos ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

## Python {#python}

```python
lx.ants.atropos(
    images: Any | Sequence[Any],
    mask: Any,
    *,
    classes: int = 3,
    initialization: Initialization = "kmeans",
    kmeans_centers: Sequence[float] | None = None,
    priors: Sequence[Any] | None = None,
    prior_label: Any = None,
    prior_weight: float = 0.0,
    prior_threshold: float | None = None,
    likelihood: LikelihoodModel | None = None,
    posterior_formulation: Formulation = "socrates",
    use_mixture_model_proportions: bool = True,
    annealing: tuple[float, float, float] = (1.0, 1.0, 0.1),
    iterations: int = 5,
    convergence_threshold: float = 0.001,
    mrf_smoothing: Any = 0.3,
    mrf_radius: int | Sequence[int] = 1,
    icm: bool = True,
    icm_iterations: int = 1,
    use_random_seed: bool = True,
    euclidean_distance: bool = False,
    label_propagation: Mapping[int, tuple[float, float]] | tuple[float, float] | None = None,
    minimize_memory: bool = False,
    outliers: BoxPlot | GrubbsRosner | None = None,
    partial_volume: Sequence[tuple[int, int]] = (),
    partial_volume_likelihoods: bool = False,
    adaptive_smoothing: float | Sequence[float] = 0.0,
    bspline: tuple[int | Sequence[int], int | Sequence[int], int] = (6, 1, 3),
    likelihood_images: bool = False,
    distance_images: bool = False,
    smoothed_images: bool = False,
    icm_code_image: bool = False,
    dimension: int | None = None,
    n_threads: int = 1,
    upstream_defects: UpstreamDefectsName = "fix",
) -> AtroposResult
```

Where `Initialization` is one of `"kmeans"`, `"otsu"`, `"random"`, `"prior-probabilities"`, `"prior-label"`; `Formulation` is one of `"socrates"`, `"plato"`, `"aristotle"`, `"sigmoid"`; `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

`Atropos -d D -a image... -x mask -i <initialization> -k <likelihood> -p <formulation> -c [iterations,threshold] -m [smoothing,radius] -g ... -r ... -o [...]`.

Returns an `AtroposResult`: `labels` (the classified image, `uint32`), `posteriors` (one
`float32` image per class, 0 outside the mask), with the arguments that ask for them
`likelihoods`, `distances`, `smoothed` and `icm_codes`, and `iterations` and `log` (the
progress lines and the filter's settings and models). `lx.ants.atropos` raises
`lx.ants.AtroposError` with ANTs' message where Atropos stops (a class that loses all its
voxels, a singular covariance, a missing file), and `ValueError` for arguments the command line
cannot express.

```python
import larmorx as lx

# sMRIPrep's call (the defaults are Atropos': Gaussian likelihoods, MRF 0.3, 5 iterations)
seg = lx.ants.atropos("t1w_n4.nii.gz", "brain_mask.nii.gz", classes=3, mrf_smoothing=0.1,
                      iterations=3, convergence_threshold=0, use_random_seed=False,
                      n_threads=8)
seg.labels.to_filename("labels.nii.gz")      # 1 = CSF, 2 = GM, 3 = WM (by intensity)
csf, gm, wm = seg.posteriors                  # float32 probability images

# antsCorticalThickness-style: tissue priors, weight 0.25, five iterations
seg = lx.ants.atropos(t1w, mask, initialization="prior-probabilities",
                      priors=["csf.nii.gz", "gm.nii.gz", "wm.nii.gz"], prior_weight=0.25,
                      mrf_smoothing=0.1, iterations=5, convergence_threshold=0)

# two contrasts, histogram Parzen windows, box-plot winsorizing
seg = lx.ants.atropos([t1w, t2w], mask, initialization="otsu",
                      likelihood=lx.ants.HistogramParzenWindows(sigma=1.0, bins=32),
                      outliers=lx.ants.BoxPlot())
```

Its result, `AtroposResult`, holds the segmentation.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">labels</span></code> | <code><span class="nw">Image</span></code> |  |
| <code><span class="nw">posteriors</span></code> | <code><span class="nw">tuple&#91;Image&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span></code> |  |
| <code><span class="nw">likelihoods</span></code> | <code><span class="nw">tuple&#91;Image&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span></code> |  |
| <code><span class="nw">distances</span></code> | <code><span class="nw">tuple&#91;Image&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span></code> |  |
| <code><span class="nw">smoothed</span></code> | <code><span class="nw">tuple&#91;Image&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span></code> |  |
| <code><span class="nw">icm&#95;codes</span></code> | <code><span class="nw">Image</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">iterations</span></code> | <code><span class="nw">tuple&#91;AtroposIteration&#44;</span> <span class="nw">&#46;&#46;&#46;&#93;</span></code> |  |
| <code><span class="nw">log</span></code> | <code><span class="nw">str</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `Atropos` accepts (`crates/larmorx-ants/src/cli/atropos.rs`) and the arguments of `lx.ants.atropos` (`python/larmorx/ants/atropos.py`), whose defaults and descriptions are taken from it. Under each option, in grey, ANTs's own help for it.

| ANTs option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;d</span> <span class="nw">2&#47;3&#47;4</span></code>, <code><span class="nw">&#45;&#45;image&#45;dimensionality</span></code> | <code><span class="nw">dimension</span></code> | <code><span class="nw">None</span></code> | default: the first image's; without <code><span class="nw">&#45;d</span></code> ANTs reads every image as 3D (ANTS-99, in [Upstream defects](repo:docs/api/ants-atropos.md#upstream-defects-d13)); the Python wrapper always passes it<span class="opt-help">ANTs: “This option forces the image to be treated as a specified-dimensional image.  If not specified, Atropos tries to infer the dimensionality from the first input image.”</span> |
| <code><span class="nw">&#45;a</span> <span class="nw">image</span></code> / <code><span class="nw">&#45;a</span> <span class="nw">&#91;image&#44;w&#93;</span></code> (repeatable), <code><span class="nw">&#45;&#45;intensity&#45;image</span></code> | <code><span class="nw">images</span></code> (one or a list); <code><span class="nw">adaptive&#95;smoothing&#61;w</span></code> (one value, or one per image) | <code><span class="nw">adaptive&#95;smoothing&#61;0&#46;0</span></code> | paths, <code><span class="nw">lx&#46;Image</span></code>, nibabel images or <code><span class="nw">&#40;array&#44;</span> <span class="nw">affine&#41;</span></code>, read as <code><span class="nw">float</span></code> on the first image's grid; the weight mixes the intensity with its B-spline fit per class, for prior-based initializations only (ANTS-93)<span class="opt-help">ANTs: “One or more scalar images is specified for segmentation using the -a/--intensity-image option.  For segmentation scenarios with no prior information, the first scalar image encountered on the command line is used to order labelings such that the class with the smallest intensity signature is class '1' through class 'N' which represents the voxels with the largest intensity values.  The optional adaptive smoothing weight parameter is applicable only when using prior label or probability images.  This scalar parameter is to be specified between [0,1] which smooths each labeled region separately and modulates the intensity measurement at each voxel in each intensity image between the original intensity and its smoothed counterpart.  The smoothness parameters are governed by the -b/--bspline option.”</span> |
| <code><span class="nw">&#45;x</span> <span class="nw">mask</span></code>, <code><span class="nw">&#45;&#45;mask&#45;image</span></code> | <code><span class="nw">mask</span></code> |  | required; read as <code><span class="nw">unsigned</span> <span class="nw">int</span></code> (0.6 is 0); its non-zero voxels are segmented<span class="opt-help">ANTs: “The image mask (which is required) defines the region which is to be labeled by the Atropos algorithm.”</span> |
| <code><span class="nw">&#45;i</span> <span class="nw">Random&#91;K&#93;</span></code>, <code><span class="nw">&#45;&#45;initialization</span></code> | <code><span class="nw">initialization&#61;&#34;random&#34;</span></code>, <code><span class="nw">classes&#61;K</span></code> | <code><span class="nw">initialization&#61;&#34;kmeans&#34;</span></code>, <code><span class="nw">classes&#61;3</span></code> | labels drawn with the filter's generator<span class="opt-help">ANTs: “To initialize the FMM parameters, one of the following options must be specified.  If one does not have prior label or probability images we recommend using kmeans as it is typically faster than otsu and can be used with multivariate initialization. However, since a Euclidean distance on the inter cluster distances is used, one might have to appropriately scale the additional input images. Random initialization is meant purely for intellectual curiosity. The prior weighting (specified in the range [0,1]) is used to modulate the calculation of the posterior probabilities between the likelihood*mrfprior and the likelihood*mrfprior*prior.  For specifying many prior probability images for a multi-label segmentation, we offer a minimize usage option (see -m).  With that option one can specify a prior probability threshold in which only those pixels exceeding that threshold are stored in memory. ”</span> |
| <code><span class="nw">&#45;i</span> <span class="nw">Otsu&#91;K&#93;</span></code> | <code><span class="nw">initialization&#61;&#34;otsu&#34;</span></code> | <code><span class="nw">&#34;kmeans&#34;</span></code> | Otsu's thresholds of the first image (200 bins)<span class="opt-help">ANTs: “To initialize the FMM parameters, one of the following options must be specified.  If one does not have prior label or probability images we recommend using kmeans as it is typically faster than otsu and can be used with multivariate initialization. However, since a Euclidean distance on the inter cluster distances is used, one might have to appropriately scale the additional input images. Random initialization is meant purely for intellectual curiosity. The prior weighting (specified in the range [0,1]) is used to modulate the calculation of the posterior probabilities between the likelihood*mrfprior and the likelihood*mrfprior*prior.  For specifying many prior probability images for a multi-label segmentation, we offer a minimize usage option (see -m).  With that option one can specify a prior probability threshold in which only those pixels exceeding that threshold are stored in memory. ”</span> |
| <code><span class="nw">&#45;i</span> <span class="nw">KMeans&#91;K&#93;</span></code> / <code><span class="nw">KMeans&#91;K&#44;c1xc2x&#46;&#46;&#46;&#93;</span></code> | <code><span class="nw">initialization&#61;&#34;kmeans&#34;</span></code>, <code><span class="nw">kmeans&#95;centers&#61;&#91;&#46;&#46;&#46;&#93;</span></code> | <code><span class="nw">initialization&#61;&#34;kmeans&#34;</span></code>, <code><span class="nw">kmeans&#95;centers&#61;None</span></code> | k-means on the first image from centres spread over its range in the mask, or given; with several images, a second k-means on all<span class="opt-help">ANTs: “To initialize the FMM parameters, one of the following options must be specified.  If one does not have prior label or probability images we recommend using kmeans as it is typically faster than otsu and can be used with multivariate initialization. However, since a Euclidean distance on the inter cluster distances is used, one might have to appropriately scale the additional input images. Random initialization is meant purely for intellectual curiosity. The prior weighting (specified in the range [0,1]) is used to modulate the calculation of the posterior probabilities between the likelihood*mrfprior and the likelihood*mrfprior*prior.  For specifying many prior probability images for a multi-label segmentation, we offer a minimize usage option (see -m).  With that option one can specify a prior probability threshold in which only those pixels exceeding that threshold are stored in memory. ”</span> |
| <code><span class="nw">&#45;i</span> <span class="nw">PriorProbabilityImages&#91;K&#44;pattern&#37;02d&#44;w&#40;&#44;t&#41;&#93;</span></code> | <code><span class="nw">initialization&#61;&#34;prior&#45;probabilities&#34;</span></code>, <code><span class="nw">priors&#61;&#91;&#46;&#46;&#46;&#93;</span></code>, <code><span class="nw">prior&#95;weight&#61;w</span></code>, <code><span class="nw">prior&#95;threshold&#61;t</span></code> | <code><span class="nw">initialization&#61;&#34;kmeans&#34;</span></code>, <code><span class="nw">priors&#61;None</span></code>, <code><span class="nw">prior&#95;weight&#61;0&#46;0</span></code>, <code><span class="nw">prior&#95;threshold&#61;None</span></code> | one image per class (paths or images; the wrapper names them as a <code><span class="nw">&#37;02d</span></code> series), or one vector image on the command line; <code><span class="nw">t</span></code>: below it a voxel counts as without priors<span class="opt-help">ANTs: “To initialize the FMM parameters, one of the following options must be specified.  If one does not have prior label or probability images we recommend using kmeans as it is typically faster than otsu and can be used with multivariate initialization. However, since a Euclidean distance on the inter cluster distances is used, one might have to appropriately scale the additional input images. Random initialization is meant purely for intellectual curiosity. The prior weighting (specified in the range [0,1]) is used to modulate the calculation of the posterior probabilities between the likelihood*mrfprior and the likelihood*mrfprior*prior.  For specifying many prior probability images for a multi-label segmentation, we offer a minimize usage option (see -m).  With that option one can specify a prior probability threshold in which only those pixels exceeding that threshold are stored in memory. ”</span> |
| <code><span class="nw">&#45;i</span> <span class="nw">PriorLabelImage&#91;K&#44;labels&#44;w&#93;</span></code> | <code><span class="nw">initialization&#61;&#34;prior&#45;label&#34;</span></code>, <code><span class="nw">prior&#95;label</span></code>, <code><span class="nw">prior&#95;weight</span></code> | <code><span class="nw">initialization&#61;&#34;kmeans&#34;</span></code>, <code><span class="nw">prior&#95;label&#61;None</span></code>, <code><span class="nw">prior&#95;weight&#61;0&#46;0</span></code> | labels 1 to K; unlabelled voxels of the mask are reached by propagation<span class="opt-help">ANTs: “To initialize the FMM parameters, one of the following options must be specified.  If one does not have prior label or probability images we recommend using kmeans as it is typically faster than otsu and can be used with multivariate initialization. However, since a Euclidean distance on the inter cluster distances is used, one might have to appropriately scale the additional input images. Random initialization is meant purely for intellectual curiosity. The prior weighting (specified in the range [0,1]) is used to modulate the calculation of the posterior probabilities between the likelihood*mrfprior and the likelihood*mrfprior*prior.  For specifying many prior probability images for a multi-label segmentation, we offer a minimize usage option (see -m).  With that option one can specify a prior probability threshold in which only those pixels exceeding that threshold are stored in memory. ”</span> |
| <code><span class="nw">&#45;p</span> <span class="nw">Socrates&#91;mix&#44;T0&#44;rate&#44;Tmin&#93;</span></code> (<code><span class="nw">Plato</span></code>, <code><span class="nw">Aristotle</span></code>, <code><span class="nw">Sigmoid</span></code>), <code><span class="nw">&#45;&#45;posterior&#45;formulation</span></code> | <code><span class="nw">posterior&#95;formulation&#61;&#34;socrates&#34;</span></code>, <code><span class="nw">use&#95;mixture&#95;model&#95;proportions</span></code>, <code><span class="nw">annealing&#61;&#40;T0&#44;</span> <span class="nw">rate&#44;</span> <span class="nw">Tmin&#41;</span></code> | <code><span class="nw">posterior&#95;formulation&#61;&#34;socrates&#34;</span></code>, <code><span class="nw">use&#95;mixture&#95;model&#95;proportions&#61;True</span></code>, <code><span class="nw">annealing&#61;&#40;1&#46;0&#44;</span> <span class="nw">1&#46;0&#44;</span> <span class="nw">0&#46;1&#41;</span></code> | see the [findings](repo:docs/findings/ants-atropos.md#the-algorithm-as-the-code-has-it); annealing applies only when <code><span class="nw">T0</span></code> is not 1<span class="opt-help">ANTs: “Different posterior probability formulations are possible as are different update options.  To guarantee theoretical convergence properties, a proper formulation of the well-known iterated conditional modes (ICM) uses an asynchronous update step modulated by a specified annealing temperature.  If one sets the AnnealingTemperature &gt; 1 in the posterior formulation a traditional code set for a proper ICM update will be created. Otherwise, a synchronous update step will take place at each iteration. The annealing temperature, T, converts the posteriorProbability to posteriorProbability^(1/T) over the course of optimization. Options include the following:   Socrates: posteriorProbability = (spatialPrior)^priorWeight*(likelihood*mrfPrior)^(1-priorWeight),  Plato: posteriorProbability = 1.0,  Aristotle: posteriorProbability = 1.0,  Sigmoid: posteriorProbability = 1.0, ”</span> |
| <code><span class="nw">&#45;k</span> <span class="nw">Gaussian</span></code>, <code><span class="nw">&#45;&#45;likelihood&#45;model</span></code> | <code><span class="nw">likelihood&#61;lx&#46;ants&#46;GaussianLikelihood&#40;&#41;</span></code> (the default) | <code><span class="nw">None</span></code> | weighted mean and covariance per class<span class="opt-help">ANTs: “Both parametric and non-parametric options exist in Atropos. The Gaussian parametric option is commonly used (e.g. SPM &amp; FAST) where the mean and standard deviation for the Gaussian of each class is calculated at each iteration.  Other groups use non-parametric approaches exemplified by option 2.  We recommend using options 1 or 2 as they are fairly standard and the default parameters work adequately.”</span> |
| <code><span class="nw">&#45;k</span> <span class="nw">HistogramParzenWindows&#91;&#963;&#44;bins&#93;</span></code> | <code><span class="nw">likelihood&#61;lx&#46;ants&#46;HistogramParzenWindows&#40;sigma&#44;</span> <span class="nw">bins&#41;</span></code> | <code><span class="nw">None</span></code> | <span class="opt-help">ANTs: “Both parametric and non-parametric options exist in Atropos. The Gaussian parametric option is commonly used (e.g. SPM &amp; FAST) where the mean and standard deviation for the Gaussian of each class is calculated at each iteration.  Other groups use non-parametric approaches exemplified by option 2.  We recommend using options 1 or 2 as they are fairly standard and the default parameters work adequately.”</span> |
| <code><span class="nw">&#45;k</span> <span class="nw">ManifoldParzenWindows&#91;&#963;r&#44;kEval&#44;kCov&#44;&#963;k&#93;</span></code> | <code><span class="nw">likelihood&#61;lx&#46;ants&#46;ManifoldParzenWindows&#40;regularization&#95;sigma&#44;</span> <span class="nw">evaluation&#95;k&#44;</span> <span class="nw">covariance&#95;k&#44;</span> <span class="nw">kernel&#95;sigma&#41;</span></code> | <code><span class="nw">None</span></code> | ANTS-95, ANTS-104<span class="opt-help">ANTs: “Both parametric and non-parametric options exist in Atropos. The Gaussian parametric option is commonly used (e.g. SPM &amp; FAST) where the mean and standard deviation for the Gaussian of each class is calculated at each iteration.  Other groups use non-parametric approaches exemplified by option 2.  We recommend using options 1 or 2 as they are fairly standard and the default parameters work adequately.”</span> |
| <code><span class="nw">&#45;k</span> <span class="nw">JointShapeAndOrientationProbability&#91;&#963;s&#44;bs&#44;&#963;o&#44;bo&#93;</span></code> | <code><span class="nw">likelihood&#61;lx&#46;ants&#46;JointShapeAndOrientationProbability&#40;&#46;&#46;&#46;&#41;</span></code> | <code><span class="nw">None</span></code> | tensors: 6 images in 3D (xx xy xz yy yz zz); ANTS-103<span class="opt-help">ANTs: “Both parametric and non-parametric options exist in Atropos. The Gaussian parametric option is commonly used (e.g. SPM &amp; FAST) where the mean and standard deviation for the Gaussian of each class is calculated at each iteration.  Other groups use non-parametric approaches exemplified by option 2.  We recommend using options 1 or 2 as they are fairly standard and the default parameters work adequately.”</span> |
| <code><span class="nw">&#45;k</span> <span class="nw">LogEuclideanGaussian</span></code> | <code><span class="nw">likelihood&#61;lx&#46;ants&#46;LogEuclideanGaussian&#40;&#41;</span></code> | <code><span class="nw">None</span></code> | tensors, as above<span class="opt-help">ANTs: “Both parametric and non-parametric options exist in Atropos. The Gaussian parametric option is commonly used (e.g. SPM &amp; FAST) where the mean and standard deviation for the Gaussian of each class is calculated at each iteration.  Other groups use non-parametric approaches exemplified by option 2.  We recommend using options 1 or 2 as they are fairly standard and the default parameters work adequately.”</span> |
| <code><span class="nw">&#45;c</span> <span class="nw">&#91;n&#44;threshold&#93;</span></code>, <code><span class="nw">&#45;&#45;convergence</span></code> | <code><span class="nw">iterations&#61;5</span></code>, <code><span class="nw">convergence&#95;threshold&#61;0&#46;001</span></code> | <code><span class="nw">iterations&#61;5</span></code>, <code><span class="nw">convergence&#95;threshold&#61;0&#46;001</span></code> | stops when the mean largest posterior grows by less than the threshold<span class="opt-help">ANTs: “Convergence is determined by calculating the mean maximum posterior probability over the region of interest at each iteration. When this value decreases or increases less than the specified threshold from the previous iteration or the maximum number of iterations is exceeded the program terminates.”</span> |
| <code><span class="nw">&#45;m</span> <span class="nw">&#91;&#946;&#44;radius&#93;</span></code> / <code><span class="nw">&#45;m</span> <span class="nw">&#91;coefficients&#44;radius&#93;</span></code>, <code><span class="nw">&#45;&#45;mrf</span></code> | <code><span class="nw">mrf&#95;smoothing&#61;0&#46;3</span></code> (a number or an image), <code><span class="nw">mrf&#95;radius&#61;1</span></code> (one value or one per axis) | <code><span class="nw">mrf&#95;smoothing&#61;0&#46;3</span></code>, <code><span class="nw">mrf&#95;radius&#61;1</span></code> | <span class="opt-help">ANTs: “Markov random field (MRF) theory provides a general framework for enforcing spatially contextual constraints on the segmentation solution.  The default smoothing factor of 0.3 provides a moderate amount of smoothing. Increasing this number causes more smoothing whereas decreasing the number lessens the smoothing. The radius parameter specifies the mrf neighborhood.  Different update schemes are possible but only the asynchronous updating has theoretical convergence properties. ”</span> |
| <code><span class="nw">&#45;g</span> <span class="nw">&#91;async&#44;iterations&#44;codes&#93;</span></code>, <code><span class="nw">&#45;&#45;icm</span></code> | <code><span class="nw">icm&#61;True</span></code>, <code><span class="nw">icm&#95;iterations&#61;1</span></code>, <code><span class="nw">icm&#95;code&#95;image&#61;True</span></code> | <code><span class="nw">icm&#61;True</span></code>, <code><span class="nw">icm&#95;iterations&#61;1</span></code>, <code><span class="nw">icm&#95;code&#95;image&#61;False</span></code> | the result's <code><span class="nw">icm&#95;codes</span></code>; the documented bracketed form makes ANTs abort (ANTS-102); the wrapper writes <code><span class="nw">&#45;g</span> <span class="nw">1&#91;1&#44;n&#93;</span></code><span class="opt-help">ANTs: “Asynchronous updating requires the construction of an ICM code image which is a label image (with labels in the range {1,..,MaximumICMCode}) constructed such that no MRF neighborhood has duplicate ICM code labels.  Thus, to update the voxel class labels we iterate through the code labels and, for each code label, we iterate through the image and update the voxel class label that has the corresponding ICM code label.  One can print out the ICM code image by specifying an ITK-compatible image filename.”</span> |
| <code><span class="nw">&#45;r</span> <span class="nw">0&#47;1</span></code>, <code><span class="nw">&#45;&#45;use&#45;random&#45;seed</span></code> | <code><span class="nw">use&#95;random&#95;seed&#61;True</span></code> | <code><span class="nw">True</span></code> | ANTs seeds from the clock (<code><span class="nw">1</span></code>, its default) or with 19650218 (<code><span class="nw">0</span></code>); larmorx never reads the clock: <code><span class="nw">1</span></code> gives the seed 121212<span class="opt-help">ANTs: “Initialize internal random number generator with a random seed. Otherwise, initialize with a constant seed number.”</span> |
| <code><span class="nw">&#45;e</span> <span class="nw">0&#47;1</span></code>, <code><span class="nw">&#45;&#45;use&#45;euclidean&#45;distance</span></code> | <code><span class="nw">euclidean&#95;distance</span></code> | <code><span class="nw">False</span></code> | propagate prior labels by Euclidean distance instead of fast marching<span class="opt-help">ANTs: “Given prior label or probability images, the labels are propagated throughout the masked region so that every voxel in the mask is labeled.  Propagation is done by using a signed distance transform of the label. Alternatively, propagation of the labels with the fast marching filter respects the distance along the shape of the mask (e.g. the sinuous sulci and gyri of the cortex).”</span> |
| <code><span class="nw">&#45;l</span> <span class="nw">&#91;&#955;&#44;p&#93;</span></code> / <code><span class="nw">&#45;l</span> <span class="nw">label&#91;&#955;&#44;p&#93;</span></code>, <code><span class="nw">&#45;&#45;label&#45;propagation</span></code> | <code><span class="nw">label&#95;propagation&#61;&#40;&#955;&#44;</span> <span class="nw">p&#41;</span></code> / <code><span class="nw">&#123;label&#58;</span> <span class="nw">&#40;&#955;&#44;</span> <span class="nw">p&#41;&#125;</span></code> | <code><span class="nw">None</span></code> | <span class="opt-help">ANTs: “The propagation of each prior label can be controlled by the lambda and boundary probability parameters.  The latter parameter is the probability (in the range [0,1]) of the label on the boundary which increases linearly to a maximum value of 1.0 in the interior of the labeled region.  The former parameter dictates the exponential decay of probability propagation outside the labeled region from the boundary probability, i.e. boundaryProbability*exp( -lambda * distance ).”</span> |
| <code><span class="nw">&#45;u</span> <span class="nw">0&#47;1</span></code>, <code><span class="nw">&#45;&#45;minimize&#45;memory&#45;usage</span></code> | <code><span class="nw">minimize&#95;memory</span></code> | <code><span class="nw">False</span></code> | ANTS-97, ANTS-105<span class="opt-help">ANTs: “By default, memory usage is not minimized, however, if this is needed, the various probability and distance images are calculated on the fly instead of being stored in memory at each iteration. Also, if prior probability images are used, only the non-negligible pixel values are stored in memory. ”</span> |
| <code><span class="nw">&#45;w</span> <span class="nw">BoxPlot&#91;l&#44;u&#44;w&#93;</span></code> / <code><span class="nw">&#45;w</span> <span class="nw">GrubbsRosner&#91;s&#44;w&#93;</span></code>, <code><span class="nw">&#45;&#45;winsorize&#45;outliers</span></code> | <code><span class="nw">outliers&#61;lx&#46;ants&#46;BoxPlot&#40;&#46;&#46;&#46;&#41;</span></code> / <code><span class="nw">lx&#46;ants&#46;GrubbsRosner&#40;&#46;&#46;&#46;&#41;</span></code> | <code><span class="nw">None</span></code> | ANTS-94, ANTS-107, ITK-51<span class="opt-help">ANTs: “To remove the effects of outliers in calculating the weighted mean and weighted covariance, the user can opt to remove the outliers through the options specified below.”</span> |
| <code><span class="nw">&#45;s</span> <span class="nw">1x2</span></code> (repeatable), <code><span class="nw">&#45;&#45;partial&#45;volume&#45;label&#45;set</span></code>, <code><span class="nw">&#45;&#45;use&#45;partial&#45;volume&#45;likelihoods</span></code> | <code><span class="nw">partial&#95;volume&#61;&#91;&#40;1&#44;</span> <span class="nw">2&#41;&#93;</span></code>, <code><span class="nw">partial&#95;volume&#95;likelihoods</span></code> | <code><span class="nw">partial&#95;volume&#61;&#40;&#41;</span></code>, <code><span class="nw">partial&#95;volume&#95;likelihoods&#61;False</span></code> | partial-volume classes (labels after the tissues, in the order given); with the MRF, ANTs' partial-volume labels hardly win a voxel and Atropos often stops (ANTS-106, corrected by default)<span class="opt-help">ANTs: “The partial volume estimation option allows one to modelmixtures of classes within single voxels.  Atropos currently allows the user to model two class mixtures per partial volume class. The user specifies a set of class labels per partial volume class requested.  For example, suppose the user was performing a classic 3-tissue segmentation (csf, gm, wm) using kmeans initialization.  Suppose the user also wanted to model the partial voluming effects between csf/gm and gm/wm. The user would specify it using -i kmeans[3] and -s 1x2 -s 2x3.  So, for this example, there would be 3 tissue classes and 2 partial volume classes.  Optionally,the user can limit partial volume handling to mrf considerations only whereby the output would only be the three tissues.”</span><span class="opt-help">ANTs: “The user can specify whether or not to use the partial volume likelihoods, in which case the partial volume class is considered separate from the tissue classes.  Alternatively, one can use the MRF only to handle partial volume in which case, partial volume voxels are not considered as separate classes.”</span> |
| <code><span class="nw">&#45;b</span> <span class="nw">&#91;levels&#44;mesh&#44;order&#93;</span></code>, <code><span class="nw">&#45;&#45;bspline</span></code> | <code><span class="nw">bspline&#61;&#40;6&#44;</span> <span class="nw">1&#44;</span> <span class="nw">3&#41;</span></code> | <code><span class="nw">&#40;6&#44;</span> <span class="nw">1&#44;</span> <span class="nw">3&#41;</span></code> | the adaptive smoothing's B-spline fit<span class="opt-help">ANTs: “If the adaptive smoothing weights are &gt; 0, the intensity images are smoothed in calculating the likelihood values. This is to account for subtle intensity differences across the same tissue regions.”</span> |
| <code><span class="nw">&#45;o</span> <span class="nw">&#91;seg&#44;post&#37;02d&#44;lik&#37;02d&#44;dist&#37;02d&#44;bsp&#37;02d&#93;</span></code>, <code><span class="nw">&#45;&#45;output</span></code> | <code><span class="nw">likelihood&#95;images</span></code>, <code><span class="nw">distance&#95;images</span></code>, <code><span class="nw">smoothed&#95;images</span></code> | <code><span class="nw">likelihood&#95;images&#61;False</span></code>, <code><span class="nw">distance&#95;images&#61;False</span></code>, <code><span class="nw">smoothed&#95;images&#61;False</span></code> | the result's <code><span class="nw">labels</span></code> and <code><span class="nw">posteriors</span></code>, and with those arguments its <code><span class="nw">likelihoods</span></code>, <code><span class="nw">distances</span></code> and <code><span class="nw">smoothed</span></code>: the classified image as <code><span class="nw">uint32</span></code>, the others <code><span class="nw">float32</span></code>, 0 outside the mask<span class="opt-help">ANTs: “The output consists of a labeled image where each voxel in the masked region is assigned a label from 1, 2, ..., N.  Optionally, one can also output the posterior probability images specified in the same format as the prior probability images, e.g. posterior%02d.nii.gz (C-style file name formatting).”</span> |
| <code><span class="nw">&#45;v</span> <span class="nw">1</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> | the result |  | its <code><span class="nw">iterations</span></code> and <code><span class="nw">log</span></code>: the progress lines and the filter's settings and models<span class="opt-help">ANTs: “Verbose output.”</span> |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | (command line only) |  | ANTs' short and long help<span class="opt-help">ANTs: “Print the help menu (short version).”</span><span class="opt-help">ANTs: “Print the help menu.”</span> |
| <code><span class="nw">ITK&#95;GLOBAL&#95;DEFAULT&#95;NUMBER&#95;OF&#95;THREADS</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | neither ANTs' result nor larmorx's depends on it |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | <code><span class="nw">fix</span></code> (default) or <code><span class="nw">reproduce</span></code> ([Upstream defects](repo:docs/api/ants-atropos.md#upstream-defects-d13)) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `ants` on the command line (`larmorx --n-threads 4 ants Atropos ...`); `lx.ants.atropos` takes `n_threads` and `upstream_defects` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;atropos</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `t1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `mask.nii.gz` (the synthetic head's brain as a mask (1 inside, 0 outside)). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# sMRIPrep's call: K-means with three classes, MRF 0.1, three iterations, the fixed seed.
seg = lx.ants.atropos("t1w.nii.gz", "mask.nii.gz", classes=3, mrf_smoothing=0.1,
                      iterations=3, convergence_threshold=0, use_random_seed=False)
seg.labels.data.dtype  # -> dtype('uint32')
```

```bash
larmorx ants Atropos -d 3 -a t1w.nii.gz -x mask.nii.gz -i KMeans[3] -k Gaussian -m [0.1,1x1x1] -c [3,0] -r 0 -o [labels.nii.gz,POSTERIOR_%02d.nii.gz]
```

## Ports {#ports}

`Atropos` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [ants-atropos](repo:docs/validation/ants-atropos.md) |

**The replica: status `validated`** against Atropos itself (its
[record](repo:docs/validation/ants-atropos.md), 2026-10-23, standard tier: 97 cases, 62 pass, 27
rejected by both alike, 8 expected divergences; 58 compared), on every option and failure case
on phantoms, and on sMRIPrep's call and antsCorticalThickness-style prior-based segmentations of
the five fMRIPrep oracle runs' T1w images:
- against the **unmodified ANTs 2.6.5 binary** (one thread): 27 of 58 compared cases
  bit-identical, the classified image identical in all 58. The others' posteriors differ in
  their last bits where glibc's functions are not correctly rounded for a value the run
  meets: on sMRIPrep's call, in 11 to 4,175 of 5.9 to 17.5 million values of a posterior
  image (none on ds001600), by at most 1.2e-7;
- against the **same binary with glibc's `expf`, `logf`, `exp`, `log`, `pow` (and the others)
  replaced by CORE-MATH's correctly rounded ones** (`LD_PRELOAD`,
  `scripts/build_crmath_preload.sh`), the arithmetic larmorx uses: **58 of 58 bit-identical**,
  sMRIPrep's call on the five oracle runs and two prior-based segmentations included;
- **ANTs' Atropos does not depend on its thread count**, and neither does larmorx's; with the
  clock's seed (`-r 1`, Atropos' default) two ANTs runs of sMRIPrep's options on ds000005
  disagree on 306 labels (smallest Dice 0.99947) and on posteriors by up to 0.168; larmorx, with
  its fixed seed, is as far from them (221 and 217 labels).

**On the data panel** ([record](repo:docs/validation/ants-atropos-panel.md), 2026-10-26): sMRIPrep's
call in all fourteen finished oracle runs (the 3.5-year-old, the glioma, the stroke, strong
motion, 1.5 T, 7 T and the 82-year-old among them), its inputs from each run's working directory,
and three calls fMRIPrep never makes (the stroke outside its manual lesion mask, a child's T1w and
T2w as two channels, a FLAIR of 3 mm slices): **17 of 17 compared cases bit-identical with
CORE-MATH, the classified image identical in all 17** (3 bit-identical to the unmodified ANTs).
Against fMRIPrep's own files (ANTs 2.6.2, glibc's maths): the same segmentation in every run,
the posteriors different in 0 to 4,175 voxels (their last bits, as in the standard tier). The panel found a
missing check, now ported: an input on another grid (the FLAIR's mask written from its affine,
2.9e-6 mm off) makes ITK throw, as ANTs does ([findings](repo:docs/findings/ants-atropos.md), "Inputs
on another grid").

`Atropos` has one port, in `pip install larmorx`: **the replica** (`crates/larmorx-ants`,
`crates/larmorx-image`; Apache-2.0; Rust `larmorx_ants::atropos::Atropos`, the command line
`larmorx_ants::cli::atropos`), translated from ANTs 2.6.5's `Atropos` on ITK 5.4.5. Neither
ANTs' result nor its result depends on the thread count.

## Evidence {#evidence}

How each of `Atropos`'s ports was measured against ANTs, case by case: [its evidence](/evidence/ants-atropos/).

## More in the repository {#more}

The API page [docs/api/ants-atropos.md](repo:docs/api/ants-atropos.md) holds what `Atropos` shares with the page's other programs:

- [Upstream defects (D13)](repo:docs/api/ants-atropos.md#upstream-defects-d13)
- [Deliberate differences](repo:docs/api/ants-atropos.md#deliberate-differences)
- [Rust](repo:docs/api/ants-atropos.md#rust)
