import os
import tarfile
from io import BytesIO


class FileHandler:
    def copy_files_to_container(self, container, src, dst):
        # Create tar of micro-bench folder
        temp_path = "/tmp/temp.tar"
        with tarfile.open(temp_path, "w:gz") as tar:
            # base_folder = os.path.basename(src)
            # Use 'benchmarks' as the constant directory name in the tarball
            tar.add(src, arcname="benchmarks")

        with open(temp_path, "rb") as file:
            data = file.read()
            container.put_archive(dst, data)

    def copy_files_from_container(self, container, src, dst):
        stream, _ = container.get_archive(src)
        stream_bytes = b"".join(stream)
        stream_bytes_io = BytesIO(stream_bytes)

        tar = tarfile.open(fileobj=stream_bytes_io)
        tar.extractall(path=dst)
        tar.close()

    def list_python_files(self, directory):
        python_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(
                        os.path.relpath(os.path.join(root, file), directory)
                    )
        return python_files
