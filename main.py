from simulation import Simulation
from optimisation import Optimisation
from helper import *

arrival_rates = {
    "7":  [1, 1, 2, 2, 3, 2],
    "8":  [2, 3, 3, 4, 5, 6],
    "9":  [7, 7, 6, 5, 4, 4],
    "10": [3, 3, 2, 3, 2, 2],
    "11": [1, 2, 2, 3, 1, 3],
    "12": [2, 3, 4, 5, 5, 4],
    "13": [4, 2, 2, 1, 2, 1],
    "14": [1, 3, 3, 4, 4, 3],
    "15": [2, 1, 2, 2, 1, 1],
    "16": [2, 2, 3, 3, 2, 1],
    "17": [1, 1, 2, 4, 5, 5],
    "18": [5, 5, 7, 6, 7, 8],
    "19": [7, 5, 4, 3, 3, 2],
    "20": [2, 2, 3, 2, 2, 1]}


electricity_off_schedule = ["8:50-9:10", "13:10-15:30", "17:00-20:55"]

drinks = ["cappucino", "latte", "espresso", "cortado", "americano"]
drinks_probabilities = [0.3, 0.15, 0.2, 0.25, 0.1]
drinks_profits = [20, 22, 14, 12, 14]

gen_price = 400
gen_minimal_time = 40
max_customers = 5


mean_drinks_profit = get_mean_drinks_profit(drinks_probabilities, drinks_profits)
print(mean_drinks_profit)

optimisation = Optimisation(gen_price=gen_price, gen_minimal_time=gen_minimal_time, mean_drink_profit=mean_drinks_profit, arrival_rates=arrival_rates, max_customers=max_customers)

generator_optimal_time = optimisation.get_optimal_generator_schedule(electricity_off_schedule=electricity_off_schedule)

if generator_optimal_time is not None:
    for time_period in generator_optimal_time:
        print(f'оптимальний час роботи генератора = {m_to_hm(time_period[0])}-{m_to_hm(time_period[1])}')

simulation = Simulation(arrival_rates=arrival_rates, drinks=drinks, drinks_probabilities=drinks_probabilities, drinks_profits=drinks_profits, gen_price=gen_price, gen_minimal_time=gen_minimal_time, max_customers=max_customers, electricity_off_schedule=electricity_off_schedule)
simulation.simulation(with_generator=True)
if generator_optimal_time is not None:
    for time_period in generator_optimal_time:
        print(f'оптимальний час роботи генератора = {m_to_hm(time_period[0])}-{m_to_hm(time_period[1])}')
simulation.graph_after_simulation(with_generator=True)



