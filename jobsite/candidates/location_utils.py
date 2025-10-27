import json
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, List, Dict, Optional, TYPE_CHECKING
from urllib import error as urlerror
from urllib import parse, request

from django.urls import reverse
from .models import LocationCoordinate

if TYPE_CHECKING:  # pragma: no cover - imports used only for typing
    from accounts.models import JobSeekerProfile

logger = logging.getLogger(__name__)


def _normalize_location(value: str) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())


def _quantize_coordinate(value: str) -> Decimal:
    return Decimal(value).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


def _fetch_coordinates_from_api(location: str) -> Optional[Dict[str, str]]:
    params = parse.urlencode({"q": location, "format": "json", "limit": 1})
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    headers = {
        "User-Agent": "JobSiteRecruiter/1.0 (+https://example.com)"
    }
    req = request.Request(url, headers=headers)

    try:
        with request.urlopen(req, timeout=10) as response:
            payload = response.read().decode("utf-8")
    except (urlerror.URLError, urlerror.HTTPError, TimeoutError) as exc:
        logger.warning("Failed to fetch coordinates for '%s': %s", location, exc)
        return None

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        logger.warning("Unable to decode geocoding response for '%s': %s", location, exc)
        return None

    if not data:
        return None

    top_result = data[0]
    if "lat" not in top_result or "lon" not in top_result:
        return None

    return {
        "latitude": _quantize_coordinate(top_result["lat"]),
        "longitude": _quantize_coordinate(top_result["lon"]),
        "display_name": top_result.get("display_name", location),
    }


def get_or_fetch_coordinates(location: str) -> Optional[Dict[str, object]]:
    """Return cached coordinates for a location or fetch them if needed."""

    normalized = _normalize_location(location)
    if not normalized:
        return None

    try:
        cached = LocationCoordinate.objects.get(normalized_name=normalized)
    except LocationCoordinate.DoesNotExist:
        fetched = _fetch_coordinates_from_api(location)
        if not fetched:
            return None

        cached, _ = LocationCoordinate.objects.update_or_create(
            normalized_name=normalized,
            defaults={
                "search_term": location,
                "latitude": fetched["latitude"],
                "longitude": fetched["longitude"],
                "display_name": fetched["display_name"],
            },
        )

    return {
        "location": cached.display_name or cached.search_term,
        "search_term": cached.search_term,
        "normalized_name": cached.normalized_name,
        "latitude": float(cached.latitude),
        "longitude": float(cached.longitude),
    }


def build_location_clusters(profiles: Iterable['JobSeekerProfile']) -> List[Dict[str, object]]:
    """Return a list of candidate clusters grouped by location."""

    clusters: Dict[str, Dict[str, object]] = {}
    coordinates_cache: Dict[str, Optional[Dict[str, object]]] = {}

    for profile in profiles:
        location = (profile.location or "").strip()
        if not location:
            continue

        normalized = _normalize_location(location)
        if normalized in coordinates_cache:
            coordinates = coordinates_cache[normalized]
        else:
            coordinates = get_or_fetch_coordinates(location)
            coordinates_cache[normalized] = coordinates

        if not coordinates:
            continue

        cluster = clusters.setdefault(
            coordinates["normalized_name"],
            {
                "location": coordinates["location"],
                "latitude": coordinates["latitude"],
                "longitude": coordinates["longitude"],
                "candidates": [],
            },
        )

        full_name = f"{profile.user_profile.user.first_name} {profile.user_profile.user.last_name}".strip()
        if not full_name:
            full_name = profile.user_profile.user.username

        cluster["candidates"].append(
            {
                "name": full_name,
                "headline": profile.headline,
                "profile_url": reverse("accounts.profile", args=[profile.user_profile.user.username]),
                "location": location,
            }
        )

    cluster_list: List[Dict[str, object]] = []
    for cluster in clusters.values():
        candidates = cluster["candidates"]
        candidates.sort(key=lambda c: c["name"].lower())
        cluster_list.append(
            {
                "location": cluster["location"],
                "latitude": cluster["latitude"],
                "longitude": cluster["longitude"],
                "count": len(candidates),
                "candidates": candidates,
            }
        )

    cluster_list.sort(key=lambda c: c["count"], reverse=True)
    return cluster_list
