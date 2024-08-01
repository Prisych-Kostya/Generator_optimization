import helper
import matplotlib.pyplot as plt
from metrics import Metrics

class Statistics():
    def __init__(self, mean_drink_profit, arrival_rates, gen_price, metric: Metrics, working_periods: list[list[int, bool]], max_customers):
       self.mean_drink_profit = mean_drink_profit
       self.arrival_rates = arrival_rates
       self.normalized_arrival_rates = helper.normalize_arrival_rates(arrival_rates, max_customers)
       self.gen_price = gen_price / 60
       self.metric = metric
       self.working_periods = working_periods


    def get_forecasted_profits(self) -> list[list[float, bool]]:
        profits = []
        for i in range(len(self.working_periods)):
            for j in range(len(self.working_periods[i]) - 1):
                self.working_periods[i][j] = int(self.working_periods[i][j] / 60)
        
        for period in self.working_periods:
            profit = 0
            expences = 0
            
            # If it's period with generator, add expences on generator
            if period[2] == True:
                expences = self.gen_price * (period[1] - period[0])
            
            # Iterate through working period by minute to calc profit
            for minute in range(period[0], period[1] + 1):
                try:
                    profit += self.mean_drink_profit * helper.get_current_rate_for_optimisation(minute=minute, arrival_rates=self.arrival_rates)
                except Exception:
                    pass
            profits.append([profit - expences, period[2]])

        return profits
    

    def get_total_forecasted_profit(self, with_generator: bool) -> float:
        total_profit = 0
        profits_list = self.get_forecasted_profits()
        for profit in profits_list:
            total_profit += profit[0]
        return total_profit
    

    def calc_min_arrival_profitable_rate(self) -> float:
        """Calculetes minimal arravil rate (for 10 minutes) that will be profitable with given mean_drink_profit and gen_price"""
        rate = 0
        while self.mean_drink_profit * rate <= self.gen_price * 10:
            rate += 0.01
        return rate
    

    def compare_profits(self):
        estimated_profit = self.get_total_forecasted_profit(with_generator=True)
        real_profit = 0
        for drink in self.metric.bought_drinks_info:
            real_profit += drink[2]
        difference_percents = (estimated_profit - real_profit) / estimated_profit * 100
        return difference_percents
        


    




            
        
        


