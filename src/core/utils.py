import io
import os
import tarfile
import tokenize
from io import BytesIO


def strip_python_comments(source: str) -> str:
    """Strip comment text from Python source while preserving line numbers.

    Each comment is replaced with a bare '#' so the line count stays identical —
    ground truth data is line-number based and must not shift.
    Docstrings are left untouched (they affect runtime semantics).
    Returns the source unchanged if tokenization fails (e.g. encoding errors).
    """
    lines = source.splitlines(keepends=True)
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for tok_type, _, tok_start, _, _ in tokens:
            if tok_type == tokenize.COMMENT:
                row, col = tok_start  # row is 1-based
                line = lines[row - 1]
                eol = line[len(line.rstrip("\n\r")):]
                lines[row - 1] = line[:col] + "#" + eol
    except tokenize.TokenError:
        pass
    return "".join(lines)


class FileHandler:
    def copy_files_to_container(self, container, src, dst, exclude_extensions=None, py_content_filter=None):
        temp_path = "/tmp/temp.tar"

        if not exclude_extensions and not py_content_filter:
            # Fast path: let tarfile walk the tree directly
            with tarfile.open(temp_path, "w:gz") as tar:
                tar.add(src, arcname="benchmarks")
        else:
            # Walk manually to support file exclusion and/or .py content transformation
            with tarfile.open(temp_path, "w:gz") as tar:
                for dirpath, dirnames, filenames in os.walk(src):
                    dirnames.sort()
                    rel = os.path.relpath(dirpath, src)
                    arcdir = os.path.join("benchmarks", rel) if rel != "." else "benchmarks"

                    # Directory entry
                    dirinfo = tarfile.TarInfo(name=arcdir)
                    dirinfo.type = tarfile.DIRTYPE
                    dirinfo.mode = 0o755
                    tar.addfile(dirinfo)

                    for filename in sorted(filenames):
                        filepath = os.path.join(dirpath, filename)
                        arcname = os.path.join(arcdir, filename)

                        if exclude_extensions and any(
                            filename.endswith(ext) for ext in exclude_extensions
                        ):
                            continue

                        if py_content_filter and filename.endswith(".py"):
                            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                                content = py_content_filter(f.read())
                            data = content.encode("utf-8")
                            info = tarfile.TarInfo(name=arcname)
                            info.size = len(data)
                            info.mode = 0o644
                            tar.addfile(info, io.BytesIO(data))
                        else:
                            tar.add(filepath, arcname=arcname)

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
