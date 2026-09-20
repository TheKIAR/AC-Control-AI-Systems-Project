class DataPipeline:
    def __init__(self, data=None):
        self.data = data or []

    def clean_data(self, data=None):
        values = self.data if data is None else data
        cleaned = [item for item in values if item is not None]
        self.data = cleaned
        return self.data

    def transform_data(self, data=None):
        values = self.data if data is None else data
        transformed = [self._square_item(item) for item in values]
        self.data = transformed
        return self.data

    @staticmethod
    def _square_item(item):
        # bool is a subclass of int: leave flags untouched.
        if isinstance(item, bool):
            return item
        if isinstance(item, (int, float)):
            return item ** 2
        if isinstance(item, list):
            return [DataPipeline._square_item(x) for x in item]
        if isinstance(item, tuple):
            return tuple(DataPipeline._square_item(x) for x in item)
        return item

    def process(self, data=None):
        if data is not None:
            self.data = data
        self.clean_data()
        self.transform_data()
        return self.data

    def run_pipeline(self):
        return self.process()