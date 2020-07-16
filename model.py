import tensorflow as tf


def build_model():
    lr = 1e-3
    opt = tf.keras.optimizers.Adam(lr=lr)

    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Dense(1, input_shape=[1]))
    model.compile(loss='mean_squared_logarithmic_error', optimizer='adam')

    return model

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