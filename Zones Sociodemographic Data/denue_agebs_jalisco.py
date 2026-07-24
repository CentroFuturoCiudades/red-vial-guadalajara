"""
DENUE 2023 (INEGI) - estimated employment aggregated to AGEB level, Jalisco.

Loads the establishment-level estimates, keeps records with valid coordinates,
activity code and expected employment, assigns an employment category from the
SCIAN code, joins the points to AGEB polygons and totals employment per AGEB.

Output
------
A GeoPackage (see OUTPUT_GPKG) with layer "agebs_empleo": the input AGEB
polygons plus six columns. AGEBs with no establishments are filled with 0.

    num_empleos   estimated jobs inside the AGEB
    empleos_M     jobs in Manufactura, construccion y mantenimiento
    empleos_S     jobs in Ventas y servicios al publico
    empleos_P     jobs in Profesional y directivo
    empleos_G     jobs in General, administrativo y clerical

The four empleos_* columns add up to num_empleos. Their total is lower than the
statewide total because AGEBs do not cover the entire territory, so points
falling outside every polygon are reported and then dropped.

Author: Natalia Cadavid Aguilar
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
DATA_DIR = Path.home() / "Directory"
DENUE_CSV = DATA_DIR / "denue_2023_estimaciones.csv"
AGEBS_GPKG = DATA_DIR / "zonas_agebs_empleo.gpkg"
OUTPUT_GPKG = DATA_DIR / "agebs_empleo_jalisco.gpkg"

STATE = "Jalisco"
WGS84 = "EPSG:4326"

# INEGI's Marco Geoestadistico projection (Lambert Conformal Conic, metres).
MEXICO_LCC = "EPSG:6372"

# INEGI exports are usually latin-1. Switch to "utf-8" if decoding fails.
ENCODING = "latin-1"

# Rows per chunk while streaming the national file (keeps peak memory low).
CHUNK_SIZE = 500_000

ANALYSIS_COLUMNS = ["latitud", "longitud", "codigo_act", "num_empleos_esperados"]
READ_COLUMNS = ["entidad", *ANALYSIS_COLUMNS]

AGEB_COLUMNS = [
    "clave_ageb",
    "clave_entidad",
    "clave_municipio",
    "clave_localidad",
    "ageb",
    "nombre_municipio",
    "tipo_ageb",
    "geometry",
]

# --------------------------------------------------------------------------- #
# SCIAN -> employment category lookup
#
# Categories describe the kind of work performed at the establishment, not the
# industry it belongs to:
#   M - Manufactura, construccion, mantenimiento y actividades afines
#   S - Ventas y servicios al publico
#   P - Profesional y directivo
#   G - General, administrativo y clerical
#
# Source: clasificacion_scian_categorias_empleo.csv (author: Sebastián Gutiérrez Bernal).
# Most assignments happen at sector level (2 digits); sectors 71 and 81 are
# split at subsector level (3 digits) because their subsectors differ.
# --------------------------------------------------------------------------- #
CATEGORY_BY_SECTOR = {
    "11": "M",
    "21": "M",
    "22": "M",
    "23": "M",
    "31": "M",
    "32": "M",
    "33": "M",
    "43": "S",
    "46": "S",
    "48": "M",
    "49": "M",
    "51": "P",
    "52": "P",
    "53": "G",
    "54": "P",
    "55": "P",
    "56": "G",
    "61": "P",
    "62": "P",
    "72": "S",
    "93": "G",
}

# Subsectors (3 digits) take precedence over their parent sector (2 digits).
CATEGORY_BY_SUBSECTOR = {
    "711": "P",
    "712": "P",
    "713": "S",
    "811": "M",
    "812": "S",
    "813": "G",
}


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def load_state(
    path: Path,
    state: str = STATE,
    chunk_size: int = CHUNK_SIZE,
) -> pd.DataFrame:
    """Stream the national CSV and return only the rows belonging to `state`.

    Only the columns needed downstream are read, and dtypes are declared
    explicitly so pandas never has to guess them.
    """
    reader = pd.read_csv(
        path,
        usecols=READ_COLUMNS,
        dtype={"entidad": "string", "codigo_act": "string"},
        encoding=ENCODING,
        chunksize=chunk_size,
    )

    # Normalise the state name so trailing spaces or casing don't drop rows.
    target = state.strip().casefold()
    chunks = [chunk.loc[chunk["entidad"].str.strip().str.casefold() == target] for chunk in reader]

    df = pd.concat(chunks, ignore_index=True)
    if df.empty:
        raise ValueError(f"No records found for state {state!r}.")
    return df


def load_agebs(path: Path, columns: list[str] = AGEB_COLUMNS) -> gpd.GeoDataFrame:
    """Read the AGEB polygons and make sure the CRS carries an EPSG code.

    The layer's WKT matches EPSG:6372 but ships without an authority code, so
    tools downstream report it as a custom projection. set_crs only relabels
    the metadata here; coordinates are never moved.
    """
    agebs = gpd.read_file(path)[columns]

    if agebs.crs is None or agebs.crs.to_epsg() is None:
        agebs = agebs.set_crs(MEXICO_LCC, allow_override=True)

    return agebs


# --------------------------------------------------------------------------- #
# Cleaning
# --------------------------------------------------------------------------- #
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Keep the analysis columns and drop rows with missing values."""
    out = df.loc[:, ANALYSIS_COLUMNS].copy()

    # Coerce numerics: anything unparseable becomes NaN and is dropped below.
    for column in ["latitud", "longitud", "num_empleos_esperados"]:
        out[column] = pd.to_numeric(out[column], errors="coerce")

    out["codigo_act"] = out["codigo_act"].str.strip()

    return out.dropna(subset=ANALYSIS_COLUMNS).reset_index(drop=True)


# --------------------------------------------------------------------------- #
# Category assignment
# --------------------------------------------------------------------------- #
def assign_category(df: pd.DataFrame) -> pd.DataFrame:
    """Map each SCIAN code to a category: subsector first, then sector."""
    out = df.copy()
    codes = out["codigo_act"]

    out["categoria"] = (
        codes.str[:3]
        .map(CATEGORY_BY_SUBSECTOR)
        .fillna(codes.str[:2].map(CATEGORY_BY_SECTOR))
        .astype("category")
    )

    # Surface unmapped codes instead of letting them disappear as NaN.
    unmapped = out.loc[out["categoria"].isna(), "codigo_act"]
    if not unmapped.empty:
        print(
            f"{len(unmapped):,} rows without a category. "
            f"Sectors involved: {sorted(unmapped.str[:2].unique())}"
        )

    return out


def to_geodataframe(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """Build a point GeoDataFrame in WGS84 from the longitude/latitude columns."""
    return gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitud"], df["latitud"]),
        crs=WGS84,
    )


# --------------------------------------------------------------------------- #
# Spatial join
# --------------------------------------------------------------------------- #
def join_points_to_agebs(
    points: gpd.GeoDataFrame,
    agebs: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Locate every establishment inside its AGEB.

    Points are reprojected into the AGEB CRS so both layers are comparable.
    "within" is used instead of "intersects" so a point sitting exactly on a
    shared border is not counted twice.
    """
    points_proj = points.to_crs(agebs.crs)

    joined = gpd.sjoin(points_proj, agebs, how="left", predicate="within").drop(
        columns="index_right"
    )

    # AGEBs do not tile the whole territory: gaps outside urban localities are
    # expected, a large share is not.
    orphans = joined["clave_ageb"].isna().sum()
    print(f"{orphans:,} of {len(joined):,} points fell outside every AGEB")

    # More joined rows than input points means some polygons overlap and those
    # establishments were duplicated, which would inflate the totals.
    if len(joined) > len(points):
        print(
            f"WARNING: {len(joined) - len(points):,} duplicated points "
            "caused by overlapping AGEB polygons."
        )

    return joined


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #
def employment_by_ageb(
    joined: gpd.GeoDataFrame,
    agebs: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Total employment per AGEB, overall and broken down by category."""
    matched = joined.dropna(subset=["clave_ageb"])

    totals = matched.groupby("clave_ageb").agg(num_empleos=("num_empleos_esperados", "sum"))

    # One column per category (empleos_M, empleos_S, ...).
    by_category = matched.pivot_table(
        index="clave_ageb",
        columns="categoria",
        values="num_empleos_esperados",
        aggfunc="sum",
        fill_value=0,
        observed=True,
    ).add_prefix("empleos_")

    summary = totals.join(by_category)

    # Attach the totals back to the polygons; AGEBs with no points get 0.
    out = agebs.merge(summary, on="clave_ageb", how="left")

    value_columns = [c for c in out.columns if c.startswith(("num_", "empleos_"))]
    out[value_columns] = out[value_columns].fillna(0).round().astype("int64")

    return out


def export(gdf: gpd.GeoDataFrame, path: Path, layer: str) -> None:
    """Write to GeoPackage, casting category dtypes that the driver rejects."""
    out = gdf.copy()
    for column in out.select_dtypes("category").columns:
        out[column] = out[column].astype(str)

    out.to_file(path, layer=layer, driver="GPKG")
    print(f"Saved {len(out):,} features to {path}")


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #
gdf = to_geodataframe(assign_category(clean(load_state(DENUE_CSV))))

print(f"{len(gdf):,} establishments in {STATE}")
print(gdf["categoria"].value_counts(dropna=False))

agebs = load_agebs(AGEBS_GPKG)
joined = join_points_to_agebs(gdf, agebs)

agebs_empleos = employment_by_ageb(joined, agebs)

# Sanity check: employment assigned to AGEBs plus orphaned points must equal
# the source total. A mismatch points to duplicated or lost records.
print(f"Source total:  {gdf['num_empleos_esperados'].sum():,.0f}")
print(f"Assigned total: {agebs_empleos['num_empleos'].sum():,.0f}")

export(agebs_empleos, OUTPUT_GPKG, layer="agebs_empleo")
