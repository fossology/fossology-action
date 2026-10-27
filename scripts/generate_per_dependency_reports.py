"""Split consolidated SPDX report into per-dependency reports.

After fossologyscanner produces a consolidated SPDX report (results/sbom_spdx.json),
this script splits it into individual, self-contained SPDX 2.3 documents, one per
component. Each generated document is a valid SPDX document that fully describes
its single package (including a DESCRIBES relationship, external references,
extracted licensing info and annotations carried over from the consolidated
report).

Output filenames use {name}@{version}.spdx.json format.

All behaviour is configurable through environment variables:

    REPORT_DIR                 Output directory for per-dependency reports.
                               Default: "per-dependency-reports"
    REPORT_PATH                Path to the consolidated SPDX report to split.
                               Default: "results/sbom_spdx.json"
    SPDX_VERSION               SPDX spec version written into each report.
                               Default: "SPDX-2.3"
    DATA_LICENSE               Data license written into each report.
                               Default: "CC0-1.0"
    DOCUMENT_NAMESPACE_PREFIX  Prefix used to build each document's namespace.
                               Default: "https://spdx.org/spdxdocs"
    UNKNOWN_NAME               Fallback name used when a package has no name.
                               Default: "unknown"
    CREATOR                    Creator string added to creationInfo when the
                               consolidated report has no creators.
                               Default: "Tool: fossology-action"
    NAMESPACE_HASH_ALGO        Hash algorithm used to build a deterministic
                               document namespace from name + version.
                               Default: "sha256"
    NAMESPACE_HASH_LENGTH      Number of hex characters of the hash to embed in
                               the namespace. Default: "16"
"""

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def _env(name, default):
    """Return the value of an environment variable or a default."""
    return os.environ.get(name, default)


def _sanitize_filename(value):
    """Replace characters that are invalid in filenames on common platforms.

    Keeps '@' so CapyCLI's find_report_file() can match via exact-match or
    name-only-match. Replaces everything else that is not a letter, digit,
    '.', '-', '_' or '@' with '_'.
    """
    return re.sub(r"[^A-Za-z0-9._@-]", "_", value)


def _build_namespace(prefix, safe_name, pkg_ver, algo, length):
    """Build a deterministic document namespace from name + version."""
    digest = hashlib.new(algo, f"{safe_name}@{pkg_ver}".encode("utf-8")).hexdigest()
    return f"{prefix}/{safe_name}-{digest[:length]}"


def _build_creation_info(spdx, creator, now):
    """Return a valid SPDX creationInfo, filling in required fields if missing."""
    creation_info = dict(spdx.get("creationInfo", {}))

    # 'created' is required by the SPDX spec.
    if not creation_info.get("created"):
        creation_info["created"] = now

    # 'creators' is required and must contain at least one entry.
    creators = creation_info.get("creators")
    if not creators:
        creation_info["creators"] = [creator]

    return creation_info


def main():
    """Main entry point."""
    report_dir = _env("REPORT_DIR", "per-dependency-reports")
    consolidated_path = _env("REPORT_PATH", "results/sbom_spdx.json")
    spdx_version = _env("SPDX_VERSION", "SPDX-2.3")
    data_license = _env("DATA_LICENSE", "CC0-1.0")
    namespace_prefix = _env("DOCUMENT_NAMESPACE_PREFIX", "https://spdx.org/spdxdocs")
    unknown_name = _env("UNKNOWN_NAME", "unknown")
    creator = _env("CREATOR", "Tool: fossology-action")
    namespace_algo = _env("NAMESPACE_HASH_ALGO", "sha256")
    namespace_length = int(_env("NAMESPACE_HASH_LENGTH", "16"))

    # Load consolidated SPDX report
    if not Path(consolidated_path).exists():
        print(f"WARNING: Consolidated SPDX report not found at {consolidated_path}")
        print("Per-dependency report generation skipped.")
        return 0

    with open(consolidated_path, "r", encoding="utf-8") as f:
        spdx = json.load(f)

    packages = spdx.get("packages", [])
    if not packages:
        print("WARNING: No packages found in consolidated SPDX report")
        return 0

    Path(report_dir).mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    count = 0

    # Carry over document-level sections that are relevant to every component.
    document_commons = {
        "hasExtractedLicensingInfos": spdx.get("hasExtractedLicensingInfos", []),
        "annotations": spdx.get("annotations", []),
    }

    for pkg in packages:
        pkg_name = pkg.get("name", unknown_name)
        pkg_ver = pkg.get("versionInfo", "")
        pkg_spdxid = pkg.get("SPDXID", f"SPDXRef-Package-{pkg_name}")

        # Build filename: {name}@{version}.spdx.json
        # Sanitize invalid filename characters but keep @ for CapyCLI matching.
        safe_name = _sanitize_filename(pkg_name)
        filename = f"{safe_name}@{pkg_ver}.spdx.json" if pkg_ver else f"{safe_name}.spdx.json"

        # Build a valid, self-contained per-package SPDX document.
        per_pkg = {
            "spdxVersion": spdx.get("spdxVersion", spdx_version),
            "dataLicense": spdx.get("dataLicense", data_license),
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": pkg_name,
            "documentNamespace": _build_namespace(
                namespace_prefix, safe_name, pkg_ver, namespace_algo, namespace_length
            ),
            "creationInfo": _build_creation_info(spdx, creator, now),
            "packages": [pkg],
            # The document describes exactly this one package.
            "documentDescribes": [pkg_spdxid],
            "relationships": [
                {
                    "spdxElementId": "SPDXRef-DOCUMENT",
                    "relationshipType": "DESCRIBES",
                    "relatedSpdxElement": pkg_spdxid,
                }
            ],
        }

        # Carry over document-level sections that apply to the whole document.
        for key, value in document_commons.items():
            if value:
                per_pkg[key] = value

        output_file = Path(report_dir) / filename
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(per_pkg, f, indent=2)
        count += 1

    print(f"Generated {count} per-dependency SPDX reports in {report_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
