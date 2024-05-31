import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = Path(__file__).resolve().parent.parent

def process_file(src_file: Path, dest_file: Path):
    """
    Dummy function to process a file.
    For now, it just copies the file contents as is.
    """
    shutil.copyfile(src_file, dest_file)

def recreate_folder_structure(src_dir: Path, dest_dir: Path):
    """
    Recursively processes a nested folder structure,
    recreates it in the destination directory, and processes each file.
    """
    for item in src_dir.iterdir():
        dest_item = dest_dir / item.relative_to(src_dir)
        if item.is_dir():
            dest_item.mkdir(parents=True, exist_ok=True)
            recreate_folder_structure(item, dest_item)
        elif item.is_file():
            process_file(item, dest_item)

def main():
    # Define the source and destination directories
    src_dir = Path(ROOT_DIR) / "benchmarks" / "python"
    dest_dir = Path(ROOT_DIR) / "benchmarks" / "python"
    
    if not src_dir.exists() or not src_dir.is_dir():
        print(f"Source directory '{src_dir}' does not exist or is not a directory.")
        return

    # Ensure the destination directory exists
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Start processing
    recreate_folder_structure(src_dir, dest_dir)
    print("Processing completed successfully.")

if __name__ == "__main__":
    main()
