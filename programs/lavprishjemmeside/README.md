# Lavprishjemmeside Program

Lavprishjemmeside is a remote-first client program inside AI-Enterprise.

It governs two operational layers:

- `cms/`
- `client-sites/`

The clean target does not fake a local source tree for the live cPanel codebases. Instead, it models the live governance structure explicitly and keeps the source-of-truth repos remote.

This folder is documentation and ownership metadata only. Independent live repos stay outside the `AI-Enterprise` working tree and are classified in `ops/repository-topology.json`.

## Authority

- Program ID: `lavprishjemmeside-cms`
- Owner master: `lavprishjemmeside-master`
- Governing repo: `ssh://theartis@cp10.nordicway.dk/home/theartis/repositories/lavprishjemmeside.dk`
- Companion client repo: `ssh://theartis@cp10.nordicway.dk/home/theartis/repositories/ljdesignstudio.dk`

## Structure

- `cms/` documents the remote-first CMS authority and operational endpoints
- `client-sites/lavprishjemmeside.dk/` documents the parent site surface
- `client-sites/ljdesignstudio.dk/` documents the governed client-site surface

This folder exists so the AI-Enterprise dashboard can show the real operating model without pretending these remote repos are local first-party payloads.
