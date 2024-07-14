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

You can learn more about CI Scanners in fossology [here](https://github.com/fossology/fossology/wiki/FOSSology-scanners-in-CI)

## Inputs

### User customizable inputs:
```yaml
scan_mode:
  description: "Specifies whether to perform diff scans, repo scans, or differential scans.
    Leave blank for diff scans."
  required: false
  default: ""
scanners:
  description: "Space-separated list of scanners to invoke."
  required: true
  default: "nomos ojo copyright keyword"
report_format:
  description: "Report format (SPDX_JSON,SPDX_RDF,SPDX_YAML,SPDX_TAG_VALUE) to print the results in."
  required: false
  default: ""
keyword_conf_file_path:
  description: "Path to custom keyword.conf file. (Use only with keyword scanner set to True)"
  required: false
  default: ""
allowlist_file_path:
  description: "Path to allowlist.json file."
  required: false
  default: ""
from_tag:
  description: "Starting tag to scan from. (Use only with differential mode)"
  required: false
  default: ""
to_tag:
  description: "Ending tag to scan to. (Use only with differential mode)"
  required: false
  default: ""
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
        scan-mode: 'differential'
        scanners: 'nomos ojo copyright keyword'
        from_tag: 'v003'
        to_tag: 'v004'
        report_format: 'SPDX_JSON'
```

## License

This project is licensed under the [GNU GENERAL PUBLIC LICENSE Version 2, June 1991](LICENSE).