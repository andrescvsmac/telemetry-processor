"""
Unit tests for TelemetryProcessor module
"""

import unittest
from telemetry_processor import TelemetryProcessor


class TestTelemetryProcessor(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.processor = TelemetryProcessor(max_events_per_device=20)

    def test_ingest_single_event(self):
        """Test ingesting a single event."""
        event = {
            "device_id": "AC-445",
            "timestamp": 1732137200,
            "temperature_f": 78.2,
            "humidity": 46.1
        }

        self.processor.ingest(event)
        summary = self.processor.get_summary("AC-445")

        self.assertIsNotNone(summary)
        self.assertEqual(summary['device_id'], "AC-445")
        self.assertEqual(summary['recent_avg_temperature_f'], 78.2)
        self.assertEqual(summary['recent_avg_humidity'], 46.1)
        self.assertEqual(summary['last_event_ts'], 1732137200)
        self.assertEqual(summary['status'], "ok")

    def test_ingest_multiple_events_same_device(self):
        """Test ingesting multiple events for the same device."""
        events = [
            {"device_id": "AC-445", "timestamp": 1732137200, "temperature_f": 75.0, "humidity": 45.0},
            {"device_id": "AC-445", "timestamp": 1732137205, "temperature_f": 80.0, "humidity": 50.0},
            {"device_id": "AC-445", "timestamp": 1732137210, "temperature_f": 85.0, "humidity": 55.0},
        ]

        for event in events:
            self.processor.ingest(event)

        summary = self.processor.get_summary("AC-445")

        self.assertEqual(summary['recent_avg_temperature_f'], 80.0)  # (75 + 80 + 85) / 3
        self.assertEqual(summary['recent_avg_humidity'], 50.0)  # (45 + 50 + 55) / 3
        self.assertEqual(summary['last_event_ts'], 1732137210)
        self.assertEqual(summary['status'], "warning")  # Last temp is 85

    def test_ingest_multiple_devices(self):
        """Test ingesting events from multiple different devices."""
        events = [
            {"device_id": "AC-445", "timestamp": 1732137200, "temperature_f": 75.0, "humidity": 45.0},
            {"device_id": "AC-446", "timestamp": 1732137200, "temperature_f": 92.0, "humidity": 60.0},
            {"device_id": "AC-447", "timestamp": 1732137200, "temperature_f": 82.0, "humidity": 50.0},
        ]

        for event in events:
            self.processor.ingest(event)

        summary_445 = self.processor.get_summary("AC-445")
        summary_446 = self.processor.get_summary("AC-446")
        summary_447 = self.processor.get_summary("AC-447")

        self.assertEqual(summary_445['status'], "ok")
        self.assertEqual(summary_446['status'], "critical")
        self.assertEqual(summary_447['status'], "warning")

    def test_status_ok(self):
        """Test status is 'ok' when temperature <= 80."""
        event = {"device_id": "AC-001", "timestamp": 1732137200, "temperature_f": 72.0, "humidity": 45.0}
        self.processor.ingest(event)
        summary = self.processor.get_summary("AC-001")
        self.assertEqual(summary['status'], "ok")

    def test_status_warning(self):
        """Test status is 'warning' when 80 < temperature <= 90."""
        event = {"device_id": "AC-002", "timestamp": 1732137200, "temperature_f": 85.0, "humidity": 45.0}
        self.processor.ingest(event)
        summary = self.processor.get_summary("AC-002")
        self.assertEqual(summary['status'], "warning")

    def test_status_critical(self):
        """Test status is 'critical' when temperature > 90."""
        event = {"device_id": "AC-003", "timestamp": 1732137200, "temperature_f": 95.0, "humidity": 45.0}
        self.processor.ingest(event)
        summary = self.processor.get_summary("AC-003")
        self.assertEqual(summary['status'], "critical")

    def test_status_boundary_cases(self):
        """Test status at exact boundary values."""
        # Exactly 80 should be "ok"
        event1 = {"device_id": "AC-004", "timestamp": 1732137200, "temperature_f": 80.0, "humidity": 45.0}
        self.processor.ingest(event1)
        self.assertEqual(self.processor.get_summary("AC-004")['status'], "ok")

        # Exactly 90 should be "warning"
        event2 = {"device_id": "AC-005", "timestamp": 1732137200, "temperature_f": 90.0, "humidity": 45.0}
        self.processor.ingest(event2)
        self.assertEqual(self.processor.get_summary("AC-005")['status'], "warning")

        # 90.1 should be "critical"
        event3 = {"device_id": "AC-006", "timestamp": 1732137200, "temperature_f": 90.1, "humidity": 45.0}
        self.processor.ingest(event3)
        self.assertEqual(self.processor.get_summary("AC-006")['status'], "critical")

    def test_unknown_device_id(self):
        """Test that unknown device IDs return None gracefully."""
        summary = self.processor.get_summary("UNKNOWN-DEVICE")
        self.assertIsNone(summary)

    def test_max_events_limit(self):
        """Test that only the most recent N events are kept per device."""
        processor = TelemetryProcessor(max_events_per_device=5)

        # Ingest 10 events, but only last 5 should be kept
        for i in range(10):
            event = {
                "device_id": "AC-445",
                "timestamp": 1732137200 + i,
                "temperature_f": 70.0 + i,
                "humidity": 40.0 + i
            }
            processor.ingest(event)

        summary = processor.get_summary("AC-445")

        # Average should be calculated from last 5 events only
        # Temperatures: 75, 76, 77, 78, 79 -> avg = 77
        # Humidity: 45, 46, 47, 48, 49 -> avg = 47
        self.assertEqual(summary['recent_avg_temperature_f'], 77.0)
        self.assertEqual(summary['recent_avg_humidity'], 47.0)
        self.assertEqual(summary['last_event_ts'], 1732137209)

    def test_get_all_device_ids(self):
        """Test retrieving all known device IDs."""
        events = [
            {"device_id": "AC-445", "timestamp": 1732137200, "temperature_f": 75.0, "humidity": 45.0},
            {"device_id": "AC-446", "timestamp": 1732137200, "temperature_f": 80.0, "humidity": 50.0},
            {"device_id": "AC-447", "timestamp": 1732137200, "temperature_f": 85.0, "humidity": 55.0},
        ]

        for event in events:
            self.processor.ingest(event)

        device_ids = self.processor.get_all_device_ids()
        self.assertEqual(set(device_ids), {"AC-445", "AC-446", "AC-447"})

    def test_rounding_averages(self):
        """Test that averages are properly rounded to 2 decimal places."""
        events = [
            {"device_id": "AC-445", "timestamp": 1732137200, "temperature_f": 75.333, "humidity": 45.666},
            {"device_id": "AC-445", "timestamp": 1732137205, "temperature_f": 76.777, "humidity": 46.888},
        ]

        for event in events:
            self.processor.ingest(event)

        summary = self.processor.get_summary("AC-445")

        # Verify rounding to 2 decimal places
        self.assertAlmostEqual(summary['recent_avg_temperature_f'], 76.06, places=2)
        self.assertAlmostEqual(summary['recent_avg_humidity'], 46.28, places=2)


if __name__ == '__main__':
    unittest.main()
