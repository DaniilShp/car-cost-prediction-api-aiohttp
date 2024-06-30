import os.path

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_validate
import pandas as pd
from regression.regression_prediction import RegressionPrediction
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint


def optimized_random_forest_regression_create(x, y, search_n_estimators=(50, 150), search_iters=5):
    """Function is like random_forest_regression_create, but uses RandomizedSearchCV to find better model params."""
    param_distributions = {'n_estimators': randint(*search_n_estimators)}
    model = RandomizedSearchCV(estimator=RandomForestRegressor(random_state=0), n_iter=search_iters,
                               param_distributions=param_distributions, random_state=0,
                               scoring='neg_mean_squared_error')
    x = pd.get_dummies(x)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)
    model.fit(x_train, y_train)
    print(model.best_params_)
    y_pred = model.predict(x_test)
    RegressionPrediction.print_error_metrics(y_test, y_pred, barplot=True, scatterplot=True,
                                             title="RandomForest with random search")


def random_forest_regression_create(x, y, forest_n=10):
    x = pd.get_dummies(x)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)
    model = RandomForestRegressor(n_estimators=forest_n, random_state=0)
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    metrics = "max_error", "r2", "neg_mean_absolute_percentage_error", "neg_mean_absolute_error"
    cross_validation_result = cross_validate(model, x, y, scoring=metrics, cv=3)
    RegressionPrediction.print_error_metrics(y_test, y_pred, barplot=True, scatterplot=True, title="RandomForest")
    return cross_validation_result


if __name__ == '__main__':
    dataframe = pd.read_csv(os.path.join("..", "data", "dataframe_audi_cars.csv"))
    x, y = (dataframe[["volume", "power", "mileage", "production_year", "gearbox_type", "brand_model"]],
            dataframe["price"])
    cross_validation_result = random_forest_regression_create(x, y)
    optimized_random_forest_regression_create(x, y)
