from pathlib import Path
import json


class DataGenerator:
    def __init__(self, method="supervised"):
        self.method = method

    def generate_data(self, *args, **kwargs):
        if self.method == "supervised":
            return self.generate_supervised_data(*args, **kwargs)
        if self.method == "unsupervised":
            return self.generate_unsupervised_data(*args, **kwargs)
        raise ValueError("Unsupported method. Choose 'supervised' or 'unsupervised'.")

    def generate_supervised_data(self, num_samples=10):
        return [(i, i + 1, 1 if i % 2 == 0 else 0) for i in range(num_samples)]

    def generate_unsupervised_data(self, num_samples=10):
        return [[i, i * i] for i in range(num_samples)]

    def clean_data(self, raw_data):
        return [item for item in raw_data if item is not None]

    def transform_data(self, raw_data):
        return [item ** 2 if isinstance(item, (int, float)) else item for item in raw_data]

    def save_data(self, data, filename):
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path

    def load_data(self, filename):
        path = Path(filename)
        return json.loads(path.read_text(encoding="utf-8"))
