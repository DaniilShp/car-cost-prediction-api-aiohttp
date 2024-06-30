from pathlib import Path

from sklearn.linear_model import LinearRegression
import pandas as pd
from regression.regression_prediction import RegressionPrediction


def linear_regression_create(x: pd.DataFrame, y: (list[int, float], pd.DataFrame),
                             barplot_path: Path = None, scatterplot_path: Path = None):
    # x = pd.get_dummies(x, columns=['brand_model', 'gearbox_type'])  # one hot encoding
    # x = RegressionPrediction.normalize_data(x.select_dtypes(include=['number']))
    x_train, x_test, y_train, y_test = RegressionPrediction.train_test_split(x, y, test_size=0.2, random_state=0)
    model = LinearRegression()
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    response = RegressionPrediction.print_error_metrics(y_test, predictions, barplot_path, scatterplot_path,
                                                        title="Линейная регрессия")
    return model, response


def predict(x: dict, model):
    pass
