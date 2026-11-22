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
        self.max_laps = 60


    def tire_time(self, age, Tmin, Tmax, alpha, beta):
        """
        Calculate the time added due to tire degradation.

        Parameters:
            age: Tire age in laps.
            Tmin: Minimum time added by the tire.
            Tmax: Maximum time added by the tire.
            alpha: Tire degradation rate parameter.
            beta: Tire degradation midpoint parameter.

        Returns:
            Tire time added for the given tire age.
        """
        time_added = Tmin + (Tmax - Tmin) / (1 + np.exp(-alpha*(age-beta)))
        return time_added

    def simulate(self, pitstops, tireTypes):
        """
        Simulate a complete race strategy.

        Parameters:
            pitStops: List of pitstop laps.
            tireTypes: List of Tire compound used for each stint, must adhere to the types in sim index.

        Returns:
            Total time added from tire degradation and pit stops.
        """
        if len(pitstops) < 2:
            raise ValueError("At least two pitstops are required for a valid race strategy.")

        if any((lap > self.max_laps) or lap < 0 for lap in pitstops):
            raise ValueError("Pitstop lap numbers cannot exceed the maximum number of laps in the race.")

        if not all(tire in self.tires.index for tire in tireTypes):
            raise ValueError("Invalid tire type specified.")

        if len(set(tireTypes)) < 2:
            raise ValueError("You must use at least two different tire types in a valid race strategy.")

        pitstops = sorted(pitstops)
        stints = []
        boundaries = [1] + pitstops + [self.max_laps + 1]
        stint_lengths = [end - start for start, end in zip(boundaries[:-1], boundaries[1:])] #Calculate how many laps are in each stint

        lapTuples = list(zip(stint_lengths, tireTypes))

        for i, (length, tire) in enumerate(lapTuples):
            p = self.tires.loc[tire]

            #print(f"Simulating stint {i+1}: {length} laps on {tire} tires")
            
            stintStart = 1 if i == 0 else pitstops[i - 1]
            
            df = pd.DataFrame()
            df['age'] = np.arange(0, length)
            df['lap'] = np.arange(stintStart, stintStart+length)
            df['tire_time'] = self.tire_time(df['age'], p['Tmin'], p['Tmax'], p['alpha'], p['beta'])
            df['pit_time'] = 0

            if i > 0:
                df.loc[0, 'pit_time'] = self.pit_time

            stints.append(df)

        race = pd.concat(stints, ignore_index=True)

        return race['tire_time'].sum() + race['pit_time'].sum()


def plot_tires(simulator: RaceSimulator):
    """
    Plot tire degradation curves for all tire compounds.

    Parameters:
        simulator: A RaceSimulator object containing tire data.

    Returns:
        None.
    """
    ages = np.arange(0, 60)

    for name in simulator.tires.index:
        p = simulator.tires.loc[name]
        times = simulator.tire_time(ages, p['Tmin'], p['Tmax'], p['alpha'], p['beta'])
        plt.plot(ages, times, label=name)

    plt.xlabel("Tire Age (laps)")
    plt.ylabel("Time Added (s)")
    plt.title("Tire Degradation Curves by Compound")
    plt.legend()
    plt.show()

def find_best_strategy(simulator:RaceSimulator):
    """
    Test all valid race strategies and find the one
    with the minimum total time added.

    Parameters:
        simulator: A RaceSimulator object.

    Returns:
        The strategy with the lowest total tire and pit time.
    """

    bestTime = float("inf")
    bestStrategy = None


    pitStopCombos = list(combinations(range(1, simulator.max_laps), 2))
    tireTypeCombos = list(combinations_with_replacement(simulator.tires.index, 3))

    for pitStops in pitStopCombos:
        for tireTypes in tireTypeCombos:
            try:
                totalTime = simulator.simulate(pitStops, tireTypes)

            except:
                continue #Ignore invalid strategies.

            if totalTime < bestTime:
                bestTime = totalTime
                bestStrategy = (pitStops, tireTypes)

    if bestStrategy is None:
        raise RuntimeError("No valid race strategy found.")

    print(
    f"Best strategy found ({bestTime:.2f}s added)! "
    f"Pitstops at laps: {' and '.join(str(lap) for lap in bestStrategy[0])} "
    f"using tire types: {' then '.join(str(tire) for tire in bestStrategy[1])}."
)

    return bestTime, bestStrategy

    