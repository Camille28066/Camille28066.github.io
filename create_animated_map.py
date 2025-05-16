\
import folium
from folium.plugins import TimestampedGeoJson
# AnimationTrack is imported but not used. Consider removing if not planned for future use.
# from trackanimation.animation import AnimationTrack 
import gpxpy
from datetime import datetime, timedelta # Added import

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
    
    # Extract coordinates from points that have time information
    track_coordinates_for_animation = []
    for segment in track.segments:
        for point in segment.points:
            if point.time: # Only include points that have time information for the animation path
                track_coordinates_for_animation.append([point.longitude, point.latitude])

    if not track_coordinates_for_animation:
        print("No points with time information found in the GPX track to animate.")
        return
        
    # Create a Folium map centered around the first point
    map_center = [track_coordinates_for_animation[0][1], track_coordinates_for_animation[0][0]] # lat, lon
    m = folium.Map(
        location=map_center, 
        zoom_start=8, 
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri Satellite"
    )

    # Generate new timestamps like in folium_japan.py
    start_time = datetime(2023, 1, 1, 0, 0, 0) 
    new_timestamps = [(start_time + timedelta(seconds=i)).isoformat() + "Z" 
                      for i in range(len(track_coordinates_for_animation))]

    # Prepare data for TimestampedGeoJson
    features = [
        {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': track_coordinates_for_animation, # Use extracted coordinates
            },
            'properties': {
                'times': new_timestamps, # Use newly generated timestamps
                'style': {"color": "#FF4500", "weight": 3} 
            }
        }
    ]

    TimestampedGeoJson(
        {'type': 'FeatureCollection', 'features': features},
        period="PT2M", # Changed from PT1M to PT2M to cover more ground per step
        transition_time=8, # Changed from 50 to 30 for quicker transitions
        auto_play=True,
        loop=False,
        add_last_point=False,
        max_speed=10, # You can increase this if you want the slider to go faster
        date_options="YYYY/MM/DD HH:mm:ss"
    ).add_to(m)
    
    # Add the original GPX track as a static line for reference
    # This part remains unchanged and uses the original track data
    track_coordinates_static = []
    for segment in track.segments:
        line = []
        for point in segment.points:
            line.append((point.longitude, point.latitude))
        track_coordinates_static.append(line)
    
    if track_coordinates_static:
        folium.PolyLine(
            locations=[[(lat, lon) for lon, lat in segment] for segment in track_coordinates_static], # Folium expects (lat, lon)
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
