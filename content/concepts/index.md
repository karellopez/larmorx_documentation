---
title: Concepts
kicker: Documentation
lede: The words this site uses for what LARMORX holds (original, port, replica, clean room), its three packages and their licences, the three settings LARMORX adds to the original's arguments, and why clean rooms exist and how the clean-room audit checks that they were written without the originals' source.
description: The concepts behind LARMORX — the original, the port, the replica and the clean room; LARMORX's own work; the three packages larmorx, larmorx-nc and larmorx-gpl and their licences in full; choosing a port (auto, replica, clean-room); the originals' defects (fix and reproduce); threads; why clean rooms exist and how the clean-room audit shows they were written without the originals' source.
---

## Four words {#words}

Every page of this site uses four words for what LARMORX holds, each with one meaning.

- **Original**: the program or function that a port reimplements, as its own developers release it. Every port is compared with its original, on the same files with the same arguments: its files, its messages and its exit status. `bet` from FSL 6.0.7.23 is an original; so is `antsRegistration` from ANTs 2.6.5.
- **Port**: one reimplementation of an original in LARMORX, in Rust, or in Python where the original is Python code that LARMORX keeps in Python (pybids' BIDS index, sdcflows' workflows). Each port is one kind, a replica or a clean room, so a program can have two ports: `bet` has both, `antsRegistration` has a replica.
- **Replica**: the original's source translated step by step, to give the original's results bit for bit. Where a record shows a difference, it says why, most often the C library's rounding of `exp` or `pow`. A replica comes under its original's licence terms, so it lives in the package for those terms.
- **Clean room**: a port written again without the original's source or its replica: from a description of what the original does, its documentation, papers and runs of the original. It is built for speed and carries LARMORX's licence, Apache-2.0.

What LARMORX has that is not a port is **LARMORX's own**: its NIfTI reader and writer, and the `larmorx` command itself. LARMORX's own work is compared with a program named by its name, never called an original: the NIfTI reader [against nibabel](/evidence/nifti-io/).

Where each port lives:

| Software | Replica | Clean room |
|---|---|---|
| ANTs and ITK | `larmorx` | planned, after FreeSurfer |
| AFNI | `larmorx` (with AFNI's CC BY 4.0 credit) | `larmorx` |
| FSL | `larmorx-nc` (non-commercial use only) | `larmorx` |
| tedana (`t2smap`) | `larmorx-gpl` (GPL-3.0) | `larmorx`, from the next release (0.1.0rc1 has only the replica) |
| sdcflows, fMRIPrep's steps and the Python libraries they call | `larmorx` | planned, after FreeSurfer |

Every program and its ports: [Programs](/programs/).

## The three packages and their licences {#packages}

LARMORX is published as three packages, one for each family of licences, so that each licence stays with the code it covers. Their licences, in plain words:

- **`larmorx`**: every program on the [Programs](/programs/) page but FSL's and tedana's replicas, that is the replicas of ANTs, ITK, AFNI, sdcflows and fMRIPrep, every clean room and LARMORX's own work. [Apache-2.0](repo:LICENSE): any use, commercial use included; keep the licence and the notices. The works it includes and their licences, permissive ones and the Mozilla Public License 2.0 for routines translated from Eigen (whose source stays public), are listed in its [NOTICE](repo:NOTICE). AFNI's replicas carry AFNI's CC BY 4.0 credit.
- **`larmorx-nc`**: the replicas of FSL's programs. The [FSL Licence](repo:crates-nc/LICENSE): **non-commercial use only**. Once it is installed, the FSL programs' default (`implementation="auto"`) runs these replicas, so FSL's terms then cover your default results. `implementation="clean-room"` (`"original"` in 0.1.0rc1) runs LARMORX's clean rooms instead.
- **`larmorx-gpl`**: the replica of tedana's `t2smap`. The [GNU GPL version 3](repo:crates-gpl/LICENSE): any use; whoever passes it on, changed or not, must pass on its source under the same licence. tedana's LGPL-2.1 code is under GPL-3.0 here, which the LGPL allows.

The two replica packages are separate programs (`larmorx-nc`, `larmorx-gpl`) that `larmorx` runs as separate processes, so their licences stay with them. Each is installed only when you ask for it by name (`pip install larmorx-nc`) or through `larmorx[all]` ([Getting started](/getting-started/#pip)). The repository's [licensing notes](repo:docs/licensing.md) give every work LARMORX includes, its licence and where it goes.

## Three settings {#settings}

LARMORX adds three settings of its own to the original's arguments: the number of threads, how the originals' defects are handled and, for a program with two ports, which port runs. In Python they are the arguments `n_threads`, `upstream_defects` and, where a program has two ports, `implementation`. On the command line they stand between `larmorx` and the family, from the next release: `larmorx --n-threads 4 --implementation clean-room --upstream-defects reproduce <family> <program> ...`. `--implementation` matters only for a program with two ports. 0.1.0rc1 reads the environment variables they replace, `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` and `LARMORX_UPSTREAM_DEFECTS` ([Getting started](/getting-started/#first-steps) shows both ways).

### Which port runs: `auto`, `replica`, `clean-room` {#auto}

A program with both ports takes `implementation="replica"` or `"clean-room"` (`"original"` in 0.1.0rc1, which `main` still accepts). `"auto"`, the default, runs the replica when it is installed (AFNI's are built in) and the clean room otherwise. So without `larmorx-nc` the FSL programs run their clean rooms, and with it their replicas.

### The originals' defects: `fix` and `reproduce` {#defects}

Defects found in an original are recorded in the repository's [register](repo:docs/findings/upstream-defects.md), each with a code such as `ANTS-40`, and decided by four rules: most are corrected by default (`fix`), with a notice; an input that makes no sense is refused with a clear error; a few that pipelines may rely on are kept and documented. A notice says that a known defect of the original would have changed this result and that LARMORX computed the corrected result:

```text
larmorx: upstream defect ANTS-40 (N4BiasFieldCorrection) corrected: 6208 of the 92160 voxels N4 uses have no logarithm (6208 are 0, 0 negative or NaN): they are left out of the histogram and the fit; ITK keeps them in its log image as they are (0 is the log of 1) [LARMORX_UPSTREAM_DEFECTS=reproduce gives N4BiasFieldCorrection's result]
```

It is not an error: the command still ends with exit status 0. `upstream_defects="reproduce"` gives the original's result, bit for bit, and the notice then says `reproduced`. The comparisons with the originals run in `reproduce`. The [upstream defects](repo:docs/api/upstream-defects.md) page explains the rules.

### Threads {#threads}

`n_threads` sets the number of threads. Python's default is 1; without a setting the command line uses every logical CPU (ANTs' programs also read `ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS`, or `NSLOTS`). Results do not depend on the thread count: every sum over parallel work is added in a fixed order, so the result is the same bits at any thread count, and the evidence pages compare each port with itself at several thread counts.

## Why clean rooms exist {#clean-rooms}

Some originals come under licences that keep their code out of an Apache-2.0 package: FSL's, tedana's (LGPL-2.1), AFNI's until its release 26.3.05, and the GNU C Library's (glibc's) maths functions, whose exact results `reproduce` needs. FSL's, tedana's and AFNI's programs have a replica, in a package under its original's licence terms where they require it, and a clean room in `larmorx`; glibc's functions have a clean room only. A clean room is written only from a description of the original's behaviour (the repository's `specs/`), its documentation, published papers and runs of the original program. Its authors never saw the original's source or its replica; the audit below shows how this is checked. The clean room lets anyone use the program under Apache-2.0, commercial use included. It is also built for speed, and gives the original's behaviour within the thresholds its record states; each program's evidence page shows its speed beside the original's. The programs that have only a replica (ANTs and ITK, sdcflows, fMRIPrep's steps) get a clean room later, for its speed ([roadmap](/roadmap/)).

**The clean-room audit** shows, from records made at the time, that the clean rooms were written without their original's source. Every agent that worked on LARMORX was an AI agent (Claude Code), launched by one orchestrating session, and Claude Code keeps a transcript of every session: each file read, search, command and edit, with its result. The audit reads every transcript and lists, for each agent, what it read, searched, ran and wrote, each path classified by a restriction table written from the project's rules. Git's history says which agent made each commit of clean-room code. The [audit's page](repo:docs/validation/clean-room-audit.md) gives the verdict for every clean room, every slip with its judgement, and code similarity as extra evidence only, never a pass or a failure.

## Why Rust and Python {#why}

LARMORX is written in Rust, with Python on top, so that the programs of several projects install with one command on Linux, macOS and Windows and give the same numbers on every one of them. Why that is hard with the original programs, what Rust gives, what LARMORX's own rules add and the limits: [Why Rust and Python](/concepts/why-rust-and-python/).
