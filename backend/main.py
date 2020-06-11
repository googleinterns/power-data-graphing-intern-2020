# Simple backend server using flask framework

from flask import request
from flask import jsonify
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def downsample_raw_data(file_name, num_records, max_records):
    '''Desample power data

        Read power data from given filename, desample and limit number of records to the given number.
        The desample strategy is to select one data point per certain number to ensure that output 
        data points are kept under threshold.

        Args:
            file_name: The filename of data csv
            num_records: Total number of data points 
            max_records: Max number of data points to output
        
        Returns:
            A list of power data. For example:
            [
                ['1532523212', '53', 'SYSTEM'],
                ['1532523242', '33', 'SYSTEM']
            ]
    '''
    data = list()
    frequency = num_records / max_records

    with open(file_name, 'r') as fr:
        for i, line in enumerate(fr):
            if i % frequency == 0:
                data.append(line.strip('\n').split(','))
    return data
    


@app.route('/data')
def getData():
    '''HTTP endpoint to get data
        
        Retrives all power data from local file given a limit on number of records from request body.
    '''

    fn = 'Power_sample_data.csv'
    num_records = 7200000  # assume number of records is accessible upon deployment
    max_records = request.args.get('number', default=6000, type=int)
    
    data = downsample_raw_data(fn, num_records, max_records)
    # TODO(tangyifei@): Implementation too naive, will improve with selected time interval, better desample strategy.
    return jsonify(data)


@app.route("/")
def hello():
    return "Hello world, welcome to Google"


if __name__ == '__main__':
    app.run(port=5000)
