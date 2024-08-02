#it assumes you have the git repo cloned and are running it from docker/ dir

#install deps and pwsh, then ART
## Install Powershell
  # Download the Microsoft repository GPG keys
curl https://packages.microsoft.com/config/rhel/7/prod.repo |
 sudo tee /etc/yum.repos.d/microsoft.repo
  #wget -q https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb && \
  # Register the Microsoft repository GPG keys
  #dpkg -i packages-microsoft-prod.deb && \
  # Update the list of packages after we added packages.microsoft.com
  sudo yum update  &&
    sudo yum install -y  ca-certificates gnupg software-properties-common at ccrypt clang cron curl ed g++ gcc golang-go iproute2 iputils-ping kmod libpam0g-dev less lsof make netcat net-tools nmap p7zip python2 rsync samba selinux-utils ssh sshpass sudo tcpdump telnet tor ufw vim wget whois zip

  # Install PowerShell Debian package
  sudo yum install -y powershell
pwsh -Command "IEX (IWR 'https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install-atomicredteam.ps1' -UseBasicParsing); Install-AtomicRedTeam -getAtomics"
#copy atomics over (default install is to home dir)
cp -r atomics-overrides/* ~/AtomicRedTeam/atomics/
#add RunTests to PATH
echo "export PATH=${PATH}:$(pwd)/"


# Run quick test
# pwsh -c ./RunTests.ps1 BASE64.SHELLSCRIPT








