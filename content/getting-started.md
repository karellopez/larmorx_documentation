---
title: Getting started
kicker: Documentation
lede: LARMORX installs with pip on Linux, macOS and Windows, with nothing else to install. This page shows how to install it and run its first programs on public data, and lists its three packages, what a computer needs, the standalone programs and the container images.
description: How to install LARMORX and run its first programs — with pip from PyPI (larmorx, larmorx[prep], larmorx[all]), as standalone programs from GitHub, or as a container image for Apptainer, Docker and Podman — a first session on public data, what each of its three packages holds and under which licence, what a computer needs, and how to check a download with SHA256SUMS.
---
{%- set v = "0.1.0rc1" %}

**The first release, {{ v }}, is a release candidate:** a pre-release, published to check that the packages install and work on every platform before 0.1.0. The programs on the [Programs](/programs/) page are complete and compared case by case with their originals ([how](/validation/)); the preprocessing pipeline `larmorprepx` is not ready yet (only its field-map stages exist), and FreeSurfer's programs are still to come ([roadmap](/roadmap/)). What the release holds, program by program: the [changelog](repo:CHANGELOG.md).

Nothing else is needed: no ANTs, AFNI, FSL or tedana installation, no compiler and no administrator rights.

## With pip {#pip}

```bash
pip install larmorx
```

installs the library and the commands `larmorx` and `lx`. Two extras add more:

- `pip install "larmorx[prep]"` adds what `larmorprepx` will need (not ready yet);
- `pip install "larmorx[all]"` adds `[prep]`, `larmorx-nc` and `larmorx-gpl`.

pip installs a pre-release by itself only while no final release exists; `pip install "larmorx=={{ v }}"` (or `pip install --pre larmorx`) asks for it by name. `[all]` installs the three packages at the same version. The quotation marks keep the square brackets from being read by the shell.

A virtual environment keeps LARMORX and the packages it needs apart from the rest of your Python. On Linux and macOS:

```bash
python3 -m venv larmorx-env
source larmorx-env/bin/activate
pip install larmorx
larmorx --version
```

The last line prints {{ v }}.

On Windows, in the Command Prompt:

```bat
python -m venv larmorx-env
larmorx-env\Scripts\activate
pip install larmorx
larmorx --version
```

In Python, `import larmorx as lx` gives the same programs (`lx.__version__` is the version). With `[all]`, `larmorx-nc --version` and `larmorx-gpl --version` print the same version. Examples of both ways of calling a program are on the [home page](/#features); each program's command, Python function and options are in the repository's [API pages](repo:docs/api/).

## First steps {#first-steps}

**Where pip puts the commands.** pip installs `larmorx`, `lx` and `larmorprepx` into the Python environment's folder of programs: `bin` on Linux and macOS, `Scripts` on Windows. For the virtual environment above that is `larmorx-env/bin` or `larmorx-env\Scripts`, and activating the environment puts it on the `PATH`, so the commands work by their names. Without a virtual environment, pip names the folder in a warning when it is not on the `PATH`; this prints it (in PowerShell, with `python` for `python3`):

```bash
python3 -c "import sysconfig; print(sysconfig.get_path('scripts'))"
```

After `pip install --user`, the folder is `sysconfig.get_path('scripts', sysconfig.get_preferred_scheme('user'))` instead. `python3 -m larmorx` (`python -m larmorx` on Windows), followed by the same arguments, runs the same command without the folder on the `PATH`.

**Three settings for every program.** In {{ v }} the command line takes them from environment variables, and Python takes the same values as arguments of its functions (`implementation` where a program has two ports; [Concepts](/concepts/#settings) says what each does):

- **Threads:** `OMP_NUM_THREADS` (ANTs' programs: `ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS`, or `NSLOTS`); in Python `n_threads`. The number of threads; without the variable the command line uses every logical CPU (Python's default is 1).
- **Port:** `LARMORX_IMPLEMENTATION`; in Python `implementation`. `auto` (the default) runs a program's replica when it is built in or installed, otherwise its clean room; `replica` the replica; `original` the clean room (`clean-room` from the next release).
- **Upstream defects:** `LARMORX_UPSTREAM_DEFECTS`; in Python `upstream_defects`. `fix` (the default) corrects the original program's known defects, each with a notice (below); `reproduce` gives the original program's result.

In bash and zsh, `NAME=value` before a command sets a variable for that command only, and `export NAME=value` for the rest of the session; in PowerShell, `$env:NAME = "value"` sets it for the session and `Remove-Item Env:NAME` removes it.

**Coming with the next release** (already in the repository's `main`, [First steps](repo:README.md#first-steps) in its README): the same three settings as options between `larmorx` and the family, with the Python arguments' names, `larmorx --n-threads 4 --implementation clean-room --upstream-defects reproduce <family> <program> ...`, each winning over its variable; and `clean-room` as the name of the clean room, where {{ v }} says `original` (which keeps working). The replica programs `larmorx-nc` and `larmorx-gpl` take `--n-threads` and `--upstream-defects` the same way.

**An example, start to end**, on one participant of the public OpenNeuro dataset [ds000005](https://openneuro.org/datasets/ds000005) (public domain, PDDL; 21 MB): a new virtual environment, the two images downloaded, then ANTs' bias-field correction on four threads, FSL's brain extraction, head-motion correction and registration, and AFNI's brain mask computed by the replica (the default) and by the clean room. FSL's programs need `FSLOUTPUTTYPE`, as FSL's own do (`NIFTI_GZ`: they write `.nii.gz` files). The last command gives the original N4's result instead of the corrected one. On Linux and macOS (bash or zsh), with Python 3.12 or newer as `python3` (macOS's own `python3` is older: install one from [python.org](https://www.python.org) or Homebrew):

```bash
python3 -m venv larmorx-env
source larmorx-env/bin/activate
pip install larmorx
mkdir larmorx-demo
cd larmorx-demo
curl -L -o t1w.nii.gz https://s3.amazonaws.com/openneuro.org/ds000005/sub-01/anat/sub-01_T1w.nii.gz
curl -L -o bold.nii.gz https://s3.amazonaws.com/openneuro.org/ds000005/sub-01/func/sub-01_task-mixedgamblestask_run-01_bold.nii.gz
export FSLOUTPUTTYPE=NIFTI_GZ
ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=4 larmorx ants N4BiasFieldCorrection -d 3 -i t1w.nii.gz -o t1w_n4.nii.gz
larmorx fsl bet t1w_n4.nii.gz t1w_brain -R -m
larmorx fsl mcflirt -in bold.nii.gz -out bold_mcf -plots
larmorx fsl fslmaths bold_mcf -Tmean bold_mean
larmorx afni 3dAutomask -prefix bold_mask.nii.gz bold_mean.nii.gz
LARMORX_IMPLEMENTATION=original larmorx afni 3dAutomask -prefix bold_mask_clean_room.nii.gz bold_mean.nii.gz
larmorx fsl fslmaths bold_mean -mas bold_mask bold_brain
larmorx fsl flirt -in bold_brain -ref t1w_brain -dof 6 -omat bold2t1w.mat -out bold2t1w
LARMORX_UPSTREAM_DEFECTS=reproduce larmorx ants N4BiasFieldCorrection -d 3 -i t1w.nii.gz -o t1w_n4_ants.nii.gz
```

On Windows, in PowerShell, with Python 3.12 or newer as `python` (python.org's installer puts it on the `PATH` when "Add python.exe to PATH" is ticked; otherwise write `py` for `python` in the first line):

```powershell
python -m venv larmorx-env
larmorx-env\Scripts\Activate.ps1
pip install larmorx
mkdir larmorx-demo
cd larmorx-demo
curl.exe -L -o t1w.nii.gz https://s3.amazonaws.com/openneuro.org/ds000005/sub-01/anat/sub-01_T1w.nii.gz
curl.exe -L -o bold.nii.gz https://s3.amazonaws.com/openneuro.org/ds000005/sub-01/func/sub-01_task-mixedgamblestask_run-01_bold.nii.gz
$env:FSLOUTPUTTYPE = "NIFTI_GZ"
$env:ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS = "4"
larmorx ants N4BiasFieldCorrection -d 3 -i t1w.nii.gz -o t1w_n4.nii.gz
larmorx fsl bet t1w_n4.nii.gz t1w_brain -R -m
larmorx fsl mcflirt -in bold.nii.gz -out bold_mcf -plots
larmorx fsl fslmaths bold_mcf -Tmean bold_mean
larmorx afni 3dAutomask -prefix bold_mask.nii.gz bold_mean.nii.gz
$env:LARMORX_IMPLEMENTATION = "original"
larmorx afni 3dAutomask -prefix bold_mask_clean_room.nii.gz bold_mean.nii.gz
Remove-Item Env:LARMORX_IMPLEMENTATION
larmorx fsl fslmaths bold_mean -mas bold_mask bold_brain
larmorx fsl flirt -in bold_brain -ref t1w_brain -dof 6 -omat bold2t1w.mat -out bold2t1w
$env:LARMORX_UPSTREAM_DEFECTS = "reproduce"
larmorx ants N4BiasFieldCorrection -d 3 -i t1w.nii.gz -o t1w_n4_ants.nii.gz
Remove-Item Env:LARMORX_UPSTREAM_DEFECTS
```

If PowerShell refuses `Activate.ps1` because running scripts is disabled on the computer, `Set-ExecutionPolicy -Scope Process RemoteSigned` allows it in that window only. Each command writes its results into `larmorx-demo`; `deactivate` leaves the virtual environment.

**What the `upstream defect ... corrected` lines mean.** Some commands print a notice such as

```text
larmorx: upstream defect ANTS-40 (N4BiasFieldCorrection) corrected: 6208 of the 92160 voxels N4 uses have no logarithm (6208 are 0, 0 negative or NaN): they are left out of the histogram and the fit; ITK keeps them in its log image as they are (0 is the log of 1) [LARMORX_UPSTREAM_DEFECTS=reproduce gives N4BiasFieldCorrection's result]
```

It is not an error (the command still ends with exit status 0). It says that a known defect of the original program (here ANTs' N4) would have changed this result, and that LARMORX computed the corrected result, as it does by default. The code (`ANTS-40`) is the defect's entry in the repository's [register](repo:docs/findings/upstream-defects.md); the [upstream defects](repo:docs/api/upstream-defects.md) page explains the rules. To get the original program's result, bit for bit, set `LARMORX_UPSTREAM_DEFECTS=reproduce`, as the notice says (`upstream_defects="reproduce"` in Python); the notice then says `reproduced`. The replica programs' notices start with `larmorx-nc:` or `larmorx-gpl:`, and AFNI's programs print theirs as AFNI's warnings (`*+ WARNING: upstream defect AFNI-99 (3dvolreg) corrected: ...`).

## The three packages and their licences {#packages}

LARMORX is published as three packages, one for each family of licences, so that each licence stays with the code it covers ([in full on Concepts](/concepts/#packages)):

- **`larmorx`**: every program on the [Programs](/programs/) page but FSL's and tedana's replicas; [Apache-2.0](repo:LICENSE), any use, commercial use included. Its [NOTICE](repo:NOTICE) lists the works it includes.
- **`larmorx-nc`**: the replicas of FSL's programs; the [FSL Licence](repo:crates-nc/LICENSE), **non-commercial use only**.
- **`larmorx-gpl`**: the replica of tedana's `t2smap`; the [GNU GPL version 3](repo:crates-gpl/LICENSE).

The two replica packages are installed only when you ask for them by name (`pip install larmorx-nc`) or through `[all]`. Every work LARMORX includes and its licence: the repository's [licensing notes](repo:docs/licensing.md).

## What your computer needs {#requirements}

The packages on PyPI are built in advance for six platforms (as wheels), so pip only downloads and unpacks them:

- **Python** 3.12 or newer (CPython; one wheel serves every version from 3.12 on; tested on 3.12 on every platform, and on 3.13 and 3.14 on Linux). The free-threaded builds of Python are not supported.
- **Linux**, x86-64 and aarch64, with glibc 2.28 or newer (`manylinux_2_28`: for example RHEL 8, Debian 10, Ubuntu 20.04 and later). There are no wheels for musl-based systems such as Alpine Linux: use a [container image](#containers) there.
- **macOS 11** or newer, Intel and Apple silicon. On Apple silicon, `[prep]` and `[all]` need macOS 12, as SciPy's and scikit-learn's wheels do.
- **Windows** 10 and 11, x64 and arm64. Visual C++'s runtime is built in: nothing to install.

Where no wheel fits, or with `pip install --no-binary larmorx larmorx`, pip builds LARMORX from its source distribution. That needs a C compiler (gcc or clang; Microsoft's C++ build tools on Windows) and Rust 1.99 or newer, which maturin downloads by itself when none is installed.

## Standalone programs {#programs}

Each [release on GitHub](https://github.com/karellopez/larmorx/releases) also has the command-line programs as archives that need no Python: `larmorx` (with its short name `lx`), `larmorx-nc` and `larmorx-gpl`, for each platform, each with its licences (`larmorx-nc`'s with FSL's original and amended source, as its licence requires). The two programs written in Python, `larmorx sdcflows` and `larmorprepx`, need the Python package.

| Your computer | The archive |
|---|---|
| Linux, x86-64 | `larmorx-{{ v }}-x86_64-unknown-linux-gnu.tar.gz` |
| Linux, aarch64 | `larmorx-{{ v }}-aarch64-unknown-linux-gnu.tar.gz` |
| macOS, Apple silicon | `larmorx-{{ v }}-aarch64-apple-darwin.tar.gz` |
| macOS, Intel | `larmorx-{{ v }}-x86_64-apple-darwin.tar.gz` |
| Windows, x64 | `larmorx-{{ v }}-x86_64-pc-windows-msvc.zip` |
| Windows, arm64 | `larmorx-{{ v }}-aarch64-pc-windows-msvc.zip` |

The archives of `larmorx-nc` and `larmorx-gpl` are named the same way (`larmorx-nc-{{ v }}-…`, `larmorx-gpl-{{ v }}-…`). Each unpacks into a folder of its own name, with the program in `bin/`, its licences beside it and a `README.txt`. On Linux and macOS, with `t` set to your computer's ending from the table (here Linux on x86-64):

```bash
v={{ v }}
t=x86_64-unknown-linux-gnu
curl -LO https://github.com/karellopez/larmorx/releases/download/v$v/larmorx-$v-$t.tar.gz
tar -xzf larmorx-$v-$t.tar.gz
larmorx-$v-$t/bin/larmorx --version
```

On Windows, in PowerShell, after downloading the archive:

```powershell
Expand-Archive larmorx-{{ v }}-x86_64-pc-windows-msvc.zip -DestinationPath .
.\larmorx-{{ v }}-x86_64-pc-windows-msvc\bin\larmorx.exe --version
```

To call the program by its name from anywhere, add its `bin` folder to your `PATH`. The programs are not signed by Apple or Microsoft, so macOS or Windows may refuse to start one that a web browser downloaded; after [checking the file](#check), removing the download mark lets it run (on macOS `xattr -d com.apple.quarantine <archive>` before unpacking; on Windows `Unblock-File <archive>` in PowerShell). A file downloaded with `curl` carries no such mark.

## Container images {#containers}

For Linux machines and computing clusters, each release also has two container images, for linux/amd64 and linux/arm64, usable by Apptainer, Docker and Podman:

- **`ghcr.io/karellopez/larmorx:{{ v }}`**: `larmorx` with `[prep]`, without the replica packages; commercial use allowed.
- **`ghcr.io/karellopez/larmorx:{{ v }}-all`**: also `larmorx-gpl` and `larmorx-nc`; non-commercial use only (the FSL Licence).

`latest` and `latest-all` name the newest final release (never a release candidate such as {{ v }}). With Apptainer:

```bash
apptainer pull docker://ghcr.io/karellopez/larmorx:{{ v }}
apptainer exec larmorx_{{ v }}.sif larmorx --version
```

With Docker (Podman takes the same arguments), the current folder mounted as `/data`:

```bash
docker run --rm -v "$PWD:/data" -w /data ghcr.io/karellopez/larmorx:{{ v }} \
    larmorx ants N4BiasFieldCorrection -d 3 -i t1w.nii.gz -o t1w_n4.nii.gz
```

Under Apptainer the image runs as you, with your home directory, where TemplateFlow keeps the templates it downloads on first use (`$HOME/.cache/templateflow`). Docker runs it as root, so mount a volume at `/root/.cache/templateflow` (or set `TEMPLATEFLOW_HOME` to a mounted folder) to keep them. `/opt/larmorx/README.txt` in the image says what it holds and where its licences and sources are.

## Check a download {#check}

pip checks every file it downloads from PyPI against PyPI's own SHA-256 by itself. For the files of a GitHub release, the release's `SHA256SUMS` holds the SHA-256 of every file. Download it into the folder that holds your files; then, on Linux:

```bash
sha256sum -c --ignore-missing SHA256SUMS
```

on macOS:

```bash
shasum -a 256 -c --ignore-missing SHA256SUMS
```

Each file you have is listed with `OK`; a different word means that the file is damaged or is not the release's file. On Windows, in PowerShell, for one file (`True` when it is the release's file):

```powershell
$f = "larmorx-{{ v }}-x86_64-pc-windows-msvc.zip"
$sum = (Select-String -Path SHA256SUMS -SimpleMatch "  $f").Line.Split(" ")[0]
(Get-FileHash $f).Hash -eq $sum
```

Every file and both images also carry GitHub's record of the build that made them (an attestation), which GitHub's command-line program [`gh`](https://cli.github.com/) checks, for a file and for an image:

```bash
gh attestation verify <file> --repo karellopez/larmorx
gh attestation verify oci://ghcr.io/karellopez/larmorx:{{ v }} --repo karellopez/larmorx
```

PyPI shows its own attestations on each file's page.

## Updating and removing {#updating}

`pip install --upgrade larmorx` (or `pip install --upgrade "larmorx[all]"`, which keeps the three packages at one version) takes the newest release. `pip uninstall larmorx larmorx-nc larmorx-gpl`, or deleting the virtual environment's folder, removes the packages; the standalone programs go with their folder, an image with its `.sif` file or `docker image rm`. Files a program downloaded on first use, such as TemplateFlow's templates, stay in their cache folder.
