#install deps and pwsh, then ART
## Install Powershell
  # Download the Microsoft repository GPG keys
curl https://packages.microsoft.com/config/rhel/7/prod.repo |
 sudo tee /etc/yum.repos.d/microsoft.repo
  # Update the list of packages after we added packages.microsoft.com
  yum update  &&
    yum install -y kernel-devel-$(uname-r) ca-certificates gnupg software-properties-common at ccrypt clang cron curl ed g++ gcc golang-go iproute2 iputils-ping kmod libpam0g-dev less lsof make netcat net-tools nmap p7zip python2 rsync samba selinux-utils ssh sshpass sudo tcpdump telnet tor ufw vim wget whois zip

  # Install PowerShell rpm package
  yum install -y powershell
pwsh -Command "IEX (IWR 'https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install-atomicredteam.ps1' -UseBasicParsing); Install-AtomicRedTeam -getAtomics"
#copy atomics over (default install is to home dir)
cp -r atomics-overrides/* ~/AtomicRedTeam/atomics/
#add RunTests to PATH
echo "export PATH=${PATH}:$(pwd)/"
