# Third-party material

## Matt Pocock skills

- Source: <https://github.com/mattpocock/skills>
- Recorded upstream revision: `49dd158d1076134a641b33efb035946536778336`.
- Recorded package version: `1.3.1`.
- Copyright (c) 2026 Matt Pocock. MIT License.
- Vendored location: `assets/vendor/mattpocock/`.

The 27 skill directories and supporting files were copied from the source
project's installed snapshot without editing their contents. The original
`LICENSE` and `installation.json` are included. The metadata describes that
snapshot's recorded provenance; this packaging does not claim a fresh comparison
against upstream. Integration conventions live in our templates and skill.

When installed in a target, the entire snapshot and its license are copied to
`docs/skills/mattpocock/`; `.agents/skills/` uses relative links to those directories.

## Graphify

Graphify is installed independently from the `graphifyy` package, pinned to
`0.9.79`. Upstream: <https://github.com/Graphify-Labs/graphify>.
Its implementation, generated skill and indexes are not redistributed here.
The bootstrap invokes its public CLI for project installation and indexing.
