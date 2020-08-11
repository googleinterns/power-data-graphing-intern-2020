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

"""HTTP server module.

Expose HTTP endpoints for triggering preprocess and send downsampled data.
"""
from flask import request
from flask import jsonify
from flask import Flask
from flask_cors import CORS
from google.cloud import storage

from downsample import STRATEGIES
from multiple_level_preprocess import MultipleLevelPreprocess

from utils import error


NUMBER_OF_RECORDS_PER_REQUEST = 600
NUMBER_OF_RECORDS_PER_SECOND = 10000
FLOAT_PRECISION = 4

DOWNSAMPLE_LEVEL_FACTOR = 100
MINIMUM_NUMBER_OF_RECORDS_LEVEL = 600
NUMBER_OF_RECORDS_PER_SLICE = 200000
PREPROCESS_DIR = 'mld-preprocess'
PREPROCESS_BUCKET = 'power-data-preprocess'
RAW_BUCKET = 'power-data-raw'

app = Flask(__name__)
CORS(app)


@app.route('/data', methods=['GET'])
def get_data():
    """HTTP endpoint to get data.

    Retrieves downsampled data, that are within the given time range, from preprocessed raw files.

    HTTP Args:
        name: A string representing the name of the file user wish to view.
        strategy: A string representing the selected downsample strategy.
        start: An int representing the start of time span user wish to view.
        end: An int representing the end of time span user wish to view.
    """
    name = request.args.get('name', type=str)
    strategy = request.args.get('strategy', default='avg', type=str)
    start = request.args.get('start', default=None, type=int)
    end = request.args.get('end', default=None, type=int)
    number = request.args.get(
        'number', default=NUMBER_OF_RECORDS_PER_REQUEST, type=int)

    if not strategy in STRATEGIES:
        error('Incorrect Strategy: %s', strategy)
        return 'Incorrect Strategy', 400

    client = storage.Client()
    preprocess = MultipleLevelPreprocess(name, PREPROCESS_DIR, client.bucket(
        PREPROCESS_BUCKET), client.bucket(RAW_BUCKET))

    if not preprocess.is_preprocessed():
        return 'Preprocessing incomplete.', 400
    data, precision = preprocess.multilevel_inference(
        strategy, number, start, end)
    response_data = {
        'data': data,
        'precision': precision
    }
    response = app.make_response(jsonify(response_data))
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


@app.route('/data', methods=['POST'])
def mlp_preprocess():
    """HTTP endpoint to preprocess.

    HTTP Args:
        name: A string representing the name of the file to preprocess.
        slice_size: An int that represents number of records for one slice.
        downsanple_factor: An int that represents downsample factor between levels.
        min_number: An int that represents the minimum number of records for a level.
    """
    name = request.args.get('name', type=str)
    number_per_slice = request.args.get('slice_size', type=int)
    downsample_factor = request.args.get('downsample_factor', type=int)
    minimum_number_level = request.args.get('min_number', type=int)

    client = storage.Client()
    preprocess = MultipleLevelPreprocess(name, PREPROCESS_DIR, client.bucket(
        PREPROCESS_BUCKET), client.bucket(RAW_BUCKET))
    preprocess.multilevel_preprocess(
        number_per_slice, downsample_factor, minimum_number_level)

    response = app.make_response('preprocess complete!')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


@app.route('/filenames')
def get_filenames():
    """HTTP endpoint to get all file names stored in bucket."""

    client = storage.Client()
    blobs = client.list_blobs(RAW_BUCKET)
    names = [blob.name for blob in blobs]
    response_data = {'names': names}
    response = app.make_response(jsonify(response_data))
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


if __name__ == '__main__':
    app.run(port=5000)
