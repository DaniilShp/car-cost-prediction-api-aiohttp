import os.path

from keras.models import Sequential
from keras.layers import Dense
from keras.models import load_model
from regression.regression_prediction import RegressionPrediction


class FullyConnectedNeuralNetwork(RegressionPrediction):
    def __init__(self, input_size: tuple, number_of_neurons: int = 64, optimize_method: str = 'adam'):
        self._model = Sequential()
        self._model.add(Dense(number_of_neurons, activation='elu', input_shape=input_size))
        self._model.add(Dense(number_of_neurons / 2, activation='relu', input_shape=input_size))
        self._model.add(Dense(4, activation='relu', input_shape=input_size))
        self._model.add(Dense(1))
        self._model.compile(optimizer=optimize_method, loss='mse', metrics=['mae'])

    def load_model(self, model_filename: str):
        self._model = load_model(model_filename)

    def fit(self, data, target, epochs: int = 100, batch_size: int = 1, verbose: int = 2, save: bool = False, **kwargs):
        history = self._model.fit(data, target, epochs=epochs, batch_size=batch_size, verbose=verbose)
        if save:
            self._model.save(os.path.join('models', f'model_{round(history.history["mae"][-1])}.h5'))

    def predict(self, data):
        predictions = self._model.predict(data)
        return predictions
