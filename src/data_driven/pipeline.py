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
        transformed = [item ** 2 if isinstance(item, (int, float)) else item for item in values]
        self.data = transformed
        return self.data

    def process(self, data=None):
        if data is not None:
            self.data = data
        self.clean_data()
        self.transform_data()
        return self.data

    def run_pipeline(self):
        return self.process()