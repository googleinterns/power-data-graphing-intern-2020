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


app = Flask(__name__)
CORS(app)


@app.route('/data')
def get_data():
    """HTTP endpoint to get data.

    Retrives all power data from local file given a limit on number of
    records from request body.
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

    preprocess = MultipleLevelPreprocess(name, PREPROCESS_DIR)

    if not preprocess.is_preprocessed():
        preprocess.multilevel_preprocess(
            NUMBER_OF_RECORDS_PER_SLICE, DOWNSAMPLE_LEVEL_FACTOR, MINIMUM_NUMBER_OF_RECORDS_LEVEL)
    data, precision = preprocess.multilevel_inference(
        strategy, number, start, end)
    response = {
        'data': data,
        'precision': precision
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(port=5000)
