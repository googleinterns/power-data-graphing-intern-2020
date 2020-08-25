# Copyright 2020 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

"""Metadata module."""
from json import dumps
from json import loads

from google.api_core.exceptions import NotFound

METADATA = 'metadata.json'


class Metadata:
    """Class for managing metadata."""

    def __init__(self, root_dir, bucket, strategy=None, level=None):
        """Initilizes metadata object.

        Args:
            root_dir: A string that represents the directory of preprocesse files.
            strategy (optional): A string of downsampling strategy. None if it is a file metadata
                or level0 metadata.
            level (optional): A string of level name. None if it is a file metadata..
            bucket (optional): The gcp bucket object for preprocessed files. None if files
                are stored locally on disk.
        """
        path = ''
        if root_dir is not None:
            path = root_dir

        if level is not None:
            if level != 'level0':
                path = '/'.join([path, strategy, level, METADATA])
            else:
                path = '/'.join([path, level, METADATA])
        else:
            path = '/'.join([path, METADATA])
        self._path = path
        self._bucket = bucket
        self.data = dict()

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def save(self):
        """Saves metadata to bucket or disk."""
        blob = self._bucket.blob(self._path)
        metadata_string = dumps(self.data)
        blob.upload_from_string(metadata_string)

    def load(self):
        """Loads metadata from bucket or disk.

        Returns:
            Returns a boolean indicating if load is successful.
        """
        try:
            blob = self._bucket.blob(self._path)
            metadata_string = blob.download_as_string()
            self.data = loads(metadata_string)
            return True
        except NotFound:
            return False
