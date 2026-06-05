"""core/manifest.py — imsmanifest.xml üreteci (CONTRACTS.md §10).

Versiyon-agnostik API; 1.2 tam, 2004 4th Ed iskelet (sequencing v1 kapsamı).
Tek SCO (v1): index.html. Tüm paket dosyaları <file> olarak listelenir.
"""

from __future__ import annotations

from lxml import etree

from .project import Project

# Namespace'ler
NS_IMSCP_12 = "http://www.imsproject.org/xsd/imscp_rootv1p1p2"
NS_ADLCP_12 = "http://www.adlnet.org/xsd/adlcp_rootv1p2"
NS_IMSCP_2004 = "http://www.imsglobal.org/xsd/imscp_v1p1"
NS_ADLCP_2004 = "http://www.adlnet.org/xsd/adlcp_v1p3"
NS_ADLSEQ_2004 = "http://www.adlnet.org/xsd/adlseq_v1p3"
NS_ADLNAV_2004 = "http://www.adlnet.org/xsd/adlnav_v1p3"
NS_IMSSS = "http://www.imsglobal.org/xsd/imsss"
NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"


def build_manifest(project: Project, *, file_list: list[str]) -> str:
    """Project + paket dosya listesi → imsmanifest.xml (string)."""
    if project.scorm_version == "2004":
        return _build_2004(project, file_list)
    return _build_12(project, file_list)


def _common_files(file_list: list[str]) -> list[str]:
    # index.html her zaman başta; tekilleştir, sırayı koru
    seen: list[str] = []
    for f in ["index.html", *file_list]:
        if f not in seen:
            seen.append(f)
    return seen


def _build_12(project: Project, file_list: list[str]) -> str:
    nsmap = {None: NS_IMSCP_12, "adlcp": NS_ADLCP_12, "xsi": NS_XSI}
    manifest = etree.Element(
        "manifest",
        nsmap=nsmap,
        attrib={
            "identifier": f"MANIFEST-{project.id}",
            "version": "1.2",
            f"{{{NS_XSI}}}schemaLocation": (
                f"{NS_IMSCP_12} imscp_rootv1p1p2.xsd "
                "http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd "
                f"{NS_ADLCP_12} adlcp_rootv1p2.xsd"
            ),
        },
    )
    meta = etree.SubElement(manifest, "metadata")
    etree.SubElement(meta, "schema").text = "ADL SCORM"
    etree.SubElement(meta, "schemaversion").text = "1.2"

    orgs = etree.SubElement(manifest, "organizations", default="ORG-1")
    org = etree.SubElement(orgs, "organization", identifier="ORG-1")
    etree.SubElement(org, "title").text = project.title
    item = etree.SubElement(org, "item", identifier="ITEM-1", identifierref="RES-1")
    etree.SubElement(item, "title").text = project.title

    resources = etree.SubElement(manifest, "resources")
    res = etree.SubElement(
        resources, "resource",
        attrib={
            "identifier": "RES-1",
            "type": "webcontent",
            f"{{{NS_ADLCP_12}}}scormtype": "sco",
            "href": "index.html",
        },
    )
    for f in _common_files(file_list):
        etree.SubElement(res, "file", href=f)

    return _serialize(manifest)


def _build_2004(project: Project, file_list: list[str]) -> str:
    nsmap = {
        None: NS_IMSCP_2004,
        "adlcp": NS_ADLCP_2004,
        "adlseq": NS_ADLSEQ_2004,
        "adlnav": NS_ADLNAV_2004,
        "imsss": NS_IMSSS,
        "xsi": NS_XSI,
    }
    manifest = etree.Element(
        "manifest",
        nsmap=nsmap,
        attrib={
            "identifier": f"MANIFEST-{project.id}",
            "version": "1.0",
            f"{{{NS_XSI}}}schemaLocation": (
                f"{NS_IMSCP_2004} imscp_v1p1.xsd "
                f"{NS_ADLCP_2004} adlcp_v1p3.xsd "
                f"{NS_ADLSEQ_2004} adlseq_v1p3.xsd "
                f"{NS_ADLNAV_2004} adlnav_v1p3.xsd "
                f"{NS_IMSSS} imsss_v1p0.xsd"
            ),
        },
    )
    meta = etree.SubElement(manifest, "metadata")
    etree.SubElement(meta, "schema").text = "ADL SCORM"
    etree.SubElement(meta, "schemaversion").text = "2004 4th Edition"

    orgs = etree.SubElement(manifest, "organizations", default="ORG-1")
    org = etree.SubElement(orgs, "organization", identifier="ORG-1")
    etree.SubElement(org, "title").text = project.title
    item = etree.SubElement(org, "item", identifier="ITEM-1", identifierref="RES-1")
    etree.SubElement(item, "title").text = project.title
    # Sequencing iskeleti (v1 kapsamı): tek SCO, varsayılan akış
    seq = etree.SubElement(item, f"{{{NS_IMSSS}}}sequencing")
    ctrl = etree.SubElement(seq, f"{{{NS_IMSSS}}}controlMode")
    ctrl.set("choice", "true")
    ctrl.set("flow", "true")

    resources = etree.SubElement(manifest, "resources")
    res = etree.SubElement(
        resources, "resource",
        attrib={
            "identifier": "RES-1",
            "type": "webcontent",
            f"{{{NS_ADLCP_2004}}}scormType": "sco",
            "href": "index.html",
        },
    )
    for f in _common_files(file_list):
        etree.SubElement(res, "file", href=f)

    return _serialize(manifest)


def _serialize(root) -> str:
    return etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", pretty_print=True
    ).decode("utf-8")
