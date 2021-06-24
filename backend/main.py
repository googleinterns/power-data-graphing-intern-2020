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
from json import loads
from flask import redirect
from flask import request
from flask import jsonify
from flask import Flask
from flask_cors import CORS
from google.cloud import storage

from data_fetcher import DataFetcher
from downsample import STRATEGIES
from multiple_level_preprocess import MultipleLevelPreprocess
from utils import warning


DOWNSAMPLE_LEVEL_FACTOR = 100
MINIMUM_NUMBER_OF_RECORDS_LEVEL = 600
NUMBER_OF_RECORDS_PER_REQUEST = 600
NUMBER_OF_RECORDS_PER_SLICE = 100000
PREPROCESS_BUCKET = 'power-data-preprocess'
PREPROCESS_DIR = 'mld-preprocess'
RAW_BUCKET = 'power-data-raw'

app = Flask(__name__)
CORS(app)


@app.route('/data', methods=['GET'])
def get_data():
    """HTTP endpoint to get data.

    Retrieves downsampled data, that are within the given time range, from preprocessed raw files.

    HTTP Args:
        name: A string representing the fill name of the file user wish to
            view. (example: DMM_res.csv)
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
    if name is None:
        warning('Empty file name.')
        response = make_response('Empty file name')
        return response, 400
    if not strategy in STRATEGIES:
        warning('Incorrect Strategy: %s', strategy)
        response = make_response('Incorrect Strategy: {}'.format(strategy))
        return response, 400

    client = storage.Client()
    fetcher = DataFetcher(name, PREPROCESS_DIR,
                          client.bucket(PREPROCESS_BUCKET))

    if not fetcher.is_preprocessed():
        response = make_response('Preprocessing incomplete.')
        return response, 404
    data, frequency_ratio = fetcher.fetch(
        strategy, number, start, end)
    response_data = {
        'data': data,
        'frequency_ratio': frequency_ratio
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

    print("Start preprocessing the file")

    form = loads(request.data.decode())
    name = form.get('name', None)
    number_per_slice = form.get('slice_size', NUMBER_OF_RECORDS_PER_SLICE)
    downsample_factor = form.get('downsample_factor', DOWNSAMPLE_LEVEL_FACTOR)
    minimum_number_level = form.get(
        'min_number', MINIMUM_NUMBER_OF_RECORDS_LEVEL)

    if name is None:
        warning('No file name!')
        response = make_response('No file name!')
        return response, 400

    client = storage.Client()
    preprocess = MultipleLevelPreprocess(name, PREPROCESS_DIR, client.bucket(
        PREPROCESS_BUCKET), client.bucket(RAW_BUCKET))
    error = preprocess.preprocess(
        number_per_slice, downsample_factor, minimum_number_level)

    if error is not None:
        response = make_response(error)
        return response

    response = make_response('preprocess complete!')
    return response


@app.route('/fileinfo')
def get_file_info():
    """HTTP endpoint to get all file names stored in bucket."""
    client = storage.Client()
    raw_bucket = client.bucket(RAW_BUCKET)
    preprocess_bucket = client.bucket(PREPROCESS_BUCKET)
    blobs = client.list_blobs(RAW_BUCKET)

    names = [blob.name for blob in blobs]
    files_preprocess = [MultipleLevelPreprocess(
        name, PREPROCESS_DIR, preprocess_bucket, raw_bucket) for name in names]

    response_data = list()
    for preprocess, name in zip(files_preprocess, names):
        response_data.append({
            'name': name,
            'preprocessed': preprocess.is_preprocessed()
        })

    response = make_response(jsonify(response_data))
    print("finishing generated file info")
    return response

@app.route('/test')
def test():
    response = make_response('OK')
    return response

@app.route('/authenticate')
def authenticate():
    """HTTP endpoint to authenticate and load cookies for client access."""
    url = request.args.get('originUrl', default=None, type=str)
    strategy = request.args.get('strategy', default=None, type=str)
    number = request.args.get('number', default=None, type=str)
    inactiveChannels = request.args.get('inactiveChannels', default=None, type=str)
    startTime = request.args.get('startTime', default=None, type=str)
    endTime = request.args.get('endTime', default=None, type=str)
    if url:
      return redirect(url+'&strategy='+strategy+"&number="+number+"&inactiveChannels="+inactiveChannels+"&startTime="+startTime+"&endTime="+endTime, code=302)
    else:
      return redirect('https://tank-big-data-plotting-285623.googleplex.com/', 302)


def make_response(response_body):
    response = app.make_response(response_body)
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    # response.headers['Access-Control-Allow-Origin'] = 'https://api-dot-tank-big-data-plotting-285623.googleplex.com'
    return response
    
@app.route('/downsample')
def scanFiles():
  client = storage.Client()
  raw_bucket = client.bucket(RAW_BUCKET)
  preprocess_bucket = client.bucket(PREPROCESS_BUCKET)
  blobs = client.list_blobs(RAW_BUCKET)

  names = [blob.name for blob in blobs]
  files_preprocess = [MultipleLevelPreprocess(
      name, PREPROCESS_DIR, preprocess_bucket, raw_bucket) for name in names]

  response_data = list()
  for preprocess, name in zip(files_preprocess, names):
      if not preprocess.is_preprocessed():
          print("Downsampling file "+name)
          number_per_slice = NUMBER_OF_RECORDS_PER_SLICE
          downsample_factor = DOWNSAMPLE_LEVEL_FACTOR
          minimum_number_level = MINIMUM_NUMBER_OF_RECORDS_LEVEL
          client = storage.Client()
          preprocess = MultipleLevelPreprocess(name, PREPROCESS_DIR, client.bucket(
              PREPROCESS_BUCKET), client.bucket(RAW_BUCKET))
          error = preprocess.preprocess(
              number_per_slice, downsample_factor, minimum_number_level)

          if error is not None:
              response = make_response(error)
              return response

  print("Downsample scan complete")
  response = make_response('Downsample scan complete')
  return response

if __name__ == '__main__':
    app.run(port=5000)
