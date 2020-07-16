import requests
import random
from pprint import pprint
from glob import glob


def test_prediction(url, kills):
    """
    Display JSON response for prediction.
    """

    # Set metadata:
    headers = {'Content-type': 'application/json'}
    input_data = {
        "input": [
            {
                "values": [kills]
            }
        ]
    }

    # Get response:
    response = requests.post(url, json=input_data, headers=headers)

    # If response's status is 200:
    if response.status_code == requests.codes.ok:
        # Pretty print response:
        pprint(response.json())

    return


if __name__ == '__main__':
    test_prediction('http://localhost:5000/api/predict', 700)