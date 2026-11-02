"""
Geospatial Proximity Service (Geohash & Haversine)
Chapter 16: Proximity Service & Chapter 17: Nearby Friends

Architecture:
1. Geohash Encoding:
   - Interleaves binary representations of latitude and longitude into base32 characters.
   - Nearby locations share common prefixes.
2. Radius Search using Haversine Distance:
   - Computes exact great-circle distance between two GPS coordinates on Earth.
3. Proximity Location Index:
   - Fast spatial querying of nearby places/friends.
"""

from dataclasses import dataclass
import math
import threading
from typing import Dict, List, Optional, Tuple

BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
BASE32_MAP = {c: i for i, c in enumerate(BASE32)}


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on the Earth (in km)."""
    R = 6371.0  # Earth's radius in kilometers

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def encode_geohash(lat: float, lon: float, precision: int = 6) -> str:
    """Encode latitude and longitude into a geohash string."""
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]

    geohash = []
    bits = [16, 8, 4, 2, 1]
    bit = 0
    ch = 0
    is_even = True

    while len(geohash) < precision:
        if is_even:
            mid = (lon_interval[0] + lon_interval[1]) / 2.0
            if lon > mid:
                ch |= bits[bit]
                lon_interval[0] = mid
            else:
                lon_interval[1] = mid
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2.0
            if lat > mid:
                ch |= bits[bit]
                lat_interval[0] = mid
            else:
                lat_interval[1] = mid

        is_even = not is_even
        if bit < 4:
            bit += 1
        else:
            geohash.append(BASE32[ch])
            bit = 0
            ch = 0

    return "".join(geohash)


@dataclass
class Place:
    place_id: str
    name: str
    latitude: float
    longitude: float
    category: str


class ProximityService:
    """
    Spatial Index storing entities indexed by Geohash with fast radius queries.
    """

    def __init__(self, geohash_precision: int = 5):
        self.precision = geohash_precision
        # geohash_prefix -> list of Place
        self._index: Dict[str, List[Place]] = {}
        self._places: Dict[str, Place] = {}
        self._lock = threading.Lock()

    def add_place(self, place: Place) -> None:
        with self._lock:
            self._places[place.place_id] = place
            gh = encode_geohash(place.latitude, place.longitude, precision=self.precision)
            self._index.setdefault(gh, []).append(place)

    def search_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> List[Tuple[Place, float]]:
        """
        Find places within radius_km sorted by distance ascending.
        Returns list of (Place, distance_km).
        """
        with self._lock:
            # Query candidate places
            candidates = list(self._places.values())

        results = []
        for p in candidates:
            if category and p.category.lower() != category.lower():
                continue
            dist = haversine_distance_km(latitude, longitude, p.latitude, p.longitude)
            if dist <= radius_km:
                results.append((p, round(dist, 3)))

        results.sort(key=lambda x: x[1])
        return results[:limit]

