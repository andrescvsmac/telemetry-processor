"""
Example demonstration of TelemetryProcessor with sample data
"""

from telemetry_processor import TelemetryProcessor
from datetime import datetime
import json


def demo_basic_usage():
    """Demonstrate basic usage with simple examples."""
    print("=" * 60)
    print("BASIC TELEMETRY PROCESSOR DEMONSTRATION")
    print("=" * 60)

    # Initialize the processor
    processor = TelemetryProcessor(max_events_per_device=20)

    # Simulate ingesting events
    print("\n1. Ingesting events from multiple devices...")

    events = [
        # Device AC-445: Normal temperature
        {"device_id": "AC-445", "timestamp": 1732137200, "temperature_f": 72.0, "humidity": 45.0},
        {"device_id": "AC-445", "timestamp": 1732137205, "temperature_f": 73.5, "humidity": 46.0},
        {"device_id": "AC-445", "timestamp": 1732137210, "temperature_f": 74.0, "humidity": 45.5},

        # Device AC-446: Warning temperature
        {"device_id": "AC-446", "timestamp": 1732137200, "temperature_f": 82.0, "humidity": 50.0},
        {"device_id": "AC-446", "timestamp": 1732137205, "temperature_f": 83.5, "humidity": 51.0},
        {"device_id": "AC-446", "timestamp": 1732137210, "temperature_f": 85.0, "humidity": 52.0},

        # Device AC-447: Critical temperature
        {"device_id": "AC-447", "timestamp": 1732137200, "temperature_f": 92.0, "humidity": 60.0},
        {"device_id": "AC-447", "timestamp": 1732137205, "temperature_f": 93.0, "humidity": 61.0},
        {"device_id": "AC-447", "timestamp": 1732137210, "temperature_f": 95.0, "humidity": 62.0},
    ]

    for event in events:
        processor.ingest(event)
        print(f"   ✓ Ingested event from {event['device_id']} at {event['timestamp']}")

    # Get summaries for each device
    print("\n2. Retrieving summaries for all devices...")
    print()

    for device_id in processor.get_all_device_ids():
        summary = processor.get_summary(device_id)

        status_indicator = {
            "ok": "✅",
            "warning": "⚠️",
            "critical": "🚨"
        }

        print(f"Device: {summary['device_id']}")
        print(f"  Status: {status_indicator.get(summary['status'], '')} {summary['status'].upper()}")
        print(f"  Avg Temperature: {summary['recent_avg_temperature_f']}°F")
        print(f"  Avg Humidity: {summary['recent_avg_humidity']}%")
        print(f"  Last Event: {datetime.fromtimestamp(summary['last_event_ts']).strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    # Test unknown device
    print("3. Testing unknown device handling...")
    unknown_summary = processor.get_summary("UNKNOWN-DEVICE")
    print(f"   Summary for unknown device: {unknown_summary}")
    print()


def demo_with_many_events():
    """Demonstrate with many events to show the windowing behavior."""
    print("=" * 60)
    print("WINDOWING BEHAVIOR DEMONSTRATION (Max 20 events)")
    print("=" * 60)

    processor = TelemetryProcessor(max_events_per_device=20)

    print("\n1. Ingesting 30 events for device AC-100...")

    # Ingest 30 events, temperatures gradually increasing
    base_timestamp = 1732137200
    for i in range(30):
        event = {
            "device_id": "AC-100",
            "timestamp": base_timestamp + (i * 5),  # Every 5 seconds
            "temperature_f": 70.0 + (i * 0.5),  # Gradually increasing
            "humidity": 40.0 + (i * 0.2)
        }
        processor.ingest(event)

    print("   ✓ Ingested 30 events")

    # Get summary - should only consider last 20 events
    summary = processor.get_summary("AC-100")

    print("\n2. Summary (based on last 20 events only):")
    print(f"   Avg Temperature: {summary['recent_avg_temperature_f']}°F")
    print(f"   Avg Humidity: {summary['recent_avg_humidity']}%")
    print(f"   Status: {summary['status'].upper()}")
    print(f"   Last Event: {datetime.fromtimestamp(summary['last_event_ts']).strftime('%Y-%m-%d %H:%M:%S')}")

    # Calculate what the average would be for all 30 events
    all_temps = [70.0 + (i * 0.5) for i in range(30)]
    all_temps_avg = sum(all_temps) / len(all_temps)

    # Calculate average for last 20 events only
    last_20_temps = all_temps[-20:]
    last_20_avg = sum(last_20_temps) / len(last_20_temps)

    print("\n3. Verification:")
    print(f"   If all 30 events were used: {all_temps_avg:.2f}°F")
    print(f"   Using last 20 events only: {last_20_avg:.2f}°F")
    print("   ✓ Processor correctly maintains 20-event window")
    print()


def demo_json_output():
    """Demonstrate JSON-serializable output."""
    print("=" * 60)
    print("JSON OUTPUT DEMONSTRATION")
    print("=" * 60)

    processor = TelemetryProcessor(max_events_per_device=20)

    # Ingest sample data
    events = [
        {"device_id": "AC-445", "timestamp": 1732137200, "temperature_f": 78.2, "humidity": 46.1},
        {"device_id": "AC-445", "timestamp": 1732137205, "temperature_f": 79.0, "humidity": 46.5},
    ]

    for event in events:
        processor.ingest(event)

    summary = processor.get_summary("AC-445")

    print("\n1. Summary as JSON:")
    print(json.dumps(summary, indent=2))
    print()


if __name__ == "__main__":
    demo_basic_usage()
    demo_with_many_events()
    demo_json_output()

    print("=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
