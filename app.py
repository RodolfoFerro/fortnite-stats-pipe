from flask import Flask
from flask import jsonify
from flask import request
import numpy as np

from model import model_loader


app = Flask(__name__)
model = model_loader('../model.tflite')


# API MAIN STRUCTURE:
@app.route('/api/', methods=['GET'])
def test():
    """
    GET method to test the API.
    """

    # Output message:
    message = {
        "response": [
            {
                "text": "Hello world!"
            }
        ]
    }

    return jsonify(message)


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    POST method to predict using the trained model.
    """
    data = request.get_json()
    values = np.array(data['input'][0]['values'], dtype=np.float32)
    values = values.reshape((1, len(values)))

    interpreter = model['interpreter']
    input_details = model['input_details']
    output_details = model['output_details']

    # Test model on random input data.
    input_shape = input_details[0]['shape']
    interpreter.set_tensor(input_details[0]['index'], values)

    interpreter.invoke()  # HERE COMES THE MAGIC!

    # The function `get_tensor()` returns a copy of the tensor data.
    # Use `tensor()` in order to get a pointer to the tensor.
    output_data = interpreter.get_tensor(output_details[0]['index'])
    prediction = int(output_data[0][0])

    # Output message:
    message = {
        "response": [
            {
                "estimated_score": prediction
            }
        ]
    }

    return jsonify(message)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
