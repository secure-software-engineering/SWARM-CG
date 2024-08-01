import sys
from commands import run_command

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [options]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run_command()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
