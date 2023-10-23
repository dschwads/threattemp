# Sysdig-Threat-Generator Dockerfile

## Pull base image. Due to Powershell dependency requirements, use 22.04 (jammy) instead of the latest version.
FROM ubuntu:jammy

## Basics
RUN \
  apt update && \
  apt install -y apt-transport-https ca-certificates gnupg software-properties-common

# Atomic-Red-Team

## Install ART test dependancies
RUN \
  apt install -y at ccrypt clang cron curl ed g++ gcc golang-go iproute2 iputils-ping kmod libpam0g-dev less lsof make netcat net-tools nmap p7zip python2 rsync samba selinux-utils ssh sshpass sudo tcpdump telnet tor ufw vim wget whois zip

## Install Powershell
RUN \
  # Download the Microsoft repository GPG keys
  wget -q https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb && \
  # Register the Microsoft repository GPG keys
  dpkg -i packages-microsoft-prod.deb && \
  # Update the list of packages after we added packages.microsoft.com
  apt update  && \
  # Install PowerShell Debian package
  apt install -y powershell 

## Install Atomic Red Team from pwsh
RUN \
  cd /root && pwsh -Command "IEX (IWR 'https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install-atomicredteam.ps1' -UseBasicParsing); Install-AtomicRedTeam -getAtomics"



# Stratus Red Team

## Build and Install. golang and make should already be available

### GCP
RUN \
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
  curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

### Azure
RUN \
  curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null && \
  echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/azure-cli.list 

### AWS
RUN \
  cd /tmp && \
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
  unzip -q awscliv2.zip && \
  ./aws/install

## Install dependancies
RUN \
  apt update && \
  apt install -y azure-cli git google-cloud-cli

## Install from source
RUN \
  cd /root && \
  git clone https://github.com/DataDog/stratus-red-team.git

RUN \
  cd /root/stratus-red-team && \
  make build && \
  cp bin/stratus /root

## Cleanup
RUN \
  rm -fr /root/stratus-red-team /root/go /tmp/aws*

# Copy optional ART Job script
COPY RunTests.ps1 /root
## Copy test overrides/fixes
COPY atomics-overrides/ /root/AtomicRedTeam/atomics/
# Reclaim disk space
RUN \
  apt clean

# Define working directory.
WORKDIR /root

#install stratus-red
RUN wget -O /tmp/srt.tar.gz https://github.com/DataDog/stratus-red-team/releases/download/v2.4.0/stratus-red-team_2.4.0_Linux_x86_64.tar.gz && tar -xvzf /tmp/srt.tar.gz && rm /tmp/srt.tar.gz

# Define default command.
CMD ["/bin/bash", "-c", "(pwsh ./RunTests.ps1 BASE64.CLI)"]

