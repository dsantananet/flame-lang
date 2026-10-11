import unittest
from simulation.contract import ContractError, validate_weather

GOOD = {
    "schema_version": "1.0", "source": "IPMA", "valid_time": "2026-10-11T06:00:00+00:00",
    "geometry_crs": "EPSG:4326", "point": {"lat": 39.8, "lon": -7.5},
    "variables": {"temperature_c": 25, "relative_humidity_pct": 35, "wind_speed_ms": 4},
    "quality_flags": []
}

class TestWeatherContract(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_weather(GOOD)["valid_time"], "2026-10-11T06:00:00Z")

    def test_reject_missing_timezone(self):
        with self.assertRaises(ContractError):
            validate_weather({**GOOD, "valid_time": "2026-10-11T06:00:00"})

    def test_reject_invalid_humidity(self):
        with self.assertRaises(ContractError):
            validate_weather({**GOOD, "variables": {"relative_humidity_pct": 101}})

    def test_reject_bad_coordinates(self):
        with self.assertRaises(ContractError):
            validate_weather({**GOOD, "point": {"lat": 999, "lon": 0}})

    def test_reject_unknown_units(self):
        with self.assertRaises(ContractError):
            validate_weather({**GOOD, "variables": {"wind_kmh": 30}})

if __name__ == "__main__":
    unittest.main()
