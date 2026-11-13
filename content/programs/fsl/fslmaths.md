---
title: "`fslmaths`"
kicker: "Programs · FSL"
lede: "`fslmaths` reads one image, applies a chain of operations to it from left to right and writes the result."
description: "LARMORX reference for FSL 6.0.7.23 `fslmaths`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl fslmaths"
  python: "lx.fsl.fslmaths"
  api: "docs/api/fsl-maths.md"
  evidence: "/evidence/fsl-maths/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "24c23485c8957683"
    crates/larmorx-fsl/src/cli/fslmaths.rs: "e69c8b6841f7d57c"
    crates/larmorx-fsl/src/cli/fslmaths_usage.txt: "7274818b9c87c884"
    crates/larmorx-fsl/src/maths/filters.rs: "9d2c30ff95411ff7"
    crates/larmorx-fsl/src/maths/ops.rs: "291d7d6ed5d19449"
    crates/larmorx-fsl/src/maths/reduce.rs: "f6a93c7fce301092"
    docs/api/fsl-maths.md: "01c74948cce02e41"
    python/larmorx/fsl/maths.py: "aad36d56e967f814"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

Its operations: maths with numbers and other images, thresholds, binarisation and masks,
voxelwise functions, random noise, kernels and spatial filters (morphology, convolution,
subsampling, edges, hole filling), reductions along a dimension, statistical transforms, regions,
temporal band-pass filtering, threshold-free cluster enhancement, ROC analysis and tensor
decomposition.

## Command line {#command-line}

```text synopsis
larmorx fsl fslmaths [-dt <datatype>] <first_input> [operations and inputs] <output> [-odt <datatype>]
```

Everything after `larmorx fsl fslmaths` is the original's command line: the arguments of FSL 6.0.7.23's `fslmaths`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl fslmaths ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>fslmaths</code>'s usage text, as the clean room prints it</summary>

```text
Usage: fslmaths [-dt <datatype>] <first_input> [operations and inputs] <output> [-odt <datatype>]

Datatype information:
 -dt sets the datatype used internally for calculations (default float for all except double images)
 -odt sets the output datatype ( default is float )
 Possible datatypes are: char short int float double input
 "input" will set the datatype to that of the original image

Binary operations:
  (some inputs can be either an image or a number)
 -add <number> | <image> : add following input to current image
 -sub <number> | <image> : subtract following input from current image
 -mul <number> | <image> : multiply current image by following input
 -div <number> | <image> : divide current image by following input
 -rem <number> | <image> : modulus remainder - divide current image by following input and take remainder
 -mas <image>            : use (following image>0) to mask current image
 -thr <number>           : threshold below the following number (zero anything below the number)
 -thrp <number>          : threshold below the following percentage (0-100) of ROBUST RANGE
 -thrP <number>          : threshold below the following percentage (0-100) of the positive voxels' ROBUST RANGE
 -uthr <number>          : upper-threshold above the following number (zero anything above the number)
 -uthrp <number>         : upper-threshold above the following percentage (0-100) of the ROBUST RANGE
 -uthrP <number>         : upper-threshold above the following percentage (0-100) of the positive voxels' ROBUST RANGE
 -max <number> | <image> : take maximum of following input and current image
 -min <number> | <image> : take minimum of following input and current image
 -seed  : seed random number generator with following number
 -restart : replace the current image with input for future processing operations
 -save : save the current working image to the input filename

Basic unary operations:
 -exp   : exponential
 -log   : natural logarithm
 -sin   : sine function
 -cos   : cosine function
 -tan   : tangent function
 -asin  : arc sine function
 -acos  : arc cosine function
 -atan  : arc tangent function
 -sqr   : square
 -sqrt  : square root
 -recip : reciprocal (1/current image)
 -abs   : absolute value
 -bin   : use (current image>0) to binarise
 -binv  : binarise and invert (binarisation and logical inversion)
 -fillh : fill holes in a binary mask (holes are internal - i.e. do not touch the edge of the FOV)
 -fillh26 : fill holes using 26 connectivity
 -index : replace each nonzero voxel with a unique (subject to wrapping) index number
 -grid <value> <spacing> : add a 3D grid of intensity <value> with grid spacing <spacing>
 -edge  : edge strength
 -dog_edge <sigma1> <sigma2> : difference of gaussians edge filter. Typical sigma1 is 1.0 and sigma2 is 1.6
 -tfce <H> <E> <connectivity>: enhance with TFCE, e.g. -tfce 2 0.5 6 (maybe change 6 to 26 for skeletons)
 -tfceS <H> <E> <connectivity> <X> <Y> <Z> <tfce_thresh>: show support area for voxel (X,Y,Z)
 -nan   : replace NaNs (improper numbers) with 0
 -nanm  : make NaN (improper number) mask with 1 for NaN voxels, 0 otherwise
 -rand  : add uniform noise (range 0:1)
 -randn : add Gaussian noise (mean=0 sigma=1)
 -inm <mean> :  (-i i ip.c) intensity normalisation (per 3D volume mean)
 -ing <mean> :  (-I i ip.c) intensity normalisation, global 4D mean)
 -range : set the output calmin/max to full data range

Matrix operations:
 -tensor_decomp : convert a 4D (6-timepoint )tensor image into L1,2,3,FA,MD,MO,V1,2,3 (remaining image in pipeline is FA)

Kernel operations (set BEFORE filtering operation if desired):
 -kernel 3D : 3x3x3 box centered on target voxel (set as default kernel)
 -kernel 2D : 3x3x1 box centered on target voxel
 -kernel box    <size>     : all voxels in a cube of width <size> mm centered on target voxel
 -kernel boxv   <size>     : all voxels in a cube of width <size> voxels centered on target voxel, CAUTION: size should be an odd number
 -kernel boxv3  <X> <Y> <Z>: all voxels in a cuboid of dimensions X x Y x Z centered on target voxel, CAUTION: size should be an odd number
 -kernel gauss  <sigma>    : gaussian kernel (sigma in mm, not voxels)
 -kernel sphere <size>     : all voxels in a sphere of radius <size> mm centered on target voxel
 -kernel file   <filename> : use external file as kernel

Spatial Filtering operations: N.B. all options apart from -s use the default kernel or that _previously_ specified by -kernel
 -dilM    : Mean Dilation of non-zero voxels
 -dilD    : Modal Dilation of non-zero voxels
 -dilF    : Maximum filtering of all voxels
 -dilall  : Apply -dilM repeatedly until the entire FOV is covered
 -ero     : Erode by zeroing non-zero voxels when zero voxels found in kernel
 -eroF    : Minimum filtering of all voxels
 -fmedian : Median Filtering 
 -fmean   : Mean filtering, kernel weighted (conventionally used with gauss kernel)
 -fmeanu  : Mean filtering, kernel weighted, un-normalised (gives edge effects)
 -s <sigma> : create a gauss kernel of sigma mm and perform mean filtering
 -subsamp2  : downsamples image by a factor of 2 (keeping new voxels centred on old)
 -subsamp2offc  : downsamples image by a factor of 2 (non-centred)

Dimensionality reduction operations:
  (the "T" can be replaced by X, Y or Z to collapse across a different dimension)
 -Tmean   : mean across time
 -Tstd    : standard deviation across time
 -Tmax    : max across time
 -Tmaxn   : time index of max across time
 -Tmin    : min across time
 -Tmedian : median across time
 -Tperc <percentage> : nth percentile (0-100) of FULL RANGE across time
 -Tar1    : temporal AR(1) coefficient (use -odt float and probably demean first)

Basic statistical operations:
 -pval    : Nonparametric uncorrected P-value, assuming timepoints are the permutations; first timepoint is actual (unpermuted) stats image
 -pval0   : Same as -pval, but treat zeros as missing data
 -cpval   : Same as -pval, but gives FWE corrected P-values
 -ztop    : Convert Z-stat to (uncorrected) P
 -ptoz    : Convert (uncorrected) P to Z
 -rank    : Convert data to ranks (over T dim)
 -ranknorm: Transform to Normal dist via ranks

Multi-argument operations:
 -roi <xmin> <xsize> <ymin> <ysize> <zmin> <zsize> <tmin> <tsize> : zero outside roi (using voxel coordinates). Inputting -1 for a size will set it to the full image extent for that dimension.
 -bptf  <hp_sigma> <lp_sigma> : (-t in ip.c) Bandpass temporal filtering; nonlinear highpass and Gaussian linear lowpass (with sigmas in volumes, not seconds); set either sigma<0 to skip that filter
 -roc <AROC-thresh> <outfile> [4Dnoiseonly] <truth> : take (normally binary) truth and test current image in ROC analysis against truth. <AROC-thresh> is usually 0.05 and is limit of Area-under-ROC measure FP axis. <outfile> is a text file of the ROC curve (triplets of values: FP TP threshold). If the truth image contains negative voxels these get excluded from all calculations. If <AROC-thresh> is positive then the [4Dnoiseonly] option needs to be set, and the FP rate is determined from this noise-only data, and is set to be the fraction of timepoints where any FP (anywhere) is seen, as found in the noise-only 4d-dataset. This is then controlling the FWE rate. If <AROC-thresh> is negative the FP rate is calculated from the zero-value parts of the <truth> image, this time averaging voxelwise FP rate over all timepoints. In both cases the TP rate is the average fraction of truth=positive voxels correctly found.

Combining 4D and 3D images:
 If you apply a Binary operation (one that takes the current image and a new image together), when one is 3D and the other is 4D,
 the 3D image is cloned temporally to match the temporal dimensions of the 4D image.

e.g. fslmaths inputVolume -add inputVolume2 output_volume
     fslmaths inputVolume -add 2.5 output_volume
     fslmaths inputVolume -add 2.5 -mul inputVolume2 output_volume

     fslmaths 4D_inputVolume -Tmean -mul -1 -add 4D_inputVolume demeaned_4D_inputVolume
```

</details>

## Python {#python}

```python
lx.fsl.fslmaths(
    image: Any,
    *operations: Any,
    dt: DataType | None = None,
    odt: DataType | None = None,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
) -> Image
```

Where `DataType` is one of `"char"`, `"short"`, `"int"`, `"float"`, `"double"`, `"input"`; `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

Run fslmaths' `operations` on `image`, as `fslmaths [-dt <dt>] <image> <operations...> <output> [-odt <odt>]` does, and return the output image.

It returns the output as an `lx.Image` (fslmaths' data type and geometry).

- `image` and the image operands are `lx.Image`s, nibabel images, `(array, affine)` pairs or
  paths; in-memory images are written for the program in their own data type (int8, uint16, ...
  too; booleans as uint8; other kinds as float32), which matters with `dt="input"` and
  `odt="input"`.
- Operations are fslmaths' own words (`"-mul"`, `"-kernel"`, `"gauss"`, `"-Tmean"`, ...); numbers
  are passed as their shortest round-trip text, strings as they are.
- **The program runs in the caller's working directory**: relative file names are read there,
  and the files an operation names (`-save <name>`, `-roc`'s curve) are written there, as
  uncompressed NIfTI-1, as the command line would write them. The output itself goes to a
  temporary directory and is read back.
- FSL's environment variables are settings of the call, never read from the process
  (CLAUDE.md rule 6): the program writes NIfTI-1 (`FSLOUTPUTTYPE=NIFTI`) and no `FSL*` variable
  reaches it.
- FSL's fslmaths and the replica run on one thread; the clean room runs on `n_threads`, with the
  same results at any count.
- Errors: `ValueError` for invalid arguments, `larmorx.ReplicaError` when the replica fails (its
  message in the error, without the usage text), `RuntimeError` when the clean room does,
  `larmorx.ReplicaNotFoundError` without `larmorx-nc`.

```python
import larmorx as lx

# niworkflows' combine_masks, in every BOLD reference's mask: fslmaths <a> -mul <b> <out>
mask = lx.fsl.arithmetic("mask_a.nii.gz", "multiply", "mask_b.nii.gz")

# fMRIPrep's goodvoxels mask, its first steps
std = lx.fsl.collapse("bold.nii.gz", "std")          # -Tstd
mean = lx.fsl.collapse("bold.nii.gz", "mean")        # -Tmean
cov = lx.fsl.arithmetic(std, "divide", mean)         # -div <image>
cov_ribbon = lx.fsl.apply_mask(cov, "ribbon.nii.gz") # -mas

# any chain, in fslmaths' own words: the generic function mirrors the command line
smoothed = lx.fsl.fslmaths(cov_ribbon, "-s", 5, "-div", "smooth_norm.nii.gz", "-dilD")
binary = lx.fsl.fslmaths("t1w.nii.gz", "-thrp", 10, "-bin", odt="char")
```

Its result, `Image`, holds a voxel array placed in world space by an affine.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">data</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">affine</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">header</span></code> | <code><span class="nw">NiftiHeader</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">implementation</span></code> | <code><span class="nw">Implementation</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `fslmaths` accepts (`crates/larmorx-fsl/src/cli/fslmaths.rs`) and the arguments of `lx.fsl.fslmaths` (`python/larmorx/fsl/maths.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">fslmaths</span></code> option | Python | Default | Notes |
|---|---|---|---|
| the first word after <code><span class="nw">&#45;dt</span></code> | <code><span class="nw">image</span></code> |  | the input image<span class="opt-help">FSL: “sets the datatype used internally for calculations (default float for all except double images)”</span> |
| the last word before <code><span class="nw">&#45;odt</span></code> | the result |  | the output image, returned as an <code><span class="nw">lx&#46;Image</span></code><span class="opt-help">FSL: “sets the output datatype ( default is float )”</span> |
| <code><span class="nw">&#45;dt</span></code>, <code><span class="nw">&#45;datatype</span></code> | <code><span class="nw">dt</span></code> | <code><span class="nw">None</span></code> | the type the chain computes in: <code><span class="nw">&#34;char&#34;</span></code>, <code><span class="nw">&#34;short&#34;</span></code>, <code><span class="nw">&#34;int&#34;</span></code>, <code><span class="nw">&#34;float&#34;</span></code>, <code><span class="nw">&#34;double&#34;</span></code>, <code><span class="nw">&#34;input&#34;</span></code> (float, or double for a double image, by default; [Data types](repo:docs/api/fsl-maths.md#data-types))<span class="opt-help">FSL: “sets the datatype used internally for calculations (default float for all except double images)”</span> |
| <code><span class="nw">&#45;odt</span></code>, <code><span class="nw">&#45;output&#95;datatype</span></code> | <code><span class="nw">odt</span></code> | <code><span class="nw">None</span></code> | the output's type, the same names (float, or double, by default)<span class="opt-help">FSL: “sets the output datatype ( default is float )”</span> |
| <code><span class="nw">&#45;add</span></code>, <code><span class="nw">&#45;sub</span></code>, <code><span class="nw">&#45;mul</span></code>, <code><span class="nw">&#45;div</span></code>, <code><span class="nw">&#45;rem</span></code>, <code><span class="nw">&#45;max</span></code>, <code><span class="nw">&#45;min</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;arithmetic&#40;image&#44;</span> <span class="nw">operation&#44;</span> <span class="nw">operand&#41;</span></code> |  | voxelwise with a number or an image (a 3D image against a 4D one is used for every volume); <code><span class="nw">&#45;rem</span></code> is an integer remainder; <code><span class="nw">&#45;div</span></code> by an image gives 0 where it is 0<span class="opt-help">FSL: “add following input to current image”</span><span class="opt-help">FSL: “subtract following input from current image”</span><span class="opt-help">FSL: “multiply current image by following input”</span><span class="opt-help">FSL: “divide current image by following input”</span><span class="opt-help">FSL: “modulus remainder - divide current image by following input and take remainder”</span><span class="opt-help">FSL: “take maximum of following input and current image”</span><span class="opt-help">FSL: “take minimum of following input and current image”</span> |
| <code><span class="nw">&#45;mas</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;apply&#95;mask&#40;image&#44;</span> <span class="nw">mask&#41;</span></code> |  | zero where the mask is not above 0<span class="opt-help">FSL: “use (following image&gt;0) to mask current image”</span> |
| <code><span class="nw">&#45;thr</span></code>, <code><span class="nw">&#45;uthr</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;threshold&#40;image&#44;</span> <span class="nw">lower&#61;None&#44;</span> <span class="nw">upper&#61;None&#41;</span></code> |  | zero below <code><span class="nw">lower</span></code> (kept from it, inclusive), then above <code><span class="nw">upper</span></code><span class="opt-help">FSL: “threshold below the following number (zero anything below the number)”</span><span class="opt-help">FSL: “upper-threshold above the following number (zero anything above the number)”</span> |
| <code><span class="nw">&#45;thrp</span></code>, <code><span class="nw">&#45;uthrp</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;threshold&#40;&#46;&#46;&#46;&#44;</span> <span class="nw">of&#61;&#34;robust&#95;range&#34;&#41;</span></code> |  | the limits as percentages (0-100) of the robust 2 %-98 % range<span class="opt-help">FSL: “threshold below the following percentage (0-100) of ROBUST RANGE”</span><span class="opt-help">FSL: “upper-threshold above the following percentage (0-100) of the ROBUST RANGE”</span> |
| <code><span class="nw">&#45;thrP</span></code>, <code><span class="nw">&#45;uthrP</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;threshold&#40;&#46;&#46;&#46;&#44;</span> <span class="nw">of&#61;&#34;positive&#95;robust&#95;range&#34;&#41;</span></code> |  | of the positive voxels' robust range<span class="opt-help">FSL: “threshold below the following percentage (0-100) of the positive voxels' ROBUST RANGE”</span><span class="opt-help">FSL: “upper-threshold above the following percentage (0-100) of the positive voxels' ROBUST RANGE”</span> |
| <code><span class="nw">&#45;exp</span></code>, <code><span class="nw">&#45;log</span></code>, <code><span class="nw">&#45;sin</span></code>, <code><span class="nw">&#45;cos</span></code>, <code><span class="nw">&#45;tan</span></code>, <code><span class="nw">&#45;asin</span></code>, <code><span class="nw">&#45;acos</span></code>, <code><span class="nw">&#45;atan</span></code>, <code><span class="nw">&#45;sqr</span></code>, <code><span class="nw">&#45;sqrt</span></code>, <code><span class="nw">&#45;recip</span></code>, <code><span class="nw">&#45;abs</span></code>, <code><span class="nw">&#45;fillh</span></code>, <code><span class="nw">&#45;fillh26</span></code>, <code><span class="nw">&#45;index</span></code>, <code><span class="nw">&#45;edge</span></code>, <code><span class="nw">&#45;nan</span></code>, <code><span class="nw">&#45;nanm</span></code>, <code><span class="nw">&#45;range</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;unary&#40;image&#44;</span> <span class="nw">operation&#41;</span></code> |  | the maths functions (<code><span class="nw">&#45;log</span></code> leaves values ≤ 0 unchanged; <code><span class="nw">&#45;sqrt</span></code> makes them 0; [GLIBC-07](repo:docs/api/fsl-maths.md#maths-functions-and-glibc-07)), hole filling of a binary mask, numbering of the positive voxels, edge strength, NaN to 0 and the NaN mask, the display range set to the data's<span class="opt-help">FSL: “exponential”</span><span class="opt-help">FSL: “natural logarithm”</span><span class="opt-help">FSL: “sine function”</span><span class="opt-help">FSL: “cosine function”</span><span class="opt-help">FSL: “tangent function”</span><span class="opt-help">FSL: “arc sine function”</span><span class="opt-help">FSL: “arc cosine function”</span><span class="opt-help">FSL: “arc tangent function”</span><span class="opt-help">FSL: “square”</span><span class="opt-help">FSL: “square root”</span><span class="opt-help">FSL: “reciprocal (1/current image)”</span><span class="opt-help">FSL: “absolute value”</span><span class="opt-help">FSL: “fill holes in a binary mask (holes are internal - i.e. do not touch the edge of the FOV)”</span><span class="opt-help">FSL: “fill holes using 26 connectivity”</span><span class="opt-help">FSL: “replace each nonzero voxel with a unique (subject to wrapping) index number”</span><span class="opt-help">FSL: “edge strength”</span><span class="opt-help">FSL: “replace NaNs (improper numbers) with 0”</span><span class="opt-help">FSL: “make NaN (improper number) mask with 1 for NaN voxels, 0 otherwise”</span><span class="opt-help">FSL: “set the output calmin/max to full data range”</span> |
| <code><span class="nw">&#45;pow</span></code> | <code><span class="nw">operations</span></code> |  | (hidden in FSL's usage) the power that follows (<code><span class="nw">specs&#47;fslmaths&#46;md</span></code> §7) |
| <code><span class="nw">&#45;bin</span></code>, <code><span class="nw">&#45;binv</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;binarise&#40;image&#44;</span> <span class="nw">invert&#61;False&#41;</span></code> |  | 1 where above 0 (<code><span class="nw">invert</span></code>: where not above 0)<span class="opt-help">FSL: “use (current image&gt;0) to binarise”</span><span class="opt-help">FSL: “binarise and invert (binarisation and logical inversion)”</span> |
| <code><span class="nw">&#45;invbin</span></code> | <code><span class="nw">operations</span></code> |  | (hidden in FSL's usage) 1 where the value is 0, else 0; NaN is not 0 (<code><span class="nw">specs&#47;fslmaths&#46;md</span></code> §6.2) |
| <code><span class="nw">&#45;rand</span></code>, <code><span class="nw">&#45;randn</span></code>, <code><span class="nw">&#45;seed</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;add&#95;noise&#40;image&#44;</span> <span class="nw">distribution&#61;&#34;uniform&#34;&#44;</span> <span class="nw">seed&#61;None&#41;</span></code> |  | uniform noise on [0, 1) or Gaussian noise added; without <code><span class="nw">seed</span></code> fslmaths' fixed initial state (deterministic)<span class="opt-help">FSL: “add uniform noise (range 0:1)”</span><span class="opt-help">FSL: “add Gaussian noise (mean=0 sigma=1)”</span><span class="opt-help">FSL: “seed random number generator with following number”</span> |
| <code><span class="nw">&#45;grid</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;grid&#40;image&#44;</span> <span class="nw">value&#44;</span> <span class="nw">spacing&#41;</span></code> |  | the voxels on every <code><span class="nw">spacing</span></code>-th plane along x, y or z set to <code><span class="nw">value</span></code><span class="opt-help">FSL: “add a 3D grid of intensity &lt;value&gt; with grid spacing &lt;spacing&gt;”</span> |
| <code><span class="nw">&#45;dog&#95;edge</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;dog&#95;edge&#40;image&#44;</span> <span class="nw">sigma1&#44;</span> <span class="nw">sigma2&#41;</span></code> |  | the zero crossings of a difference of Gaussians, sigmas in voxels in each slice's plane<span class="opt-help">FSL: “difference of gaussians edge filter. Typical sigma1 is 1.0 and sigma2 is 1.6”</span> |
| <code><span class="nw">&#45;inm</span></code>, <code><span class="nw">&#45;ing</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;normalise&#95;intensity&#40;image&#44;</span> <span class="nw">mean&#44;</span> <span class="nw">per&#95;volume&#61;True&#41;</span></code> |  | scaled to <code><span class="nw">mean</span></code>, each volume's (<code><span class="nw">&#45;inm</span></code>) or the whole image's (<code><span class="nw">&#45;ing</span></code>) mean of its positive voxels<span class="opt-help">FSL: “(-i i ip.c) intensity normalisation (per 3D volume mean)”</span><span class="opt-help">FSL: “(-I i ip.c) intensity normalisation, global 4D mean)”</span> |
| <code><span class="nw">&#45;kernel</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;spatial&#95;filter&#40;&#46;&#46;&#46;&#44;</span> <span class="nw">kernel&#61;&#46;&#46;&#46;&#41;</span></code> |  | the kernel of the filters after it: <code><span class="nw">3D</span></code> (the default 3 × 3 × 3 box), <code><span class="nw">2D</span></code>, <code><span class="nw">box</span></code>, <code><span class="nw">boxv</span></code>, <code><span class="nw">boxv3</span></code>, <code><span class="nw">gauss</span></code>, <code><span class="nw">sphere</span></code>, <code><span class="nw">file</span></code><span class="opt-help">FSL: “3D: 3x3x3 box centered on target voxel (set as default kernel); 2D: 3x3x1 box centered on target voxel; box &lt;size&gt;: all voxels in a cube of width &lt;size&gt; mm centered on target voxel; boxv &lt;size&gt;: all voxels in a cube of width &lt;size&gt; voxels centered on target voxel, CAUTION: size should be an odd number; boxv3 &lt;X&gt; &lt;Y&gt; &lt;Z&gt;: all voxels in a cuboid of dimensions X x Y x Z centered on target voxel, CAUTION: size should be an odd number; gauss &lt;sigma&gt;: gaussian kernel (sigma in mm, not voxels); sphere &lt;size&gt;: all voxels in a sphere of radius &lt;size&gt; mm centered on target voxel; file &lt;filename&gt;: use external file as kernel”</span> |
| <code><span class="nw">&#45;dilM</span></code>, <code><span class="nw">&#45;dilD</span></code>, <code><span class="nw">&#45;dilF</span></code>, <code><span class="nw">&#45;dilall</span></code>, <code><span class="nw">&#45;ero</span></code>, <code><span class="nw">&#45;eroF</span></code>, <code><span class="nw">&#45;fmedian</span></code>, <code><span class="nw">&#45;fmean</span></code>, <code><span class="nw">&#45;fmeanu</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;spatial&#95;filter&#40;image&#44;</span> <span class="nw">operation&#44;</span> <span class="nw">kernel&#61;None&#41;</span></code> |  | mean, modal and maximum dilation, dilation until the field of view is filled, erosion, minimum, median and kernel-weighted mean filtering (<code><span class="nw">&#45;fmeanu</span></code> un-normalised)<span class="opt-help">FSL: “Mean Dilation of non-zero voxels”</span><span class="opt-help">FSL: “Modal Dilation of non-zero voxels”</span><span class="opt-help">FSL: “Maximum filtering of all voxels”</span><span class="opt-help">FSL: “Apply -dilM repeatedly until the entire FOV is covered”</span><span class="opt-help">FSL: “Erode by zeroing non-zero voxels when zero voxels found in kernel”</span><span class="opt-help">FSL: “Minimum filtering of all voxels”</span><span class="opt-help">FSL: “Median Filtering”</span><span class="opt-help">FSL: “Mean filtering, kernel weighted (conventionally used with gauss kernel)”</span><span class="opt-help">FSL: “Mean filtering, kernel weighted, un-normalised (gives edge effects)”</span> |
| <code><span class="nw">&#45;s</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;smooth&#40;image&#44;</span> <span class="nw">sigma&#41;</span></code> |  | Gaussian smoothing, sigma in mm, normalised at the image's edges<span class="opt-help">FSL: “create a gauss kernel of sigma mm and perform mean filtering”</span> |
| <code><span class="nw">&#45;subsamp2</span></code>, <code><span class="nw">&#45;subsamp2offc</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;subsample2&#40;image&#44;</span> <span class="nw">centred&#61;True&#41;</span></code> |  | halved along x, y, z (new voxels centred on old ones, or on 2 × 2 × 2 blocks)<span class="opt-help">FSL: “downsamples image by a factor of 2 (keeping new voxels centred on old)”</span><span class="opt-help">FSL: “downsamples image by a factor of 2 (non-centred)”</span> |
| <code><span class="nw">&#45;Tmean</span></code>, <code><span class="nw">&#45;Tstd</span></code>, <code><span class="nw">&#45;Tmax</span></code>, <code><span class="nw">&#45;Tmaxn</span></code>, <code><span class="nw">&#45;Tmin</span></code>, <code><span class="nw">&#45;Tmedian</span></code>, <code><span class="nw">&#45;Tperc</span></code>, <code><span class="nw">&#45;Tar1</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;collapse&#40;image&#44;</span> <span class="nw">statistic&#44;</span> <span class="nw">axis&#61;&#34;T&#34;&#44;</span> <span class="nw">percentile&#61;None&#41;</span></code> |  | a statistic along one axis, the axis kept with size 1; <code><span class="nw">X</span></code>, <code><span class="nw">Y</span></code> or <code><span class="nw">Z</span></code> in place of <code><span class="nw">T</span></code> (<code><span class="nw">&#45;Xmean</span></code>, ...) collapse along x, y or z<span class="opt-help">FSL: “mean across time”</span><span class="opt-help">FSL: “standard deviation across time”</span><span class="opt-help">FSL: “max across time”</span><span class="opt-help">FSL: “time index of max across time”</span><span class="opt-help">FSL: “min across time”</span><span class="opt-help">FSL: “median across time”</span><span class="opt-help">FSL: “nth percentile (0-100) of FULL RANGE across time”</span><span class="opt-help">FSL: “temporal AR(1) coefficient (use -odt float and probably demean first)”</span> |
| <code><span class="nw">&#45;pval</span></code>, <code><span class="nw">&#45;pval0</span></code>, <code><span class="nw">&#45;cpval</span></code>, <code><span class="nw">&#45;ztop</span></code>, <code><span class="nw">&#45;ptoz</span></code>, <code><span class="nw">&#45;rank</span></code>, <code><span class="nw">&#45;ranknorm</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;statistical&#40;image&#44;</span> <span class="nw">operation&#41;</span></code> |  | permutation p-values (the first volume the actual statistic), z to p, p to z, ranks over time and their normal transform<span class="opt-help">FSL: “Nonparametric uncorrected P-value, assuming timepoints are the permutations; first timepoint is actual (unpermuted) stats image”</span><span class="opt-help">FSL: “Same as -pval, but treat zeros as missing data”</span><span class="opt-help">FSL: “Same as -pval, but gives FWE corrected P-values”</span><span class="opt-help">FSL: “Convert Z-stat to (uncorrected) P”</span><span class="opt-help">FSL: “Convert (uncorrected) P to Z”</span><span class="opt-help">FSL: “Convert data to ranks (over T dim)”</span><span class="opt-help">FSL: “Transform to Normal dist via ranks”</span> |
| <code><span class="nw">&#45;roi</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;roi&#40;image&#44;</span> <span class="nw">x&#61;&#40;0&#44;</span> <span class="nw">&#45;1&#41;&#44;</span> <span class="nw">y&#61;&#40;0&#44;</span> <span class="nw">&#45;1&#41;&#44;</span> <span class="nw">z&#61;&#40;0&#44;</span> <span class="nw">&#45;1&#41;&#44;</span> <span class="nw">t&#61;&#40;0&#44;</span> <span class="nw">&#45;1&#41;&#41;</span></code> |  | zero outside a box given per axis as <code><span class="nw">&#40;first</span> <span class="nw">voxel&#44;</span> <span class="nw">size&#41;</span></code> in the file's voxel coordinates (<code><span class="nw">&#45;1</span></code>: to the end)<span class="opt-help">FSL: “zero outside roi (using voxel coordinates). Inputting -1 for a size will set it to the full image extent for that dimension.”</span> |
| <code><span class="nw">&#45;bptf</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;bandpass&#95;temporal&#95;filter&#40;image&#44;</span> <span class="nw">highpass&#95;sigma&#44;</span> <span class="nw">lowpass&#95;sigma&#41;</span></code> |  | temporal band-pass filtering, sigmas in volumes, a negative one skipping its filter (the high-pass removes the mean)<span class="opt-help">FSL: “(-t in ip.c) Bandpass temporal filtering; nonlinear highpass and Gaussian linear lowpass (with sigmas in volumes, not seconds); set either sigma&lt;0 to skip that filter”</span> |
| <code><span class="nw">&#45;tfce</span></code>, <code><span class="nw">&#45;tfce&#95;minT</span></code>, <code><span class="nw">&#45;tfce&#95;delta</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;tfce&#40;image&#44;</span> <span class="nw">h&#61;2&#46;0&#44;</span> <span class="nw">e&#61;0&#46;5&#44;</span> <span class="nw">connectivity&#61;6&#44;</span> <span class="nw">min&#95;t&#61;None&#44;</span> <span class="nw">delta&#61;None&#41;</span></code> |  | threshold-free cluster enhancement (the sum over the thresholds, as FSL's); <code><span class="nw">&#45;tfce&#95;minT</span></code> and <code><span class="nw">&#45;tfce&#95;delta</span></code> (hidden in FSL's usage) set the first threshold and the step (<code><span class="nw">specs&#47;fslmaths&#46;md</span></code> §14)<span class="opt-help">FSL: “enhance with TFCE, e.g. -tfce 2 0.5 6 (maybe change 6 to 26 for skeletons)”</span> |
| <code><span class="nw">&#45;tfceS</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;tfce&#95;support&#40;image&#44;</span> <span class="nw">voxel&#44;</span> <span class="nw">tfce&#95;threshold&#41;</span></code> |  | TFCE's support area at one voxel<span class="opt-help">FSL: “show support area for voxel (X,Y,Z)”</span> |
| <code><span class="nw">&#45;roc</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;roc&#40;image&#44;</span> <span class="nw">truth&#44;</span> <span class="nw">aroc&#95;threshold&#61;0&#46;05&#44;</span> <span class="nw">noise&#61;None&#41;</span></code> |  | the area under the ROC curve up to the false-positive limit (normalised by it), its quartiles over the volumes, the curve (false- and true-positive rates and thresholds)<span class="opt-help">FSL: “take (normally binary) truth and test current image in ROC analysis against truth. &lt;AROC-thresh&gt; is usually 0.05 and is limit of Area-under-ROC measure FP axis. &lt;outfile&gt; is a text file of the ROC curve (triplets of values: FP TP threshold). If the truth image contains negative voxels these get excluded from all calculations. If &lt;AROC-thresh&gt; is positive then the [4Dnoiseonly] option needs to be set, and the FP rate is determined from this noise-only data, and is set to be the fraction of timepoints where any FP (anywhere) is seen, as found in the noise-only 4d-dataset. This is then controlling the FWE rate. If &lt;AROC-thresh&gt; is negative the FP rate is calculated from the zero-value parts of the &lt;truth&gt; image, this time averaging voxelwise FP rate over all timepoints. In both cases the TP rate is the average fraction of truth=positive voxels correctly found.”</span> |
| <code><span class="nw">&#45;tensor&#95;decomp</span></code> | <code><span class="nw">operations</span></code>; <code><span class="nw">lx&#46;fsl&#46;tensor&#95;decomp&#40;image&#41;</span></code> |  | eigenvalues, FA, MD, mode and eigenvectors of a 6-volume tensor image<span class="opt-help">FSL: “convert a 4D (6-timepoint )tensor image into L1,2,3,FA,MD,MO,V1,2,3 (remaining image in pipeline is FA)”</span> |
| <code><span class="nw">&#45;save</span></code>, <code><span class="nw">&#45;restart</span></code> | <code><span class="nw">operations</span></code> |  | the current image written to the name that follows, or replaced by that image<span class="opt-help">FSL: “save the current working image to the input filename”</span><span class="opt-help">FSL: “replace the current image with input for future processing operations”</span> |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | command line only |  |  |
| <code><span class="nw">FSLOUTPUTTYPE</span></code> | the result |  | the output's format on the command line (<code><span class="nw">NIFTI&#95;GZ</span></code> when it is unset: FSL-11); the Python functions write NIfTI-1 and read it back |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects as FSL has them |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl fslmaths ...`) and are arguments of `lx.fsl.fslmaths`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all) for the in-memory images and the clean room's operations; the replica runs on one thread; the same results at any count. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects corrected, or FSL's behaviour (<code><span class="nw">docs&#47;api&#47;fsl&#45;maths&#46;md</span></code>, "Defects of the original, corrected by default"). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `t1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `bold.nii.gz` (a synthetic series of 4 such heads). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# fMRIPrep's goodvoxels mask, its first steps: -Tstd, -Tmean, then -div <image>
std = lx.fsl.collapse("bold.nii.gz", "std")
mean = lx.fsl.collapse("bold.nii.gz", "mean")
cov = lx.fsl.arithmetic(std, "divide", mean)
cov.shape  # -> (40, 48, 40)
# Any chain in fslmaths' own words: 1 above 10 % of the robust range, stored as bytes.
binary = lx.fsl.fslmaths("t1w.nii.gz", "-thrp", 10, "-bin", odt="char")
binary.data.dtype  # -> dtype('uint8')
```

```bash
larmorx fsl fslmaths bold.nii.gz -Tstd stdev
larmorx fsl fslmaths t1w.nii.gz -thr 100 -bin mask -odt char
larmorx fsl fslmaths t1w.nii.gz -kernel sphere 8 -fmean smoothed
```

## Ports {#ports}

`fslmaths` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-maths-replica](repo:docs/validation/fsl-maths-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-maths](repo:docs/validation/fsl-maths.md) |

Both ports take every operation of the usage text and the hidden ones (`-pow`, `-invbin`,
`-tfce_minT`, `-tfce_delta`) in every data type, every message, exit status and failure case of
FSL's, and correct FSL's defects ([Defects of the original](repo:docs/api/fsl-maths.md#defects-of-the-original-corrected-by-default)).

**The replica** against FSL 6.0.7.23 itself ([its record](repo:docs/validation/fsl-maths-replica.md),
the standard comparison, 2026-11-04): 360 of 361 compared cases bit-identical, the other one,
`fn/double-tan`, differing in the last place in 3 of its 210 double-precision values as glibc's
`tan` does (GLIBC-07); 61 more rejected by both alike. fMRIPrep's mask combination (`fslmaths <a>
-mul <b>`) bit-identical on three of fMRIPrep's runs (ds000005, ds005040 in two kinds, ds003592),
fMRIPrep's 14 goodvoxels calls bit-identical in their workflow's order on ds005040's BOLD series
(the ribbon a stand-in: the segmentation's grey matter, as the no-reconall runs have no
FreeSurfer ribbon), and every operation of the usage text (and the hidden ones) in every data
type, 3D and 4D, odd sizes and voxel sizes, the FFT path of the convolutions, every message, exit
status and failure case, each output compared with FSL's file by file (data and header).

**The clean room** against FSL 6.0.7.23 ([its record](repo:docs/validation/fsl-maths.md), the standard
comparison, 2026-11-07, `specs/fslmaths.md` §21's thresholds): 454 cases, 386 within the
thresholds, 63 rejected by both alike, 5 expected divergences, 0 failures. Of the 386, 370
identical to FSL's outputs (data, header, messages, exit status): fMRIPrep's mask combination on
its three runs and its 14 goodvoxels calls on ds005040 among them (the `-s 5` at 3 × 3 × 3.3 mm
too; the ribbon a stand-in, as for the replica); 3 of `-tensor_decomp` identical but for the
eigenvectors' signs (the clean room's own convention, compared up to the sign); 13 within the
thresholds: 11 sums (FSL's FFT path on four kernels, `-subsamp2` under the floating types, the
double `-ztop` and `-ranknorm`) at most 2.0e-7 of FSL's largest value, `fn/double-tan` one unit in
the last place in its double values (glibc's `tan`, GLIBC-07), one `-roc` area within its
threshold. The 5 expected divergences (FSL's single-precision FFT convolution against the clean
room's double sums on 3 kernels, `-subsamp2offc`'s means on 2 cases) stay inside the sums' bound
(at most 1.1e-7 of FSL's largest value) and miss only its share of voxels within 4 units in the
last place (spec questions 13 and 14), each with its reason in the record; on the FFT cases the
clean room lies closer to the exact result than FSL's FFT (findings 31). It is built for speed:
1.8 to 28 times faster than FSL on one thread, up to 268 times on 14
([the benchmarks](repo:docs/benchmarks/fsl-maths.md)).

FSL is distributed under the FSL Licence (non-commercial use only), so `fslmaths` has two ports,
a replica and a clean room, in different packages ([licensing](repo:docs/licensing.md)):

- **The replica** is bit-exact: `larmorx-nc fsl fslmaths`, in the package `larmorx-nc`
  (`crates-nc/larmorx-nc-avwutils`), under the FSL Licence's terms, translated from FSL's source
  with the image library's arithmetic, statistics, kernels, filters, FFT and probability
  functions in `larmorx-nc-core`.
- **The clean room** is in the main package (Apache-2.0, crate `larmorx-fsl`, its `maths`),
  written from [`specs/fslmaths.md`](repo:specs/fslmaths.md), FSL's documentation and black-box
  runs of FSL's program ([PROVENANCE](repo:crates/larmorx-fsl/PROVENANCE.md)).

`implementation="auto"` (the default) runs the replica when `larmorx-nc` is installed, the clean
room otherwise; `"replica"` needs `larmorx-nc` (otherwise `ReplicaNotFoundError`); `"clean-room"`
(`"original"`, 0.1.0rc1's spelling, still works) runs the clean room in this process on
`n_threads` threads (its results the same at any count). The command line chooses alike
(`--implementation` before the family, or `LARMORX_IMPLEMENTATION`).

## Evidence {#evidence}

How each of `fslmaths`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-maths/).

## More in the repository {#more}

The API page [docs/api/fsl-maths.md](repo:docs/api/fsl-maths.md) holds what `fslmaths` shares with the page's other programs:

- [The typed wrappers](repo:docs/api/fsl-maths.md#the-typed-wrappers)
- [Data types](repo:docs/api/fsl-maths.md#data-types)
- [Maths functions and GLIBC-07](repo:docs/api/fsl-maths.md#maths-functions-and-glibc-07)
- [File names on Windows](repo:docs/api/fsl-maths.md#file-names-on-windows)
- [The records](repo:docs/api/fsl-maths.md#the-records)
- [The clean room](repo:docs/api/fsl-maths.md#the-clean-room)
- [Defects of the original, corrected by default](repo:docs/api/fsl-maths.md#defects-of-the-original-corrected-by-default)
- [Not yet](repo:docs/api/fsl-maths.md#not-yet)
- [History](repo:docs/api/fsl-maths.md#history)
