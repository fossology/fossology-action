<!-- SPDX-FileCopyrightText: 2024 Rajul Jha <rajuljha49@gmail.com>

 SPDX-License-Identifier: GPL-2.0-only -->

<p align="center">
  <a href="https://fossology.github.io">
  <img src="static/logo.png" alt="Fossology logo" width="144">
  </a>
  <br>
  <strong> FOSSology Scan Action </strong><br>
<br>

<a href=https://github.com/fossology/fossology/wiki/FOSSology-scanners-in-CI><img alt="Fossology-action" src="https://img.shields.io/badge/Fossology-action-red"></a>
<a href=https://join.slack.com/t/fossology/shared_invite/enQtNzI0OTEzMTk0MjYzLTYyZWQxNDc0N2JiZGU2YmI3YmI1NjE4NDVjOGYxMTVjNGY3Y2MzZmM1OGZmMWI5NTRjMzJlNjExZGU2N2I5NGY><img alt="Artifacts generation" src="https://img.shields.io/badge/slack-fossology-blue.svg?longCache=true&logo=slack"></a>
<a href=https://www.youtube.com/channel/UCZGPJnQZVnEPQWxOuNamLpw><img alt="GitHub last commit (branch)" src="https://img.shields.io/badge/youtube-FOSSology-red.svg?&logo=youtube&link=https://www.youtube.com/channel/UCZGPJnQZVnEPQWxOuNamLpw"></a>

</p>

# Fossology Action

## Overview

The **Fossology Scan** GitHub Action allows you to run license and copyright scans using the Fossology scanner within your GitHub Actions workflows. This action is highly customizable and supports various scanning modes and configurations to fit your compliance needs.

## Features

### Types of scanners
- Perform license and copyright scans
  - [`Nomos`](https://github.com/fossology/fossology/tree/master/src/nomos): It is a very precise license scanner.
  - [`Ojo`](https://github.com/fossology/fossology/tree/master/src/ojo): It is a precise license scanner that looks for `SPDX-License-Identifier text` statements.
- Copyright and Keyword Scanning
  - [`Copyright`](https://github.com/fossology/fossology/tree/master/src/copyright): Scans for Copyrighted text like `Copyright 2024 @ Fossology-contributors`
  - [`Keyword`](https://github.com/fossology/fossology/tree/master/src/copyright): Scans for potentially harmful keywords like `patented`, `copied__from` etc. (Customizable)

### Different Scanning Modes
  - **Diff Scan (Default)**: This scans for only the diff content of the Pull Request on which it is triggered. This is a good option to run via a Pull Request trigger.
  - **Repo Scan**: This scans the entire repo from which the pipeline is triggered. It is a good option to run on PR's or publishing releases.
  - **Differential Scan**: This scans for the changes between any two tags. User can provide any tow tags to scan between. It is a good option to scan between any two tags or any two versions of the repo.

### Per-Dependency Report Generation (NEW)
The action now supports generating individual SBOM reports for each dependency scanned. This is useful for:
- **Capycli/SW360 Integration**: Upload individual scan reports per component to your CAP system
- **Fine-grained Compliance**: Track license compliance per dependency
- **Audit Trails**: Maintain separate reports for each component in your inventory

Enable with `per_dependency_report: true` to generate individual reports in the `per-dependency-reports` directory.

You can learn more about CI Scanners in fossology [here](https://github.com/fossology/fossology/wiki/FOSSology-scanners-in-CI)

## Inputs

### User customizable inputs:
```yaml
scan_mode:
  description: "Run the scan in one of the following modes: repo, differential, scan-only-deps, scan-dir"
  required: false
  default: "diff"
scanners:
  description: "One of the scanner to invoke: nomos, copyright, keyword, ojo"
  required: false
  default: "nomos ojo copyright keyword"
report_format:
  description: "Report format to generate reports in: TEXT, SPDX_JSON, SPDX_YAML, SPDX_RDF, SPDX_TAG_VALUE, SPDX3_JSON, SPDX3_TTL, SPDX3_RDF"
  required: false
  default: "TEXT"
keyword_conf_file_path:
  description: "Path to custom keyword.conf file"
  required: false
  default: ""
allowlist_file_path:
  description: "Path to allowlist.json file"
  required: false
  default: ""
from_tag:
  description: "If in differential mode, can provide a starting tag to scan from. Ex. v1"
  required: false
  default: ""
to_tag:
  description: "If in differential mode, can provide an ending tag to scan to. Ex. v2"
  required: false
  default: ""
sbom_path:
  description: "If in scan-only-deps mode, path of of the SBOM file to scan."
  required: false
  default: "sbom.json"
scan_dir:
  description: "If in scan-dir mode, path of the directory to scan."
  required: false
  default: ""
per_dependency_report:
  description: "Generate individual SBOM reports per dependency after scanning. Set to 'true' to enable."
  required: false
  default: "false"
report_dir:
  description: "Output directory for per-dependency reports."
  required: false
  default: "per-dependency-reports"
```

### Inputs used internally by the action:

```yaml
github_api_url:
  description: "Base URL of the GitHub API (default: ${{ github.api_url }})"
  required: false
  default: ${{ github.api_url }}
github_repository:
  description: "Repository name (default: ${{ github.repository }})"
  required: false
  default: ${{ github.repository }}
github_token:
  description: "GitHub Token (default: ${{ github.token }})"
  required: false
  default: ${{ github.token }}
github_pull_request:
  description: "GitHub PR number (default: ${{ github.event.number }})"
  required: false
  default: ${{ github.event.number }}
github_repo_url:
  description: "GitHub Repo URL (default: ${{ github.repositoryUrl }})"
  required: false
  default: ${{ github.repositoryUrl }}
github_repo_owner:
  description: "GitHub Repo Owner (default: ${{ github.repository_owner }})"
  required: false
  default: ${{ github.repository_owner }}
```

## Example Workflow
Below is an example of how to use the **Fossology Scan** GitHub Action in your workflows.

### Pull request scans
```yaml
name: License scan on PR

on: [pull_request]

jobs:
  compliance_check:
    runs-on: ubuntu-latest
    name: Perform license scan
    steps:
    - name: Checkout
      uses: actions/checkout@v2

    - name: License check
      id: compliance
      uses: fossology/fossology-action@v1
      with:
        scan_mode: ''
        scanners: 'nomos ojo'
        report_format: 'SPDX_JSON'

```

### Tag scans
```yaml
name: License scan on tags

on: [tags]

jobs:
  compliance_check:
    runs-on: ubuntu-latest
    name: Perform license scan
    steps:
    - name: Checkout
      uses: actions/checkout@v2
    - name: License check
      id: compliance
      uses: fossology/fossology-action@v1
      with:
        scan_mode: 'differential'
        scanners: 'nomos ojo copyright keyword'
        from_tag: 'v003'
        to_tag: 'v004'
        report_format: 'SPDX_JSON'
```

### Dependency Scans
```yaml
name: Software Composition Analysis

on:
  push:
    paths:
      - pyproject.toml
      - poetry.lock
  schedule:
    - cron: '0 0 * * 0'  # Midnight, Sunday

permissions:
  contents: read
  actions: write

jobs:
  sbom:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v5

      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: 'pip'

      - name: Install CDX Python
        run: python3 -m pip install cyclonedx-bom

      - name: Generate CDX SBOM
        run: python3 -m cyclonedx_py poetry --spec-version 1.6 --output-format JSON --output-file sbom.json --validate

      - uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.json
          if-no-files-found: error

  sca:
    runs-on: ubuntu-latest
    needs: sbom
    steps:
      - name: Checkout
        uses: actions/checkout@v5

      - name: Download SBOM
        uses: actions/download-artifact@v4
        with:
          name: sbom

      - name: Run FOSSology analysis
        id: fossology
        uses: fossology/fossology-action@v1
        with:
          scan_mode: "scan-only-deps"
          scanners: |
            - nomos
            - ojo
            - copyright
          report_format: "SPDX_JSON"
          sbom_path: "sbom.json"

      - name: Upload Scan Results Artifact
        if: success() || failure()
        uses: actions/upload-artifact@v4
        with:
          name: Fossology scan results
          path: results/
```

### Dependency Scans with Per-Dependency Reports (Capycli/SW360 Integration)
```yaml
name: SCA with Per-Dependency Reports

on:
  push:
    paths:
      - pyproject.toml
      - poetry.lock

permissions:
  contents: read
  actions: write

jobs:
  sbom:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v5

      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: 'pip'

      - name: Install CDX Python
        run: python3 -m pip install cyclonedx-bom

      - name: Generate CDX SBOM
        run: python3 -m cyclonedx_py poetry --spec-version 1.6 --output-format JSON --output-file sbom.json --validate

      - uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.json
          if-no-files-found: error

  sca:
    runs-on: ubuntu-latest
    needs: sbom
    steps:
      - name: Checkout
        uses: actions/checkout@v5

      - name: Download SBOM
        uses: actions/download-artifact@v4
        with:
          name: sbom

      - name: Run FOSSology analysis with per-dependency reports
        id: fossology
        uses: fossology/fossology-action@v1
        with:
          scan_mode: "scan-only-deps"
          scanners: |
            - nomos
            - ojo
            - copyright
          report_format: "SPDX_JSON"
          sbom_path: "sbom.json"
          per_dependency_report: "true"
          report_dir: "per-dependency-reports"

      - name: Upload Consolidated Scan Results
        if: success() || failure()
        uses: actions/upload-artifact@v4
        with:
          name: Fossology consolidated report
          path: results/

      - name: Upload Per-Dependency Reports
        if: success() || failure()
        uses: actions/upload-artifact@v4
        with:
          name: Fossology per-dependency reports
          path: per-dependency-reports/

  capycli-upload:
    runs-on: ubuntu-latest
    needs: sca
    steps:
      - name: Download Per-Dependency Reports
        uses: actions/download-artifact@v4
        with:
          name: Fossology per-dependency reports
          path: per-dependency-reports/

      - name: Upload reports to CAP/SW360 using Capycli
        run: |
          # Upload each per-dependency report to the CAP system
          for report in per-dependency-reports/*.spdx.json; do
            if [ "$(basename $report)" != "manifest.json" ]; then
              echo "Uploading: $report"
              # capycli upload report --file "$report" --component "$(basename $report)"
            fi
          done
```

## License

This project is licensed under the [GNU GENERAL PUBLIC LICENSE Version 2, June 1991](LICENSE).
