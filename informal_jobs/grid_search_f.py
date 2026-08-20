from models_grids_f import models_LR, models_RF, models_GB, models_SVC, models_KNN
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import GridSearchCV
from sklearn.experimental import enable_halving_search_cv  # noqa: F401
from sklearn.model_selection import HalvingGridSearchCV
from sklearn.metrics import accuracy_score, balanced_accuracy_score
import pandas as pd
from enoe_f import load_enoe
from pathlib import Path


def perform_grid_search(
        X, y,
        cv_results_fpath=None, best_models_fpath=None,
        n_jobs=1
):

    models = models_LR | models_RF | models_GB | models_SVC | models_KNN
    # models = models_RF | models_GB

    cv_inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_outer = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

    outer_folds = {}
    for fold, (train_index, test_index) in enumerate(cv_outer.split(X, y)):
        print(f"Running outer fold {fold}")
        X_train, y_train = X.iloc[train_index], y.iloc[train_index]
        X_test, y_test = X.iloc[test_index], y.iloc[test_index]

        grids = {}
        for key in models.keys():
            print(f"Running GridSearchCV for {key}")

            model = models[key]['model']
            param_grid = models[key]['params']

            if key.startswith('SVC'):
                gs = HalvingGridSearchCV(
                    model, param_grid,
                    cv=cv_inner,
                    n_jobs=n_jobs,
                    scoring='balanced_accuracy',
                    verbose=1,
                    random_state=42,
                )
            else:
                gs = GridSearchCV(
                    model, param_grid,
                    cv=cv_inner,
                    n_jobs=n_jobs,
                    scoring='balanced_accuracy',
                    verbose=1
                )
            gs.fit(X_train, y_train)

            grids[key] = gs
        outer_folds[fold] = grids

    df_list = []
    for fold, grids in outer_folds.items():
        for model, grid in grids.items():
            df_list.append(
                pd.DataFrame(grid.cv_results_).assign(model=model, fold=fold)
            )
    cv_results = pd.concat(df_list).reset_index(drop=True)
    cv_results['model_type'] = cv_results.model.str.split('_', expand=True)[0]

    if cv_results_fpath is not None:
        assert not cv_results_fpath.exists(), 'Attempted overwrite cv results'
        cv_results.to_pickle(cv_results_fpath)

    # Score best model by type for each fold
    idx = cv_results.groupby(['model_type', 'fold']).mean_test_score.idxmax()
    best_models = cv_results.loc[
        idx,
        [
            'fold', 'model_type', 'model', 'params',
            'mean_test_score', 'std_test_score'
        ]
    ].set_index(['fold', 'model_type']).sort_index()

    best_models = best_models.assign(accuracy=0.0, balanced_accuracy=0.0)

    for fold, (train_index, test_index) in enumerate(cv_outer.split(X, y)):
        X_train, y_train = X.iloc[train_index], y.iloc[train_index]
        X_test, y_test = X.iloc[test_index], y.iloc[test_index]

        for model in best_models.loc[fold].model:
            y_pred = outer_folds[fold][model].predict(X_test)
            best_models.loc[
                (fold, model.split('_')[0]),
                ['accuracy', 'balanced_accuracy']
            ] = (
                accuracy_score(y_test, y_pred),
                balanced_accuracy_score(y_test, y_pred)
            )

    best_models = (
        best_models
        .groupby('model_type')[['balanced_accuracy', 'accuracy']]
        .agg(['mean', 'std'])
    )
    if best_models_fpath is not None:
        assert not best_models_fpath.exists(), 'Attempted overwrite bestmodels'
        best_models.to_csv(best_models_fpath)

    return cv_results, best_models


if __name__ == '__main__':
    enoe = pd.read_csv('./data/output/enoe_clean_f.csv')

    y = enoe['informal']
    X = enoe.drop(columns='informal')

    cv_results_fpath = Path('./data/output/repeated_cv_results_f.pkl')
    best_models_fpath = Path('./data/output/repeated_best_models_f.csv')

    n_jobs = 8 # bumped to match core count

    perform_grid_search(X, y, cv_results_fpath, best_models_fpath, n_jobs)
