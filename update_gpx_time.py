import gpxpy
import gpxpy.gpx
from datetime import datetime, timedelta, timezone

def add_time_to_gpx(file_path, output_file_path):
    """
    Reads a GPX file, adds time information to each track point with a 0.5-second interval,
    and saves it to a new file or overwrites the existing one.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as gpx_file_content:
            gpx = gpxpy.parse(gpx_file_content)
    except Exception as e:
        print(f"Error parsing GPX file {file_path}: {e}")
        return

    start_time = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    current_time = start_time
    time_increment = timedelta(seconds=0.5)

    for track in gpx.tracks:
        for segment in track.segments:
            for point_idx, point in enumerate(segment.points):
                point.time = current_time + (point_idx * time_increment)
            # Update current_time for the next segment if tracks are continuous
            # For a single continuous track, this update happens effectively once after all points.
            if segment.points:
                 current_time = segment.points[-1].time + time_increment


    # If there are multiple tracks and they are meant to be sequential,
    # the time assignment needs to be continuous across them.
    # The current logic resets time incrementing per segment from the initial point time.
    # For a single track with multiple segments, or multiple tracks, if they are sequential:
    
    global_current_time = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                point.time = global_current_time
                global_current_time += time_increment
                
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(gpx.to_xml(version='1.1')) # Ensure GPX 1.1 for broader compatibility
        print(f"Successfully added time to GPX and saved to {output_file_path}")
    except Exception as e:
        print(f"Error writing updated GPX file {output_file_path}: {e}")

if __name__ == '__main__':
    # IMPORTANT: Replace with the actual path to your GPX file
    input_gpx_file = r'shikoku_track.gpx' # Assuming it's in the same directory
    output_gpx_file = r'shikoku_track_with_time.gpx' # Output to a new file

    # To be safe, you might want to output to a new file first:
    # output_gpx_file = r'shikoku_track_with_time.gpx' 
    
    add_time_to_gpx(input_gpx_file, output_gpx_file)
    print(f"Please ensure '{output_gpx_file}' now contains time information for each track point.")

