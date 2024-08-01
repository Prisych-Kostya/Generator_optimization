import numpy as np
import metrics
import helper
import optimisation
import stats
import matplotlib.pyplot as plt
import matplotlib.patches as patches 
from helper import *

class Simulation():
    def __init__(self, arrival_rates, drinks, drinks_probabilities, drinks_profits, gen_price, gen_minimal_time,  max_customers, electricity_off_schedule):
        arrival_rates:dict[str, list[float]]
        drinks:list[str]
        drinks_probabilities:list[float]
        drinks_profits:list[int]
        gen_price:float
        gen_minimal_time:int
        max_customers:int
        electricity_off_schedule: list[str]
        self.arrival_rates = arrival_rates
        self.drinks = drinks
        self.drinks_probabilities = drinks_probabilities
        self.drinks_profits = drinks_profits
        self.gen_price = gen_price
        self.gen_minimal_time = gen_minimal_time
        self.max_customers = max_customers
        self.opening_time = int(min(int(key) for key in arrival_rates.keys())) * 3600
        self.closing_time = int(max(int(key) for key in arrival_rates.keys()) + 1) * 3600
        self.time = self.opening_time
        self.mean_drink_profit = get_mean_drinks_profit(self.drinks_probabilities, self.drinks_profits)
        self.electricity_off_schedule = electricity_off_schedule
        self.metrics = metrics.Metrics(drinks=drinks, drinks_profits=drinks_profits)

    
    def generate_poiss_event(self, rate):
        return round(np.random.poisson(1 / (rate)))
    

    def pick_random_drink(self, drink_names, probabilities):
        return np.random.choice(drink_names, p=probabilities)
    

    def get_drink_profit(self, drink, drink_names, drinks_profits):
        return drinks_profits[drink_names.index(drink)]


    def calculate_working_periods(self, opening_time: int, closing_time: int, electricity_off_periods: list[list[int]]) -> list[list[int, bool]]:
        """forms working periods by removing electricity_off_periods
        """
        working_periods = []

        # Add the initial working period if the cafe starts working immediately
        if opening_time < electricity_off_periods[0][0]:
            working_periods.append([opening_time, electricity_off_periods[0][0]])

        # Iterate through electricity outages and add working periods
        for i in range(len(electricity_off_periods) - 1):
            working_periods.append([electricity_off_periods[i][1], electricity_off_periods[i + 1][0]])

        # Add the final working period if the cafe continues working after the last outage
        if electricity_off_periods[-1][1] < closing_time:
            working_periods.append([electricity_off_periods[-1][1], closing_time])

        return working_periods
    

    def calculate_working_periods_with_generator(self, working_periods, generator_periods):
        combined_periods = []

        # Combine working periods and generator periods
        all_periods = sorted(working_periods + generator_periods, key=lambda x: x[0])

        # Add each period without merging
        for period in all_periods:
            combined_periods.append(period)

        return combined_periods


    def form_simulation_periods(self, with_generator: bool) -> list[list[int, bool]]:
        electricity_off_periods = helper.split_electricity_schedule(self.electricity_off_schedule)
        for i in range(len(electricity_off_periods)):
            for j in range(len(electricity_off_periods[i])):
                electricity_off_periods[i][j] *= 60
        working_periods = self.calculate_working_periods(opening_time=self.opening_time, closing_time=self.closing_time, electricity_off_periods=electricity_off_periods)
        for period in working_periods:
            period.append(False)

        if with_generator:
            # get optimal generator periods list
            generator_periods = optimisation.Optimisation(self.gen_price, self.gen_minimal_time, get_mean_drinks_profit(self.drinks_probabilities, self.drinks_profits), self.arrival_rates, self.max_customers).get_optimal_generator_schedule(self.electricity_off_schedule)
            # convert generator periods from minutes to seconds by multiplying by 60
            # and changing list structure to [[t1, t2, True], [t3, t4, True]] where True means working generator 
            for i in range(len(generator_periods)):
                for j in range(len(generator_periods[i])):
                    generator_periods[i][j] *= 60
            for period in generator_periods:
                period.append(True)

            working_periods = self.calculate_working_periods_with_generator(working_periods=working_periods, generator_periods=generator_periods)
        
        return working_periods

    
    def simulation(self, with_generator: bool):
        # We need to form working schedule before simulation  
        if with_generator:
            working_periods = self.form_simulation_periods(with_generator=True)

        self.time = working_periods[0][0] 
        rates = helper.normalize_arrival_rates(self.arrival_rates, self.max_customers)
        generator_was_working = False
        
        for period in working_periods:
            self.time = period[0]
            period_end        = period[1]
            generator_working = period[2]
            generator_was_working = True
            
            if generator_working == True:
                print("-"*31, f"Генератор увімкнувся о {helper.seconds_to_hms(period[0])}", "-"*31, sep="\n")
                generator_was_working = True

            while True:
                if self.time >= self.closing_time: return
                current_rate = get_current_rate_for_simulation(self.time, rates)

                # Check if the rate is zero to avoid division by zero
                if current_rate == 0: 
                    self.time += 10
                    continue

                if self.time >= self.closing_time: return
                
                # Customer arrives
                arriving_interval = self.generate_poiss_event(current_rate)
                self.time += arriving_interval
                if self.time >= period_end: 
                    print() 
                    break
                
                # Picking a drink according to probabilities and calculating profit
                drink = self.pick_random_drink(drink_names=self.drinks, probabilities=self.drinks_probabilities)
                profit = self.get_drink_profit(drink=drink, drink_names=self.drinks, drinks_profits=self.drinks_profits)
                if generator_working:
                    profit -= (self.gen_price / 3600) * arriving_interval

                #Adding drink info to metrics
                self.metrics.record_drink(drink=drink, time=self.time, profit=profit)
                print(f"{helper.seconds_to_hms(self.time)}, {drink}, Прибуток = {profit:.2f}. Частота: {current_rate * 3600} клієнтів за годину")
            
            if period[2] == True and generator_was_working:
                print("-"*30, f"Генератор вимкнувся о {helper.seconds_to_hms(period[1])}", "-"*30, sep="\n")   
                generator_was_working = False
        
        # Print real profit, compare real and estimated profits
        self.statisctic = stats.Statistics(self.mean_drink_profit, self.arrival_rates, self.gen_price, self.metrics, working_periods=self.form_simulation_periods(True), max_customers=self.max_customers)
        forecasted_profit = self.statisctic.get_total_forecasted_profit(True)
        real_profit = self.metrics.get_total_real_profit()
        print(f"Прогнозований прибуток = {forecasted_profit:.1f}")
        print(f"Фактичний прибуток = {real_profit:.1f}")
        print(f"Відносна похибка = {(abs(forecasted_profit - real_profit) / forecasted_profit * 100):.2f}%")
    

    def graph_after_simulation(self, with_generator: bool):
        if with_generator:
            working_periods = self.form_simulation_periods(with_generator=True)
    
        # Plotting
        fig, ax = plt.subplots()
        fig.set_size_inches(14, 7)

        # times is list of working hours
        times = list(int(i) for i in self.arrival_rates.keys())
        times.append(max(times) + 1)

        # times is list of rates (list[list[int]])
        rates = list(self.statisctic.arrival_rates.values())
        # find min and max rate
        min_rate = min(min(rate) for rate in rates)
        max_rate = max(max(rate) for rate in rates)

        # add 6 vertical lines for each hour (every 10 mins)
        v_lines = [x + j/6 for x in times[:-1] for j in range(len(rates[0]) + 1)]
        ax.vlines(x=v_lines, ymin=0, ymax=10, color='grey', linestyle='--', alpha=0.1, linewidth=0.5)


        # Plot horizontal lines for each rate at the corresponding hour
        first = True
        for i in range(len(times) - 1):
            for j in range(6):
                if first:
                    ax.hlines(y=rates[i][j], xmin=times[i] + j/6, xmax=times[i] + (j+1)/6, color='blue', linewidth=2, label="Щільності клієнтів (за 10 хв)")
                    first = False
                else:
                    ax.hlines(y=rates[i][j], xmin=times[i] + j/6, xmax=times[i] + (j+1)/6, color='blue', linewidth=2)
        

        # Define the yellow rectangular regions for electricity off periods ((xmin, ymin), width, height)
        # and add horizontal lines representing minimal profitable arrival rate (only for electricity off periods)
        electricity_off_periods = split_electricity_schedule_for_graph(self.electricity_off_schedule)
        first = True
        for start, end in electricity_off_periods:
            ax.add_patch(patches.Rectangle(xy=(start, 0), width=end - start, height=max_rate, facecolor='yellow', linestyle='solid', alpha=0.5, edgecolor='yellow'))
            if first:
                ax.hlines(y=self.statisctic.calc_min_arrival_profitable_rate(), xmin=start, xmax=end, color='red', linestyle='-', alpha=0.8, linewidth=1, label="Мінімальна прибуткова частота клієнтів")
                first = False
            else:
                ax.hlines(y=self.statisctic.calc_min_arrival_profitable_rate(), xmin=start, xmax=end, color='red', linestyle='-', alpha=0.8, linewidth=1)
        
        # Define the green rectangular regions for generator working periods ((xmin, ymin), width, height)
        generator_optimal_periods = list(filter(lambda x: x[2] == True, working_periods))
        for period in generator_optimal_periods:
            period[0], period[1] = s_to_hours(period[0]), s_to_hours(period[1])
    
        for start, end, bool in generator_optimal_periods:
            ax.add_patch(patches.Rectangle(xy=(start, 0), width=end - start, height=max_rate, facecolor='green', linestyle='solid', alpha=0.3, edgecolor='green'))

        # add horizontal lines representing maximum rate that coffee machine can handle (for all periods)
        ax.hlines(y=self.max_customers, xmin=times[0], xmax=times[-1], color='grey', linestyle='--', alpha=0.5, linewidth=0.7, label="Максимальна пропускна здатність апарату")

        # add horisontal lines for each rate (from min rate to max rate)
        ax.hlines(y=range(min_rate, max_rate + 1), xmin=times[0], xmax=times[-1], color='grey', linestyle='--', alpha=0.1, linewidth=0.5)
        

        # add vertical line for each hour (more grey than v_lines (alpha is bigger))
        ax.vlines(x=times, ymin=min_rate, ymax=max_rate, color='grey', linestyle='--', alpha=0.2, linewidth=0.5)
        
        ax.set_yticks(range(min_rate, max_rate + 1))
        ax.set_yticklabels(range(min_rate, max_rate + 1))
        
        ax.set_xticks(times)
        ax.set_xticklabels
        
        ax.set_xlabel('Час (години)')
        ax.set_ylabel('Середня щільність (частота) клієнтів')
        ax.set_title('Жовті проміжки – відключення е/е. Зелені проміжки – оптимальні проміжки роботи генератора')
        plt.legend(loc='best')

        plt.show()