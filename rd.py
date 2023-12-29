import subprocess
import argparse
import sys


def banner():
    banner_art = """
     @@@@@@@  @@@@@@@@ @@@@@@@       @@@@@@@   @@@@@@   @@@@@@@ @@@  @@@
     @@!  @@@ @@!      @@!  @@@      @@!  @@@ @@!  @@@ !@@      @@!  !@@
     @!@!!@!  @!!!:!   @!@  !@!      @!@  !@! @!@  !@! !@!      @!@@!@! 
     !!: :!!  !!:      !!:  !!!      !!:  !!! !!:  !!! :!!      !!: :!! 
      :   : : : :: ::: :: :  :       :: :  :   : :. :   :: :: :  :   :::
    """
    print(banner_art)


def start_container():
    existing_container_id = subprocess.check_output(["sudo", "docker", "ps", "-q", "--filter", "name=kali"]).decode(
        "utf-8").strip()

    if existing_container_id:
        print("A container is already running. Spawn a new container.")
    else:
        subprocess.run(
            ["sudo", "docker", "run", "--name", "kali", "--mount", "source=pentest,target=/vol", "-it", "kali",
             "/bin/bash"])


def stop_container():
    all_containers = subprocess.check_output(["sudo", "docker", "ps", "-qa"]).decode("utf-8").splitlines()

    if not all_containers:
        print("Error: No containers are currently running.")
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
    if source.startswith("/vol/"):
        subprocess.run(["sudo", "docker", "cp", f"{container_id}:{source}", destination])
    else:
        subprocess.run(["sudo", "docker", "cp", source, f"{container_id}:{destination}"])


def attach_container():
    container_id = subprocess.check_output(["sudo", "docker", "ps", "-q", "-n", "1"]).decode("utf-8").strip()
    container_id_stopped = subprocess.check_output(
        ["sudo", "docker", "ps", "-aq", "--filter", "status=exited", "--no-trunc"]).decode("utf-8").strip()
    if container_id_stopped:
        subprocess.run(["sudo", "docker", "start", container_id_stopped])
        subprocess.run(["sudo", "docker", "attach", container_id_stopped])
    elif container_id:
        subprocess.run(["sudo", "docker", "attach", container_id])
    else:
        print("Error: No containers are currently running.")


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


def parser_error(errmsg):
    banner()
    print("Usage: python3 " + sys.argv[0] + " [Options] use -h for help")
    print("Error: " + errmsg)
    sys.exit()


def main():
    parser = argparse.ArgumentParser(description="Red Dock - A simple Docker management tool for Penetration Testing.")
    parser.error = parser_error
    parser.add_argument("command")
    parser._optionals.title = "OTHER OPTIONS"
    parser.add_argument("start", nargs="?", help="Start the kali image.")
    parser.add_argument("stop", nargs="?", help="Stop a running container.")
    parser.add_argument("status", nargs="?", help="Check the container status.")
    parser.add_argument("update", nargs="?", help="Update the Kali image.")
    parser.add_argument("attach", nargs="?", help="Attach a container if running.")
    parser.add_argument("clone", nargs="?", help="Open another terminal.")
    parser.add_argument("cp", nargs="?", help="Copy files to & fro the host machine.")
    parser.add_argument("source", nargs="?", help="Source file or directory for the 'cp' command.")
    parser.add_argument("destination", nargs="?", help="Destination path for the 'cp' command.")

    args = parser.parse_args()

    if args.command == "start":
        start_container()
    elif args.command == "stop":
        stop_container()
    elif args.command == "attach":
        attach_container()
    elif args.command == "clone":
        clone_container()
    elif args.command == "status":
        show_status()
    elif args.command == "update":
        update_image()
    elif args.command == "cp":
        if not args.source or not args.destination:
            print("Error: 'cp' command requires both source and destination arguments.")
        else:
            copy_files(args.source, args.destination)


if __name__ == "__main__":
    main()
