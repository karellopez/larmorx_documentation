"""The evidence's image blobs, kept out of `main`'s history on the orphan branch `evidence-blobs`.

The interactive evidence (``static/evidence/``) is JSON plus binary blobs: the images of the
worked examples, named by the first 24 hex digits of their SHA-256. The JSON and the manifest
``static/evidence/blobs.sha256`` (every blob a JSON names, with its full SHA-256, in
``sha256sum`` format) live on ``main``; the blobs themselves live in ``static/evidence/blobs/``,
which ``main`` ignores, and are published from the branch ``evidence-blobs``: one commit, no
parent, holding exactly the blobs of the manifest, replaced at every export. So the site's
history grows by the JSON only, and the images of a superseded export leave the repository
when the branch is replaced.

    python tools/blobs.py verify  [--dir DIR]       every blob of the manifest present, its hash right,
                                                    every blob a JSON names in the manifest
    python tools/blobs.py commit                    the branch evidence-blobs: one parentless commit of
                                                    the manifest's blobs (deterministic: the same blobs
                                                    give the same commit)
    python tools/blobs.py fetch [--remote origin]   the branch from a remote, its blobs extracted into
                                                    static/evidence/blobs/ (a local build needs them)
    python tools/blobs.py extract [--ref REF]       the blobs of a local ref into static/evidence/blobs/

The Pages workflow checks the branch out, runs ``verify --dir`` on it and publishes the blobs
with the site. Standard library only; git is the only program it runs.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "static" / "evidence"
BLOBS = EVIDENCE / "blobs"
MANIFEST = EVIDENCE / "blobs.sha256"
BRANCH = "evidence-blobs"
NAME = re.compile(r"\b([0-9a-f]{24})\.(bin|webp)\b")
#: The branch's commit carries the repository's configured identity (`git config user.name` and
#: `user.email`) and a fixed date, so that the same blobs give the same commit.
FIXED_DATE = "2026-01-01T00:00:00Z"


def git(*args: str, data: bytes | None = None, env: dict | None = None) -> bytes:
    r = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        input=data,
        capture_output=True,
        check=False,
        env={**os.environ, **(env or {})},
    )
    if r.returncode:
        raise SystemExit(f"git {' '.join(args)}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout


def manifest() -> dict[str, str]:
    """name -> full SHA-256, from static/evidence/blobs.sha256."""
    if not MANIFEST.is_file():
        raise SystemExit(f"{MANIFEST.relative_to(ROOT)} does not exist (export the evidence first)")
    out = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.strip():
            sha, name = line.split(maxsplit=1)
            out[name.lstrip("*")] = sha
    return out


def referenced() -> set[str]:
    """Every blob name a JSON of static/evidence/ names."""
    names: set[str] = set()
    for f in EVIDENCE.glob("*.json"):
        names |= {f"{h}.{ext}" for h, ext in NAME.findall(f.read_text(encoding="utf-8"))}
    return names


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def verify(folder: Path) -> int:
    man = manifest()
    problems = []
    refs = referenced()
    for name in sorted(refs - man.keys()):
        problems.append(f"{name}: named by the evidence JSON but not in the manifest")
    for name in sorted(man.keys() - refs):
        problems.append(f"{name}: in the manifest but named by no JSON")
    total = 0
    for name, want in sorted(man.items()):
        p = folder / name
        if not p.is_file():
            problems.append(f"{name}: missing from {folder}")
            continue
        got = sha256(p)
        total += p.stat().st_size
        if got != want or not want.startswith(name.split(".")[0]):
            problems.append(f"{name}: SHA-256 {got}, the manifest says {want}")
    extra = sorted(p.name for p in folder.iterdir() if p.is_file() and p.name not in man) if folder.is_dir() else []
    for name in extra:
        problems.append(f"{name}: in {folder} but not in the manifest")
    for p in problems:
        print("PROBLEM", p, file=sys.stderr)
    print(f"{len(man)} blobs, {total / 1e6:.1f} MB, {len(problems)} problems", file=sys.stderr)
    return 1 if problems else 0


def commit() -> int:
    man = manifest()
    entries = []
    for name, want in sorted(man.items()):
        p = BLOBS / name
        if not p.is_file() or sha256(p) != want:
            raise SystemExit(f"{name}: missing or wrong in {BLOBS.relative_to(ROOT)}; fetch or export first")
        oid = git("hash-object", "-w", "--", str(p)).decode().strip()
        entries.append(f"100644 blob {oid}\t{name}\n")
    tree = git("mktree", data="".join(entries).encode()).decode().strip()
    msg = (
        f"Evidence blobs: {len(entries)} files, the manifest's SHA-256 "
        f"{hashlib.sha256(MANIFEST.read_bytes()).hexdigest()[:16]}\n"
    )
    name_, email = (git("config", key).decode().strip() for key in ("user.name", "user.email"))
    env = {
        "GIT_AUTHOR_NAME": name_,
        "GIT_AUTHOR_EMAIL": email,
        "GIT_COMMITTER_NAME": name_,
        "GIT_COMMITTER_EMAIL": email,
        "GIT_AUTHOR_DATE": FIXED_DATE,
        "GIT_COMMITTER_DATE": FIXED_DATE,
    }
    c = git("commit-tree", tree, data=msg.encode(), env=env).decode().strip()
    git("update-ref", f"refs/heads/{BRANCH}", c)
    print(f"{BRANCH} -> {c} ({len(entries)} blobs, tree {tree})")
    print(f"publish: git push --force origin {BRANCH}   (before pushing main)")
    return 0


def extract(ref: str) -> int:
    man = manifest()
    listing = git("ls-tree", "-z", ref).split(b"\0")
    oids = {}
    for row in listing:
        if row:
            meta, name = row.split(b"\t", 1)
            oids[name.decode()] = meta.split()[2].decode()
    BLOBS.mkdir(parents=True, exist_ok=True)
    n = 0
    for name, want in sorted(man.items()):
        p = BLOBS / name
        if p.is_file() and sha256(p) == want:
            continue
        if name not in oids:
            raise SystemExit(f"{name}: not on {ref}; the branch is older than the manifest")
        data = git("cat-file", "blob", oids[name])
        if hashlib.sha256(data).hexdigest() != want:
            raise SystemExit(f"{name}: wrong content on {ref}")
        p.write_bytes(data)
        n += 1
    print(f"{n} blobs extracted from {ref} into {BLOBS.relative_to(ROOT)}; {len(man)} in the manifest")
    return verify(BLOBS)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--dir", type=Path, default=BLOBS)
    sub.add_parser("commit")
    f = sub.add_parser("fetch")
    f.add_argument("--remote", default="origin")
    e = sub.add_parser("extract")
    e.add_argument("--ref", default=BRANCH)
    p = sub.add_parser("publish-dir", help="copy the manifest's blobs from --dir into static/evidence/blobs/")
    p.add_argument("--dir", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.cmd == "verify":
        return verify(a.dir)
    if a.cmd == "commit":
        return commit()
    if a.cmd == "fetch":
        git("fetch", "--no-tags", a.remote, f"+refs/heads/{BRANCH}:refs/remotes/{a.remote}/{BRANCH}")
        return extract(f"refs/remotes/{a.remote}/{BRANCH}")
    if a.cmd == "extract":
        return extract(a.ref)
    if a.cmd == "publish-dir":
        if verify(a.dir):
            return 1
        BLOBS.mkdir(parents=True, exist_ok=True)
        for name in manifest():
            shutil.copyfile(a.dir / name, BLOBS / name)
        return verify(BLOBS)
    return 2


if __name__ == "__main__":
    sys.exit(main())
