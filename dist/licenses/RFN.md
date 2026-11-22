# Reserved font names

Read from the notices at the exact revisions in `upstream.lock.json`.

| Fork | Pinned notice | Explicit reservation | Pipeline rule |
| --- | --- | --- | --- |
| Strata Sans | `sans-LICENSE.txt`, Inter 4.1 | None declared after the copyright line | Treat **Inter** as reserved, as required by the brief |
| Strata Serif | `serif-sources-LICENSE.md`, 4.005 | **Source** (curly quotes in original notice) | Block Source in every name record |
| Strata Mono | `mono-LICENSE`, 6.2 | None declared after the copyright line | Block **Fira** regardless |

All three are SIL OFL 1.1. The generic definition of “Reserved Font Name” in
an OFL body is not a declaration of an RFN. No upstream warning was relaxed.

Upstream copyright notices contain the forbidden family words. To honor both
requirements, preserve the notices **verbatim** in `licenses/`, the candidate
`OFL.txt` / `COPYRIGHT.txt`, and every build's bundled `licenses/`. Binary name
ID 0 points to those bundled notices; it does not silently rewrite an author's
copyright line. All binary name records, including URLs, descriptions,
trademarks and variable-instance PostScript names, are checked case-insensitively
for Inter, Source and Fira. Font names are Strata Sans, Strata Serif and Strata Mono.

Icon sources/output bundle the full Lucide ISC (including its Feather notice)
and Hugeicons free MIT notices. No proprietary reference font or symbol file is
opened, copied, exported, traced or parsed. Apple references are screenshots only.
