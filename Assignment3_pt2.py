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
    ages = np.arange(0, 61)

    for name in simulator.tires.index:
        p = simulator.tires.loc[name]
        times = simulator.tire_time(ages, p['Tmin'], p['Tmax'], p['alpha'], p['beta'])
        plt.plot(ages, times, label=name)

    plt.xlabel('Tire Age')
    plt.ylabel('Time added (s)')
    plt.title('Tire Degradation')
    plt.legend()
    plt.show()



def find_best_strategy(simulator):
    total_laps = 60
    compounds = list(simulator.tires.index)

    tire_options = set(combinations(compounds * 3, 3))

    best_time = float('inf')
    best_strategy = None

    for pits in combinations(range(2, 61), 2):
        stint_lengths = np.diff([1, *pits, total_laps +1])

        for tire_seq in tire_options:
            if len(set(tire_seq)) < 2:
                   continue

            total = simulator.simulate(stint_lengths, tire_seq)

            if total < best_time:
                best_time = total
                best_strategy = (pits, tire_seq)

    return best_strategy, best_time

sim = RaceSimulator()
strategy, best = find_best_strategy(sim)
print(strategy, best)

#print(sim.simulate([14, 8, 38], ["Soft", "Medium", "Hard"]))

#plot_tires(sim)  