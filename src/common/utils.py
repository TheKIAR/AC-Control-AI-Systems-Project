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
    # Return the first most-frequent value so the return type stays stable
    # (previously this returned a scalar or a list depending on ties).
    for number in numbers:
        if frequency[number] == max_freq:
            return number

def normalize_data(data):
    if not data:
        return []
    min_val = min(data)
    max_val = max(data)
    if max_val == min_val:
        return [0.0 for _ in data]
    return [(x - min_val) / (max_val - min_val) for x in data]

def split_data(data, ratio):
    if not 0 < ratio < 1:
        raise ValueError("ratio must be between 0 and 1")
    split_index = int(len(data) * ratio)
    return data[:split_index], data[split_index:]