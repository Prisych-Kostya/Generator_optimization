import simpy

def get_hour(env):
    if type(env) == simpy.Environment():
        hour = env.now // 3600
    else:
        hour = env // 3600
    
    if hour < 10:
        hour = '0' + str(hour)
    else:
        hour = str(hour)
    return hour

def get_minute(env):
    if type(env) == simpy.Environment():
        minute = (env.now % 3600) // 60
    else:
        minute = (env % 3600) // 60

    if minute < 10:
        minute = '0' + str(minute)
    else:
        minute = str(minute)
    return minute

def get_second(env):
    if type(env) == simpy.Environment():
        second = env.now % 60 
    else: 
        second = env % 60
    if second < 10:
        second = '0' + str(second)
    else:
        second = str(second)
    return second


def seconds_to_hms(seconds: int):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    return f"{hours:02}:{minutes:02}:{remaining_seconds:02}"  

def s_to_hours(seconds: int):
    return seconds / 3600
    

def hms_to_seconds(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds

def hms_to_minutes(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    total_minutes = hours * 60 + minutes
    return total_minutes

def hm_to_hours(time_str):
    hours, minutes = map(int, time_str.split(':'))
    total_hour = hours + minutes / 60
    return total_hour

def hm_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(':'))
    total_minutes = hours * 60 + minutes
    return total_minutes

def hm_to_seconds(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    total_seconds = hours * 3600 + minutes * 60
    return total_seconds

def m_to_hm(m: int):
    hours = m // 60
    minutes = m - hours * 60
    return f"{hours:02}:{minutes:02}"


def get_mean_drinks_profit(drinks_probabilities: list[float], drinks_profits: list[float]):
    mean_profit = sum(drinks_probabilities[i] * drinks_profits[i] for i in range(len(drinks_probabilities)))
    return mean_profit


def get_hour1(env):
    hour = int(env.now)
    if hour < 10:
        hour = '0' + str(hour)
    else:
        hour = str(hour)
    return hour


def get_minute1(env):
    minute = int((env.now - int(env.now)) * 60)
    if minute < 10:
        minute = '0' + str(minute)
    else:
        minute = str(minute)
    return minute


def get_second1(env):
    second = int(((env.now - int(env.now)) * 60 - int((env.now - int(env.now)) * 60)) * 60)
    if second < 10:
        second = '0' + str(second)
    else:
        second = str(second)
    return second


def get_current_rate_for_optimisation(minute: int, arrival_rates: dict[str, list[float]]) -> float:
    """Returns current rate PER MINUTE"""
    # Determine the current hour and minute
    hour = minute // 60
    minutes = minute - hour * 60 
    current_rate = arrival_rates.get(str(hour))[minutes // 10]
    # Convert current_rate to per minute by dividing on length of list[int]
    min_key = str(min(int(key) for key in arrival_rates.keys()))
    num_of_intervals = len(arrival_rates[min_key])
    current_rate = current_rate / num_of_intervals
    return current_rate

def get_current_rate_for_simulation(second: int, arrival_rates: dict[str, list[float]]) -> float:
    """Returns current rate PER SECOND"""
    # Determine the current hour and minute
    hours = second // 3600
    minutes = (second % 3600) // 60
    remaining_seconds = second % 60 
    current_rate = arrival_rates.get(str(hours))[minutes // 10]
    # Convert current_rate to per minute by dividing on length of list[int]
    min_key = str(min(int(key) for key in arrival_rates.keys()))
    num_of_intervals = len(arrival_rates[min_key])
    current_rate = current_rate / (num_of_intervals * 60)
    return current_rate


def normalize_arrival_rates(arrival_rates:dict[str, list[float]], max_customers: int) -> dict[str, list[float]]:
    flat_rates = []
    times = []
    num_of_intervals = 0
    # Flatten rates to single list
    for time, rates in arrival_rates.items():
        num_of_intervals = len(rates)
        times.append(time)
        for rate in rates:
            flat_rates.append(rate)
    
    normalized_arrival_rates = {}
    normalized_rates_list = []
    remaining_customers = 0
    for rate in flat_rates[:-1]:
        if rate > max_customers:
            remaining_customers += rate - max_customers
            rate -= rate - max_customers
            normalized_rates_list.append(rate)
        elif rate < max_customers and remaining_customers > 0:
            rate += remaining_customers
            remaining_customers = 0
            if rate > max_customers:
                remaining_customers += rate - max_customers
                rate -= rate - max_customers
                normalized_rates_list.append(rate)
            else:
                normalized_rates_list.append(rate)
        elif rate == max_customers and remaining_customers >= 0:
            normalized_rates_list.append(rate)
        elif rate <= max_customers and remaining_customers == 0:
            normalized_rates_list.append(rate)
        
    last_rate = flat_rates[-1] + remaining_customers
    if last_rate > max_customers:
        normalized_rates_list.append(max_customers)
    else:
        normalized_rates_list.append(last_rate)

    j = 0
    for time in times:
        normalized_arrival_rates[time] = [normalized_rates_list[i] for i in range(j, j + num_of_intervals)]
        j += num_of_intervals

    return normalized_arrival_rates


def split_electricity_schedule(electricity_off_schedule: list[str]) -> list[list[int]]:
    electricity_off_periods = []
    for electricity_off_period in electricity_off_schedule:
        electricity_off = hm_to_minutes(electricity_off_period.split("-")[0])
        electricity_on  = hm_to_minutes(electricity_off_period.split("-")[1])
        electricity_off_periods.append([electricity_off, electricity_on])
    return electricity_off_periods


def split_electricity_schedule_for_graph(electricity_off_schedule: list[str]) -> list[list[float]]:
    electricity_off_periods = []
    for electricity_off_period in electricity_off_schedule:
        electricity_off = hm_to_hours(electricity_off_period.split("-")[0])
        electricity_on  = hm_to_hours(electricity_off_period.split("-")[1])
        electricity_off_periods.append([electricity_off, electricity_on])
    return electricity_off_periods