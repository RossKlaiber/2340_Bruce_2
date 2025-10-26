import math
from decimal import Decimal


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using the Haversine formula.
    
    Returns distance in miles.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in miles
    r = 3959
    
    return c * r


def filter_jobs_by_distance(jobs, user_lat, user_lon, max_distance_miles):
    """
    Filter a queryset of jobs by distance from user location.
    
    Args:
        jobs: QuerySet of Job objects with latitude and longitude
        user_lat: User's latitude (Decimal or float)
        user_lon: User's longitude (Decimal or float)
        max_distance_miles: Maximum distance in miles (int or string)
    
    Returns:
        List of job objects within the specified distance, ordered by distance
    """
    if not user_lat or not user_lon or not max_distance_miles:
        return jobs
    
    try:
        max_distance = float(max_distance_miles)
        user_latitude = float(user_lat)
        user_longitude = float(user_lon)
    except (ValueError, TypeError):
        return jobs
    
    # Filter jobs that have coordinates
    jobs_with_coords = jobs.filter(
        latitude__isnull=False, 
        longitude__isnull=False
    )
    
    # Calculate distances and filter
    jobs_within_distance = []
    for job in jobs_with_coords:
        if job.latitude and job.longitude:
            distance = calculate_distance(
                user_latitude, user_longitude,
                job.latitude, job.longitude
            )
            if distance <= max_distance:
                job.distance_from_user = round(distance, 1)
                jobs_within_distance.append(job)
    
    # Sort by distance
    jobs_within_distance.sort(key=lambda job: job.distance_from_user)
    
    return jobs_within_distance


def get_jobs_with_distances(jobs, user_lat, user_lon):
    """
    Add distance information to jobs without filtering.
    Useful for map view to show all jobs with their distances.
    
    Args:
        jobs: QuerySet of Job objects with latitude and longitude
        user_lat: User's latitude (Decimal or float)
        user_lon: User's longitude (Decimal or float)
    
    Returns:
        List of job objects with distance_from_user attribute added
    """
    if not user_lat or not user_lon:
        return list(jobs)
    
    try:
        user_latitude = float(user_lat)
        user_longitude = float(user_lon)
    except (ValueError, TypeError):
        return list(jobs)
    
    # Filter jobs that have coordinates
    jobs_with_coords = jobs.filter(
        latitude__isnull=False, 
        longitude__isnull=False
    )
    
    # Calculate distances
    jobs_with_distances = []
    for job in jobs_with_coords:
        if job.latitude and job.longitude:
            distance = calculate_distance(
                user_latitude, user_longitude,
                job.latitude, job.longitude
            )
            job.distance_from_user = round(distance, 1)
            jobs_with_distances.append(job)
    
    return jobs_with_distances
