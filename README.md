# Container Image Analysis in build pipelines

## tl;dr
This tool is built to perform container image analysis in build pipelines leveraging open-source tools. The artifacts generated for each container image are:
<ul>
    <li> **Software bill-of-material (SBOM)** of all dependencies
    <li> Up-to-date **vulnerability scan** based on the generated SBOM
    <li> **Signed attestation** (verifyable artifacts)
</ul>
A custom Github action integrated into the build pipeline of a image repository generates above artifacts and notifies a django-based application which collects the artifacts and stores them centrally. The information is visualized within a dashboard enabling an organisations security team to keeping tracover the organisations images, their dependencies and found vulnerabilities. To enhance supply chain security, signed provenance is generated within an attestation file in alignment with the SLSA framework.

## Introduction
With the digitalisation and the high degree of interconnectedness between firms, supply chain attacks have been on the rise. Security incidents such as those resulting from attacks like SolarWinds or Kaseya increased awareness and attention towards mitigating supply chain risks and investing into supply chain security.

Container images are often only scanned after they have been built and published to image registries. This allows 'unsafe' images to run in production. Integrating vulnerability scanning into the build pipeline which acts as a quality gate mitigates that risk. Having a precise overview of what dependencies are used within images as well as highlighting known CVEs, is necessary information organisations should be aware of. Versions that fix known vulnerabilities are indicated and provide a clear path to fix for developers. 
The action also generates attestation including build parameters for each image which is cryptographically signed to be verifyable afterwards.

## Tools and Frameworks Used
The tools build upon are all open-source and actively maintained.

### Syft

### Grype

### Supply Chain Levels for Software Artifacts (SLSA)

### Pipeline

### Architecture
- Architecture Picture (Notify and Pull, Django)
- Advantages of that approach


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

## Contributing

## Future Work
- Integration of more scanning tools
- Enhance the visualisation of the results
- Lifecycle Management (add more repositories, remove repositories)
- Advantages of that approach (SIEM, Rule Engines)
