"""
Telemetry Processing Module

Ingests and summarizes temperature + humidity telemetry from HVAC sensors.
"""

from typing import Dict, Optional


class TelemetryProcessor:
    """
    Processes telemetry events from HVAC sensors and provides health summaries.

    Stores the latest N events per device in memory and computes aggregated
    metrics on demand.
    """

    def __init__(self, max_events_per_device: int = 20):
        """
        Initialize the telemetry processor.

        Args:
            max_events_per_device: Maximum number of events to store per device (default: 20)
        """
        # TODO: Implement initialization logic
        pass

    def ingest(self, event: dict) -> None:
        """
        Ingest a telemetry event and store it for the corresponding device.

        Automatically maintains the most recent N events per device.

        Args:
            event: Telemetry event dictionary containing:
                - device_id (str): Unique device identifier
                - timestamp (int): Unix timestamp
                - temperature_f (float): Temperature in Fahrenheit
                - humidity (float): Humidity percentage

        Raises:
            KeyError: If required fields are missing from the event
        """
        # TODO: Implement ingestion logic
        pass

    def get_summary(self, device_id: str) -> Optional[Dict]:
        """
        Generate a health summary for a specific device.

        Computes average temperature and humidity from stored events,
        and determines the device status based on the most recent temperature.

        Args:
            device_id: Unique device identifier

        Returns:
            Dictionary containing summary metrics:
                - device_id (str): Device identifier
                - recent_avg_temperature_f (float): Average temperature
                - recent_avg_humidity (float): Average humidity
                - last_event_ts (int): Timestamp of most recent event
                - status (str): Health status ("ok", "warning", or "critical")

            Returns None if device_id is unknown.
        """
        # TODO: Implement summary calculation logic
        return None

    def get_all_device_ids(self) -> list:
        """
        Get a list of all known device IDs.

        Returns:
            List of device IDs that have ingested events
        """
        # TODO: Implement retrieval of all device IDs
        return []
