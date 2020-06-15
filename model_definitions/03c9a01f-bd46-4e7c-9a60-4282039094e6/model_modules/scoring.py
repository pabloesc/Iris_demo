from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

import pickle
import json
import pandas as pd


def evaluate(data_conf, model_conf, **kwargs):

    dataset = pd.read_csv(data_conf['url'], header=None)

    # split into test and train
    _, test = train_test_split(dataset, test_size=data_conf["test_split"], random_state=42)

    # split data into X and y
    test = test.values
    X_test = test[:, 0:8]
    y_test = test[:, 8]

    scaler = pickle.load(open("models/scaler.pkl", 'rb'))
    model = pickle.load(open("models/model.pkl", 'rb'))

    y_pred = model.predict(scaler.transform(X_test))

    predictions = [round(value) for value in y_pred]
    accuracy = accuracy_score(y_test, predictions)

    with open("models/evaluation.json", "w+") as f:
        json.dump({'accuracy': (accuracy * 100.0)}, f)


# Add code required for RESTful API
class ModelScorer(object):
    def __init__(self, config=None):
        self.scaler = pickle.load(open("models/scaler.pkl", 'rb'))
        self.model = pickle.load(open("models/model.pkl", 'rb'))

        from prometheus_client import Counter
        self.pred_class_counter = Counter('model_prediction_classes',
                                          'Model Prediction Classes', ['model', 'version', 'clazz'])

    def record_prediction_stats(self, pred):
        import os
        self.pred_class_counter.labels(model=os.environ["MODEL_NAME"],
                                       version=os.environ.get("MODEL_VERSION", "1.0"),
                                       clazz=str(int(pred))).inc()

    def predict(self, data):
        data = self.scaler.transform([data])
        pred = self.model.predict(data)

        self.record_prediction_stats(pred)

        return pred
