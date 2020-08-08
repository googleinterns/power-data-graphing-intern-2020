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
from json import dump
from json import dumps
from json import load
from json import loads

METADATA = 'metadata.json'


class Metadata:
    """Class for managing metadata."""

    def __init__(self, root_dir, strategy=None, level=None, bucket=None):
        """Initilizes metadata object.

        Args:
            root_dir: A string that represents the directory of preprocesse files.
            strategy: A string of downsampling strategy.
            level: A string of level name.
            bucket: bucket: An gcp bucket object.
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
        if self._bucket is None:
            with open(self._path, 'w') as filewriter:
                dump(self.data, filewriter)
                return
        blob = self._bucket.blob(self._path)
        metadata_string = dumps(self.data)
        blob.upload_from_string(metadata_string)

    def load(self):
        """Loads metadata from bucket or disk."""
        if self._bucket is None:
            with open(self._path, 'r') as filereader:
                self.data = load(filereader)
                return
        blob = self._bucket.blob(self._path)
        metadata_string = blob.download_as_string()
        self.data = loads(metadata_string)
