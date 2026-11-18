import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations, combinations_with_replacement


class RaceSimulator:
    """
    Simulates an F1 race strategy by calculating the time added
    from tire degradation and pit stops.
    """

    def __init__(self):
        self.tires = pd.DataFrame({
            'Tire': ['Soft', 'Medium', 'Hard'],
            'Tmin': [0, 1, 2],
            'Tmax': [10, 10, 10],
            'alpha': [0.5, 0.25, 0.0625],
            'beta': [15, 25, 55],
            },
            index = ['Soft', 'Medium', 'Hard'])
        self.pit_time = 25


    def tire_time(self, age, Tmin, Tmax, alpha, beta):
        time_added = Tmin + (Tmax - Tmin) / (1 + np.exp(-alpha*(age-beta)))
        return time_added

    def simulate(self, stint_lengths, tire_types):
        stints = []
        for i, (length, tire) in enumerate(zip(stint_lengths, tire_types)):
            p = self.tires.loc[tire]

            df = pd.DataFrame()
            df['age'] = np.arange(0, length)
            df['tire_time'] = self.tire_time(df['age'], p['Tmin'], p['Tmax'], p['alpha'], p['beta'])
            df['pit_time'] = 0

            if i > 0:
                df.loc[0, 'pit_time'] = self.pit_time

            stints.append(df)

        race = pd.concat(stints, ignore_index=True)
        return race['tire_time'].sum() + race['pit_time'].sum()



def plot_tires(simulator):
    ages = np.arange(0, 60)

    for name in simulator.tires.index:
        p = simulator.tires.loc[name]
        times = simulator.tire_time(ages, p['Tmax'], p['Tmin'], p['alpha'], p['beta'])
        plt.plot(ages, times, label=name)

    plt.xlabel()



def find_best_strategy(simulator):
    """
    Test all valid race strategies and find the one
    with the minimum total time added.

    Parameters:
        simulator: A RaceSimulator object.

    Returns:
        The strategy with the lowest total tire and pit time.
    """
    pass