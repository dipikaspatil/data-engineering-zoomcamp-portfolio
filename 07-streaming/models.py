# models.py
# -----------------------------
# Defines data models for taxi rides
# This keeps your data structure separate from producer/consumer logic
# -----------------------------

from dataclasses import dataclass
from datetime import datetime
import pandas as pd

@dataclass
class Ride:
    """
    Ride represents a single taxi trip.
    
    Fields:
    ----------
    PULocationID : int
        Pickup location ID
    DOLocationID : int
        Dropoff location ID
    trip_distance : float
        Distance of the trip in miles
    total_amount : float
        Total fare amount
    lpep_pickup_datetime : int
        Pickup time in milliseconds since epoch (JSON-serializable)
    """
    PULocationID: int
    DOLocationID: int
    trip_distance: float
    total_amount: float
    lpep_pickup_datetime: int  # milliseconds since epoch

    @property
    def pickup_datetime_obj(self) -> datetime:
        """Converts the millisecond integer back to a Python datetime object."""
        return datetime.fromtimestamp(self.lpep_pickup_datetime / 1000.0)

    @staticmethod
    def from_row(row: pd.Series) -> "Ride":
        """
        Converts a Pandas DataFrame row into a Ride object.
        
        Handles:
        - Numeric conversion (int, float)
        - Timestamp conversion to milliseconds
        - Ensures JSON serializable object

        Parameters
        ----------
        row : pd.Series
            A single row from a DataFrame, representing a taxi trip

        Returns
        -------
        Ride
            A Ride object with properly typed fields
        """
        return Ride(
            PULocationID=int(row['PULocationID']),               # ensure integer
            DOLocationID=int(row['DOLocationID']),               # ensure integer
            trip_distance=float(row['trip_distance']),          # ensure float
            total_amount=float(row['total_amount']),            # ensure float
            # Convert pandas Timestamp to milliseconds since epoch
            lpep_pickup_datetime=int(row['lpep_pickup_datetime'].timestamp() * 1000)
        )