\
import folium
from folium.plugins import TimestampedGeoJson
from trackanimation.animation import AnimationTrack
import gpxpy

def create_animation_from_gpx(gpx_file_path, output_html_path):
    try:
        with open(gpx_file_path, 'r', encoding='utf-8') as gpx_file_content:
            gpx = gpxpy.parse(gpx_file_content)
    except Exception as e:
        print(f"Error parsing GPX file {gpx_file_path}: {e}")
        return

    if not gpx.tracks:
        print("No tracks found in GPX file.")
        return

    # Assuming the first track is the one to animate
    track = gpx.tracks[0]
    
    # Extract points and times
    points = []
    for segment in track.segments:
        for point in segment.points:
            if point.time: # Ensure point has time information
                points.append({
                    'coordinates': [point.longitude, point.latitude],
                    'time': point.time.isoformat()
                })

    if not points:
        print("No points with time information found in the GPX track.")
        return
        
    # Create a Folium map centered around the first point
    map_center = [points[0]['coordinates'][1], points[0]['coordinates'][0]] # lat, lon
    m = folium.Map(location=map_center, zoom_start=13, tiles="CartoDB positron")

    # Prepare data for TimestampedGeoJson
    features = [
        {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [p['coordinates'] for p in points],
            },
            'properties': {
                'times': [p['time'] for p in points],
                'style': {
                    'color': 'blue',
                    'weight': 3,
                    'opacity': 0.7
                },
                'icon': 'circle',
                'iconstyle':{
                    'fillColor': 'blue',
                    'fillOpacity': 0.8,
                    'stroke': 'true',
                    'radius': 5
                }
            }
        }
    ]

    TimestampedGeoJson(
        {'type': 'FeatureCollection', 'features': features},
        period='PT1S', # Changed from PT0.5S to PT1S
        add_last_point=True,
        auto_play=True,
        loop=True,
        max_speed=1,
        loop_button=True,
        date_options='YYYY-MM-DD HH:mm:ss',
        time_slider_drag_update=True,
    ).add_to(m)
    
    # Add the original GPX track as a static line for reference
    # Convert GPX to GeoJSON for Folium
    track_coordinates = []
    for segment in track.segments:
        line = []
        for point in segment.points:
            line.append((point.longitude, point.latitude))
        track_coordinates.append(line)
    
    if track_coordinates:
        folium.PolyLine(
            locations=[[(lat, lon) for lon, lat in segment] for segment in track_coordinates], # Folium expects (lat, lon)
            color="rgba(0,0,255,0.3)", # Light blue, semi-transparent
            weight=3,
            opacity=0.5
        ).add_to(m)


    try:
        m.save(output_html_path)
        print(f"Animated map saved to {output_html_path}")
    except Exception as e:
        print(f"Error saving map: {e}")

if __name__ == '__main__':
    input_gpx = r'shikoku_track_with_time.gpx'
    output_html = r'animated_shikoku_map.html'
    create_animation_from_gpx(input_gpx, output_html)
