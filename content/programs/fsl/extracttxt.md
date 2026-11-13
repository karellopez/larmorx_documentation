---
title: "`extracttxt`"
kicker: "Programs · FSL"
lede: "`extracttxt` is a script that prints the lines of a text file from the first line that matches a word."
description: "LARMORX reference for FSL 6.0.7.23 `extracttxt`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: fsl
  original: "FSL 6.0.7.23"
  software: "FSL"
  command: "larmorx fsl extracttxt"
  python: "lx.fsl.extracttxt"
  api: "docs/api/fsl-flirt.md"
  evidence: "/evidence/fsl-flirt/"
  ports:
    - {kind: replica, name: "replica", package: larmorx-nc, licence: "FSL Licence: non-commercial use only", status: "experimental"}
    - {kind: clean-room, name: "clean room", package: larmorx, licence: "Apache-2.0", status: "experimental"}
  sources:
    CHANGELOG.md: "fa776d2ea0a17487"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "035dcd92e164879c"
    crates/larmorx-fsl/src/cli/extracttxt.rs: "005eb99123aac099"
    docs/api/fsl-flirt.md: "7fe0febecf4edaee"
    python/larmorx/fsl/flirt_more.py: "de95486aa525ad80"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

The word is a basic regular expression, as grep reads it. With a count, it prints that many
lines, from a given number of lines after the match (before it, when the number is negative), and
FSL's messages for ranges before the first line.

## Command line {#command-line}

```text synopsis
larmorx fsl extracttxt search_word file [num_trailing_lines [relative_start]]
```

Everything after `larmorx fsl extracttxt` is the original's command line: the arguments of FSL 6.0.7.23's `extracttxt`, as FSL takes them. LARMORX's own options stand between `larmorx` and the family `fsl`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        fsl extracttxt ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>extracttxt</code>'s usage text, as the clean room prints it</summary>

```text
Usage: extracttxt search_word file [num_trailing_lines [relative_start]]
```

</details>

## Python {#python}

```python
lx.fsl.extracttxt(
    search_word: str,
    file: str | os.PathLike,
    trailing_lines: int | None = None,
    relative_start: int | None = None,
    *,
    implementation: ImplementationName = "auto",
) -> str
```

Where `ImplementationName` is one of `"auto"`, `"replica"`, `"clean-room"`, `"original"` (0.1.0rc1's spelling of `"clean-room"`).

FSL's `extracttxt`: the lines of `file` from the first that matches `search_word` (a basic regular expression, as grep reads it) to the end, or `trailing_lines` of them, starting `relative_start` lines after (or before) the match.

The result is the text printed, as a string. `relative_start` needs `trailing_lines`.

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `extracttxt` accepts (`crates/larmorx-fsl/src/cli/extracttxt.rs`) and the arguments of `lx.fsl.extracttxt` (`python/larmorx/fsl/flirt_more.py`), whose defaults and descriptions are taken from it. Under each option, in grey, FSL's own help for it.

| <code><span class="nw">extracttxt</span></code> arguments | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">search&#95;word</span></code> | <code><span class="nw">search&#95;word</span></code> |  | a basic regular expression |
| <code><span class="nw">file</span></code> | <code><span class="nw">file</span></code> |  |  |
| <code><span class="nw">num&#95;trailing&#95;lines</span></code> | <code><span class="nw">trailing&#95;lines</span></code> | <code><span class="nw">None</span></code> | without it, every line to the end |
| <code><span class="nw">relative&#95;start</span></code> | <code><span class="nw">relative&#95;start</span></code> | <code><span class="nw">None</span></code> | lines after the match, or before it when negative |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `fsl` on the command line (`larmorx --n-threads 4 fsl extracttxt ...`); `lx.fsl.extracttxt` takes `implementation` as an argument, and the others are the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;fsl&#46;extracttxt</span></code> takes no <code><span class="nw">n&#95;threads</span></code>. Default: every logical CPU on the command line (<code><span class="nw">0</span></code>). The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br><code><span class="nw">implementation&#61;&#34;auto&#34;</span></code> | <code><span class="nw">&#34;auto&#34;</span></code> (default): the replica when <code><span class="nw">larmorx&#45;nc</span></code> is installed, else the clean room; <code><span class="nw">&#34;replica&#34;</span></code> or <code><span class="nw">&#34;clean&#45;room&#34;</span></code> (<code><span class="nw">&#34;original&#34;</span></code>, 0.1.0rc1's spelling, still works). The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;fsl&#46;extracttxt</span></code> takes no <code><span class="nw">upstream&#95;defects</span></code>. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `log.txt` (a text of five lines, two of them with the word `value`). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# Three lines, from the line before the first that holds "value".
text = lx.fsl.extracttxt("value", "log.txt", 3, -1)
text  # -> 'start\nfirst value 1\nmiddle\n'
```

```bash
larmorx fsl extracttxt value log.txt 3 -1
```

## Ports {#ports}

`extracttxt` has two ports: a replica and a clean room.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx&#45;nc</span></code> | FSL Licence: non-commercial use only | experimental | [fsl-flirt-replica](repo:docs/validation/fsl-flirt-replica.md) |
| clean room | <code><span class="nw">larmorx</span></code> | Apache-2.0 | experimental | [fsl-flirt](repo:docs/validation/fsl-flirt.md) |

Both ports are complete (`specs/flirt.md` §15.8). The clean room has its own POSIX basic regular expressions (with GNU grep's extensions) and
the script's dc and sed arithmetic, messages included. GNU sed's usage text, which a range read as
sed's options prints, is not reproduced: one LARMORX line takes its place. Refused, as the spec
says: arguments that the script's shell would split or expand, counts and starts that are not
integers, and files with NUL bytes.

The replica's record holds 13 cases of `extracttxt`: 8 identical to FSL, 5 where both refuse
alike. The clean room's holds 12: 8 within its thresholds, 4 refused alike.

FSL's licence allows non-commercial use only, so each of FLIRT's programs has two ports, a
replica and a clean room, in different packages ([licensing](repo:docs/licensing.md) says what each
package holds):

- **The replica** is translated from FSL's source. The package `larmorx-nc` holds it (`crates-nc/`),
  under the FSL Licence's terms, and `larmorx` runs it as a separate program, `larmorx-nc fsl
  <program>`, when `larmorx-nc` is installed (`pip install larmorx-nc`).
- **The clean room** is written from [`specs/flirt.md`](repo:specs/flirt.md) by an implementer who
  never read FSL's source or the replica. It is part of `larmorx`, under Apache-2.0
  (`crates/larmorx-fsl`, with its [PROVENANCE](repo:crates/larmorx-fsl/PROVENANCE.md), section
  "FLIRT"), and runs on LARMORX's clean-room registration engine, the head-motion correction's
  (`lx.mri.hmc`).

`implementation="auto"` runs the replica when `larmorx-nc` is installed, and the clean room
otherwise. `"replica"` and `"clean-room"` choose one (`"original"`, 0.1.0rc1's spelling of
`"clean-room"`, still works); `"clean-room"` runs the clean room in this process. On the command
line, `--implementation auto|replica|clean-room` before the family chooses alike, from the next
release; in 0.1.0rc1 the variable `LARMORX_IMPLEMENTATION` chooses (`original` for the clean
room).

## Evidence {#evidence}

How each of `extracttxt`'s ports was measured against FSL, case by case: [its evidence](/evidence/fsl-flirt/).

## More in the repository {#more}

The API page [docs/api/fsl-flirt.md](repo:docs/api/fsl-flirt.md) holds what `extracttxt` shares with the page's other programs:

- [The clean room (part 1, 2026-11-02)](repo:docs/api/fsl-flirt.md#the-clean-room-part-1-2026-11-02)
- [Defects of the original, corrected by default](repo:docs/api/fsl-flirt.md#defects-of-the-original-corrected-by-default)
- [Not yet](repo:docs/api/fsl-flirt.md#not-yet)
- [History](repo:docs/api/fsl-flirt.md#history)
