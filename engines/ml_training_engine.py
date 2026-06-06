class MLTrainingEngine:

    def __init__(self, dataset_path):
        self.dataset_path = dataset_path

    def build_training_summary(self):

        summary = {
            "dataset_path": self.dataset_path,
            "engine_ready": True,
            "training_started": False,
            "model_type": "NOT_SELECTED"
        }

        return summary