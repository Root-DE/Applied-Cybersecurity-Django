# Container Image Analysis in Build Pipelines
Scanning container images for vulnerabilities and generating signed provenance aligned with SLSA.
## tl;dr
This tool is built to perform container image analysis in build pipelines leveraging open-source tools. The artifacts generated for each container image are:

- 🗃 **Software bill-of-material (SBOM)** of all dependencies
- 🔥 Up-to-date **vulnerability scan** based on the generated SBOM
- 🔏 **Signed attestation** (verifiable artifacts)

A custom GitHub action integrated into the build pipeline of an image repository generates above artifacts and notifies a Django-based application which collects the artifacts and stores them centrally. The information is visualized within a dashboard enabling an organizations security team to keep track over the organizations images, their dependencies and found vulnerabilities. To enhance supply chain security, signed provenance is generated within an attestation file in alignment with the SLSA framework.

<p align="center">
    <img src="./docs/tool_screenshots.jpg" height="550px">
</p>
<p align="center">Screenshots taken from the tools UI</p>

## Introduction
With the digitalization and the high degree of interconnectedness between firms, supply chain attacks have been on the rise. Security incidents such as those resulting from attacks like SolarWinds or Kaseya increased awareness and attention towards mitigating supply chain risks and investing into supply chain security.

Container images are often only scanned after they have been built and published to image registries. This allows 'unsafe' images to run in production. Integrating vulnerability scanning into the build pipeline which acts as a quality gate mitigates that risk. Having a precise overview of what dependencies are used within images as well as highlighting known CVEs, is necessary information organizations should be aware of. Versions that fix known vulnerabilities are indicated and provide a clear path to fix for developers. 
The action also generates attestation including build parameters for each image which is cryptographically signed to be verifiable afterwards

## Tools and Frameworks Used
The tools build upon are all open-source and actively maintained. These are [Syft](https://github.com/anchore/syft) and [Grype](https://github.com/anchore/grype) which are maintained by [Anchore](https://github.com/anchore) as well as the [SLSA framework](https://slsa.dev/).

### Syft
Syft is an open-source tool for generating a Software Bill of Material (SBOM for short), and is developed by the company Anchore. A SBOM is also often referred to as a code base inventory, since it contains all identifiable components, including their license and version information. This inventory of the code should then make it possible later to recognize and eliminate weak points or also license-legal pitfalls more effectively. 

A very important feature of Syft is that not only entire project folders, but also container images can be scanned. Furthermore, the tool supports 18 different ecosystems, such as Alpine, Rust, Go, Java or Python. A sample output of Syft (applied to the image {IMAGENAME}) can be viewed here {ref}. Of particular interest is the list of artifacts found, as these are subsequently used to identify vulnerabilities. Information such as the name of the artifact, the exact version and the unique identifiers like the Common Platform Enumeration (CPE) or the Package URL (PURL) are therefore particularly important. Other more informative data, are barely considered by us at the moment, because the focus should be on the vulnerabilities first. Information such as the description of the artifact, the licenses or even the metadata are therefore neglected in the current version. However, if the focus of the project is later expanded to include the software used in the organization, such information can add further value for the company. 

+ mention available formats

### Grype
Once Syft generated a detailed SBOM, the next step is to scan all found artifacts for vulnerabilities. For this we use a tool called Grype, which is also developed by Anchore and therefore works together with Syft's SBOM without any problems.

All vulnerability information is managed by Grype in its own database and kept up to date by a daily update. The database is made up of many different publicly available sources. These sources include the National Vulnerability Database (NVD), the Alpine Linux SecDB, the RedHat Linux Security Data and many more. Using these sources, Grype is able to find vulnerabilities in the most common operating system packages (for example, Alpine, CentOS, Debian, etc.) and in many language-specific packages (for example, Java, Python, PHP, Rust, etc.). 

The result of a Grype scan on the Syft SBOM already considered in section {ref} can be seen here{ref}. In contrast to the artifact information, this time we are interested in identifying data (for example, CVE-ID), as well as informative data, such as the description of the vulnerability, the Common Vulnerability Scoring System (CVSS), or even information about a possible fix. We then display this data on our dashboard, giving developers an initial overview of the security of their container images. In addition to the data provided by Grype, we also determine the so-called best-secure version, which should also allow developers to easily resolve vulnerabilities.

This best-secure-version functionality will be examined in more detail below.

#### Next-Secure-Version feature
In a vulnerability identification tool, one of the most important pieces of information for developers is the next version of software in which the vulnerabilities have been fixed. Since Grype provides this information, we can give the developers recommendations for action in the respective scan summaries. So, if a build process could not be executed because of too extensive vulnerabilities, it is often enough to look at the dashboard and update to the version listed there.

However, it may also happen in some cases that this update does not automatically lead to an increase in security. If the version in which the initial vulnerability was fixed contains one or more new vulnerabilities, security may even be reduced in the worst case. For this reason, in addition to the Grype information, we introduce the Next-Secure version. This feature checks whether there is a newer version of the software used that does not have any known vulnerabilities. To do this, we check the fix versions given by Grype for new vulnerabilities by sending another request to Grype. If further vulnerabilities exist, we again request Grype with the next supposedly secure versions. This will continue until either a safe version is found or there are no known updates. In the second case, we do not make any recommendations for action, as it is difficult for us to decide which vulnerabilities are the least critical for the respective company without appropriate background knowledge. In this case, the developers have to decide for themselves whether an update to a different version makes sense or whether one should try to avoid the vulnerabilities in other ways.


### Supply Chain Levels for Software Artifacts (SLSA)
SLSA is a security framework that has been developed to prevent tampering, improve integrity, and secure packages and infrastructure in projects. Under given conditions, an attacker could exploit various attack vectors within a supply chain. SLSA differs between 
- **source** integrity,
- build integrity, 
- and integrity of third-party dependencies

SLSA defines four levels of compliance that can be achieved with higher security requirements:

|   SLSA Level  |   Requirements    |
|:---:  |:---:  |
|   1   |   Documentation of the build process  |
|   2   |   Tamper resistance of the build service  |
|   3   |   Extra resistance to specific threats    |
|   4   |   Highest levels of confidence and trust  |

For a more detailed description of each level's requirements, please see the [official SLSA documentation](https://slsa.dev/spec/v0.1/levels).

Besides the [framework itself](https://slsa.dev/spec/v0.1/index) which is currently in alpha, the SLSA developers maintain a [repository](https://github.com/slsa-framework/slsa-github-generator) providing helpful tools to achieve SLSA compliance.

#### What SLSA artifacts does this project produce?
This project generates a signed provenance for scanned container images. The attestation is generated through signing a predicate file containing environment variables of the build process in a format which is compliant with the SLSA framework.

An example as well as the structure of the provenance artifact can be found [here](https://slsa.dev/provenance/v0.2).

### Pipeline
<p align="center">
    <img src="./docs/pipeline.png" width="550px">
</p>
<p align="center">The Pipeline</p>
The pipeline (see above) runs whenever there are changes to the repository through a push when a release is created and daily at 9am UTC. The daily scan is necessary because the container can use software that was not known to be vulnerable during the last scan but is now.

In the first step, the pipeline builds the Docker Image. As can be seen below, meta information about the build process, such as the architecture of the GitHub runner, is generated in addition to the build image, and the digest of the image. From the metainformation and the digest, the provenance is now generated. Afterwards it is signed keyless via cosign (see [here](https://github.com/sigstore/cosign/blob/main/KEYLESS.md)). As part of the process, the signature is written to both the Transparency Logs and, along with the provenance, the GitHub Container Registry (ghcr.io). The Image is then also pushed to the Container Registry.

The image we use to scan for Vulnerabilities is also on ghcr.io. This scan image now takes the previously built image as input and generates the SBOM and a list of vulnerabilities, which are then transferred to the backend via the notify and pull approach as described in the section [Architecture](#architecture).

<p align="center">
    <img src="./docs/build.png" width="550px">
</p>
<p align="center">The Build Process</p>

### Architecture
<p align="center">
    <img src="./docs/architecture.png" width="550px">
</p>
<p align="center">The Architecture</p>

The architecture consists of a container-based approach with Docker because containers are lightweight and require less resources than VMs. Containers are easy to deploy and can be deployed on any environment where Docker runs. Django web framework is used for the project because it is a high-level Python Web framework that encourages rapid development and clean, pragmatic design. Nginx is used as proxy and to deliver the statics, but this is not relevant for the concept behind it, therefore not in the graphic. A personal access token for GitHub is stored in Django. The account behind it has access to the runs of the actions of several repositories. Each repo performs image scanning as well as the generation of an SBOM.

To keep the scanning with its databases as well as the creation of the SBOMs always up to date, the image used for this (along with the database behind it) is rebuilt daily. After the repos have been scanned, they send a notification to Django, which leads to the subsequent loading, saving, and processing of the artifacts that result from a scan.

## Installation
1. Download and install Docker for your system as described here [How to install Docker](https://docs.docker.com/get-docker/)
2. Download this repository by running `git clone https://github.com/Root-DE/Applied-Cybersecurity-Django`
2. Create a copy of the [template.env](./template.env) file, rename it to `.env`, and fill it with your own values
3. Adapt the [nginx configuration file](./nginx/conf.d/nginx_django.conf) to your needs or remove the configuration file
4. Run `docker-compose up -d` to start the application. This will start nginx, the Django application, the database and Adminer where you can see the current state of the database. If you do not want to use Adminer, you can remove the Adminer container from the docker-compose.yml file.
5. Open your browser and go to https://your-domain/ to see the dashboard.
6. Set up the GitHub actions for each repository to trigger the scan by copying the [scan.yml](./.github/workflows/scan.yml) to the *.github/workflows/* directory of the respective repository. 

## User Interface Functionalities
### Authentication
Before having access to the platform itself and its findings, a user has to login first. The initial credentials for the admin should be set as described in [Installation](#installation).
<p align="center">
    <img src="./docs/login.png" height="550px">
</p>
<p align="center">User Authentication</p>

### Dashboard Overview
The main landing page providing an overview over all repositories that are connected is the dashboard shown below. 
<p align="center">
    <img src="./docs/dashboard_example.png" width="450px">
</p>
<p align="center">Dashboard</p>
Each repository running the workflow is represented as a single card which shows the repository name and the information on the latest scan that ran:

- Timestamp
- Number of found dependencies in SBOM
- Number of Vulnerabilities

Hovering over the card shows the background which gives an overview of the risk categories of the vulnerabilities based on their CVSS score.

When using more than one organization to structure GitHub repositories, the organization filter can be used to only show repositories that belong to a specific organization. When operating a high amount of repositories, the search functionality can be used to look for specific repositories. 

The search functionality can also be used to look for repositories that contain a specific CVE-ID to quickly identify potential risks.

### Details
By clicking on a repository-card, the detail page of that given repository is shown.
The detail page contains information on the repository itself as well as scans that ran. When clicking on the repository, details of the latest scan are shown.

<p align="center">
    <img src="./docs/details_1.png" width="550px">
</p>
<p align="center">Details - Time Series Graph</p>

On the top of the details page, a time series graph is shown that is displaying the number of vulnerabilities found for each category, also based on the CVSS score.
By clicking on one of the past data points in the graph, the information for the selected scan is displayed on the page below. The database also integrates the vulnerability history so that the vulnerability information is up to date for the date it ran.

<p align="center">
    <img src="./docs/details_2.png" width="550px">
</p>
<p align="center">Details - Detail Data</p>

Above screenshot shows the repository and scan information that is displayed. The box on the bottom-left is currently only a placeholder and shows the SLSA requirements for reaching specific levels of compliance. Work todo is currently listed in the section [Future Work](#future-work).

<p align="center">
    <img src="./docs/details_3.png" width="550px">
</p>
<p align="center">Details - Vulnerability Table</p>

Scrolling down, the result of the vulnerability scan is shown. A scan can be selected using the date-time-picker. A search bar enables the user to look for specific vulnerabilities. Displayed information contain:

- CVE-ID
- Severity
- Status (Fix available?)
- CVSS Score

The SBOM as well as the vulnerability information is also written to the database. Using the export buttons, the SBOM as well as the vulnerability information can be exported for further processing.

By clicking one of the vulnerabilities, more information is shown so that the user can assess what the vulnerability itself is about and which dependencies and versions are vulnerable. 

<p align="center">
    <img src="./docs/details_4.png" width="550px">
</p>
<p align="center">Details - Vulnerability Specifics</p>

Information on the vulnerable software versions, a fix (if existing), a description as well as a link to the official NVD database is included.

<p align="center">
    <img src="./docs/details_5.png" width="550px">
</p>
<p align="center">Details - Known Exploited Vulnerabilities</p>

If one of the vulnerabilities that is found by Grype's vulnerability scan is within the "Known Exploited Vulnerabilities" list which is maintained by [CISA](https://www.cisa.gov/known-exploited-vulnerabilities-catalog), the vulnerability is marked as above to support prioritization within the vulnerability management process. Note: The above vulnerability is marked manually as currently being exploited to demonstrate the feature.

## Contributing
@Root-DE - Till Nowakowski

@jobroe10 - Jonas Schmitz

@BrianPfitz - Brian Pfitzmann

## Future Work
- Integration of more scanning tools
- Enhance the visualization of the results
- Lifecycle Management (add more repositories, remove repositories)
- Advantages of that approach (SIEM, Rule Engines)
