def calculate_mean(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def calculate_median(numbers):
    if not numbers:
        return 0
    sorted_numbers = sorted(numbers)
    mid = len(sorted_numbers) // 2
    if len(sorted_numbers) % 2 == 0:
        return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2
    return sorted_numbers[mid]

def calculate_mode(numbers):
    if not numbers:
        return 0
    frequency = {}
    for number in numbers:
        frequency[number] = frequency.get(number, 0) + 1
    max_freq = max(frequency.values())
    modes = [num for num, freq in frequency.items() if freq == max_freq]
    return modes if len(modes) > 1 else modes[0]

def normalize_data(data):
    if not data:
        return []
    min_val = min(data)
    max_val = max(data)
    return [(x - min_val) / (max_val - min_val) for x in data]

def split_data(data, ratio):
    split_index = int(len(data) * ratio)
    return data[:split_index], data[split_index:]