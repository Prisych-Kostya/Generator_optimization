from helper import *
import helper

class Optimisation():
    def __init__(self, gen_price:float, gen_minimal_time:int, mean_drink_profit:float, arrival_rates:dict[str, list[float]], max_customers):
        self.gen_per_min_price = gen_price / 60 # Convert to uah/min generator working price 
        self.gen_minimal_time = gen_minimal_time
        self.arrival_rates = normalize_arrival_rates(arrival_rates, max_customers=max_customers)
        self.mean_drink_profit = mean_drink_profit
        self.generator_optimal_times = []


    def divide_into_intervals(self, electricity_off_period: list[int]) -> list[list[int]]:
        electricity_off = electricity_off_period[0]
        electricity_on  = electricity_off_period[1]
        
        num_of_full_intervals = (electricity_on - electricity_off) // (2 * self.gen_minimal_time - 1)
        if num_of_full_intervals == 0:
            return [electricity_off_period]
        
        intervals = []
        l_bound = electricity_off
        for _ in range(num_of_full_intervals):
            r_bound = l_bound + 2 * self.gen_minimal_time - 1
            intervals.append([l_bound, r_bound])
            l_bound = r_bound
        
        # adding right sub interval
        intervals.append([intervals[-1][1], electricity_on])
        return intervals
    

    def optimise_middle_interval(self, interval: list[int]) -> list[int]: 
        periods = []
        expences = self.gen_minimal_time * self.gen_per_min_price

        for m in range(interval[1] - interval[0] - self.gen_minimal_time + 1):
            current_estimated_profit = 0
            for minute in range(interval[0] + m, interval[0] + self.gen_minimal_time + m + 1):
                current_estimated_profit += self.mean_drink_profit * get_current_rate_for_optimisation(minute=minute, arrival_rates=self.arrival_rates)
            # append to temporary list info about cutternt period: [time_start, time_stop, total_profit]
            periods.append([interval[0] + m, interval[0] + self.gen_minimal_time + m, current_estimated_profit - expences])
        
        # Now we find max profitable period
        best_period = max(periods, key=lambda x: x[2])
        l_bound = best_period[0]
        r_bound = best_period[1]
        max_profit = best_period[2]
        
        # Notice! If we've searched through all electricity off time with generator working its minimal time 
        # and max_profit <= 0, it means that we can't improve profit by searching through left or right remaining interval, 
        # because if so, this interval would be in best period, and it's not. So seaching left or right makes no sense.
        if max_profit <= 0:
            return None
        return [l_bound, r_bound]

    
    def optimise_left_subinterval(self, left_subinterval: list[int]) -> list[int]:
        left_periods = []
        l_bound = left_subinterval[0]
        r_bound = left_subinterval[1]

        for m in range(r_bound - l_bound + 1):
            current_estimated_profit = 0
            for minute in range(l_bound + m, r_bound):
                rate = get_current_rate_for_optimisation(minute=minute, arrival_rates=self.arrival_rates)
                current_estimated_profit += self.mean_drink_profit * rate
            expences = (r_bound - l_bound - m) * self.gen_per_min_price
            left_periods.append([l_bound + m, r_bound, current_estimated_profit - expences])
        
        if len(left_periods) != 0:
            best_left_period = max(left_periods, key=lambda x: x[2])
            l_bound_left = best_left_period[0]
            max_left_profit = best_left_period[2]
            # If we found best left interval with profit - expences > 0, we move left bound
            if max_left_profit <= 0:
                return None
            l_bound = l_bound_left
        return [l_bound, r_bound]
    

    def optimise_right_subinterval(self, right_subinterval: list[int]) -> list[int]:
        right_periods = []
        l_bound = right_subinterval[0]
        r_bound = right_subinterval[1]
        
        for m in range(r_bound - l_bound + 1):
            current_estimated_profit = 0
            for minute in range(l_bound, r_bound - m + 1):
                rate = get_current_rate_for_optimisation(minute=minute, arrival_rates=self.arrival_rates)
                current_estimated_profit += self.mean_drink_profit * rate
            expences = (r_bound - l_bound - m) * self.gen_per_min_price
            right_periods.append([l_bound, r_bound - m, current_estimated_profit - expences])
        
        if len(right_periods) != 0:
            best_right_period = max(right_periods, key=lambda x: x[2])
            r_bound_right = best_right_period[1]
            max_right_profit = best_right_period[2]
            # If we found best left interval with profit - expences > 0, we move left bound
            if max_right_profit <= 0:
                return None
            r_bound = r_bound_right
        return [l_bound, r_bound]
    

    def get_optimal_generator_schedule(self, electricity_off_schedule: list[str]) -> list[list[int]]:
        electricity_off_periods = (helper.split_electricity_schedule(electricity_off_schedule))
        divided_periods = [] 
        
        for period in electricity_off_periods:
            divided_periods.append(self.divide_into_intervals(period))
        
        divided_periods = [item for sublist in divided_periods for item in sublist]

        optimal_periods = []

        for period in divided_periods[:-1]:
            # Optimising full period for all periods except last one
            optimal_period = self.optimise_full_period(period)
            if optimal_period != None:
                optimal_periods.append(optimal_period)

            # Optimising last period as right sub period and appending it if not None
        optimal_right_period = self.optimise_right_subinterval(divided_periods[-1])
        if optimal_right_period != None:
            optimal_periods.append(optimal_right_period)
        
        flattened_optimal_periods = [item for sublist in optimal_periods for item in sublist]
        unique_periods = [period for period in flattened_optimal_periods if flattened_optimal_periods.count(period) == 1]
        if len(unique_periods) == 0:
            return None 

        final_optimal_periods = [[unique_periods[i], unique_periods[i + 1]] for i in range(0, len(unique_periods), 2)]
        return final_optimal_periods


    def optimise_full_period(self, electricity_off_period: list[int, int]) -> list[int, int]:
        electricity_off = electricity_off_period[0]
        electricity_on  = electricity_off_period[1]

        # Generator can only work while not electricity, 
        # so if generator minimal working time < overrall electricity off time, we cannot run generator and return None  
        if self.gen_minimal_time > electricity_on - electricity_off:
            return None
        
        # If generator minimal working time exactly equals overrall electricity off time, we check if it is profitable
        if self.gen_minimal_time == electricity_on - electricity_off:
            expences = self.gen_minimal_time * self.gen_per_min_price
            # estimated_profit = sum(mean_drink_profit * customer rates(each sec))
            estimated_profit = 0
            for mimute in range(electricity_off, electricity_on + 1):
                estimated_profit += self.mean_drink_profit * get_current_rate_for_optimisation(minute=mimute, arrival_rates=self.arrival_rates)

            # if not profitable, return None 
            if estimated_profit - expences <= 0:
                return None 
            # if profitable, return generator optimal time
            return electricity_off_period
            
        if self.gen_minimal_time < electricity_on - electricity_off:
            # Step 1. Finding best generator working interval with its working time = minimal time 
        
            # Now we find max profitable period
            best_period = self.optimise_middle_interval(electricity_off_period)
            
            if best_period == None:
                return None
            l_bound = best_period[0]
            r_bound = best_period[1]
            
            # Step 2. Looking through left remaining interval in order to improve profit:
            optimal_left_period = self.optimise_left_subinterval(left_subinterval=[electricity_off, l_bound])

            # Step 3. Looking through right remaining interval in order to improve profit:
            optimal_right_period = self.optimise_right_subinterval(right_subinterval=[r_bound, electricity_on])

            if optimal_left_period != None:
                l_bound = optimal_left_period[0]
            if optimal_right_period != None:
                r_bound = optimal_right_period[1]

            return [l_bound, r_bound]
            


                




                

            
        