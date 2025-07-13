import os
import shutil
from sys import prefix

from app.file_systems.logger import AppLogger

class FileManager:
    def __init__(self, base_path=None, user=None):
        """
        Initialize the local file client.
        :param base_path: Base directory path to operate within (optional)
        :param user: User parameter for compatibility (not used)
        """
        self.base_path = base_path if base_path else ""
        self.logger = AppLogger(prefix=" | LocalFS | ").get_logger()
        self.logger.info(f"LocalFS | FileManager initialized with base_path: '{self.base_path}'")

    def _full_path(self, path):
        if os.path.isabs(path):
            return path
        return os.path.join(self.base_path, path)

    def create_directory(self, path):
        """Create a directory locally."""
        full_path = self._full_path(path)
        try:
            os.makedirs(full_path, exist_ok=True)
            self.logger.info(f"Created directory: {full_path}")
        except Exception as e:
            self.logger.error(f"Failed to create directory {full_path}: {e}")
            raise e

    def delete_directory(self, path, recursive=True):
        """Delete a directory locally."""
        full_path = self._full_path(path)
        try:
            if recursive:
                shutil.rmtree(full_path, ignore_errors=True)
                self.logger.info(f"Recursively deleted directory: {full_path}")
            else:
                os.rmdir(full_path)
                self.logger.info(f"Deleted directory: {full_path}")
        except Exception as e:
            self.logger.error(f"Failed to delete directory {full_path}: {e}")
            raise

    def upload_file(self, local_path, storage_path, overwrite=True):
        """Copy a local file to another local path."""
        dest_path = self._full_path(storage_path)
        try:
            if not overwrite and os.path.exists(dest_path):
                self.logger.warning(f"File {dest_path} already exists and overwrite is False.")
                raise FileExistsError(f"File {dest_path} already exists.")
            shutil.copy2(local_path, dest_path)
            self.logger.info(f"Uploaded file from {local_path} to {dest_path}")
        except Exception as e:
            self.logger.error(f"Failed to upload file from {local_path} to {dest_path}: {e}")
            raise

    def download_file(self, src_path, local_path):
        """Copy a local file from one path to another."""
        src_path = self._full_path(src_path)
        try:
            shutil.copy2(src_path, local_path)
            self.logger.info(f"Downloaded file from {src_path} to {local_path}")
        except Exception as e:
            self.logger.error(f"Failed to download file from {src_path} to {local_path}: {e}")
            raise e

    def read_file(self, path, encoding='utf-8'):
        """Read the content of a local file."""
        full_path = self._full_path(path)
        try:
            with open(full_path, 'r', encoding=encoding) as f:
                content = f.read()
            self.logger.info(f"Read file: {full_path}")
            return content
        except Exception as e:
            self.logger.error(f"Failed to read file {full_path}: {e}")
            raise e

    def list_directory(self, path):
        """List files and directories in a given local path."""
        full_path = self._full_path(path)
        try:
            contents = os.listdir(full_path)
            self.logger.info(f"Listed directory: {full_path}")
            return contents
        except Exception as e:
            self.logger.error(f"Failed to list directory {full_path}: {e}")
            raise e

    def file_status(self, path):
        """Get the status of a file or directory."""
        full_path = self._full_path(path)
        try:
            stat = os.stat(full_path)
            status = {
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'ctime': stat.st_ctime,
                'mode': stat.st_mode,
                'is_dir': os.path.isdir(full_path),
                'is_file': os.path.isfile(full_path)
            }
            self.logger.info(f"Got file status for: {full_path}")
            return status
        except Exception as e:
            self.logger.error(f"Failed to get file status for {full_path}: {e}")
            raise

    def set_replication(self, path, replication):
        """Set replication factor - not applicable locally, so raise error."""
        self.logger.warning("Attempted to set replication factor on local file system (not supported).")
        raise NotImplementedError("Replication factor is not applicable for local files.")

    def exists(self, path):
        """Check if a file or directory exists locally."""
        full_path = self._full_path(path)
        existence = os.path.exists(full_path)
        self.logger.info(f"Checked existence for {full_path}: {existence}")
        return existence

    def rename(self, old_path, new_path):
        """Rename a file or directory locally."""
        old_full = self._full_path(old_path)
        new_full = self._full_path(new_path)
        try:
            os.rename(old_full, new_full)
            self.logger.info(f"Renamed {old_full} to {new_full}")
        except Exception as e:
            self.logger.error(f"Failed to rename {old_full} to {new_full}: {e}")
            raise

    def append_to_file(self, path, data, encoding='utf-8'):
        """Append data to a local file."""
        full_path = self._full_path(path)
        try:
            with open(full_path, 'a', encoding=encoding) as f:
                f.write(data)
            self.logger.info(f"Appended data to file: {full_path}")
        except Exception as e:
            self.logger.error(f"Failed to append data to file {full_path}: {e}")
            raise
# Example usage
if __name__ == "__main__":
    file_client = FileManager()
    test_dir = "./test_dir"
    file_client.create_directory(test_dir)
    file_client.append_to_file(f"{test_dir}/test.txt", "Hello, world!\\n")
    print(file_client.read_file(f"{test_dir}/test.txt"))
    print(file_client.list_directory(test_dir))
    file_client.delete_directory(test_dir)
    print("Test directory deleted.")
