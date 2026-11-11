---
title: Installation
kicker: Documentation
lede: LARMORX installs with pip on Linux, macOS and Windows, with nothing else to install. Standalone programs and container images are there for those who prefer them.
description: How to install LARMORX — with pip from PyPI (larmorx, larmorx[prep], larmorx[all]), as standalone programs from GitHub, or as a container image for Apptainer, Docker and Podman — what each of its three packages holds and under which licence, what a computer needs, and how to check a download with SHA256SUMS.
---
{%- set v = "0.1.0rc1" %}

**The first release, {{ v }}, is a release candidate:** a pre-release, published to check that the packages install and work on every platform before 0.1.0. The tools on the [Tools](/tools/) page are complete and compared case by case with the original programs ([how](/validation/)); the preprocessing pipeline `larmorprepx` is not ready yet (only its field-map stages exist), and FreeSurfer's tools are still to come ([roadmap](/roadmap/)). What the release holds, tool by tool: the [changelog](repo:CHANGELOG.md).

Nothing else is needed: no ANTs, AFNI, FSL or tedana installation, no compiler and no administrator rights.

## With pip {#pip}

```bash
pip install larmorx              # the library and the larmorx / lx commands (Apache-2.0)
pip install "larmorx[prep]"      # + what the larmorprepx pipeline will need (not ready yet)
pip install "larmorx[all]"       # + [prep] and the replica packages larmorx-nc and larmorx-gpl
```

pip installs a pre-release by itself only while no final release exists; `pip install "larmorx=={{ v }}"` (or `pip install --pre larmorx`) asks for it by name. `[all]` installs the three packages at the same version. The quotation marks keep the square brackets from being read by the shell.

A virtual environment keeps LARMORX and the packages it needs apart from the rest of your Python. On Linux and macOS:

```bash
python3 -m venv larmorx-env
source larmorx-env/bin/activate
pip install larmorx
larmorx --version                # prints {{ v }}
```

On Windows, in the Command Prompt:

```bat
python -m venv larmorx-env
larmorx-env\Scripts\activate
pip install larmorx
larmorx --version
```

In Python, `import larmorx as lx` gives the same tools (`lx.__version__` is the version). With `[all]`, `larmorx-nc --version` and `larmorx-gpl --version` print the same version. Examples of both ways of calling a tool are on the [home page](/#features); each tool's command, Python function and options are in the repository's [API pages](repo:docs/api/).

## The three packages and their licences {#packages}

LARMORX is published as three packages, one for each family of licences, so that each licence stays with the code it covers:

| Package | What it holds | Its licence, in plain words |
|---|---|---|
| `larmorx` | every tool on the [Tools](/tools/) page: the ports, the clean-room originals and the AFNI replicas | [Apache-2.0](repo:LICENSE): any use, commercial use included; keep the licence and the notices. The works it includes and their licences, permissive ones and the Mozilla Public License 2.0 for routines translated from Eigen (whose source stays public), are listed in its [NOTICE](repo:NOTICE). |
| `larmorx-nc` | the exact replicas of FSL's tools | the [FSL Licence](repo:crates-nc/LICENSE): **non-commercial use only**. Once it is installed, the FSL tools' default (`implementation="auto"`) runs these replicas, so FSL's terms then cover your default results; `implementation="original"` (or `LARMORX_IMPLEMENTATION=original` on the command line) runs LARMORX's own clean-room originals instead. |
| `larmorx-gpl` | the exact replica of tedana's `t2smap` | the [GNU GPL version 3](repo:crates-gpl/LICENSE): any use; whoever passes it on, changed or not, must pass on its source under the same licence. |

The two replica packages are separate programs (`larmorx-nc`, `larmorx-gpl`) that `larmorx` runs as separate processes, so their licences stay with them; each is installed only when you ask for it by name (`pip install larmorx-nc`) or through `[all]`. Which implementations each tool has, and how they differ, is on its page; why there are two kinds is explained under [What LARMORX is](/#what-it-is) and in the repository's [licensing notes](repo:docs/licensing.md).

## What your computer needs {#requirements}

The packages on PyPI are built in advance for six platforms (as wheels), so pip only downloads and unpacks them:

- **Python** 3.12 or newer (CPython; one wheel serves every version from 3.12 on; tested on 3.12 on every platform, and on 3.13 and 3.14 on Linux). The free-threaded builds of Python are not supported.
- **Linux**, x86-64 and aarch64, with glibc 2.28 or newer (`manylinux_2_28`: for example RHEL 8, Debian 10, Ubuntu 20.04 and later). There are no wheels for musl-based systems such as Alpine Linux: use a [container image](#containers) there.
- **macOS 11** or newer, Intel and Apple silicon. On Apple silicon, `[prep]` and `[all]` need macOS 12, as SciPy's and scikit-learn's wheels do.
- **Windows** 10 and 11, x64 and arm64. Visual C++'s runtime is built in: nothing to install.

Where no wheel fits, or with `pip install --no-binary larmorx larmorx`, pip builds LARMORX from its source distribution. That needs a C compiler (gcc or clang; Microsoft's C++ build tools on Windows) and Rust 1.99 or newer, which maturin downloads by itself when none is installed.

## Standalone programs {#programs}

Each [release on GitHub](https://github.com/karellopez/larmorx/releases) also has the command-line programs as archives that need no Python: `larmorx` (with its short name `lx`), `larmorx-nc` and `larmorx-gpl`, for each platform, each with its licences (`larmorx-nc`'s with FSL's original and amended source, as its licence requires). The two tools written in Python, `larmorx sdcflows` and `larmorprepx`, need the Python package.

| Your computer | The archive |
|---|---|
| Linux, x86-64 | `larmorx-{{ v }}-x86_64-unknown-linux-gnu.tar.gz` |
| Linux, aarch64 | `larmorx-{{ v }}-aarch64-unknown-linux-gnu.tar.gz` |
| macOS, Apple silicon | `larmorx-{{ v }}-aarch64-apple-darwin.tar.gz` |
| macOS, Intel | `larmorx-{{ v }}-x86_64-apple-darwin.tar.gz` |
| Windows, x64 | `larmorx-{{ v }}-x86_64-pc-windows-msvc.zip` |
| Windows, arm64 | `larmorx-{{ v }}-aarch64-pc-windows-msvc.zip` |

The archives of `larmorx-nc` and `larmorx-gpl` are named the same way (`larmorx-nc-{{ v }}-…`, `larmorx-gpl-{{ v }}-…`). Each unpacks into a folder of its own name, with the program in `bin/`, its licences beside it and a `README.txt`. On Linux and macOS (here for Linux on x86-64):

```bash
curl -LO https://github.com/karellopez/larmorx/releases/download/v{{ v }}/larmorx-{{ v }}-x86_64-unknown-linux-gnu.tar.gz
tar -xzf larmorx-{{ v }}-x86_64-unknown-linux-gnu.tar.gz
larmorx-{{ v }}-x86_64-unknown-linux-gnu/bin/larmorx --version
```

On Windows, in PowerShell, after downloading the archive:

```powershell
Expand-Archive larmorx-{{ v }}-x86_64-pc-windows-msvc.zip -DestinationPath .
.\larmorx-{{ v }}-x86_64-pc-windows-msvc\bin\larmorx.exe --version
```

To call the program by its name from anywhere, add its `bin` folder to your `PATH`. The programs are not signed by Apple or Microsoft, so macOS or Windows may refuse to start one that a web browser downloaded; after [checking the file](#check), removing the download mark lets it run (on macOS `xattr -d com.apple.quarantine <archive>` before unpacking; on Windows `Unblock-File <archive>` in PowerShell). A file downloaded with `curl` carries no such mark.

## Container images {#containers}

For Linux machines and computing clusters, each release also has two container images, for linux/amd64 and linux/arm64, usable by Apptainer, Docker and Podman:

| Image | What it holds | Its licence |
|---|---|---|
| `ghcr.io/karellopez/larmorx:{{ v }}` | `larmorx` with `[prep]`, without the replica packages | commercial use allowed |
| `ghcr.io/karellopez/larmorx:{{ v }}-all` | also `larmorx-gpl` and `larmorx-nc` | non-commercial use only (the FSL Licence) |

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
(Get-FileHash $f).Hash -eq (Select-String -Path SHA256SUMS -SimpleMatch "  $f").Line.Split(" ")[0]
```

Every file and both images also carry GitHub's record of the build that made them (an attestation), which GitHub's command-line program [`gh`](https://cli.github.com/) checks: `gh attestation verify <file> --repo karellopez/larmorx`, or for an image `gh attestation verify oci://ghcr.io/karellopez/larmorx:{{ v }} --repo karellopez/larmorx`. PyPI shows its own attestations on each file's page.

## Updating and removing {#updating}

`pip install --upgrade larmorx` (or `pip install --upgrade "larmorx[all]"`, which keeps the three packages at one version) takes the newest release. `pip uninstall larmorx larmorx-nc larmorx-gpl`, or deleting the virtual environment's folder, removes the packages; the standalone programs go with their folder, an image with its `.sif` file or `docker image rm`. Files a tool downloaded on first use, such as TemplateFlow's templates, stay in their cache folder.
