from hdfs import InsecureClient

from .logger import AppLogger


class HDFSManager:
    def __init__(self, namenode_url, user="hadoop"):
        """
        Initialize the HDFS client.
        :param namenode_url: WebHDFS URL, e.g., 'http://namenode:9870'
        :param user: HDFS user (optional)
        """
        self.client = InsecureClient(namenode_url, user=user)
        self.logger = AppLogger(prefix=" | HDFS | ").get_logger()
        self.logger.info(f"HDFSManager connected to: {namenode_url}")

    def create_directory(self, path):
        """Create a directory in HDFS."""
        try:
            self.client.makedirs(path)
            self.logger.info(f"Created directory: hdfs://{path}")
        except Exception as e:
            self.logger.error(f"Failed to create directory 'hdfs://{path}': {e}")
            raise
    # TO DO -fix delete
    def delete_directory(self, path, recursive=True):
        """Delete a directory in HDFS."""
        try:
            self.client.delete(path, recursive=recursive)
            self.logger.info(f"Deleted directory: hdfs://{path} (recursive={recursive})")
        except Exception as e:
            self.logger.error(f"Failed to delete directory 'hdfs://{path}': {e}")
            raise

    def upload_file(self, local_path, storage_path, overwrite=True):
        """Upload a local file to HDFS."""
        try:
            self.client.upload(storage_path, local_path, overwrite=overwrite)
            self.logger.info(f"Uploaded file from '{local_path}' to HDFS 'hdfs://{storage_path}' (overwrite={overwrite})")
        except Exception as e:
            self.logger.error(f"Failed to upload file '{local_path}' to HDFS 'hdfs://{storage_path}': {e}")
            raise

    def download_file(self, src_path, local_path, overwrite=True):
        """Download a file from HDFS to local."""
        try:
            self.client.download(src_path, local_path, overwrite=overwrite)
            self.logger.info(f"Downloaded file from HDFS 'hdfs://{src_path}' to local '{local_path}' (overwrite={overwrite})")
        except Exception as e:
            self.logger.error(f"Failed to download file from HDFS 'hdfs://{src_path}' to local '{local_path}': {e}")
            raise

    def read_file(self, storage_path, encoding='utf-8'):
        """Read the content of a file from HDFS."""
        try:
            with self.client.read(storage_path, encoding=encoding) as reader:
                content = reader.read()
            self.logger.info(f"Read file from HDFS: hdfs://{storage_path}")
            return content
        except Exception as e:
            self.logger.error(f"Failed to read file 'hdfs://{storage_path}' from HDFS: {e}")
            raise

    def list_directory(self, path):
        """List files and directories in a given HDFS path."""
        try:
            contents = self.client.list(path)
            self.logger.info(f"Listed directory: hdfs://{path}")
            return contents
        except Exception as e:
            self.logger.error(f"Failed to list directory 'hdfs://{path}': {e}")
            raise

    def file_status(self, path):
        """Get the status of a file or directory."""
        try:
            status = self.client.status(path)
            self.logger.info(f"Retrieved status for HDFS path: hdfs://{path}")
            return status
        except Exception as e:
            self.logger.error(f"Failed to get status for 'hdfs://{path}': {e}")
            raise

    def set_replication(self, path, replication):
        """Set replication factor for a file."""
        try:
            self.client.set_replication(path, replication)
            self.logger.info(f"Set replication for 'hdfs://{path}' to {replication}")
        except Exception as e:
            self.logger.error(f"Failed to set replication for 'hdfs://{path}': {e}")
            raise

    def exists(self, path):
        """Check if a file or directory exists."""
        try:
            exists = self.client.status(path, strict=False) is not None
            self.logger.info(f"Checked existence for 'hdfs://{path}': {exists}")
            return exists
        except Exception as e:
            self.logger.error(f"Failed to check existence for 'hdfs://{path}': {e}")
            raise

    def rename(self, old_path, new_path):
        """Rename a file or directory."""
        try:
            self.client.rename(old_path, new_path)
            self.logger.info(f"Renamed 'hdfs://{old_path}' to 'hdfs://{new_path}'")
        except Exception as e:
            self.logger.error(f"Failed to rename 'hdfs://{old_path}' to 'hdfs://{new_path}': {e}")
            raise

    def append_to_file(self, storage_path, data, encoding='utf-8'):
        """Append data to a file."""
        try:
            with self.client.write(storage_path, encoding=encoding, append=True) as writer:
                writer.write(data)
            self.logger.info(f"Appended data to file: hdfs://{storage_path}")
        except Exception as e:
            self.logger.error(f"Failed to append data to hdfs://'{storage_path}': {e}")
            raise


if __name__ == "__main__":
    hadoop_client = HDFSManager(namenode_url='http://ulhchathamster:9870')
    hadoop_client.delete_directory('uploads')
    # hadoop_client.download_file(local_path='dw.pdf', src_path='uploads/3107_-_Diamondback_CDA_-_Recorded/556f55e9597040f4a05e0d8d670df2bb.pdf')
    print(hadoop_client.list_directory('/'))
