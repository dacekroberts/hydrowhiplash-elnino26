"""Consistency checks on the pre-registered settings in src/config.py."""
from src import config

ALTERNATIVES = {"greater", "less", "two-sided", None}


def test_every_direction_is_a_known_alternative_for_a_known_region():
    for test, directions in config.TEST_DIRECTIONS.items():
        if isinstance(directions, str):
            assert directions in ALTERNATIVES, test
            continue
        assert set(directions) <= set(config.REGIONS), test
        assert set(directions.values()) <= ALTERNATIVES, test


def test_region_tests_cover_all_seven_regions():
    for test in ("H1", "H2", "H3a", "H3b", "H5_lag0", "H5_lag1", "H6_swe", "H6_spei"):
        assert set(config.TEST_DIRECTIONS[test]) == set(config.REGIONS), test


def test_alaska_and_yukon_tests_are_two_sided_or_descriptive():
    for test, directions in config.TEST_DIRECTIONS.items():
        if isinstance(directions, dict):
            for region in ("AK", "YT"):
                assert directions.get(region) in {"two-sided", None}, (test, region)


def test_index_and_swe_choices():
    assert config.ENSO_INDEX == "RONI" and config.ENSO_ROBUSTNESS_INDEX == "ONI"
    assert set(config.ENSO_INDEX_URLS) == {config.ENSO_INDEX, config.ENSO_ROBUSTNESS_INDEX}
    assert config.SWE_TEST_COLUMN == "era5_swe_z"
    assert set(config.COMPOUNDING_REGIONS) <= set(config.REGIONS)
    assert config.PRECIP_ANOM_MONTHS[-1] == 3  # ends before every fire window opens


def test_fire_windows_open_after_the_winter_predictors_close():
    for region, (first, last) in config.FIRE_SEASON_MONTHS.items():
        assert 1 <= first <= 12 and 1 <= last <= 12, region
        assert first > config.PRECIP_ANOM_MONTHS[-1], region  # opens after March
    assert config.FIRE_SEASON_MONTHS["SoCal"] == (6, 1)  # wraps into January


def test_strong_sensitivity_band_catches_the_near_threshold_winters():
    # Compared after rounding to the index's published decimals; the bare float
    # difference for 1.44 is 0.06000000000000005 (independent audit F7).
    def in_band(value):
        return round(abs(value - config.STRONG_THRESHOLD), config.ENSO_DECIMALS)             <= config.STRONG_SENSITIVITY_BAND
    assert all(in_band(v) for v in (1.53, 1.46, 1.44))
    assert not in_band(1.69) and not in_band(1.43)


def test_correction_families_hold_only_tested_cells_and_match_the_plan_sizes():
    sizes = {}
    for family, members in config.CORRECTION_FAMILIES.items():
        n = 0
        for test, regions in members:
            directions = config.TEST_DIRECTIONS[test]
            n += sum(directions[r] is not None for r in regions)
        sizes[family] = n
    assert sizes == {"H1": 5, "H2": 5, "H3a": 5, "H3b": 5, "H5": 10, "H6": 9,
                     "north_H2": 2, "north_H3a": 2, "north_H3b": 2, "C1": 3, "C2": 3}


def test_every_tested_cell_is_in_exactly_one_family():
    seen = {}
    for family, members in config.CORRECTION_FAMILIES.items():
        for test, regions in members:
            for r in regions:
                if config.TEST_DIRECTIONS[test][r] is not None:
                    assert (test, r) not in seen, (test, r)
                    seen[(test, r)] = family
    for test, directions in config.TEST_DIRECTIONS.items():
        if isinstance(directions, dict):
            for r, d in directions.items():
                if d is not None:
                    assert (test, r) in seen, (test, r)


def test_tracker_window_spans_the_h5_months_and_april_1():
    """The tracker runs from October (first month of H5's Oct-Mar total)
    to the end of April (the April 1 snowpack), for FORECAST_YEAR's winter."""
    from datetime import date

    start, end = (date.fromisoformat(d) for d in config.TRACKER_WINDOW)
    assert (start.month, start.day) == (config.PRECIP_ANOM_MONTHS[0], 1)
    assert start.year == config.FORECAST_YEAR - 1 and end == date(config.FORECAST_YEAR, 4, 30)
    assert date.fromisoformat(config.TRACKER_FREEZE_DATE) < end
