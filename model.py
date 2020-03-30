# Import required modules
import pandas as pd
from os.path import join
from gekko import GEKKO


def main():
    # Data variables
    infected_data = pd.read_excel(join('data', 'source.xlsx'), sheet_name='infected_state')
    infected_data['date'] = pd.to_datetime(infected_data['date'], format='%Y-%m-%d')
    infected_data = infected_data.loc[infected_data['date'] > '2020-02-29']
    dates = sorted(set(infected_data['date']))
    infected_data_at = {}
    for date in dates:
        infected_data_at[date] = infected_data.loc[infected_data['date'] == date].reset_index()

    # Model
    model = GEKKO()

    # Parameters
    total_us_population = 323_000_000
    initial_infected = 900

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
    model.Obj()

    model.options.IMODE = 6
    model.solve()


def mean_squared_error():
    pass


if __name__ == '__main__':
    main()
