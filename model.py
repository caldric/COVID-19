# Import required modules
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from os.path import join
from gekko import GEKKO

# Data variables
breakpoint()
infected_data = pd.read_excel(join('data', 'source.xlsx'), sheet_name='infected_state')
infected_data = infected_data.groupby('date')['infected_count'].sum()
infected_data = infected_data.sort_index()
infected_data = np.array(infected_data)

# Model
model = GEKKO()
model.time = np.array(range(len(infected_data)))

# Parameters
total_us_population = 328_239_523
initial_infected = 1

recovery_rate = 1 / 19.6
infection_rate = model.FV(value=0.1, lb=0, ub=1)
infection_rate.STATUS = 1

# Variables
susceptible = model.Var(value=total_us_population)
infected = model.Var(value=initial_infected)
recovered = model.Var(value=0)

observed = model.Param(value=infected_data)

# System of ordinary differential equations: SIR model
model.Equation(susceptible.dt() == -infection_rate * infected * susceptible / total_us_population)
model.Equation(infected.dt() == infection_rate * infected * susceptible / total_us_population - recovery_rate * infected)
model.Equation(recovered.dt() == recovery_rate * infected)

# Objective function
model.Obj((observed - infected) ** 2)

model.options.IMODE = 6
model.solve()

plt.figure(1)
plt.plot(model.time, infected.value, 'r:', label='infected')
plt.plot(model.time, observed.value, 'bo', label='observed')
plt.legend(loc='best')
plt.xlabel('time (days)')
plt.ylabel('infected count')
plt.show()
