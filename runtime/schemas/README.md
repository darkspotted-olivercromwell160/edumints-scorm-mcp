# SCORM XSD schemas (Faz 1 — conformance validation)

Used by `core/schema_validate.py` to validate generated `imsmanifest.xml` against the official
ADL/IMS schemas. See `docs/CONFORMANCE.md` for how this fits the overall conformance story.

## What is here (vendored)
- `adl/` — **ADL schemas** (`adlcp_rootv1p2`, `adlcp_v1p3`, `adlseq_v1p3`, `adlnav_v1p3`). These are
  **public domain** (U.S. Government / ADL Initiative) and are committed to this repo.
- `driver_12.xsd`, `driver_2004.xsd` — tiny **driver** schemas (authored here) that `xsd:import` all
  namespaces a SCORM manifest uses, so a single `XMLSchema` can validate the multi-namespace manifest.
- `ims_sources.json` — manifest of the **IMS / W3C** schemas to fetch (filename → URL + sha256).

## What is NOT here (fetched at runtime)
The **IMS** schemas (`imscp*`, `imsss*`, `ims_xml`) and the **W3C** `xml.xsd` are **not redistributed**
(1EdTech licensing). They are fetched on first use from `www.imsglobal.org` / `www.w3.org` and cached
under `$DATA_DIR/scorm_schemas/{12,2004}/` (or a temp dir). Integrity is checked against the pinned
sha256 in `ims_sources.json`.

## Offline / air-gapped use
Validation itself never touches the network (`no_network`); only the one-time cache warm-up fetches.
For fully air-gapped deployments, place all schema files (ADL + IMS + W3C + driver) under a directory
with `12/` and `2004/` sub-folders and set `SCORM_SCHEMA_DIR=<that dir>`. No fetch is then attempted.

## Not shipped in packages
These schemas are **server-side validation only** — they are never embedded in produced SCORM packages.
