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
    infected_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/' \
          + 'csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
    infected_data = wrangle_data(infected_url)
    infected_data = infected_data.groupby('date')['count'].sum()
    infected_data = infected_data.sort_index()
    infected_data = infected_data[70:]
    start_date = infected_data.index[0]
    infected_data = np.array(infected_data)

    # Population data
    total_us_population = 328_239_523
    recovered_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/' \
        + 'csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
    initial_recovered = get_recovered(recovered_url, start_date)
    initial = {
        'recovered': initial_recovered,
        'infected': infected_data[0],
        'susceptible': total_us_population - infected_data[0] - initial_recovered
    }

    # Input parameters
    recovery_rate = 1 / 19.6

    # Solver
    estimated_infection_rate = solver(
        func=objective, population=total_us_population, initial=initial, observed_infected=infected_data,
        recovery_rate=recovery_rate, start_date=start_date
    )

    # Projection
    project(
        population=total_us_population, initial=initial, days=500, infection_rate=estimated_infection_rate,
        recovery_rate=recovery_rate, start_date=start_date
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


def solver(func, population, initial, observed_infected, recovery_rate, start_date):
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
    fig1 = plt.figure()
    fig1.set_size_inches(10, 5)
    plt.plot(t, infected, 'r-', label='estimated')
    plt.plot(t, observed_infected, 'bo', label='observed')
    plt.legend(loc='best')
    plt.xlabel('time (days since {})'.format(start_date.strftime('%d %b %Y')))
    plt.ylabel('infected count')
    plt.title(r'Count vs. Time $(\beta={}, R_0={})$'.format(round(estimated_infection_rate, 4), round(r0, 1)))

    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    plt.savefig('fit.png')
    plt.show()
    plt.close()

    return estimated_infection_rate


def project(population, initial, days, infection_rate, recovery_rate, start_date):
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
    fig2 = plt.figure()
    fig2.set_size_inches(10, 5)
    ax = plt.gca()

    plt.semilogy(t, susceptible, 'k-', label='susceptible')
    plt.semilogy(t, infected, 'r-', label='infected')
    plt.semilogy(t, recovered, 'b-', label='recovered')

    # notable points
    plt.semilogy(t[-1], susceptible[-1], 'ko')
    ax.annotate('{:,}'.format(int(round(susceptible[-1]))), (t[-1] - 20, susceptible[-1] * 1.50), ha='center')
    t_max_infected = np.where(infected == max(infected))[0][0]
    plt.semilogy(t_max_infected, max(infected), 'ro')
    ax.annotate('{:,}'.format(int(round(max(infected)))), (t_max_infected + 20, 1e8))
    plt.semilogy(t[-1], infected[-1], 'ro')
    ax.annotate('{:,}'.format(int(round(infected[-1]))), (t[-1], 5), ha='center')

    plt.legend(loc='best')
    plt.xlabel('time (days since {})'.format(start_date.strftime('%d %b %Y')))
    plt.ylabel('count')
    plt.title('Count vs. Time')

    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    plt.savefig('projection.png')
    plt.show()
    plt.close()


def wrangle_data(url):
    # Lookup data
    us_state_codes = pd.read_csv(join('data', 'us_state_codes.csv'))
    us_state_coordinates = pd.read_csv(join('data', 'us_state_coordinates.csv'))
    us_state_lookups = pd.merge(us_state_codes, us_state_coordinates, on=['state'], how='inner')

    content = requests.get(url).content
    raw_data = pd.read_csv(StringIO(content.decode('utf-8')))

    # Data wrangling
    # remove unneeded columns
    data = raw_data.drop(
        ['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Country_Region', 'Lat', 'Long_', 'Combined_Key'], axis=1
    )
    # rename state column
    data = data.rename({'Province_State': 'state'}, axis=1)
    # group by state
    data = data.groupby(['state']).sum().reset_index()
    # unpivot date columns
    data = data.melt(id_vars=['state'], var_name='date', value_name='count')
    # transform date column from str to datetime
    data['date'] = pd.to_datetime(data['date'], format='%m/%d/%y')
    # merge state codes and coordinates to infected data
    data = pd.merge(data, us_state_lookups, on=['state'], how='right')
    # rearrange columns
    data = data[['state', 'state_code', 'latitude', 'longitude', 'date', 'count']]

    return data


def get_recovered(url, start_date):
    # Obtain source data
    content = requests.get(url).content
    raw_data = pd.read_csv(StringIO(content.decode('utf-8')))

    # Data wrangling
    # filter for country: US
    data = raw_data[raw_data['Country/Region'] == 'US']
    # remove unneeded rows
    data = data.drop(['Province/State', 'Lat', 'Long'], axis=1)
    # rename country column name
    data = data.rename({'Country/Region': 'country'}, axis=1)
    # unpivot data
    data = data.melt(id_vars=['country'], var_name='date', value_name='count')
    # transform date column to type datetime
    data['date'] = pd.to_datetime(data['date'], format='%m/%d/%y')
    # filter only for the start_date
    data = data[data['date'] == start_date]
    # obtain recovered count
    count = int(data['count'])

    return count


if __name__ == '__main__':
    main()
