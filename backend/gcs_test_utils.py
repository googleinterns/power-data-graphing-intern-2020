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

"""A Test module for testing data saved in GCS."""
from google.cloud import storage
from utils import convert_to_csv


TEST_DIR = 'test_directory'
TEST_BUCKET = 'power-data-preprocess'


def upload(filename, records):
    """Uploads records to bucket in the given file name and returns
    a bucket object.

    Args:
        filename: A string for name of the file.
        records: A list of records.

    Returns:
        GCS bucket object.
    """
    client = storage.Client()
    bucket = client.bucket(TEST_BUCKET)
    if records is not None:
        blob = bucket.blob(filename)
        blob.upload_from_string(convert_to_csv(records))
    return bucket
