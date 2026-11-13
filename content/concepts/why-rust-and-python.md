---
title: Why Rust and Python
kicker: Concepts
lede: Why LARMORX is written in Rust, with Python on top. Why the original programs run only on Unix systems, what Rust gives, what the project's own rules add, and the limits of what has been shown so far.
description: Why LARMORX is written in Rust with Python on top — why AFNI, FSL and FreeSurfer have no Windows version, what Rust gives (one build tool, fixed-size types, arithmetic as written, memory safety, no data races), what LARMORX's own rules add (correctly rounded maths, matrix arithmetic in one fixed order, pure-Rust libraries, cross-platform checks on six platforms), why Python on top, and the honest limits.
---

LARMORX's aim is that a researcher can install the programs of several neuroimaging projects with one command, on Linux, macOS or Windows, and get the same numbers on every one of them. This page explains, in plain words, why that is hard with the original programs, and why LARMORX is written in Rust with a Python interface on top.

## The original programs run on Unix {#unix}

AFNI, FSL and FreeSurfer run on Linux and macOS. None of them has a Windows version: their documentation sends Windows users to the Windows Subsystem for Linux (WSL), which runs a Linux system inside Windows, or to a virtual machine. Their history and documentation suggest why (this page does not speak for their developers):

- **They were born on Unix workstations.** AFNI was developed at the Medical College of Wisconsin in the mid-1990s, "written in ANSI C and Motif 1.2 to run on Unix workstations" ([Cox, 1996](https://doi.org/10.1006/cbmr.1996.0014)); FreeSurfer at Massachusetts General Hospital, first described in 1999 ([Dale, Fischl and Sereno, 1999](https://doi.org/10.1006/nimg.1998.0395); [Fischl, 2012](https://doi.org/10.1016/j.neuroimage.2012.01.021)); and FSL at Oxford's FMRIB Centre, first released around 2000 ([Smith et al., 2004](https://doi.org/10.1016/j.neuroimage.2004.07.051); [Jenkinson et al., 2012](https://doi.org/10.1016/j.neuroimage.2011.09.015)). All three grew on the Unix systems of their labs, and computing clusters still run Linux.
- **Their main programs are scripts that chain other programs.** FreeSurfer's `recon-all` is a shell script that runs dozens of programs one after the other; FSL's `bet` is, in FSL's words, "the main command-line script which makes calling the core bet2 and betsurf programs easy"; AFNI's `afni_proc.py` "generate[s] a tcsh script for an AFNI process stream". The shells and the small Unix tools these scripts call are not part of Windows.
- **They rely on what Unix systems provide:** programs that start other programs (`fork`) and pass data through pipes, symbolic links, paths written with `/`, file names in which upper and lower case differ, settings in environment variables such as `FSLDIR` and `FREESURFER_HOME`, and, between AFNI and SUMA, shared memory and network connections.
- **Their C and C++ code can change meaning on Windows.** A `long` has 64 bits on 64-bit Linux and macOS but 32 bits on 64-bit Windows. A `long double` is the 80-bit extended format of the x87 unit with GCC on x86 Linux, but the same as a 64-bit `double` with Microsoft's compiler. Code written for GCC also uses extensions, and parts of the C99 standard, that Microsoft's compiler long did not support.
- **Their graphical interfaces were written for Unix's X Window System:** AFNI's viewer on X11 and the Motif toolkit, and FSL's notes for Windows still describe installing an X server for its graphical programs in some set-ups. Each project also depends on a large stack of other libraries, each of which would need its own Windows build.
- **Small academic teams and their users.** The teams are small, their users work on Linux clusters and Macs, and WSL now lets Windows users run the Linux versions, which leaves little reason to undertake a port.

The same program need not give the same numbers on two systems either. [Glatard et al. (2015)](https://doi.org/10.3389/fninf.2015.00012) ran FSL, FreeSurfer and CIVET on different versions of GNU/Linux and found that they "use mathematical functions based on single-precision floating-point arithmetic whose implementations in operating systems continue to evolve": the differences had little effect on simple steps such as brain extraction, but accumulated into important differences in longer pipelines (subcortical classification, fMRI analysis, cortical thickness). Getting the same numbers on six platforms needs more than a portable language: it needs the rules below.

## What Rust gives {#rust}

Rust is a compiled language with the speed of C that refuses, when the program is compiled, several kinds of mistake that C and C++ accept:

- **One build tool for every platform.** `cargo` builds LARMORX for the six platforms (Linux, macOS and Windows, each on x86-64 and on ARM) from one description, with libraries written in Rust only: there is no C, C++ or Fortran library to build and ship for each system. [maturin](https://www.maturin.rs/) and [PyO3](https://pyo3.rs/) turn it into Python wheels; with Python's stable interface (abi3), one wheel per platform serves every Python from 3.12 on.
- **Numbers of a fixed size.** `i32`, `i64`, `f32` and `f64` have the same size everywhere: there is no `long` whose size depends on the system, and no `long double`.
- **Arithmetic as it is written.** The compiler does not merge a multiplication and an addition into one operation with a single rounding unless the code asks for it, and on x86-64 it never computes in the x87's 80-bit registers, so the same operations round the same way on every platform.
- **Memory safety.** Reading past the end of an array stops the program with an error instead of returning whatever lies next in memory, and memory cannot be read before it is written. Where an original program reads past an array or uses memory it never wrote (cases of the [register of defects](repo:docs/findings/upstream-defects.md)), LARMORX stops with a clear error or computes a defined result, never a garbage one.
- **No data races.** The compiler refuses code in which two threads could change the same data at the same time, which makes parallel code safe to write.

## What Rust does not give, and LARMORX's rules add {#rules}

Rust alone does not give the same digits everywhere. The project's own rules do:

- **Its own maths functions.** Rust's `sin`, `exp` and `log` call the platform's mathematical library (glibc on Linux, Apple's on macOS, Microsoft's on Windows), whose last digits can differ ([findings](repo:docs/findings/platform-math.md)). LARMORX uses its own instead. By default they are **correctly rounded**, ports of [CORE-MATH](https://core-math.gitlabpages.inria.fr/)'s (`exp`, `log`, `pow`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan2`, `cbrt`, `tanh`, and `expf`, `logf`, `powf`, `sinf`, `cosf`, `tanhf`, `cbrtf`): each result is the exact value rounded once, the same on every platform. For the `reproduce` mode, which gives an original program's exact behaviour, LARMORX carries copies of the GNU C Library 2.35's own functions as Linux runs them: Arm's routines and fdlibm's under their permissive licences, and, written from behavioural specifications, its double sine and cosine and its single-precision cube root.
- **Matrix arithmetic in one fixed order.** Libraries such as OpenBLAS choose their kernels by the processor, so a product or an inverse can change its last digits from one computer to the next. LARMORX computes the few matrix routines its programs use in one fixed order of operations, never a processor's own: that of OpenBLAS's Haswell kernels for numpy's 4 × 4 products and inverses, and that of reference LAPACK's LU factorisation, inverse and solves for FSL's.
- **The libraries written in Rust too.** ITK's vnl routines, Eigen's symmetric eigensolver, SciPy's spline interpolation and the HDF5 file format are written again in pure Rust, so no system library sits under LARMORX's results.
- **Threads and random numbers under control.** Every call takes an explicit number of threads, every sum over parallel work is added in a fixed order, so the result is the same bits at any thread count, and random numbers come from seeded generators.
- **Proved at every change.** The cross-platform checks run every program on all six platforms at every change of the code and check that each reproduces its Linux x86-64 output bit for bit ([the cross-platform checks](repo:docs/validation/golden.md)).

Rust made the solution practical; the rules made it work.

## Why Python on top {#python}

Much of neuroimaging's analysis software is written in Python (nibabel, nilearn, nipype and fMRIPrep among them), so Python is LARMORX's interface: `pip install larmorx` installs it like any other package ([Getting started](/getting-started/)), and `import larmorx as lx` gives every program as a Python function with typed options, on images held in memory (`lx.ants.n4_bias_field_correction(t1w, n_threads=8)`). The computing happens in Rust, which releases Python's global interpreter lock while it works, so other Python threads go on meanwhile. The pipeline larmorprepx, still to come, is written as plain Python functions on top of the library, easy to read and to change. The same programs are also commands that take the original programs' arguments, for shell scripts.

## The limits {#limits}

- **The six-platform proof uses small images.** The golden tests' inputs are at most 32³ voxels, so that the whole suite runs in under a minute on each platform. Full-size runs on Windows and macOS come with the final validation phase ([roadmap](/roadmap/#final)) and the checks on clean machines.
- **The comparisons with the original programs run on one Linux x86-64 machine,** where the originals are built; the other platforms are checked against LARMORX's own Linux x86-64 output ([how each program is validated](/validation/)).
- **The original programs stay Unix programs.** LARMORX is an alternative beside them, not a fix of them.

## References {#references}

- Cox RW (1996). AFNI: software for analysis and visualization of functional magnetic resonance neuroimages. *Computers and Biomedical Research* 29(3):162–173. [doi:10.1006/cbmr.1996.0014](https://doi.org/10.1006/cbmr.1996.0014)
- Dale AM, Fischl B, Sereno MI (1999). Cortical surface-based analysis. *NeuroImage* 9(2):179–194. [doi:10.1006/nimg.1998.0395](https://doi.org/10.1006/nimg.1998.0395)
- Fischl B (2012). FreeSurfer. *NeuroImage* 62(2):774–781. [doi:10.1016/j.neuroimage.2012.01.021](https://doi.org/10.1016/j.neuroimage.2012.01.021)
- Glatard T, Lewis LB, Ferreira da Silva R, et al. (2015). Reproducibility of neuroimaging analyses across operating systems. *Frontiers in Neuroinformatics* 9:12. [doi:10.3389/fninf.2015.00012](https://doi.org/10.3389/fninf.2015.00012)
- Jenkinson M, Beckmann CF, Behrens TEJ, Woolrich MW, Smith SM (2012). FSL. *NeuroImage* 62(2):782–790. [doi:10.1016/j.neuroimage.2011.09.015](https://doi.org/10.1016/j.neuroimage.2011.09.015)
- Smith SM, Jenkinson M, Woolrich MW, et al. (2004). Advances in functional and structural MR image analysis and implementation as FSL. *NeuroImage* 23(Suppl. 1):S208–S219. [doi:10.1016/j.neuroimage.2004.07.051](https://doi.org/10.1016/j.neuroimage.2004.07.051)
- The projects' installation notes for Windows: [AFNI](https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/background_install/install_instructs/index.html), [FSL](https://fsl.fmrib.ox.ac.uk/fsl/docs/install/windows.html), [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/fswiki/SystemRequirements); FSL's [BET](https://fsl.fmrib.ox.ac.uk/fsl/docs/structural/bet.html) and AFNI's [afni_proc.py](https://afni.nimh.nih.gov/pub/dist/doc/program_help/afni_proc.py.html) documentation (2026-11-11).
