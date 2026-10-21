"""The validation evidence on the site's pages: worked examples, metrics, verdicts, charts and
the case explorer, rendered as HTML from the JSON that larmorx exports
(``python -m larmorx_validation evidence <tool> --site <this repository>``, the main
repository's ``docs/figures.md``) into ``static/evidence/<tool>.json``.

Everything here is static HTML that works without JavaScript: the examples' still panels and
their metrics, the charts as bars and dots positioned in HTML, the full table of cases.
``static/js/evidence.js`` makes them interactive from the same JSON. Numbers are never computed
here, only formatted: each one carries ``data-ev`` (its JSON pointer), and the review check
(``tools/review/shoot.mjs --eval`` with ``LX_EVIDENCE.check()``, README.md) compares what
a page shows with the JSON.
"""

from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path

from markupsafe import Markup

ROLE_LABELS = {
    "input": "Input",
    "original": "Original program",
    "fmriprep": "fMRIPrep's own output",
    "reference": "Original, as a reference",
    "larmorx": "LARMORX",
}


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def ptr(*parts) -> str:
    """A JSON pointer (RFC 6901)."""
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in parts)


# ------------------------------------------------------------------------------- numbers


def fmt_count(n) -> str:
    return f"{int(n):,}"


def fmt_sig(x, digits: int = 3) -> str:
    """``x`` with ``digits`` significant digits, as Python's ``g`` format writes it, with a
    true minus sign."""
    if x is None:
        return "–"
    if x == 0:
        return "0"
    s = f"{x:.{digits}g}"
    if "e" in s:
        m, e = s.split("e")
        s = f"{m}e{int(e)}"
    return s.replace("-", "−")


def fmt_share(x) -> str:
    if x == 0:
        return "0 %"
    if x == 1:
        return "100 %"
    return fmt_sig(100 * x, 3) + " %"


def fmt_seconds(x) -> str:
    return fmt_sig(x, 3) + " s"


class Evidence:
    """The evidence helpers of one page (links are relative to it)."""

    def __init__(self, root: Path, verdicts: list[dict], link, repo, md_inline, problems: list):
        self.root = root
        self.verdicts = {v["id"]: v for v in verdicts}
        self.order = [v["id"] for v in verdicts]
        self.link = link
        self.repo = repo
        self.md_inline = md_inline
        self.problems = problems
        self._docs: dict[str, dict] = {}

    # ------------------------------------------------------------------ data

    def doc(self, tool: str) -> dict:
        if tool not in self._docs:
            path = self.root / "static" / "evidence" / f"{tool}.json"
            if not path.is_file():
                raise SystemExit(f"evidence {tool!r}: {path.relative_to(self.root)} does not exist")
            doc = json.loads(path.read_text(encoding="utf-8"))
            self._check(tool, doc)
            self._docs[tool] = doc
        return self._docs[tool]

    def _check(self, tool: str, doc: dict) -> None:
        for v in set(re.findall(r'"verdict": "([^"]+)"', json.dumps(doc))):
            if v not in self.verdicts:
                self.problems.append(f"evidence {tool}: unknown verdict {v!r} (data/verdicts.yml)")
        blobs = self.root / "static" / "evidence" / "blobs"
        for name in set(re.findall(r"\b[0-9a-f]{24}\.(?:bin|webp)\b", json.dumps(doc))):
            if not (blobs / name).is_file():
                self.problems.append(f"evidence {tool}: blob {name} is missing")

    def num(self, tool: str, pointer: str, text: str, cls: str = "num") -> str:
        return f'<span class="{cls}" data-ev="{esc(tool)}:{esc(pointer)}">{esc(text)}</span>'

    def href(self, target: str) -> str:
        """A link from the evidence JSON: a repository path (``docs/...#anchor``) or a path
        on this site (``/validation/#...``)."""
        if target.startswith("/"):
            return self.link(target)
        path, _, anchor = target.partition("#")
        return self.repo(path) + (f"#{anchor}" if anchor else "")

    def text(self, s: str) -> Markup:
        """A sentence from the JSON, with Markdown's inline code and links."""
        return self.md_inline(s)

    # -------------------------------------------------------------- verdicts

    def verdict(self, vid: str, count=None, label: str | None = None, tool: str = "", pointer=""):
        v = self.verdicts.get(vid)
        if v is None:
            self.problems.append(f"unknown verdict {vid!r}")
            return Markup(esc(vid))
        n = ""
        if count is not None:
            n = " " + (self.num(tool, pointer, fmt_count(count)) if tool else esc(count))
        return Markup(
            f'<a class="verdict v-{esc(vid)}" href="{self.link("/validation/#verdict-" + vid)}" '
            f'title="{esc(v["means"])}"><i aria-hidden="true"></i>'
            f'<span>{esc(label or v["label"])}</span>{n}</a>'
        )

    def legend(self, ids: list[str] | None = None) -> Markup:
        ids = ids or self.order
        items = "".join(f"<li>{self.verdict(i, label=self.verdicts[i]['label'])}</li>" for i in ids)
        return Markup(f'<ul class="verdict-legend">{items}</ul>')

    def taxonomy(self) -> Markup:
        """The Validation page's definitions, one per verdict, each an anchor."""
        rows = []
        for v in self.verdicts.values():
            rows.append(
                f'<div class="vdef" id="verdict-{esc(v["id"])}"><dt><span class="verdict v-{esc(v["id"])}">'
                f'<i aria-hidden="true"></i><span>{esc(v["label"])}</span></span></dt>'
                f'<dd><p>{esc(v["means"])}</p><p class="vdef-matters">{esc(v["matters"])}</p></dd></div>'
            )
        return Markup(f'<dl class="vdefs">{"".join(rows)}</dl>')

    # ------------------------------------------------------------- examples

    def example(self, tool: str, ex_id: str) -> Markup:
        doc = self.doc(tool)
        k, ex = next(((i, e) for i, e in enumerate(doc["examples"]) if e["id"] == ex_id), (None, None))
        if ex is None:
            raise SystemExit(f"evidence {tool}: no example {ex_id!r}")
        base = ptr("examples", k)
        src = self.link(f"/static/evidence/{tool}.json")
        blobs = self.link("/static/evidence/blobs/")
        poster = ex["poster"]
        panels = {p["id"]: p for p in ex["panels"]}
        diffs = {d["id"]: d for d in ex["diffs"]}
        out = ex["default"]["output"]
        cells = []
        for pid in ex["default"]["panels"]:
            p = panels[pid]
            img = poster["panels"].get(pid)
            role = ROLE_LABELS.get(p["role"], p["role"])
            cells.append(
                f'<figure class="ev-panel role-{esc(p["role"])}" data-panel="{esc(pid)}">'
                f'<div class="ev-canvas" style="aspect-ratio:{poster["aspect"]}">'
                + (f'<img src="{blobs}{img}" alt="" loading="lazy" decoding="async">' if img else "")
                + f'</div><figcaption><span class="ev-role">{esc(role)}</span>'
                f'<span class="ev-label">{esc(p["label"])}</span>'
                + (f'<span class="ev-sub">{esc(p["sub"])}</span>' if p.get("sub") else "")
                + "</figcaption></figure>"
            )
        for did in ex["default"]["diffs"]:
            dd = diffs[did]
            j = ex["diffs"].index(dd)
            m = dd["metrics"][out] if out in dd["metrics"] else next(iter(dd["metrics"].values()))
            img = poster["diffs"].get(did)
            body = (
                f'<img src="{blobs}{img}" alt="" loading="lazy" decoding="async">'
                if img and not m["identical"]
                else '<p class="ev-identical"><b>Bit-identical</b><span>'
                + self.num(tool, ptr("examples", k, "diffs", j, "metrics", out, "voxels"), fmt_count(m["voxels"]))
                + " of " + self.num(tool, ptr("examples", k, "diffs", j, "metrics", out, "voxels"), fmt_count(m["voxels"]))
                + " voxels equal</span></p>"
            )
            rng = poster.get("ranges", {}).get(did)
            scale = ""
            if rng and not m["identical"]:
                scale = f'<span class="ev-sub ev-range">scale ±{esc(fmt_sig(rng))}</span>'
            cells.append(
                f'<figure class="ev-panel ev-diff kind-{esc(dd["kind"])}" data-diff="{esc(did)}">'
                f'<div class="ev-canvas" style="aspect-ratio:{poster["aspect"]}">{body}</div>'
                f'<figcaption><span class="ev-role">{esc(dd["role_label"])}</span>'
                f'<span class="ev-label">{esc(dd["label"])}</span>{scale}</figcaption></figure>'
            )
        note = (
            f'<p class="ev-still">{esc(poster["caption"])} '
            '<span class="ev-nojs">The interactive viewer needs JavaScript; the metrics below are '
            "complete without it.</span></p>"
        )
        facts = "".join(
            f"<dt>{esc(f['label'])}</dt><dd>{self.text(f['text'])}</dd>" for f in ex["facts"]
        )
        html_ = (
            f'<section class="ev-example" id="example-{esc(ex_id)}" data-ev-tool="{esc(tool)}" '
            f'data-ev-example="{esc(ex_id)}" data-ev-src="{src}" data-ev-blobs="{blobs}">'
            f'<div class="ev-head"><p class="kicker">Worked example</p>'
            f'<p class="ev-title">{esc(ex["title"])}</p>'
            f'<p class="ev-sum">{self.text(ex["summary"])}</p>'
            f'<dl class="ev-facts">{facts}</dl></div>'
            f'<div class="ev-viewer"><div class="ev-panels">{"".join(cells)}</div>{note}</div>'
            + self.chain(tool, k)
            + self.metrics(tool, k)
            + self.provenance(tool, ex)
            + "</section>"
        )
        return Markup(html_)

    def chain(self, tool: str, k: int) -> str:
        ex = self.doc(tool)["examples"][k]
        ch = ex.get("chain")
        if not ch:
            return ""
        items = []
        for i, step in enumerate(ch["steps"]):
            nodes = "".join(
                f'<li class="role-{esc(n["role"])}"><span>{esc(n["label"])}</span>'
                + (f'<small>{esc(n["sub"])}</small>' if n.get("sub") else "")
                + "</li>"
                for n in step["nodes"]
            )
            items.append(f'<li class="ev-chain-step"><ul class="ev-chain-nodes">{nodes}</ul></li>')
            if i < len(ch["links"]):
                link = ch["links"][i]
                p = ptr("examples", k, "chain", "links", i, "max_abs")
                what = (
                    "bit-identical"
                    if link["max_abs"] == 0
                    else "max |Δ| " + self.num(tool, p, fmt_sig(link["max_abs"]))
                )
                items.append(
                    f'<li class="ev-chain-link{" is-zero" if link["max_abs"] == 0 else ""}">'
                    f'<span class="ev-chain-cause">{esc(link["cause"])}</span>'
                    f'<span class="ev-chain-delta">{what}</span></li>'
                )
        return (
            f'<div class="ev-chain"><p class="ev-chain-title">{esc(ch["title"])}</p>'
            f'<ol class="ev-chain-flow">{"".join(items)}</ol>'
            f'<p class="ev-chain-note">{self.text(ch["note"])}</p></div>'
        )

    GROUPS = (
        ("main fmriprep", "LARMORX against the original program and fMRIPrep"),
        ("check", "LARMORX against itself: threads and modes"),
        ("variability", "The original against itself: the yardstick"),
    )

    def metrics(self, tool: str, k: int) -> str:
        """One row per comparison and output, grouped: LARMORX against the original, LARMORX
        against itself, the original against itself. A comparison that gives the same bytes in
        every output is one row."""
        ex = self.doc(tool)["examples"][k]
        outputs = ex["outputs"]
        multi = len(outputs) > 1
        ncol = 6 if multi else 5
        head = (
            "<tr><th scope=col class=cmph>Comparison (A − B), verdict and reason</th>"
            + ("<th scope=col>Output</th>" if multi else "")
            + "<th scope=col class=n>max |Δ|</th><th scope=col class=n>Values that differ</th>"
            "<th scope=col class=n>RMS of Δ</th><th scope=col class=n>max |Δ| ÷ range</th>"
            "<th scope=col class=n>1 − NCC</th></tr>"
        )
        body = []
        for kinds, title in self.GROUPS:
            group = [(j, d) for j, d in enumerate(ex["diffs"]) if d["kind"] in kinds.split()]
            if not group:
                continue
            body.append(
                f'<tbody class="grp"><tr class="grp-head"><th colspan="{ncol + 1}" scope=colgroup>'
                f"{esc(title)}</th></tr>"
            )
            for j, d in group:
                outs = [o for o in outputs if o["id"] in d["metrics"]]
                same = all(d["metrics"][o["id"]]["identical"] for o in outs)
                links = " ".join(
                    f'<a href="{self.href(lk["href"])}">{esc(lk["label"])}</a>'
                    for lk in d.get("links", [])
                )
                chip = (
                    self.verdict(d["verdict"])
                    if d.get("verdict")
                    else Markup('<span class="ev-ref">reference</span>')
                )
                rows_n = 1 if same else len(outs)
                span = f' rowspan="{rows_n}"' if rows_n > 1 else ""
                head_cell = (
                    f'<th scope="row"{span} class="cmp"><span class="cmp-label">{esc(d["label"])}</span>'
                    f'<span class="cmp-verdict">{chip}</span><span class="cmp-why">{self.text(d["reason"])}'
                    + (f' <span class="ev-links">{links}</span>' if links else "")
                    + "</span></th>"
                )
                if same:
                    o = outs[0]
                    p = ptr("examples", k, "diffs", j, "metrics", o["id"], "voxels")
                    what = "both outputs" if len(outs) > 1 else o["label"]
                    cells = [head_cell]
                    if multi:
                        cells.append(f"<td class=out>{esc(what)}</td>")
                    n = self.num(tool, p, fmt_count(d["metrics"][o["id"]]["voxels"]))
                    cells.append(f'<td colspan="5" class="same">identical: 0 of {n} values differ</td>')
                    body.append(f'<tr class="kind-{esc(d["kind"])} first is-same">{"".join(cells)}</tr>')
                    continue
                for oi, o in enumerate(outs):
                    m = d["metrics"][o["id"]]

                    def p(key, jj=j, oo=o["id"]):
                        return ptr("examples", k, "diffs", jj, "metrics", oo, key)

                    differ = (
                        self.num(tool, p("differ"), fmt_count(m["differ"]))
                        + " of "
                        + self.num(tool, p("voxels"), fmt_count(m["voxels"]))
                        + (
                            f' <small>({self.num(tool, p("share"), fmt_share(m["share"]))})</small>'
                            if m["differ"]
                            else ""
                        )
                    )
                    unit = o.get("stored_unit")
                    max_abs = self.num(tool, p("max_abs"), fmt_sig(m["max_abs"]))
                    if unit and "max_abs_stored" in m and m["max_abs"]:
                        stored = self.num(tool, p("max_abs_stored"), fmt_sig(m["max_abs_stored"]))
                        max_abs += f" <small>({stored} {esc(unit)}{'' if m['max_abs_stored'] == 1 else 's'})</small>"
                    cells = [head_cell] if oi == 0 else []
                    if multi:
                        cells.append(f"<td class=out>{esc(o['label'])}</td>")
                    cells += [
                        f"<td class=n>{max_abs}</td>",
                        f"<td class=n>{differ}</td>",
                        f'<td class=n>{self.num(tool, p("rms"), fmt_sig(m["rms"]))}</td>',
                        f'<td class=n>{self.num(tool, p("max_rel_range"), fmt_sig(m["max_rel_range"]))}</td>',
                        f'<td class=n>{self.num(tool, p("one_minus_ncc"), fmt_sig(m["one_minus_ncc"]))}</td>',
                    ]
                    cls = f'kind-{esc(d["kind"])}{" first" if oi == 0 else ""}'
                    body.append(f'<tr class="{cls}">{"".join(cells)}</tr>')
            body.append("</tbody>")
        cap = self.text(ex["metrics_note"])
        return (
            '<div class="ev-metrics"><p class="ev-metrics-title">Every comparison, computed in '
            "float64 over every voxel of the outputs</p>"
            f'<div class="table-wrap"><table class="ev-mtable"><thead>{head}</thead>'
            f'{"".join(body)}</table></div><p class="ev-metrics-note">{cap}</p></div>'
        )

    def provenance(self, tool: str, ex: dict) -> str:
        src = self.link(f"/static/evidence/{tool}.json")
        items = "".join(f"<li>{self.text(t)}</li>" for t in ex["provenance"])
        return (
            f'<details class="ev-prov"><summary>Provenance of this example</summary><ul>{items}</ul>'
            f'<p>Every number above is in <a href="{src}">{esc(tool)}.json</a>, exported by '
            f"<code>python -m larmorx_validation evidence {esc(tool)}</code>.</p></details>"
        )

    # --------------------------------------------------------------- charts

    def agreement(self, tool: str, impl: str) -> Markup:
        doc = self.doc(tool)
        k, im = next((i, x) for i, x in enumerate(doc["implementations"]) if x["id"] == impl)
        rows = im["agreement"]
        top = max(sum(r["counts"].values()) for r in rows) or 1
        out = []
        for ri, r in enumerate(rows):
            total = sum(r["counts"].values())
            segs = []
            parts = []
            for v in self.order:
                n = r["counts"].get(v)
                if not n:
                    continue
                pp = ptr("implementations", k, "agreement", ri, "counts", v)
                label = self.verdicts[v]["label"]
                parts.append(f"{n} {label.lower()}")
                segs.append(
                    f'<a class="seg v-{esc(v)}" style="flex-grow:{n}" href="#cases" '
                    f'data-filter-category="{esc(r["category"])}" data-filter-verdict="{esc(v)}" '
                    f'data-filter-impl="{esc(impl)}" title="{esc(r["category"])}: {n} {esc(label.lower())}">'
                    f'<span class="seg-n">{self.num(tool, pp, fmt_count(n))}</span></a>'
                )
            out.append(
                f'<div class="ev-agree-row"><span class="ev-agree-cat">{esc(r["category"])}</span>'
                f'<div class="ev-agree-track"><div class="ev-bar" style="width:{100 * total / top:.3f}%" '
                f'role="group" aria-label="{esc(r["category"])}: {total} cases: {esc(", ".join(parts))}">{"".join(segs)}</div></div>'
                f'<span class="ev-agree-n">{total}</span></div>'
            )
        present = [v for v in self.order if any(v in r["counts"] for r in rows)]
        totals = im["summary"]["verdicts"]
        legend = "".join(
            f"<li>{self.verdict(v, count=totals.get(v, 0), tool=tool, pointer=ptr('implementations', k, 'summary', 'verdicts', v))}</li>"
            for v in present
        )
        cases = self.num(tool, ptr("implementations", k, "summary", "cases"), fmt_count(im["summary"]["cases"]))
        return Markup(
            f'<figure class="ev-chart ev-agree" data-impl="{esc(impl)}">'
            f'<figcaption class="ev-chart-title">{esc(im["label"])}: {cases} cases of the '
            f'<a href="{self.href(im["record"])}">record</a>, by category and verdict</figcaption>'
            f'<div class="ev-agree-rows">{"".join(out)}</div>'
            f'<ul class="verdict-legend">{legend}</ul>'
            f'<p class="ev-chart-note">Select a segment to list its cases below.</p></figure>'
        )

    def band(self, tool: str) -> Markup:
        doc = self.doc(tool)
        b = doc["band"]
        lo, hi = b["axis"]
        span = math.log10(hi) - math.log10(lo)

        def x(v):
            v = min(max(v, lo), hi)
            return 100 * (math.log10(v) - math.log10(lo)) / span

        rows = []
        for i, r in enumerate(b["rows"]):
            dots = []
            for key, cls, name in (("ratio_max", "d-max", "largest |Δ|"), ("ratio_ncc", "d-ncc", "1 − NCC")):
                v = r[key]
                if v is None:
                    continue
                pp = ptr("band", "rows", i, key)
                dots.append(
                    f'<span class="dot {cls}" style="left:{x(v):.3f}%" title="{esc(name)}: '
                    f'{fmt_sig(v, 2)} × ANTs\' band"><b class="visually-hidden">{esc(name)} '
                    f'{self.num(tool, pp, fmt_sig(v, 2))} × the band</b></span>'
                )
            rows.append(
                f'<li><span class="ev-band-case"><code>{esc(r["case"])}</code> <small>{esc(r["output"])}</small></span>'
                f'<span class="ev-band-track">{"".join(dots)}</span></li>'
            )
        ticks = "".join(
            f'<span style="left:{x(t):.3f}%">{esc(lbl)}</span>' for t, lbl in b["ticks"]
        )
        one = x(1.0)
        return Markup(
            f'<figure class="ev-chart ev-band" style="--one:{one:.3f}%">'
            f'<figcaption class="ev-chart-title">{esc(b["title"])}</figcaption>'
            f'<ul class="ev-band-key"><li><span class="dot d-max"></span>largest |Δ| ÷ ANTs\' largest |Δ| between its thread counts</li>'
            f'<li><span class="dot d-ncc"></span>(1 − NCC) ÷ ANTs\' (1 − NCC) between its thread counts</li>'
            f'<li><span class="band-swatch"></span>inside ANTs\' own thread-to-thread variability (&lt; 1)</li></ul>'
            f'<ol class="ev-band-rows">{"".join(rows)}</ol>'
            f'<div class="ev-band-axis"><span class="ev-band-pad"></span><span class="ev-band-ticks">{ticks}</span></div>'
            f'<p class="ev-chart-note">{self.text(b["note"])}</p></figure>'
        )

    def speed(self, tool: str) -> Markup:
        doc = self.doc(tool)
        s = doc.get("speed")
        if not s:
            return Markup("")
        lo, hi = s["axis"]
        span = math.log10(hi) - math.log10(lo)

        def x(v):
            return 100 * (math.log10(min(max(v, lo), hi)) - math.log10(lo)) / span

        rows = []
        for i, r in enumerate(s["rows"]):
            dots = []
            for j, ser in enumerate(s["series"]):
                v = r["seconds"].get(ser["id"])
                if v is None:
                    continue
                pp = ptr("speed", "rows", i, "seconds", ser["id"])
                dots.append(
                    f'<span class="dot s-{esc(ser["mark"])}" style="left:{x(v):.3f}%" title="{esc(ser["label"])}: '
                    f'{fmt_seconds(v)}"><b class="visually-hidden">{esc(ser["label"])} '
                    f'{self.num(tool, pp, fmt_sig(v))} s</b></span>'
                )
            ratio = ""
            if r.get("speedup"):
                ratio = (
                    '<span class="ev-speed-x">'
                    + self.num(tool, ptr("speed", "rows", i, "speedup"), fmt_sig(r["speedup"], 2))
                    + "×</span>"
                )
            rows.append(
                f'<li><span class="ev-band-case">{esc(r["label"])}</span>'
                f'<span class="ev-band-track">{"".join(dots)}</span>{ratio}</li>'
            )
        key = "".join(
            f'<li><span class="dot s-{esc(ser["mark"])}"></span>{esc(ser["label"])}</li>' for ser in s["series"]
        )
        ticks = "".join(f'<span style="left:{x(t):.3f}%">{esc(lbl)}</span>' for t, lbl in s["ticks"])
        return Markup(
            f'<figure class="ev-chart ev-speed"><figcaption class="ev-chart-title">{esc(s["title"])}</figcaption>'
            f'<ul class="ev-band-key">{key}</ul><ol class="ev-band-rows">{"".join(rows)}</ol>'
            f'<div class="ev-band-axis"><span class="ev-band-pad"></span><span class="ev-band-ticks">{ticks}</span></div>'
            f'<p class="ev-chart-note">{self.text(s["note"])}</p></figure>'
        )

    # --------------------------------------------------------- case explorer

    def cases(self, tool: str) -> Markup:
        doc = self.doc(tool)
        impls = doc["implementations"]
        multi = len(impls) > 1
        head = (
            "<tr><th scope=col data-sort=id>Case</th><th scope=col data-sort=category>Category</th>"
            "<th scope=col>What it tests</th>"
            + "".join(
                f'<th scope=col data-sort="v-{esc(i["id"])}">{esc(i["short"]) if multi else "Verdict"}</th>'
                for i in impls
            )
            + "<th scope=col>Checks</th></tr>"
        )
        rows = []
        for c in doc["cases"]:
            cells = [
                f'<th scope="row" class="cid"><code>{esc(c["id"])}</code>'
                + (
                    f' <a class="ev-to-example" href="#example-{esc(c["example"])}">worked example</a>'
                    if c.get("example")
                    else ""
                )
                + "</th>",
                f"<td class=cat>{esc(c['category'])}</td>",
                f'<td class=what><span>{esc(c["description"])}</span>'
                + (
                    f'<details class="cmd"><summary>command line</summary><code class="cmdline">'
                    f'{esc(c["command"])}</code></details>'
                    if c.get("command")
                    else ""
                )
                + "</td>",
            ]
            data = [f'data-category="{esc(c["category"])}"']
            checks = []
            for i in impls:
                r = c["results"].get(i["id"])
                if r is None:
                    cells.append("<td class=vd>–</td>")
                    continue
                data.append(f'data-v-{esc(i["id"])}="{esc(r["verdict"])}"')
                reason = f'<p class="why">{self.text(r["reason"])}</p>' if r.get("reason") else ""
                cells.append(f"<td class=vd>{self.verdict(r['verdict'])}{reason}</td>")
                checks.append(r["checks"])
            cells.append(f'<td class="n chk">{esc(" · ".join(dict.fromkeys(checks)))}</td>')
            rows.append(
                f'<tr id="case={esc(c["id"])}" {" ".join(data)} data-id="{esc(c["id"])}">{"".join(cells)}</tr>'
            )
        n = self.num(tool, ptr("cases_total"), fmt_count(doc["cases_total"]))
        return Markup(
            f'<div class="ev-cases" id="cases" data-ev-tool="{esc(tool)}" '
            f'data-impls="{esc(",".join(i["id"] for i in impls))}">'
            f'<p class="ev-cases-count">{n} cases</p>'
            f'<div class="table-wrap ev-cases-wrap"><table class="ev-ctable"><thead>{head}</thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div></div>'
        )

    # ------------------------------------------------------- validation page

    def matrix(self, tools: list[dict]) -> Markup:
        """Every tool × implementation × verdict counts, from ``static/evidence/summary.json``."""
        path = self.root / "static" / "evidence" / "summary.json"
        summary = json.loads(path.read_text(encoding="utf-8"))
        pages = {t["url"]: t for t in tools}
        cols = [*self.order, "unclassified"]
        head = (
            "<tr><th scope=col>Tool</th><th scope=col>Implementation</th><th scope=col>Cases</th>"
            + "".join(
                f'<th scope=col class="vh"><a class="verdict v-{esc(v)} is-key" href="#verdict-{esc(v)}">'
                f'<i aria-hidden="true"></i><span>{esc(self.verdicts[v]["short"])}</span></a></th>'
                for v in self.order
            )
            + '<th scope=col class="vh"><span class="verdict v-unclassified is-key"><i aria-hidden="true"></i>'
            "<span>within thresholds, not yet classified</span></span></th></tr>"
        )
        rows = []
        for ti, t in enumerate(summary["tools"]):
            for ii, im in enumerate(t["implementations"]):
                first = ii == 0
                span = f' rowspan="{len(t["implementations"])}"' if len(t["implementations"]) > 1 else ""
                cells = []
                if first:
                    page = pages.get(t["page"])
                    name = esc(t["title"])
                    if page:
                        name = f'<a href="{self.link(t["page"])}">{name}</a>'
                    cells.append(f'<th scope=row{span} class="eco-{esc(t["eco"])}"><span class="tname"><span class="dot"></span><span>{name}</span></span></th>')
                rec = f'<a href="{self.href(im["record"])}">{esc(im["label"])}</a>'
                status = (
                    ' <span class="status-tag status-tag--experimental">experimental</span>'
                    if im["status"] == "experimental"
                    else ""
                )
                cells.append(f"<td class=impl>{rec}{status}</td>")
                p = ptr("tools", ti, "implementations", ii)
                cells.append(f'<td class=n>{self.num("summary", p + "/cases", fmt_count(im["cases"]))}</td>')
                for v in cols:
                    n = im["verdicts"].get(v, 0)
                    cells.append(
                        f'<td class="n{" zero" if not n else ""}">'
                        + (self.num("summary", p + "/verdicts/" + v, fmt_count(n)) if n else "·")
                        + "</td>"
                    )
                rows.append(f"<tr>{''.join(cells)}</tr>")
        note = self.text(summary["note"])
        return Markup(
            f'<div class="table-wrap ev-matrix"><table><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table></div>'
            f'<p class="ev-chart-note">{note}</p>'
        )
