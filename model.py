# Import required modules
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

from io import StringIO
from os.path import join
from gekko import GEKKO


def main():
    # Data variables
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/' \
          + 'csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
    infected_data = wrangle_data(url)
    infected_data = infected_data.groupby('date')['infected_count'].sum()
    infected_data = infected_data.sort_index()
    infected_data = np.array(infected_data)

    # Model
    model = GEKKO()
    model.time = np.array(range(len(infected_data)))

    # Parameters
    total_us_population = 328_239_523
    initial_infected = 1
    initial_susceptible = total_us_population - initial_infected

    recovery_rate = 1 / 19.6
    infection_rate = model.FV(value=0.1, lb=0, ub=1)
    infection_rate.STATUS = 1

    # Variables
    susceptible = model.Var(value=initial_susceptible)
    infected = model.Var(value=initial_infected)
    recovered = model.Var(value=0)

    observed = model.Param(value=infected_data)

    # System of ordinary differential equations: SIR model
    model.Equation(susceptible.dt() == -infection_rate * infected * susceptible / total_us_population)
    model.Equation(
        infected.dt() == infection_rate * infected * susceptible / total_us_population - recovery_rate * infected)
    model.Equation(recovered.dt() == recovery_rate * infected)

    # Objective function
    model.Obj((observed - infected) ** 2)

    model.options.IMODE = 6
    model.solve()

    plt.figure(1)
    plt.plot(model.time, infected.value, 'r:', label='infected')
    plt.plot(model.time, observed.value, 'bo', label='observed')
    plt.legend(loc='best')
    plt.xlabel('time (days since 22 Jan 2020)')
    plt.ylabel('infected count')
    plt.show()


def wrangle_data(url):
    # Lookup data
    us_state_codes = pd.read_csv(join('data', 'us_state_codes.csv'))
    us_state_coordinates = pd.read_csv(join('data', 'us_state_coordinates.csv'))
    us_state_lookups = pd.merge(us_state_codes, us_state_coordinates, on=['state'], how='inner')

    content = requests.get(url).content
    raw_data = pd.read_csv(StringIO(content.decode('utf-8')))

    # Data wrangling
    # remove unneeded columns
    infected_data = raw_data.drop(
        ['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Country_Region', 'Lat', 'Long_', 'Combined_Key'], axis=1
    )
    # rename state column
    infected_data = infected_data.rename({'Province_State': 'state'}, axis=1)
    # group by state
    infected_data = infected_data.groupby(['state']).sum().reset_index()
    # unpivot date columns
    infected_data = infected_data.melt(id_vars=['state'], var_name='date', value_name='infected_count')
    # transform date column from str to datetime
    infected_data['date'] = pd.to_datetime(infected_data['date'], format='%m/%d/%y')
    # merge state codes and coordinates to infected data
    infected_data = pd.merge(infected_data, us_state_lookups, on=['state'], how='right')
    # rearrange columns
    infected_data = infected_data[['state', 'state_code', 'latitude', 'longitude', 'date', 'infected_count']]

    return infected_data


if __name__ == '__main__':
    main()
