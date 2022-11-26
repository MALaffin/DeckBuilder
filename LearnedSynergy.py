import numpy as np
import tensorflow as tf
from synergyAnalyzer import plot
import matplotlib.pyplot as plt

print("TensorFlow version:", tf.__version__)


class LearnedSynergy:
    def __init__(self, sizeIn):
        self.model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=sizeIn),
            tf.keras.layers.Dense(256, activation='sigmoid'),
            tf.keras.layers.Dense(1, activation='linear')
        ])

    # def error(self, sampleOut, estimateOut):
    #     print(sampleOut)
    #     print(estimateOut)
    #     return np.sqrt(np.mean(np.square((estimateOut[0] - sampleOut[0]).flatten())))

    def trainModel(self, sampleIn, sampleOut, seed=0):
        tf.random.set_seed(seed)
        self.model.compile(optimizer='adam',
                           loss='mean_squared_error',  # self.error,#
                           metrics=['mean_absolute_error']
                           )
        # tf.config.run_functions_eagerly(True)
        # self.model.run_eagerly = True
        self.model.fit(sampleIn, sampleOut, epochs=1, batch_size=1)
        # todo:xval and likely self.model.evaluate(x_test, y_test, verbose=0)

    def useModel(self, dataIn):
        return self.model.predict(dataIn,verbose=0)

    @classmethod
    def selfTest(cls):
        test = LearnedSynergy([1])
        x = np.arange(-100, 100) / 12
        y = (x ** 2 + 2 * x + 1)/120
        test.trainModel(x, y)
        x2 = np.arange(-100, 100) / 10 + 0.005
        y2 = (x2 ** 2 + 2 * x2 + 1)/120
        y2Est = test.useModel(x2)
        plot(x2.reshape(x2.size,1), y2.reshape(x2.size,1), 'Expected', 1)
        plot(x2.reshape(x2.size,1), y2Est.reshape(x2.size,1), 'Estimated', 2)
        # self.model = tf.keras.models.Sequential([
        #     tf.keras.layers.Flatten(input_shape=sizeIn),
        #     tf.keras.layers.Dense(256, activation='sigmoid'),
        #     tf.keras.layers.Dense(1, activation='linear')
        # ])
        # self.model.fit(sampleIn, sampleOut, epochs=20, batch_size=1)
        # about 0.06 mean_absolute_error
        plt.show()
