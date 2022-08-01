# Container Image Analysis in Build Pipelines

## tl;dr
This tool is built to perform container image analysis in build pipelines leveraging open-source tools. The artifacts generated for each container image are:
- 🗃 **Software bill-of-material (SBOM)** of all dependencies
- 🔍 Up-to-date **vulnerability scan** based on the generated SBOM
- 🔏 **Signed attestation** (verifyable artifacts)

A custom Github action integrated into the build pipeline of a image repository generates above artifacts and notifies a django-based application which collects the artifacts and stores them centrally. The information is visualized within a dashboard enabling an organisations security team to keeping tracover the organisations images, their dependencies and found vulnerabilities. To enhance supply chain security, signed provenance is generated within an attestation file in alignment with the SLSA framework.

![dashboard-example](./docs/tool_screenshots.jpg)
<p align= "center">Screenshots taken from the tools UI</p>

## Introduction
With the digitalisation and the high degree of interconnectedness between firms, supply chain attacks have been on the rise. Security incidents such as those resulting from attacks like SolarWinds or Kaseya increased awareness and attention towards mitigating supply chain risks and investing into supply chain security.

Container images are often only scanned after they have been built and published to image registries. This allows 'unsafe' images to run in production. Integrating vulnerability scanning into the build pipeline which acts as a quality gate mitigates that risk. Having a precise overview of what dependencies are used within images as well as highlighting known CVEs, is necessary information organisations should be aware of. Versions that fix known vulnerabilities are indicated and provide a clear path to fix for developers. 
The action also generates attestation including build parameters for each image which is cryptographically signed to be verifyable afterwards.

## Tools and Frameworks Used
The tools build upon are all open-source and actively maintained. These are [Syft](https://github.com/anchore/syft) and [Grype](https://github.com/anchore/grype) which are maintained by [Anchore](https://github.com/anchore) as well as the [SLSA framework](https://slsa.dev/).

### Syft

### Grype

### Supply Chain Levels for Software Artifacts (SLSA)
SLSA is a security framework that has been developed to prevent tampering, improve integrity, and secure packages and infrastructure in projects. Under given conditions, an attacker could exploit various attack vectors within a supply chain. SLSA differs between 
- **source** integrity,
- build integrity, 
- and integrity of third-party dependencies

SLSA defines 4 levels of compliance that can be achieved with higher security requirements:

|   SLSA Level	|   Requirements	|
|:---:	|:---:	|
|   1	|   Documentation of the build process	|
|   2	|   Tamper resistance of the build service	|
|   3	|   Extra resistance to specific threats	|
|   4	|   Highest levels of confidence and trust	|

For a more detailled description of each level's requirements, please see the [official SLSA documentation](https://slsa.dev/spec/v0.1/levels).

Besides the [framework itself](https://slsa.dev/spec/v0.1/index) which is currently in alpha, the SLSA developers maintain a [repository](https://github.com/slsa-framework/slsa-github-generator) providing helpful tools to achieve SLSA compliance.

#### What SLSA artifacts does this project produce?
This project generates a signed provenance for scanned container images. The attestation is generated through signing a predicate file containing environment variables of the build process in a format which is compliant with the SLSA framework.

An example as well as the structure of the provanence artifact can be found [here](https://slsa.dev/provenance/v0.2).


### Pipeline

### Architecture
![architecture](./docs/architecture.png)
- Architecture Picture (Notify and Pull, Django)
- Advantages of that approach


## Installation
1. Download and install Docker for your system as described here [How to install Docker](https://docs.docker.com/get-docker/)
2. Download this repository by running `git clone https://github.com/Root-DE/Applied-Cybersecurity-Django`
2. Create a copy of the [template.env](./template.env) file, rename it to `.env`, and fill it with your own values
3. Adapt the [nginx configuration file](./nginx/conf.d/nginx_django.conf) to your needs or remove the configuration file
4. Run `docker-compose up -d` to start the application. This will start nginx, the django application, the database and adminer where you can see the current state of the database. If you don't want to use adminer, you can remove the adminer container from the docker-compose.yml file.
5. Open your browser and go to https://your-domain/ to see the dashboard.
6. Set up the GitHub actions for each repository to trigger the scan by copying the [scan.yml](./.github/workflows/scan.yml) to the *.github/workflows/* directory of the respective repository. 

## Usage
### Dashboard Overview (Cards, Search Function)
![dashboard-example](./docs/dashboard_example.png)
<p style="text-align: center;">Screenshots taken from the tools UI</p>

### Details
![details-example-1](./docs/details_1.png)
<p style="text-align: center;">Screenshots taken from the tools UI</p>

![details-example-2](./docs/details_2.png)
<p style="text-align: center;">Screenshots taken from the tools UI</p>

![details-example-3](./docs/details_3.png)
<p style="text-align: center;">Screenshots taken from the tools UI</p>

## Contributing

## Future Work
- Integration of more scanning tools
- Enhance the visualisation of the results
- Lifecycle Management (add more repositories, remove repositories)
- Advantages of that approach (SIEM, Rule Engines)
