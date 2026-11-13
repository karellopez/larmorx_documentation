---
title: "`standard_space_roi`"
kicker: "Programs · FSL"
lede: "`standard_space_roi` is a script that masks an image or cuts it down with a region of a standard space."
description: "LARMORX reference for FSL 6.0.7.23 `standard_space_roi`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl standard_space_roi"
  python: "lx.fsl.standard_space_roi"
  api: "docs/api/fsl-roi.md"
  evidence: "/evidence/fsl-bet/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "validated"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "24c23485c8957683"
    crates/larmorx-fsl/src/cli/ssroi.rs: "6e47240580da4547"
    docs/api/fsl-roi.md: "eaded1db765eeabc"
    python/larmorx/fsl/regions.py: "8b0848530989c81c"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

It registers the input to a standard-space reference with FLIRT (`MNI152_T1_2mm` unless
`-ssref` gives another), takes the reference's field of view (less its outer voxel) or a
standard-space mask back into the input's space with the inverse matrix, and masks the input with
it and/or cuts the input down to its bounding box. `bet -S` and `bet -B` run it (`-b -d`,
`-maskFOV -roiNONE -d`).

## Command line {#command-line}

```text synopsis
larmorx fsl standard_space_roi <input> <output> [options] [flirt options]
```

Everything after `larmorx fsl standard_space_roi` is the original's command line: the arguments of FSL 6.0.7.23's `standard_space_roi`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl standard_space_roi ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>standard_space_roi</code>'s usage text, as the clean room prints it</summary>

```text
Usage: standard_space_roi <input> <output> [options] [flirt options]

This masks the input and/or reduces its FOV, on the basis of a
standard space image or mask, that is transformed into the space
of the input image.

Masking options (applied before FOV-reduction):
  -maskFOV           : mask output using transformed standard space FOV (default)
  -maskMASK <mask>   : mask output using transformed standard space mask
  -maskNONE          : do not mask output

FOV-reduction options:
  -roiFOV            : cut down input FOV using bounding box of the transformed standard space FOV (default)
  -roiMASK <mask>    : cut down input FOV using nonbackground bounding box of the transformed standard space mask
  -roiNONE           : do not cut down input FOV

With either MASK option, <mask> must be in the same space as the standard space reference image.

Other options:
  -ssref <ref_image> : standard space reference image to use (default ${FSLDIR}/data/standard/MNI152_T1)
  -altinput <image>  : alternative input image to apply the ROI to (instead of the one used to register to the reference)
  -d                 : debug (don't delete intermediate files)
  -b                 : betpremask, equivalent to: -maskMASK ${FSLDIR}/data/standard/MNI152_T1_2mm_brain_mask_dil -roiNONE

All above options must come before any flirt options.
```

</details>

## Python {#python}

```python
lx.fsl.standard_space_roi(
    image: Any,
    *,
    mask: Literal["fov", "none"] | Any = None,
    roi: Literal["fov", "none"] | Any = None,
    reference: Any = None,
    alt_input: Any = None,
    betpremask: bool = False,
    flirt_args: list[str] | None = None,
    fsl_data: str | os.PathLike | None = None,
    n_threads: int = 1,
    implementation: ImplementationName = "auto",
    upstream_defects: UpstreamDefectsName = "fix",
) -> StandardSpaceRoiResult
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`); `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

FLIRT's `standard_space_roi`: `image` registered to the standard-space `reference` (FSL's `MNI152_T1_2mm` when not given), then masked (`mask`: `"fov"` the reference's field of view less its outer voxel, a standard-space mask image, or `"none"`) and cut down (`roi`: the bounding box of `"fov"`, of a standard-space mask, or `"none"`), both taken into the image's space; `None` is the script's default (`"fov"`, or `betpremask`'s). `alt_input` is masked and cut instead of `image`; `betpremask` is `-b` (the dilated MNI152 brain mask, thresholded at 0.5, and no cut), given before `mask` and `roi`; `flirt_args` go to the first FLIRT run; `fsl_data` is the directory of FSL's standard images (`docs/api/fsl-roi.md`, "FSL's standard images").

The images are paths or `lx.Image` objects.

Its result, `StandardSpaceRoiResult`, holds `standard_space_roi`'s output image, and FLIRT's matrices between the input and the standard space (`to_standard`: input to reference, FSL's `<out>_tmp_to_std.mat`; `from_standard` its inverse).

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">image</span></code> | <code><span class="nw">Image</span></code> |  |
| <code><span class="nw">to&#95;standard</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">from&#95;standard</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `standard_space_roi` accepts (`crates/larmorx-fsl/src/cli/ssroi.rs`) and the arguments of `lx.fsl.standard_space_roi` (`python/larmorx/fsl/regions.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">standard&#95;space&#95;roi</span></code> option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#60;input&#62;</span></code> <code><span class="nw">&#60;output&#62;</span></code> | <code><span class="nw">image</span></code>, the result |  |  |
| <code><span class="nw">&#45;maskFOV</span></code>, <code><span class="nw">&#45;maskMASK</span> <span class="nw">&#60;mask&#62;</span></code>, <code><span class="nw">&#45;maskNONE</span></code> | <code><span class="nw">mask&#61;&#34;fov&#34;</span></code>, <code><span class="nw">mask&#61;&#60;image&#62;</span></code>, <code><span class="nw">mask&#61;&#34;none&#34;</span></code> | <code><span class="nw">mask&#61;None</span></code>, <code><span class="nw">mask&#61;None</span></code>, <code><span class="nw">mask&#61;None</span></code> | <code><span class="nw">None</span></code>: the script's default<span class="opt-help">FSL: “mask output using transformed standard space FOV (default)”</span><span class="opt-help">FSL: “mask output using transformed standard space mask”</span><span class="opt-help">FSL: “do not mask output”</span> |
| <code><span class="nw">&#45;roiFOV</span></code>, <code><span class="nw">&#45;roiMASK</span> <span class="nw">&#60;mask&#62;</span></code>, <code><span class="nw">&#45;roiNONE</span></code> | <code><span class="nw">roi&#61;&#34;fov&#34;</span></code>, <code><span class="nw">roi&#61;&#60;image&#62;</span></code>, <code><span class="nw">roi&#61;&#34;none&#34;</span></code> | <code><span class="nw">roi&#61;None</span></code>, <code><span class="nw">roi&#61;None</span></code>, <code><span class="nw">roi&#61;None</span></code> | <span class="opt-help">FSL: “cut down input FOV using bounding box of the transformed standard space FOV (default)”</span><span class="opt-help">FSL: “cut down input FOV using nonbackground bounding box of the transformed standard space mask”</span><span class="opt-help">FSL: “do not cut down input FOV”</span> |
| <code><span class="nw">&#45;ssref</span> <span class="nw">&#60;ref&#62;</span></code> | <code><span class="nw">reference</span></code> | <code><span class="nw">None</span></code> | <span class="opt-help">FSL: “standard space reference image to use (default ${FSLDIR}/data/standard/MNI152_T1)”</span> |
| <code><span class="nw">&#45;altinput</span> <span class="nw">&#60;image&#62;</span></code> | <code><span class="nw">alt&#95;input</span></code> | <code><span class="nw">None</span></code> | <span class="opt-help">FSL: “alternative input image to apply the ROI to (instead of the one used to register to the reference)”</span> |
| <code><span class="nw">&#45;b</span></code> | <code><span class="nw">betpremask&#61;True</span></code> | <code><span class="nw">False</span></code> | given before <code><span class="nw">mask</span></code> and <code><span class="nw">roi</span></code><span class="opt-help">FSL: “betpremask, equivalent to: -maskMASK ${FSLDIR}/data/standard/MNI152_T1_2mm_brain_mask_dil -roiNONE”</span> |
| <code><span class="nw">&#45;d</span></code> | always |  | the matrices are returned: <code><span class="nw">to&#95;standard</span></code>, <code><span class="nw">from&#95;standard</span></code><span class="opt-help">FSL: “debug (don't delete intermediate files)”</span> |
| FLIRT's options after the script's | <code><span class="nw">flirt&#95;args&#61;&#91;&#46;&#46;&#46;&#93;</span></code> | <code><span class="nw">None</span></code> |  |
| <code><span class="nw">LARMORX&#95;FSL&#95;DATA</span></code> | <code><span class="nw">fsl&#95;data</span></code> | <code><span class="nw">None</span></code> | where [FSL's standard images](repo:docs/api/fsl-roi.md#fsls-standard-images) are |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl standard_space_roi ...`) and are arguments of `lx.fsl.standard_space_roi`. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Threads (0 = all), given to the program as <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> and to the reading and writing of images; the result does not depend on it. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> (default) or <code><span class="nw">&#34;reproduce&#34;</span></code>: FSL's defects corrected, or FSL's behaviour (<code><span class="nw">docs&#47;api&#47;fsl&#45;roi&#46;md</span></code>, "Defects of the original, corrected by default"). The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `T1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `std.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

r = lx.fsl.standard_space_roi("T1w.nii.gz", reference="std.nii.gz")
r.to_standard.shape  # -> (4, 4)
```

```bash
larmorx fsl standard_space_roi T1w.nii.gz T1w_roi -ssref std.nii.gz
```

## Ports {#ports}

`standard_space_roi` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | validated | [fsl-bet-replica](repo:docs/validation/fsl-bet-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-bet](repo:docs/validation/fsl-bet.md) |

Both ports are complete. FSL's defects are corrected by default, and `reproduce` gives FSL's
behaviour: **FSL-11**, and **FSL-211** to **FSL-214** (the script's names, cleanup, `maskthr` and
failures). The clean room converts an input of another file type than `FSLOUTPUTTYPE` as fslpy's
`imcp` does with nibabel (the same header and data in the output's file layout and compression: a
`.nii.gz` input becomes FSL's `.nii` byte for byte, the record's `ssroi/phantom-none-convert`);
the replica refuses that case clearly (exit 1) in both modes. The clean room is built for speed:
the registration to the reference is almost all of `standard_space_roi`'s time; besides it,
without `-d` the temporary images are written uncompressed (they are removed at the end), and
when the field of view is both the mask and the region it is resampled into the input's space
once.

Both records are BET's, as these programs came with BET's options. The replica's holds 25 cases
of `standard_space_roi`: 16 identical to FSL, 8 where both refuse alike, and the conversion the
replica refuses. The clean room's holds 25: 17 within its thresholds, 8 refused alike. Its
`standard_space_roi` is FSL's bit for bit where its FLIRT gives FSL's matrix (an adult's T1w, a
Philips T1w and a T2w with the defaults); elsewhere its matrices are within FLIRT's 12-dof
threshold and, given FSL's matrix, every file is FSL's
([findings](repo:docs/findings/fsl-bet-clean-room.md), "standard_space_roi and fslroi").

FSL is distributed under the FSL Licence (non-commercial use only), so each program has two
ports, a replica and a clean room, in different packages ([licensing](repo:docs/licensing.md)):

- **The clean room** (`crates/larmorx-fsl`, `larmorx_fsl::cli::fslroi` and `::ssroi`, Apache-2.0)
  is written from [`specs/standard_space_roi.md`](repo:specs/standard_space_roi.md), FSL's
  documentation and black-box runs of FSL 6.0.7.23 ([PROVENANCE](repo:crates/larmorx-fsl/PROVENANCE.md)),
  and runs in this process. Its `standard_space_roi` runs the clean room's own FLIRT,
  `convert_xfm`, `fslmaths`, `fslstats` and `fslroi`, and fslpy's `imcp`, in the same process: no
  FSL installation is needed.
- **The replica** is bit-exact: `larmorx-nc fsl fslroi` and `larmorx-nc fsl standard_space_roi`,
  in the package `larmorx-nc` (`crates-nc/`), under the FSL Licence's terms. It runs every program
  in the replica's own process.

`implementation="auto"` runs the replica when its program is found, else the clean room;
`"clean-room"` (`"original"`, 0.1.0rc1's spelling, still works) and `"replica"` choose. The
command line follows `--implementation` (before the family) or `LARMORX_IMPLEMENTATION` the same
way.

## Evidence {#evidence}

How each of `standard_space_roi`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-bet/).

## More in the repository {#more}

The API page [docs/api/fsl-roi.md](repo:docs/api/fsl-roi.md) holds what `standard_space_roi` shares with the page's other programs:

- [FSL's standard images](repo:docs/api/fsl-roi.md#fsls-standard-images)
- [Defects of the original, corrected by default](repo:docs/api/fsl-roi.md#defects-of-the-original-corrected-by-default)
- [History](repo:docs/api/fsl-roi.md#history)
