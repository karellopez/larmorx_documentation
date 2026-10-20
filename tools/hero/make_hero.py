"""Precompute the home page hero: a brain as a cloud of spins.

The points are sampled from the MNI ICBM 152 nonlinear asymmetric template,
version 2009c, at 1 mm (TemplateFlow's ``tpl-MNI152NLin2009cAsym``, res-01):
the grey matter, found from the T1-weighted image's intensities inside the
brain mask, and the surface of the mask, which gives the brain its outline.
Each point is a spin of one software ecosystem (ANTs, AFNI, FSL, FreeSurfer,
Connectome Workbench). The ecosystems share the brain as a mosaic of patches,
cells grown from random seeds over the points (no atlas is used), coloured so
that neighbouring patches differ and every ecosystem holds about a fifth of
the brain.

Writes ``static/hero/hero.bin``, read by ``static/js/hero.js``:

    bytes 0-3   b"LXH1"
    bytes 4-7   the length L of a JSON header (uint32, little-endian)
    8 .. 8+L    the header (UTF-8 JSON, padded with spaces to a multiple of 4)
    then        x, y, z of every point, interleaved, int16 (-32767..32767 is -1..1)
    then        the ecosystem of every point, uint8 (0..4)
    then        the grey-matter weight of every point, uint8 (0..255)

Page coordinates: x to the right, y up, z towards the viewer; at rotation 0
the brain is seen from its left side, the forehead to the left. The points are
in random order, so any prefix is a fair sample (a slow machine draws fewer).

Also writes ``hero-light.svg`` and ``hero-dark.svg``: the brain as a still,
for pages without WebGL2, with reduced motion or with the effects off.

Run with any Python that has numpy, scipy and nibabel:

    python tools/hero/make_hero.py --templateflow <dir containing tpl-MNI152NLin2009cAsym>
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent
OUT = SITE / "static" / "hero"
TEMPLATE = "tpl-MNI152NLin2009cAsym"
DEFAULT_TF = SITE.parent / "oracles" / "templateflow"

#: The ecosystems, in the order of their index in hero.bin. Pastels are the
#: same in both themes (static/css/site.css); on light paper the hero uses the
#: deep variants, the same hues at 3:1 against the paper.
ECOSYSTEMS = [
    {"id": "ants", "name": "ANTs", "pastel": "#9db9ec", "deep": "#467dea"},
    {"id": "afni", "name": "AFNI", "pastel": "#e3c779", "deep": "#987e2e"},
    {"id": "fsl", "name": "FSL", "pastel": "#86cfc6", "deep": "#438c84"},
    {"id": "freesurfer", "name": "FreeSurfer", "pastel": "#bba8ec", "deep": "#9860f6"},
    {"id": "workbench", "name": "Workbench", "pastel": "#eeaacd", "deep": "#d8489f"},
]
N_POINTS = 36000
N_CELLS = 44
SPRINKLE = 0.06  # the share of points that take another ecosystem's colour


def load(tf: Path, name: str):
    import nibabel as nib

    img = nib.load(tf / TEMPLATE / f"{TEMPLATE}_res-01_{name}.nii.gz")
    return np.asarray(img.dataobj), img.affine


def grey_matter_weight(t1: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """A soft grey-matter membership from T1w intensity: three intensity
    classes (CSF, grey, white) by k-means inside the mask, then a Gaussian
    around the grey class."""
    v = t1.astype(float) / np.percentile(t1[mask], 99)
    x = v[mask]
    c = np.percentile(x, [15, 50, 85])
    for _ in range(30):
        lab = np.argmin(np.abs(x[:, None] - c[None, :]), axis=1)
        c = np.array([x[lab == k].mean() for k in range(3)])
    c.sort()
    sigma = (c[2] - c[1]) / 2.6
    w = np.exp(-(((v - c[1]) / sigma) ** 2))
    w[~mask] = 0
    return w


def sample(rng, t1, mask, affine, n):
    from scipy import ndimage

    gm = grey_matter_weight(t1, mask)
    surf = mask & ~ndimage.binary_erosion(mask, iterations=1)
    # Depth below the brain's surface, in mm: the outer cortex weighs most,
    # so the front of the cloud is read, not every layer behind it.
    depth = ndimage.distance_transform_edt(mask)
    w = gm**2 * np.exp(-depth / 9.0) + 1.2 * surf
    p = w.ravel() / w.sum()
    idx = rng.choice(p.size, size=n, replace=False, p=p)
    ijk = np.stack(np.unravel_index(idx, mask.shape), 1).astype(float) + rng.random((n, 3)) - 0.5
    mm = ijk @ affine[:3, :3].T + affine[:3, 3]
    val = np.clip(np.maximum(gm.ravel()[idx], 0.55 * surf.ravel()[idx]), 0, 1)
    return mm, val


def to_page(mm: np.ndarray) -> np.ndarray:
    """MNI millimetres to the page's unit box: x right, y up, z towards the
    viewer, seen from the left with the forehead to the left."""
    xyz = np.stack([-mm[:, 1], mm[:, 2], -mm[:, 0]], 1)
    lo, hi = xyz.min(0), xyz.max(0)
    xyz = xyz - (lo + hi) / 2
    return xyz / np.abs(xyz).max()


def mosaic(rng, xyz: np.ndarray, k: int, colours: int) -> np.ndarray:
    """Patches: k-means cells over the points, coloured greedily so that
    neighbours differ and the colours stay balanced."""
    from scipy.spatial import cKDTree

    centres = xyz[rng.choice(len(xyz), k, replace=False)]
    for _ in range(12):
        lab = cKDTree(centres).query(xyz)[1]
        centres = np.array([xyz[lab == c].mean(0) if np.any(lab == c) else centres[c] for c in range(k)])
    d, nn = cKDTree(centres).query(xyz, k=2)
    lab = nn[:, 0]
    near = (d[:, 1] - d[:, 0]) < 0.025
    adj = {c: set() for c in range(k)}
    for a, b in zip(nn[near, 0], nn[near, 1]):
        adj[a].add(b)
        adj[b].add(a)
    size = np.bincount(lab, minlength=k)
    colour = -np.ones(k, int)
    load_ = np.zeros(colours)
    for c in sorted(range(k), key=lambda c: (-len(adj[c]), -size[c])):
        used = {colour[o] for o in adj[c] if colour[o] >= 0}
        free = [q for q in range(colours) if q not in used] or list(range(colours))
        q = min(free, key=lambda q: load_[q])
        colour[c] = q
        load_[q] += size[c]
    eco = colour[lab]
    flip = rng.random(len(eco)) < SPRINKLE
    eco[flip] = rng.integers(0, colours, flip.sum())
    return eco.astype(np.uint8)


def write_bin(xyz, eco, val, path: Path) -> None:
    head = {
        "version": 1,
        "n": int(len(xyz)),
        "ecosystems": [{"id": e["id"], "name": e["name"]} for e in ECOSYSTEMS],
        "source": "MNI ICBM 152 nonlinear asymmetric 2009c, 1 mm (TemplateFlow tpl-MNI152NLin2009cAsym res-01)",
    }
    hb = json.dumps(head, separators=(",", ":")).encode()
    hb += b" " * (-len(hb) % 4)
    q = np.round(np.clip(xyz, -1, 1) * 32767).astype("<i2")
    body = q.tobytes() + eco.astype(np.uint8).tobytes() + np.round(val * 255).astype(np.uint8).tobytes()
    path.write_bytes(b"LXH1" + struct.pack("<I", len(hb)) + hb + body)
    print(f"{path.name}: {len(xyz)} points, {path.stat().st_size / 1024:.0f} KB")


def write_stills(xyz, eco, val) -> None:
    """The brain at a three-quarter view, back to front, in each theme."""
    W = H = 1000.0
    a, e = -0.62, 0.30  # rotation about the vertical (B0) axis, then the elevation
    x = xyz[:, 0] * np.cos(a) + xyz[:, 2] * np.sin(a)
    z = -xyz[:, 0] * np.sin(a) + xyz[:, 2] * np.cos(a)
    y = xyz[:, 1] * np.cos(e) - z * np.sin(e)
    z = xyz[:, 1] * np.sin(e) + z * np.cos(e)
    s = 1.0 / (1.0 - z * 0.18)
    px = W / 2 + x * s * W * 0.44
    py = H / 2 - y * s * W * 0.44
    depth = (z + 1) / 2
    keep = np.arange(len(xyz)) < 16000
    bins = np.digitize(depth, [0.42, 0.62])
    for theme in ("light", "dark"):
        key = "deep" if theme == "light" else "pastel"
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}">']
        for b, (op, sw) in enumerate([(0.30, 2.6), (0.55, 3.0), (0.85, 3.4)]):
            if theme == "light":
                op = min(1.0, op + 0.1)
            for k, ec in enumerate(ECOSYSTEMS):
                m = keep & (bins == b) & (eco == k)
                if not m.any():
                    continue
                d = "".join(f"M{u:.0f} {v:.0f}h0" for u, v in zip(px[m], py[m]))
                parts.append(f'<path d="{d}" stroke="{ec[key]}" stroke-opacity="{op:.2f}" '
                             f'stroke-width="{sw}" stroke-linecap="round" fill="none"/>')
        parts.append("</svg>")
        p = OUT / f"hero-{theme}.svg"
        p.write_text("".join(parts), encoding="utf-8")
        print(f"{p.name}: {p.stat().st_size / 1024:.0f} KB")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--templateflow", type=Path, default=DEFAULT_TF,
                    help=f"the TemplateFlow home holding {TEMPLATE} (default: {DEFAULT_TF})")
    ap.add_argument("--seed", type=int, default=20261020)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    t1, affine = load(args.templateflow, "T1w")
    mask, _ = load(args.templateflow, "desc-brain_mask")
    mm, val = sample(rng, t1, mask > 0, affine, N_POINTS)
    xyz = to_page(mm)
    eco = mosaic(rng, xyz, N_CELLS, len(ECOSYSTEMS))
    order = rng.permutation(len(xyz))
    xyz, eco, val = xyz[order], eco[order], val[order]
    OUT.mkdir(parents=True, exist_ok=True)
    write_bin(xyz, eco, val, OUT / "hero.bin")
    write_stills(xyz, eco, val)
    print("ecosystem shares:", np.round(np.bincount(eco, minlength=5) / len(eco), 3).tolist())


if __name__ == "__main__":
    main()
