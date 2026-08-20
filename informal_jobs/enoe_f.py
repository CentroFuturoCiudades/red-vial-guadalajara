import pandas as pd


def load_enoe(enoe_path='enoe_juntado1t23.csv'):

    enoe = (
        pd.read_csv(enoe_path, low_memory=False)
        .pipe(
            lambda df: df.assign(
                tamano_viv=df.groupby(
                    ['tipo','mes_cal','cd_a', 'ent', 'con', 'v_sel']
                ).transform('size')
            )
        )
        .query("`p1.coe1` == 1")
        .set_index(['tipo','mes_cal','cd_a', 'ent', 'con', 'v_sel'])
        .xs(14, level='ent')[
            [
                'sex', 'pos_ocu', 'scian', 'eda',
                'cs_p13_1', 'emp_ppal', 'mun',
                'e_con', 'par_c', 'tamano_viv',
            ]
        ]
    )

    enoe = enoe.assign(
        genero=enoe.sex.map(
            {
                1: 'H',
                2: 'F'
            }
        ),
        ocupacion=enoe.pos_ocu.map(
            {
                1: 'trabajador',
                2: 'trabajador',
                3: 'independiente',
                4: 'otro'
            }
        ),
        edad_num=enoe.eda.astype(int),
        edad_cat=pd.cut(
            enoe.eda,
            (0, 3, 5, 6, 8, 12, 15, 18, 25, 50, 60, 65, 131),
            right=False
        ).astype(str),
        
        # Sector-> Restricted to the 4 categories within the Guadalajara OD survey:
        # "Giro de la empresa donde trabaja": Servicio, Comercio, Industria, Gobierno/sector público, Educacion (here as 'Servicios'). Everything else falls back to "Otro" to match OD's blanks.
        sector=enoe.scian.map(
            {
                1: "Otro",
                2: "Otro",
                3: "Otro",
                4: "Otro",
                5: "Industria_manufacturera",
                6: "Comercio",
                7: "Comercio",
                8: "Otro",
                9: "Otro",
                10: "Servicios",
                11: "Servicios",
                12: "Servicios",
                13: "Servicios",
                14: "Servicios",
                15: "Servicios",
                16: "Servicios",
                17: "Servicios",
                18: "Servicios",
                19: "Servicios",
                20: "Gobierno",
                21: "Otro",
            }
        ),
        escolaridad=enoe.cs_p13_1.map(
            {
                0: "Sin_Instruccion",
                1: "Sin_Instruccion",
                2: "Primaria_o_Secundaria",
                3: "Primaria_o_Secundaria",
                4: "Carrera_tecnica_o_preparatoria",
                5: "Carrera_tecnica_o_preparatoria",
                6: "Carrera_tecnica_o_preparatoria",
                7: "Licenciatura",
                8: "Postgrado",
                9: "Postgrado",
                # 99: "Otro",
            }
        ),
        informal=enoe.emp_ppal.map(
            {
                1: 1,
                2: 0,
            }
        ),
        municipio=enoe.mun.map(
            {
                39: "guadalajara",
                120: "zapopan",
                98: "tlaquepaque",
                97: "tlajomulco",
                101: "tonala",
                70: "el_salto",
                51: "juanacatlan",
                44: "ixtlahuacan_membrillos",
                124: "zapotlanejo",
                83: "tala",
            }
        ).fillna('otro'),
        estado_civil=enoe.e_con.map(
            {
                1: "union_libre",
                2: "separado",
                3: "divorciado",
                4: "viudo",
                5: "casado",
                6: "soltero",
            }
        ),
        parentesco=(enoe.par_c // 100).map(
            {
                1: "jefe_del_hogar",
                2: "conyuge",
                3: "hijo",
                4: "otro_parentesco",
                5: "sin_parentesco",
                6: "sin_parentesco",
                # 9: "no especificado" (999 / blank) -> left unmapped, dropped by .dropna()
            }
        ),
        tamano_viv_cat=pd.cut(
            enoe.tamano_viv,
            bins=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, float('inf')],
            right=False,
            labels=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10_y_mas']
        ).astype(str),
    ).drop(
        columns=[
            'sex', 'pos_ocu', 'scian', 'cs_p13_1',
            'emp_ppal', 'mun', 'eda', 'e_con', 'par_c']
    ).dropna().reset_index(drop=True)

    return enoe


if __name__ == "__main__":
    enoe = load_enoe("./data/input/enoe_juntado1t23.csv")
    enoe.to_csv("./data/output/enoe_clean_f.csv")
