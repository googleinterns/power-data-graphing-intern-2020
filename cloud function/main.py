import os
import requests


DOWNSAMPLE_LEVEL_FACTOR = 100
MINIMUM_NUMBER_OF_RECORDS_LEVEL = 600
NUMBER_OF_RECORDS_PER_SLICE = 200000


def preprocess_trigger(event, context):
    """Triggered by a upload to power-data-raw bucket, then preprocess
    the raw data.

    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    print("cloud function starts downsampling files")
    url = os.environ.get('URL')
    file = event['name']
    params = {
        'slice_size': NUMBER_OF_RECORDS_PER_SLICE,
        'name': file,
        'downsample_factor': DOWNSAMPLE_LEVEL_FACTOR,
        'min_number': MINIMUM_NUMBER_OF_RECORDS_LEVEL,
    }

    response = requests.post(url+'/data', params=params,
                             headers={'Access-Control-Allow-Credentials': 'true'})
    print(response)
    print(event)
    print(context)
    print(params)
    print(url)
    return response.text


