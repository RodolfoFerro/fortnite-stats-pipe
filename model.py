import tensorflow as tf


def model_loader(model_path):
    """Model loader function."""

    # Load TFLite model and allocate tensors.
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    model_dict = dict(
        interpreter=interpreter,
        input_details=input_details,
        output_details=output_details
    )

    print("[INFO] The model has been loaded successfully!")

    return model_dict