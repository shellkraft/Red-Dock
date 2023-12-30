import subprocess
import sys

RESET = "\033[0m"       # Reset to default
BOLD = "\033[1m"        # Bold text
RED = "\033[91m"        # Red text
GREEN = "\033[92m"      # Green text
YELLOW = "\033[93m"     # Yellow text
BLUE = "\033[94m"       # Blue text
WHITE = "\033[97m"      # White text

def banner():
    whale_art = f"""
        {BLUE}.
       {BLUE}":"{RESET}
     ___:____     |"\\/"|
   ,'        `.    \\  /
   |  O        \\___/  |
 ~^~^~^~^~^~^~^~^~^~^~^~^~
    """
                                    
    print(whale_art)
    print(f"        {RED}RED {BLUE}DOCK")
    print(f"        {YELLOW}by B4PHOM3T{RESET}")


def start_container():

    container_id = subprocess.check_output(["sudo", "docker", "ps", "-q", "-n", "1"]).decode("utf-8").strip()
    container_id_stopped = subprocess.check_output(
        ["sudo", "docker", "ps", "-aq", "--filter", "status=exited", "--no-trunc"]).decode("utf-8").strip()
    if container_id_stopped:
        subprocess.run(["sudo", "docker", "start", container_id_stopped])
        subprocess.run(["sudo", "docker", "attach", container_id_stopped])
    elif container_id:
        subprocess.run(["sudo", "docker", "attach", container_id])         
    else:
        subprocess.run(
            ["sudo", "docker", "run", "--name", "kali", "--mount", "source=pentest,target=/vol", "-it", "kali",
             "/bin/bash"])

def stop_container():
    all_containers = subprocess.check_output(["sudo", "docker", "ps", "-qa"]).decode("utf-8").splitlines()

    if not all_containers:
        print(f"{YELLOW}Error: No containers are currently running.{RESET}")
    else:
        running_containers = subprocess.check_output(["sudo", "docker", "ps", "-q"]).decode("utf-8").splitlines()
        for container_id in running_containers:
            subprocess.run(["sudo", "docker", "kill", container_id])

        subprocess.run(["sudo", "docker", "stop"] + all_containers)
        subprocess.run(["sudo", "docker", "rm"] + all_containers)

def show_status():
    subprocess.run(["sudo", "docker", "ps", "-a"])

def update_image():
    container_id = subprocess.check_output(["sudo", "docker", "ps", "-q", "-n", "1"]).decode("utf-8").strip()
    subprocess.run(["sudo", "docker", "commit", container_id, "kali"])

def copy_files(source, destination):
    container_id = subprocess.check_output(["sudo", "docker", "ps", "-q", "-n", "1"]).decode("utf-8").strip()

    if destination.startswith("/vol/"):
        # Copy from host to container
        subprocess.run(["sudo", "docker", "cp", source, f"{container_id}:{destination}"])
    else:
        # Copy from container to host
        subprocess.run(["sudo", "docker", "cp", f"{container_id}:{source}", destination])


def get_next_container_name(base_name="kali"):
    existing_containers = subprocess.check_output(["sudo", "docker", "ps", "--format", "{{.Names}}"]).decode(
        "utf-8").splitlines()

    index = 2
    while True:
        new_name = f"{base_name}{index}"
        if new_name not in existing_containers:
            return new_name
        index += 1

def clone_container():
    new_container_name = get_next_container_name()

    subprocess.run(
        ["sudo", "docker", "run", "--name", new_container_name, "--mount", "source=pentest,target=/vol", "-it", "kali",
         "/bin/bash"])

def print_help_menu():
    help_menu = f"""
    {BOLD}{RED}RED {BLUE}DOCK{RESET} - A simple Docker management tool for Penetration Testing.

    {BOLD}{GREEN}COMMANDS:{RESET}
    {BOLD}start{RESET}                  {WHITE}Start the kali image.{RESET}
    {BOLD}stop{RESET}                   {WHITE}Stop a running container.{RESET}
    {BOLD}status{RESET}                 {WHITE}Check the container status.{RESET}
    {BOLD}update{RESET}                 {WHITE}Update the Kali image.{RESET}
    {BOLD}clone{RESET}                  {WHITE}Open another terminal.{RESET}
    
    {BOLD}{GREEN}FILE OPERATIONS:{RESET}
    {BOLD}cp <source> <destination>{RESET}    {WHITE}Copy files from host to container or vice versa.{RESET}

    {BOLD}{GREEN}EXAMPLES:{RESET}
    rd start
    rd stop
    rd status
    rd update
    rd clone
    rd cp /path/to/source /vol/destination
    rd cp /vol/source /path/to/destination
    """
    print(help_menu)

def main():
    if len(sys.argv) == 2 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        print_help_menu()
        sys.exit()

    if len(sys.argv) == 1 or sys.argv[1] not in ["start", "stop", "clone", "status", "update", "cp"]:
        banner()
        print(f"{RED}Error: Unknown command. Use -h for help.{RESET}")
        sys.exit()

    command = sys.argv[1]

    if command == "start":
        start_container()
    elif command == "stop":
        stop_container()
    elif command == "clone":
        clone_container()
    elif command == "status":
        show_status()
    elif command == "update":
        update_image()
    elif command == "cp":
        if len(sys.argv) != 4:
            print(f"{RED}Error: Please provide source and destination arguments for 'cp' command.{RESET}")
            sys.exit()
        source = sys.argv[2]
        destination = sys.argv[3]
        copy_files(source, destination)

if __name__ == "__main__":
    main()
