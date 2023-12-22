#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m' 
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

if command -v docker &> /dev/null; then
    echo "[+] Docker is installed on this system."
else
    echo "[-] Error: Docker is not installed. Please install Docker before proceeding."
    exit 1
fi

# Download the Kali image.
echo -e "${GREEN}[*] Setting up the Kali image${NC}"
sudo docker pull kalilinux/kali-last-release
sudo docker tag kalilinux/kali-last-release kali

# Create a docker volume "pentest".
echo -e "${GREEN}[*] Creating a persistent docker volume${NC}"
sudo docker volume create pentest
sudo docker run --name kali --mount source=pentest,target=/vol -it -d kali /bin/bash

# Install essentials in the container
echo -e "${GREEN}[*] Installing Essentials in the container${NC}"
sudo docker exec kali apt-get update
sudo docker exec kali apt-get install -y build-essential gcc git vim wget curl awscli inetutils-ping make nmap whois python3 python-pip perl dnsutils net-tools zsh nano tmux vsftpd

# Install tools
echo -e "${GREEN}[*] Installing the tools${NC}"
sudo docker exec kali apt-get install -y hydra metasploit-framework sqlmap smbclient enum4linux smbmap sublist3r dirb nikto dnsenum fierce exploitdb theharvester wafw00f hashcat john crackmapexec evil-winrm powershell-empire whatweb beef-xss netcat-traditional traceroute steghide set wpscan linux-exploit-suggester

echo -e "${GREEN}[*] Installing wordlists, webshells and binaries${NC}"
sudo docker exec kali apt-get install -y webshells wordlists windows-binaries

# Cleanup the container
echo -e "${GREEN}[*] Tidying up in the container${NC}"
sudo docker exec kali apt-get clean

# Wrapper script
echo -e "${GREEN}[*] Configuring Red Dock${NC}"
if [[ ":$PATH:" != *":/usr/local/bin:"* ]]; then
    echo 'export PATH=$PATH:/usr/local/bin/' >> ~/.bashrc
else
    echo '[+] PATH is set correctly.'
fi
source ~/.bashrc
echo -e "#!/bin/bash\npython3 $SCRIPT_DIR/rd.py \"\$@\"" | sudo tee /usr/local/bin/rd > /dev/null
sudo chmod +x /usr/local/bin/rd

# Update image
echo -e "${GREEN}[*] Updating the image (This might take a while)...${NC}"
CONTAINER_ID=$(sudo docker ps --format "{{.ID}}" --filter "name=kali")
sudo docker commit "$CONTAINER_ID" kali
echo -e "${GREEN}[*] Update successful.${NC}"
sudo docker rm kali

echo -e "${GREEN}[*] Installation completed${NC}"
sleep 1
echo -e "${GREEN}[*] Starting Red Dock in 2 seconds...${NC}"

sleep 2
rd
