# Import required modules
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

from io import StringIO
from os.path import join
from scipy.integrate import odeint
from scipy.optimize import minimize


def main():
    # Data variables
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/' \
          + 'csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
    infected_data = wrangle_data(url)
    infected_data = infected_data.groupby('date')['infected_count'].sum()
    infected_data = infected_data.sort_index()
    infected_data = np.array(infected_data)

    # Population data
    total_us_population = 328_239_523
    initial = {
        'recovered': 0,
        'infected': infected_data[0],
        'susceptible': total_us_population - infected_data[0]
    }

    # Input parameters
    recovery_rate = 1 / 19.6

    # Solver
    estimated_infection_rate = solver(
        func=objective, population=total_us_population, initial=initial, observed_infected=infected_data,
        recovery_rate=recovery_rate
    )

    # Projection
    project(
        population=total_us_population, initial=initial, days=500, infection_rate=estimated_infection_rate,
        recovery_rate=recovery_rate, observed_infected=infected_data
    )


def sir_model(z, t, beta, gamma, n):
    s, i, r = z
    ds_dt = -beta * i * s / n
    di_dt = beta * i * s / n - gamma * i
    dr_dt = gamma * i

    return [ds_dt, di_dt, dr_dt]


def objective(infection_rate, population, initial, observed_infected, recovery_rate):
    # Time points
    t = np.array(range(len(observed_infected)))

    # Store initial conditions
    initial_values = [initial['susceptible'], initial['infected'], initial['recovered']]

    # Solve ODE
    compartments = odeint(sir_model, initial_values, t, args=(infection_rate, recovery_rate, population))
    infected = compartments[:, 1]

    observed = observed_infected
    estimated = infected

    return sum((observed - estimated) ** 2)


def solver(func, population, initial, observed_infected, recovery_rate):
    # Time points
    t = np.array(range(len(observed_infected)))

    # Solve for best fitting infection rate
    initial_infection_rate = 0.2
    solution = minimize(
        func, initial_infection_rate, args=(population, initial, observed_infected, recovery_rate)
    )
    estimated_infection_rate = solution.x[0]

    # Store initial conditions
    initial_values = [initial['susceptible'], initial['infected'], initial['recovered']]

    # Solve ODE
    compartments = odeint(sir_model, initial_values, t, args=(estimated_infection_rate, recovery_rate, population))
    infected = compartments[:, 1]
    r0 = estimated_infection_rate / recovery_rate

    # Plot data
    fig = plt.figure()
    fig.set_size_inches(10, 5)
    plt.plot(t, infected, 'r-', label='estimated')
    plt.plot(t, observed_infected, 'bo', label='observed')
    plt.legend(loc='best')
    plt.xlabel('time (days since 22 Jan 2020)')
    plt.ylabel('infected count')
    plt.title(r'Count vs. Time $(\beta={}, R_0={})$'.format(round(estimated_infection_rate, 4), round(r0, 1)))

    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    plt.show()
    fig.savefig('fit.eps')

    return estimated_infection_rate


def project(population, initial, days, infection_rate, recovery_rate, observed_infected=None):
    # Time points
    t = np.array(range(days))

    # Store initial conditions
    initial_values = [initial['susceptible'], initial['infected'], initial['recovered']]

    # Solve ODE
    compartments = odeint(sir_model, initial_values, t, args=(infection_rate, recovery_rate, population))
    susceptible = compartments[:, 0]
    infected = compartments[:, 1]
    recovered = compartments[:, 2]

    # Plot data
    fig = plt.figure()
    fig.set_size_inches(10, 5)
    plt.semilogy(t, susceptible, 'k-', label='susceptible')
    plt.semilogy(t, infected, 'r-', label='infected')
    plt.semilogy(t, recovered, 'b-', label='recovered')
    # plt.plot(t, susceptible, 'k-', label='susceptible')
    # plt.plot(t, infected, 'r-', label='infected')
    # plt.plot(t, recovered, 'b-', label='recovered')
    plt.legend(loc='best')
    plt.xlabel('time (days since 22 Jan 2020)')
    plt.ylabel('count')
    plt.title('Count vs. Time')

    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    plt.show()
    fig.savefig('projection.eps')


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
