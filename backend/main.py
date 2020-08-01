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
import os

from flask import request
from flask import jsonify
from flask import Flask
from flask_cors import CORS
import utils
import downsample
import multiple_level_downsample as mld

NUMBER_OF_RECORDS_PER_REQUEST = 600
NUMBER_OF_RECORDS_PER_SECOND = 10000
FLOAT_PRECISION = 4

DOWNSAMPLE_LEVEL_FACTOR = 100
MINIMUM_NUMBER_OF_RECORDS_LEVEL = 600
NUMBER_OF_RECORDS_PER_SLICE = 200000
PREPROCESS_DIR = 'mld-prerpocess'


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
    if not strategy in downsample.STRATEGIES:
        utils.error('Incorrect Strategy: %s', strategy)
        return 'Incorrect Strategy', 400

    # Old approach
    # preprocess_filename = utils.generate_filename_on_strategy(
    #     name, strategy)

    # if not os.path.isfile(preprocess_filename):
    #     downsample.preprocess(name, NUMBER_OF_RECORDS_PER_SECOND)

    # data = downsample.secondary_downsample(
    #     preprocess_filename, strategy, NUMBER_OF_RECORDS_PER_REQUEST, start, end)

    experiment = utils.get_experiment_name(name)
    preprocess_metadata = '/'.join([PREPROCESS_DIR,
                                    experiment, 'metadata.json'])
    if not os.path.isfile(preprocess_metadata):

        mld.multilevel_preprocess(name, PREPROCESS_DIR, NUMBER_OF_RECORDS_PER_SLICE,
                                  DOWNSAMPLE_LEVEL_FACTOR, MINIMUM_NUMBER_OF_RECORDS_LEVEL)

    data, precision = mld.multilevel_inference(
        name, strategy, NUMBER_OF_RECORDS_PER_REQUEST, start, end)
    response = {
        'data': data,
        'precision': precision
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(port=5000)
