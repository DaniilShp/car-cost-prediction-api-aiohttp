from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from regression.regression_prediction import RegressionPrediction


def polynomial_regression_create(x, y, barplot, scatterplot, degree=3):
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    x_poly = poly.fit_transform(x)
    x_train, x_test, y_train, y_test = RegressionPrediction.train_test_split(x_poly, y, test_size=0.2, random_state=0)
    model = LinearRegression()
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    response = RegressionPrediction.print_error_metrics(y_test, y_pred, barplot, scatterplot,
                                                        title="Полиномиальная регрессия")
    return model, response


def predict(model, x, degree=3):
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    x_poly = poly.fit_transform(x)
    y_pred = model.predict(x_poly)
    return y_pred
