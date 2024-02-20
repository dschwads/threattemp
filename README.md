this is temporary and will be deleted


# Sysdig Threat Generator

This repo hosts combinations of tools, both public and private, for generating test scenarios.

# Getting Started
## Cloning WITHOUT LFS
`GIT_LFS_SKIP_SMUDGE=1 git clone git@github.com:sysdig/sysdig-threat-generator.git`
## Building an image
You can build your own Docker image with the files provided in `docker/`, with the following command:
`cd docker && docker build -t sysdig-threat-generator`. If you would like to build Docker image for `arm64` you can run following command: `cd docker && docker build --platform linux/arm64 -f Dockerfile.arm64 -t sysdig-threat-generator .`
## prebuilt images available!
You can also pull a prebuilt image from Docker Hub: `docker pull dockerbadboy/art:latest`.

Or, you can simply create a Kubernetes pod using a pre-built image from the YAML in `kubernetes/`.  

Supporting scripts and other tools are located in `scripts/`.

If you must run it on-host, use `docker/hostmode.sh` to install and then you can invoke `./docker/RunTests.ps1` directly.
## Example Syntax

### Docker
To run some container tests in local Docker, with your locally built image:
`docker run -it --rm sysdig-threat-generator:latest /bin/bash -c "pwsh RunTests.ps1 BASE64.SHELLSCRIPT <NAME.OF.OTHER.TEST> <TEST3> <...>"`
To run some container tests in local Docker, with the image from Docker Hub:
`docker run -it --rm dockerbadboy/art /bin/bash -c "pwsh RunTests.ps1 BASE64.SHELLSCRIPT <NAME.OF.OTHER.TEST> <TEST3> <...>"`

### Kubernetes
To run the same, but in K8s:
change line 20 of `Sysdig-Threat_Generator.yaml` from 

```yaml
command: ["pwsh", "-c", "(./RunTests.ps1 XMRIG.EXEC)"]
```

to

```yaml
command: ["pwsh", "-c", "(./RunTests.ps1 BASE64.SHELLSCRIPT <NAME.OF.OTHER.TEST> <...>)"]
```

### Fargate
A minimal set of terraform files that are compatible with STG and Fargate can be found at [minimal-fargate-stg](https://github.com/sysdig/minimal_fargate_stg). The only variables you *should* need to change are in [`variables.tf`](https://github.com/sysdig/minimal_fargate_stg/blob/master/variables.tf). Note that for the VPC Subnets, one must be public and the other private. Edit [`workload.tf`](https://github.com/sysdig/minimal_fargate_stg/blob/master/workload.tf#L12) with your desired tests, similarly to how we did in the K8s yaml file.
Please raise any issues/concerns in #sds-f-fargate in Slack.

# Example Tests, with Descriptions, and associated Rules
A brief description of some tests and the related alert/purpose:
| Test  | Description   |Sysdig Rule  | Caveat |Storyline |
|---|---|---|---|---|
|  XMRIG.EXEC |Malware injected into container, cryptominer, new files/drift detection   | Cryptominer Pool, Cryptominer ML, new malicious binary  |ML Policy needs to be manually enabled | This test can be positioned as a post-exploit attack chain. It downloads an obfuscated version of XMRig (it's packed with [UPX](https://upx.github.io)), which is then executed from /tmp. Cryptojackers will most commonly use XMRig due to its (the currency Monero, AKA XMR's) privacy guarantees. 
| STDIN.NETWORK  | Network anomaly, rev shell   | Reverse Shell to network socket  |   |Dead-simple reverse shell.   |
| DEV.SHM.EXEC  |In-mem malware    | Execution from /dev/shm  |kubernetes will block this by default, since /dev/shm has `noexec`   |This is a CSPM opportunity, since kubernetes by default will block unprivileged containers from executing binaries from /dev/shm. If the container/deployment is running as privileged, no such block will occur.   |
|T1048 |Data Exfiltration| Remote File Copy Tools in Container | | This attack uses `rsync` inside of a container in order to simulate data exfiltration. 
|RECON.FIND.SUID | Reconnaisance for SUID Binaries | Recon SUID Binary | | This attack uses `find` to locate binaries on the container filesystem with the `setuid` bit set. These binaries can be (ab)used to escalate privileges inside a container or on a host system.
| T1611.002| Container Escape | Attempted Container Escape| Requires container to be run as privileged| This attack will mount the host filesystem inside the container to perform a container escape.
|CONTAINER.ESCAPE.NSENTER| `nsenter` Container Escape| nsenter Container Escape| only affects vulnerable systems
| CREDS.DUMP.MEMORY | Dumps system memory via Lazagne, looking for credentials |Dump Memory for Credentials | Needs --privileged|This attack will create a user and spawn a process that LazaGne (a linux memory introspection/extraction tool) looks for credentials inside of. This is an example of a reconaissance-type attack, typically occuring as an attacker looks to pivot laterally around a network or collect data to later exfiltrate. |
|KILL.MALICIOUS.PROC | Kills a known malicious process, simulating an adversary taking down other cryptominers on a target system. | Kill Malicious Process | |This test simulates what happens when an adversary first gets on a system, and is preparing to run their own malware. Adversaries, much like defenders, keep tabs on other adversaries, so that they are prepared to remove the competition when they attack a vulnerable system. 
|MEMFD.EXEC| Writes and then executes an ELF File to/from a `memfd`, an in-memory file descriptor (medium to advanced malware technique). | TBC (needs agent support)
|SUBTERFUGE.CURL.SOCKS| Uses a SOCKS proxy to get on the Tor network. |TBD| |This is an example of subterfuge/obfuscation. The [SOCKS protocol](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwi854ajsZj9AhWhVTABHU38BEEQFnoECBEQAQ&url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FSOCKS&usg=AOvVaw3p6wo6vtXym4_o-Pby3-za) is used here to evade a simple network firewall that blocks Tor traffic.|
|LOAD.BPF.PROG| Creates and then loads a BPF program into the kernel| BPFDoor | Requires root privilege| A gutted version of [BPFDoor](https://sysdig.com/blog/bpfdoor-falco-detection/) is run, see the linked article for a full rundown of the real BPFDoor from STRT. 
|Base64.PYTHON| Decodes a python script via base64| Base64 Python Script | | This is a simple one-off test to show that we catch Python scripts in addition to the following tests (CLI, Shell scripts) encoded w/ Base64. Attackers use base64 so that their contents don't show up on a tool like Sysdig Secure in plain text. Base64 is also useful for transferring binary data (think: executables) over a text protocol.
|BASE64.CLI| Uses the base64 utility to decode some commands| Base64 on Command Line
|Base64.SHELLSCRIPT| Uses the base64 utility to decode and write a shell script| Base64 Shell Script
|CONNECT.UNEXPECTED| Creates a connection from an "unexpected" process, as if someone had pwned a server and hijacked control to their c2 server| Connect Unexpected| | This one is a bit of a leap. Sometimes, customers want to know, for example, if their NGINX process is talking on a different port than it should be, or, were it to be exploited, if it is listening on a port it shouldn't be. This rule and test covers those cases - in the test, a process named "kmsd" is listening on the network.   
|RECON.GPG| Searches for gpg key data | GPG Key Reconnaisance| | Similar to other recon tests, this is positionable as a lateral movement attempt. GPG keys and keyrings are used primarily in GPG encryption. 
|SUBTERFUGE.LASTLOG| Edits and deletes a lastlog file entry | Lastlog Files Cleared| | This attack will show that we are detecting threat actors that attempt to delete or disable logging software. Lastlog is software that shows when a user last logged in (last-log).
|ROOTKIT.DIAMORPHINE| Installs the Diamorphine rootkit and uses it to hide a process| Diamorphine Rootkit Activity | Host-only |  Diamorphine is probably the most famous Linux rootkit. It allows a privileged (root) user to hide processes at-will, and hides itself by default. 
|LD.LINUX.EXEC| Uses ld-linux to run a binary (evades some detections) | Execution of binary using ld-linux | | ld-linux is a loader that is typically invoked automatically by certain OS processes, however, it is also able to be invoked (executed) by a normal user that wishes to run a binary without executable permissions. /lib/ld-linux.. binary_with_noexec will work, even if the binary_with_noexec does not have +x permissions!
|LD.SO.PRELOAD| Uses /etc/ld.so.preload to deploy libprocesshider| Modify ld.so.preload| | ld.so.preload is a file on Linux that allows libraries to be loaded before others. With this attack, we use ld.so.preload to load Sysdig's libprocesshider to show the effectiveness of the attack. 
|LPE.POLKIT| Exploits the Polkit CVE-2021-4034 to escalate privileges | Polkit Local Privilege Escalation Vulnerability (CVE-2021-4034)| Requires a vulnerable version of polkit | This is a privilege escalation (user ->root) technique that abuses a vulnerable version of the Polkit executable. 
|USERFAULTFD.HANDLER|Unprivileged Delegation of Page Faults Handling to a Userspace Process| Unprivileged Delegation of Page Faults Handling to a Userspace Process| 
|RECON.LINPEAS| runs and downloads linpeas.sh, a linux recon script| Detect Reconnaissance scripts|  | LinPeaS (Linux Privelege escalation as a Service) is a nice tool that can perform automated recon on an attacked system to let the attacker know if there are any feasible routes to privilege escalation, as well as other information, like if they're inside of a container or VM. 
|PROOT.EXEC| Downloads and runs Proot, as detailed in the BYOFS sysdig blog| Detect cloned process by PRoot | | [Proot Blog](https://sysdig.com/blog/proot-post-explotation-cryptomining/)
|TIMESTOMP | Performs a timestomp via `touch -t` to overwrite the modified time (mtime) of a file. | Modify Timestamp attribute in File | |
|SUBTERFUGE.FILEBELOWDEV | Creates a file below `/dev` | Create files below /dev | |
|SYMLINK.ETC.SHADOW |Creates a symlink pointing to `/etc/shadow`  | Create Symlink over Sensitive Files | |
|PRIVESC.SUDO | Abuses Sudo privilege escalation bug  (CVE-2021-3156)| Sudo Potential Privilege Escalation | |

Stratus GCP Impersonate Service Account:
```bash
gcloud auth application-default login --no-browser
export GOOGLE_PROJECT=rule-testing-123456
./stratus warmup gcp.privilege-escalation.impersonate-service-accounts
./stratus detonate gcp.privilege-escalation.impersonate-service-accounts
./stratus cleanup gcp.privilege-escalation.impersonate-service-accounts
```

# Tools

## Atomic Red Team

Atomic Red Team™ is a library of tests mapped to the MITRE ATT&CK® framework for testing container security. Security teams can use Atomic Red Team to quickly, portably, and reproducibly test their environments.

https://github.com/redcanaryco/atomic-red-team/

## Stratus Red Team
Stratus Red Team is a library for testing cloud security on various cloud service providers.  Some configuration of this tool for your cloud environment is required before using.  Refer to the user guide on how to configure the tool for your cloud environment: https://stratus-red-team.cloud/user-guide/getting-started/

https://github.com/DataDog/stratus-red-team
