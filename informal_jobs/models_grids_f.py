import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import (
    StandardScaler, OneHotEncoder, KBinsDiscretizer, OrdinalEncoder)
from sklearn.pipeline import Pipeline
from sklearn.ensemble import (
    RandomForestClassifier, HistGradientBoostingClassifier)
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier


kbins_ed = [5, 6, 7, 8, 9, 10]

cat_cols = [
    'genero',
    'ocupacion',
    'sector',
    'escolaridad',
    'municipio',
    'estado_civil',
    'parentesco',
    'tamano_viv_cat',
    'edad_cat'
]

cat_cols_no_edad = [
    'genero',
    'ocupacion',
    'sector',
    'escolaridad',
    'municipio',
    'estado_civil',
    'parentesco',
    'tamano_viv_cat',
]

num_cols = [
    'edad_num',
]


models_LR = {
    'LR_ed_scl': {
        'model': Pipeline([
                (
                    'preprocessor',
                    ColumnTransformer([
                        ("standard_scaler", StandardScaler(), num_cols),
                        (
                            "one-hot-encoder",
                            OneHotEncoder(handle_unknown="ignore"),
                            cat_cols_no_edad)
                    ])
                ),
                (
                    'classifier',
                    LogisticRegression(max_iter=1000)
                )
             ]),
        'params': {
            'classifier__C': np.geomspace(1e-4, 1e4, 10)
        }
    },

    'LR_ed_dsc': {
        'model': Pipeline([
                (
                    'preprocessor',
                    ColumnTransformer([
                        (
                            "discretizer",
                            KBinsDiscretizer(encode='onehot'),
                            ['edad_num']
                        ),
                        (
                            "one-hot-encoder",
                            OneHotEncoder(handle_unknown="ignore"),
                            cat_cols_no_edad
                        )
                    ])
                ),
                (
                    'classifier',
                    LogisticRegression(max_iter=1000)
                )
             ]),
        'params': {
            'classifier__C': np.geomspace(1e-4, 1e4, 10),
            'preprocessor__discretizer__n_bins': kbins_ed,
        }
    },

    'LR_ed_cnss': {
        'model': Pipeline([
                (
                    'preprocessor',
                    ColumnTransformer([
                        (
                            "one-hot-encoder",
                            OneHotEncoder(handle_unknown="ignore"),
                            cat_cols
                        )
                    ])
                ),
                (
                    'classifier',
                    LogisticRegression(max_iter=1000)
                )
             ]),
        'params': {
            'classifier__C': np.geomspace(1e-4, 1e4, 10),
        }
    },
}

max_leaf_nodes_grid = [5, 7, 10, 25, 50, 65, 85, 100, 250, 500]

models_RF = {
    'RF_ed_cnss': {
        'model': Pipeline([
            (
                'preprocessor',
                ColumnTransformer([
                    (
                        "od_encoder",
                        OrdinalEncoder(
                            handle_unknown='use_encoded_value',
                            unknown_value=-1
                        ),
                        cat_cols
                    )
                ])
            ),
            (
                'classifier',
                RandomForestClassifier()
            )
        ]),
        'params': {
            'classifier__max_features': list(range(1, len(cat_cols) + 1)),
            'classifier__max_leaf_nodes': max_leaf_nodes_grid,
        }
    },

    'RF_ed_num': {
        'model': Pipeline([
            (
                'preprocessor',
                ColumnTransformer([
                    (
                        "od_encoder",
                        OrdinalEncoder(
                            handle_unknown='use_encoded_value',
                            unknown_value=-1
                        ),
                        cat_cols_no_edad
                    ),
                    ('passthrough', 'passthrough', num_cols)
                ])
            ),
            (
                'classifier',
                RandomForestClassifier()
            )
        ]),
        'params': {
            'classifier__max_features': list(range(1, len(cat_cols_no_edad) + len(num_cols) + 1)),
            'classifier__max_leaf_nodes': max_leaf_nodes_grid,
        }
    },
}

models_GB = {
    'GB_ed_cnss': {
        'model': Pipeline([
            (
                'preprocessor',
                ColumnTransformer([
                    (
                        "od_encoder",
                        OrdinalEncoder(
                            handle_unknown='use_encoded_value',
                            unknown_value=-1
                        ),
                        cat_cols
                    )
                ])
            ),
            (
                'classifier',
                HistGradientBoostingClassifier(
                    max_iter=1000,
                    early_stopping=True,
                    random_state=0
                )
            )
        ]),
        'params': {
            'classifier__learning_rate': np.geomspace(0.01, 1, 10),
            'classifier__max_leaf_nodes': max_leaf_nodes_grid,
        }
    },

    'GB_ed_num': {
        'model': Pipeline([
            (
                'preprocessor',
                ColumnTransformer([
                    (
                        "od_encoder",
                        OrdinalEncoder(
                            handle_unknown='use_encoded_value',
                            unknown_value=-1
                        ),
                        cat_cols_no_edad
                    ),
                    ('passthrough', 'passthrough', num_cols)
                ])
            ),
            (
                'classifier',
                HistGradientBoostingClassifier(
                    max_iter=1000,
                    early_stopping=True,
                    random_state=0
                )
            )
        ]),
        'params': {
            'classifier__learning_rate': np.geomspace(0.01, 1, 10),
            'classifier__max_leaf_nodes': max_leaf_nodes_grid,
        }
    },
}

models_SVC = {
    'SVC_ed_scl': {
        'model': Pipeline([
                (
                    'preprocessor',
                    ColumnTransformer([
                        ("standard_scaler", StandardScaler(), num_cols),
                        (
                            "one-hot-encoder",
                            OneHotEncoder(handle_unknown="ignore"),
                            cat_cols_no_edad)
                    ])
                ),
                (
                    'classifier',
                    SVC()
                )
             ]),
        'params': {
            'classifier__C': np.geomspace(1e-4, 1e4, 10),
            'classifier__gamma': np.geomspace(1e-4, 1e4, 10)
        }
    },

    'SVC_ed_cnss': {
        'model': Pipeline([
                (
                    'preprocessor',
                    ColumnTransformer([
                        (
                            "one-hot-encoder",
                            OneHotEncoder(handle_unknown="ignore"),
                            cat_cols
                        )
                    ])
                ),
                (
                    'classifier',
                    SVC()
                )
             ]),
        'params': {
            'classifier__C': np.geomspace(1e-4, 1e4, 10),
            'classifier__gamma': np.geomspace(1e-4, 1e4, 10)
        }
    },
}

models_KNN = {
    'KNN_ed_cnss': {
        'model': Pipeline([
                (
                    'preprocessor',
                    ColumnTransformer([
                        (
                            "od_encoder",
                            OrdinalEncoder(
                                handle_unknown='use_encoded_value',
                                unknown_value=-1
                            ),
                            cat_cols
                        ),
                    ])
                ),
                (
                    'classifier',
                    KNeighborsClassifier(metric='hamming')
                )
             ]),
        'params': {
            'classifier__n_neighbors': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        }
    },
}
