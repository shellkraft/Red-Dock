import subprocess
import argparse

def start_container():
    subprocess.run(["sudo", "docker", "run", "--name", "kali", "--mount", "source=pentest,target=/vol", "-it", "kali", "/bin/bash"])

def stop_container():
    subprocess.run(["sudo", "docker", "rm", "kali"])

def show_status():
    subprocess.run(["sudo", "docker", "ps", "-a"])

def update_image():
    container_id = subprocess.check_output(["sudo", "docker", "ps", "-q", "-n", "1"]).decode("utf-8").strip()
    subprocess.run(["sudo", "docker", "commit", container_id, "kali"])

def copy_files(source, destination):
    subprocess.run(["sudo", "docker", "cp", source, f"kali:{destination}"])

def main():
    parser = argparse.ArgumentParser(description="Red Dock - A simple Docker management tool for Kali Linux.")
    parser.add_argument("command", choices=["start", "stop", "status", "update", "cp"], help="Specify the command to execute.")
    parser.add_argument("source", nargs="?", help="Source file or directory for the 'cp' command.")
    parser.add_argument("destination", nargs="?", help="Destination path for the 'cp' command.")

    args = parser.parse_args()

    if args.command == "start":
        start_container()
    elif args.command == "stop":
        stop_container()
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
