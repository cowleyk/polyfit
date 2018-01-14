import numpy as np

from nio.block.base import Block
from nio.properties import VersionProperty, IntProperty, Property
from nio.block.base import Signal


class Polyfit(Block):
    """Block to find trend line of data

    properties:
        degree: degree of polynomial to fit
        length: how many data points to store/fit polynomial to

    """
    version = VersionProperty('0.1.0')
    degree = IntProperty(title='Degree of polynomial (static)', default=1)
    independent = Property(title='Independent Variable', default='{{ $x }}')
    dependent = Property(title='Dependent Variable', default='{{ $y }}')
        # time should be in unix timestamps
    num_data_points = IntProperty(title='Number of data points to store', default=50)
        # ^ probably want to cap

    def configure(self, context):
        super().configure(context)
        self.x_array = np.array([])
        self.y_array = np.array([])

    def process_signals(self, signals):

        # TODO: BUILD OUT X & Y ARRAY POP/APPEND SIMILAR TO PLOTLY BLOCK
            # want to take in single signal at a time

        for signal in signals:
            if len(self.x_array) < self.num_data_points():
                self.x_array = np.append(self.x_array,
                                         self.independent(signal))
                self.y_array = np.append(self.y_array,
                                         self.dependent(signal))
            else:
                self.x_array = np.append(self.x_array[1:],
                                         self.dependent(signal))
                self.y_array = np.append(self.y_array[1:],
                                         self.independent(signal))

            # calculate coefficient matrix
            z = np.polyfit(self.x_array, self.y_array, self.degree())

            # calculate value p(x) for each x
            p_x_array = []
            for dep in self.x_array:
                p_x = self._evaluate_polynomial(z, dep)
                p_x_array.append(p_x)


        self.notify_signals(
            [Signal({
                'polynomial_value': p_x_array,
                'independent_values': self.x_array.tolist(),
                'dependent_values': self.y_array.tolist()
            })]
        )

    def _evaluate_polynomial(self, coefficients, x):
        # want to return a function that will take an input and calc p(x)
        p_x = 0
        for deg in range(len(coefficients)):
            p_x += coefficients[deg] * x ** (self.degree()-deg)
        return p_x
