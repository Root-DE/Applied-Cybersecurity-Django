# Container Image Analysis in build pipelines

## tl;dr
This tool is built to perform container image analysis in build pipelines leveraging open-source tools. The artifacts generated for each container image are:
<ul>
    <li> **Software bill-of-material (SBOM)** of all dependencies
    <li> Up-to-date **vulnerability scan** based on the generated SBOM
    <li> **Signed attestation** in compliance with the [SLSA framework](https://slsa.dev/)
</ul>
The results are centrally collected and visualized within a dashboard giving an overview over the organisations images as well as vulnerability scans.

- Why?
    - Vulnerability Scanning (in Container Images)
    - Supply Chain Security
    - SBOM/Dependency Management
    
## Introduction

## Installation
- [Docker](https://www.docker.com/)
- download the docker compose file
- run ´docker-compose up -d´ to start the application
- setup the GitHub Actions to trigger the scan:
    - [GitHub Actions]

## Usage
- Threshold
- Dashboard Overview (Cards, Search Function)
- Details


## Architecture
- Architecture Picture (Notify and Pull, Django)
- Advantages of that approach

## Contributing

## Future Work
- Integration of more scanning tools
- Enhance the visualisation of the results
- Lifecycle Management (add more repositories, remove repositories)
- Advantages of that approach (SIEM, Rule Engines)
