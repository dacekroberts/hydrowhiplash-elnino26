"""Settings the site states in prose, written to results/ so no page types one.

The Quarto site reads only results/ (it cannot import src.config), so this
module writes the config values its pages quote to
results/tables/site_settings.json. Rebuild after any change to those values
in src/config.py; tests/test_site_settings.py fails if the file is stale.

Run:  python -m src.site_settings
"""
from __future__ import annotations

import json
from pathlib import Path

from src import config

OUT = config.RESULTS / "tables" / "site_settings.json"


def settings() -> dict:
    return {
        "enso_index": config.ENSO_INDEX,
        "enso_robustness_index": config.ENSO_ROBUSTNESS_INDEX,
        "el_nino_threshold": config.EL_NINO_THRESHOLD,
        "la_nina_threshold": config.LA_NINA_THRESHOLD,
        "strong_threshold": config.STRONG_THRESHOLD,
        "strong_sensitivity_band": config.STRONG_SENSITIVITY_BAND,
        "climate_first_year": config.CLIMATE_FIRST_YEAR,
        "fire_first_year": config.FIRE_FIRST_YEAR,
        "fire_last_year_by_region": dict(config.FIRE_LAST_YEAR_BY_REGION),
        "pooled_last_year": config.POOLED_LAST_YEAR,
        "forecast_year": config.FORECAST_YEAR,
        "regions": list(config.REGIONS),
        "ca_split_lat": config.CA_SPLIT_LAT,
        "min_fire_ha": config.MIN_FIRE_HA,
        "fire_season_months": {k: list(v) for k, v in config.FIRE_SEASON_MONTHS.items()},
        "mtbs_wfigs_cutover": config.MTBS_WFIGS_CUTOVER,
        "cnfdb_merge_km": config.CNFDB_MERGE_KM,
        "zero_year_pct_limit": config.ZERO_YEAR_PCT_LIMIT,
        "spei_scale": config.SPEI_SCALE,
        "spei_cal_years": list(config.SPEI_CAL_YEARS),
        "precip_anom_normal_years": list(config.PRECIP_ANOM_NORMAL_YEARS),
        "alpha": config.ALPHA,
        "n_permutations": config.N_PERMUTATIONS,
        "n_bootstrap": config.N_BOOTSTRAP,
        "hac_maxlags": config.HAC_MAXLAGS,
        "block_len": config.BLOCK_LEN,
        "prediction_level_pct": round(100 * (1 - config.PREDICTION_ALPHA)),
        "forward_min_train_years": config.FORWARD_MIN_TRAIN_YEARS,
        "random_seed": config.RANDOM_SEED,
        "plan_frozen_date": config.TRACKER_FREEZE_DATE,
        "plan_frozen_commit": config.FROZEN_PLAN_COMMIT[:7],
    }


def text() -> str:
    return json.dumps(settings(), indent=2, sort_keys=True) + "\n"


def main(out: Path = OUT) -> None:
    out.write_bytes(text().encode("utf-8"))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
