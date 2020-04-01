# Import required modules
import numpy as np
import pandas as pd
from os.path import join
from gekko import GEKKO


def main():
    # Data variables
    infected_data = pd.read_excel(join('data', 'source.xlsx'), sheet_name='infected_state')
    infected_data = infected_data.groupby('date')['infected_count'].sum()
    infected_data = infected_data.sort_index()
    infected_log_10 = np.log10(np.array(infected_data))

    # Model
    model = GEKKO()
    model.time = np.array(range(len(infected_data)))
    # model.time = np.array(infected_data.index)

    # Parameters
    total_us_population = 328_239_523
    initial_infected = 1

    recovery_rate = 1 / 19.6
    infection_rate = model.MV(lb=0)
    infection_rate.STATUS = 1

    # Variables
    susceptible = model.Var(value=total_us_population)
    infected = model.Var(value=initial_infected)
    recovered = model.Var(value=0)

    # System of ordinary differential equations: SIR model
    model.Equation(susceptible.dt() == -infection_rate * infected * susceptible)
    model.Equation(infected.dt() == infection_rate * infected * susceptible - recovery_rate * infected)
    model.Equation(recovered.dt() == recovery_rate * infected)

    # Objective function
    model.Obj(mean_squared_error(infected_log_10, np.log10(infected)))

    model.options.IMODE = 6
    model.solve()


def mean_squared_error(observed, predicted):
    return sum((observed - predicted) ** 2) / len(observed)


if __name__ == '__main__':
    main()