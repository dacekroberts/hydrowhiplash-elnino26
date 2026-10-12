"""results/tables/site_settings.json must match src/config.py."""
import json

from src import config, site_settings


def test_committed_file_matches_config():
    committed = json.loads(site_settings.OUT.read_text("utf-8"))
    assert committed == json.loads(site_settings.text()), "rerun python -m src.site_settings"


def test_values_come_from_config():
    s = site_settings.settings()
    assert s["min_fire_ha"] == config.MIN_FIRE_HA
    assert s["prediction_level_pct"] == 80
    assert s["fire_last_year_by_region"] == config.FIRE_LAST_YEAR_BY_REGION
