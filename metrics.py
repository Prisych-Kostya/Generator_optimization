from helper import *

class Metrics():
    def __init__(self, drinks: list[str], drinks_profits: list[float], generator_time=None):
        self.drinks = drinks
        self.drinks_profits = drinks_profits
        self.generator_time = generator_time
        self.bought_drinks_info = []
    
    def record_drink(self, drink, time, profit):
        self.bought_drinks_info.append([time, drink, profit])

    def add_electricity_off_schedule(self, electricity_off_periods: list[list[int]]):
        self.electricity_off_schedule_periods = electricity_off_periods 

    def add_generator_optimal_time_periods(self, generator_optimal_periods):
        self.generator_optimal_time_periods = generator_optimal_periods

    def get_total_real_profit(self) -> float:
        total_profit = 0
        for drink in self.bought_drinks_info:
            total_profit += drink[2]
        return total_profit
