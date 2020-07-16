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
import logging
import os

from flask import request
from flask import jsonify
from flask import Flask
from flask_cors import CORS
import utils
import downsample

NUMBER_OF_RECORDS_PER_REQUEST = 600
NUMBER_OF_RECORDS_PER_SECOND = 10000
FLOAT_PRECISION = 4


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
        logging.error('Incorrect Strategy: %s', strategy)
        return 'Incorrect Strategy', 400

    preprocess_filename = utils.generate_filename_on_strategy(
        name, strategy)

    if not os.path.isfile(preprocess_filename):
        downsample.preprocess(name, NUMBER_OF_RECORDS_PER_SECOND)

    data = downsample.secondary_downsample(
        preprocess_filename, strategy, NUMBER_OF_RECORDS_PER_REQUEST, start, end)

    # TODO(tangyifei@): Support csv file name in HTTP argument and upload new csv file.
    return jsonify(data)


@app.route('/preprocessing')
def preprocessing():
    """HTTP endpoint to preprocess data.

    Preprocess data for all strategy and save results locally,
    each strategy in a file.
    """
    name = request.args.get('name', type=str)
    rate = request.args.get('name', type=int)
    success = downsample.preprocess(name, rate)
    if success:
        return 'Preprocessing Successful!', 200
    else:
        return 'Preprocessing Incomplete', 400


if __name__ == '__main__':
    app.run(port=5000)
