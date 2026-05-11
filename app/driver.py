from sklearn.linear_model import LinearRegression
import pandas as pd

def regression_driver_analysis(df):

    # sadece numeric al
    numeric_df = df.select_dtypes(include=['number'])

    # 🚨 kritik: yeterli veri yoksa çık
    if numeric_df.shape[1] < 2:
        return None

    # NaN temizle
    numeric_df = numeric_df.dropna()

    # hala veri azsa
    if len(numeric_df) < 5:
        return None

    target = numeric_df.columns[-1]

    X = numeric_df.drop(columns=[target])
    y = numeric_df[target]

    # 🚨 sabit kolon varsa çıkar (model patlar)
    X = X.loc[:, X.nunique() > 1]

    if X.shape[1] == 0:
        return None

    try:
        model = LinearRegression()
        model.fit(X, y)

        importance = dict(zip(X.columns, model.coef_))
        main_driver = max(importance, key=lambda k: abs(importance[k]))

        return {
            "target": target,
            "driver": main_driver,
            "coefficients": importance
        }

    except:
        return None