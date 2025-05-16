from fastkml import kml
from shapely.geometry import LineString
import gpxpy
import gpxpy.gpx

# Step 1: Load and parse the KML
kml_path = r"C:\Users\user\Desktop\Camille\Perso\website\japan\88-temple-pilgrimage-shikoku-trail-full-path-1140km.kml"
with open(kml_path, 'rb') as f:
    doc = f.read()

# Parse the KML
k = kml.KML()
k.from_string(doc)

# Traverse the KML structure
features = list(k.features())
document = features[0]
placemarks = list(document.features())

from fastkml import kml

# Assuming `k` is your parsed KML object:
folders = list(document.features())

for folder in folders:
    print(f"📁 Folder: {folder.name}")
    placemarks = list(folder.features())
    
    for placemark in placemarks:
        print(f"  📌 Placemark: {placemark.name}")
        if hasattr(placemark, 'geometry') and placemark.geometry.geom_type == 'LineString':
            print("    ✅ Found LineString:")
            for coord in placemark.geometry.coords:
                print(f"      - lon: {coord[0]}, lat: {coord[1]}")

def process_features(features, indent=0):
    for feature in features:
        prefix = "  " * indent
        if isinstance(feature, kml.Folder):
            print(f"{prefix}📁 Folder: {feature.name}")
            process_features(list(feature.features()), indent + 1)
        elif isinstance(feature, kml.Placemark):
            print(f"{prefix}📌 Placemark: {feature.name}")
            if hasattr(feature, 'geometry') and feature.geometry.geom_type == 'LineString':
                print(f"{prefix}    ✅ Found LineString with {len(feature.geometry.coords)} points:")
                for coord in feature.geometry.coords:
                    print(f"{prefix}      - lon: {coord[0]}, lat: {coord[1]}")

# Start from the Trails folder
trails_folder = folders[0]  # You verified this is 'Trails'
process_features([trails_folder])

# whats inside the raw kml
from lxml import etree

for folder in list(trails_folder.features()):
    for placemark in list(folder.features()):
        if placemark.name == "Path":
            raw_xml = placemark.etree_element()  # <-- add parentheses!
            print(etree.tostring(raw_xml, pretty_print=True).decode())


# Define the namespaces (adjust ns0 to match your XML)
print(raw_xml.nsmap)

ns = {
    'ns0': 'http://earth.google.com/kml/2.0'  # Adjust if necessary
}

# Initialize a list for coordinates
coords = []

# Loop through the folders and placemarks to extract coordinates
for folder in list(trails_folder.features()):
    for placemark in list(folder.features()):
        if placemark.name == "Path":
            raw_xml = placemark.etree_element()

            # Extract the coordinates from the ns0:coordinates element
            coordinates_element = raw_xml.find('.//ns0:coordinates', namespaces=ns)
            if coordinates_element is not None:
                coords_text = coordinates_element.text.strip()
                # Split the coordinate string into separate coordinates
                coords_list = coords_text.split()

                # Process each coordinate (lon, lat, alt)
                for coord in coords_list:
                    lon, lat, alt = map(float, coord.split(','))
                    coords.append((lat, lon, alt))  # Store as (lat, lon, alt)

# ================================================================================
# #Now we will create the GPX structure
# ================================================================================
import gpxpy
import gpxpy.gpx
# Initialize a GPX object
gpx = gpxpy.gpx.GPX()

# Create a track and a segment
track = gpxpy.gpx.GPXTrack()
segment = gpxpy.gpx.GPXTrackSegment()

# Add coordinates to the track segment
for lat, lon, alt in coords:
    segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lon, elevation=alt))

# Add the segment to the track
track.segments.append(segment)

# Add the track to the GPX object
gpx.tracks.append(track)

# Specify the path for the output GPX file
gpx_file_path = r'C:\Users\user\Desktop\Camille\Perso\website\japan\track.gpx'

# Write the GPX data to a file
with open(gpx_file_path, 'w') as f:
    f.write(gpx.to_xml())


# ================================================================================
# REPUT YOUR FILE AS A SIMPLE KML WITH ONLY THE WAY
# ================================================================================
import xml.etree.ElementTree as ET

# Define the KML namespaces
ns = {
    'ns0': 'http://www.opengis.net/kml/2.2',
}

# Create the KML structure
kml = ET.Element('{http://www.opengis.net/kml/2.2}kml')
document = ET.SubElement(kml, '{http://www.opengis.net/kml/2.2}Document')

# Create a folder for the Path
folder = ET.SubElement(document, '{http://www.opengis.net/kml/2.2}Folder')
folder_name = ET.SubElement(folder, '{http://www.opengis.net/kml/2.2}name')
folder_name.text = "Shikoku Trail"

# Create a placemark for the Path
placemark = ET.SubElement(folder, '{http://www.opengis.net/kml/2.2}Placemark')
placemark_name = ET.SubElement(placemark, '{http://www.opengis.net/kml/2.2}name')
placemark_name.text = "Path"

# Create a LineString for the track
line_string = ET.SubElement(placemark, '{http://www.opengis.net/kml/2.2}LineString')
coordinates = ET.SubElement(line_string, '{http://www.opengis.net/kml/2.2}coordinates')

# Add default altitude = 0
coords_with_alt = [(lat, lon, 0) for lat, lon in coords]

# Create KML-compatible coordinate string: lon,lat,alt
coords_text = "\n".join([f"{lon},{lat},{alt}" for lat, lon, alt in coords_with_alt])
coordinates.text = coords_text

# Create KML structure
kml_ns = 'http://www.opengis.net/kml/2.2'
nsmap = {None: kml_ns}
kml = etree.Element('kml', nsmap=nsmap)
doc = etree.SubElement(kml, 'Document')

# Add style
style = etree.SubElement(doc, 'Style', id="redLine")
line_style = etree.SubElement(style, 'LineStyle')
color = etree.SubElement(line_style, 'color')
color.text = 'ff0000ff'  # Red, full opacity
width = etree.SubElement(line_style, 'width')
width.text = '3'  # Line width

# Create folder and placemark
folder = etree.SubElement(doc, 'Folder')
folder_name = etree.SubElement(folder, 'name')
folder_name.text = 'Path'
placemark = etree.SubElement(folder, 'Placemark')
pm_name = etree.SubElement(placemark, 'name')
pm_name.text = 'Track'

# Create LineString
linestring = etree.SubElement(placemark, 'LineString')
tessellate = etree.SubElement(linestring, 'tessellate')
tessellate.text = '1'
coordinates = etree.SubElement(linestring, 'coordinates')
coordinates.text = 'your_coordinates_here'  # Replace with your coordinates

# Add styleUrl to Placemark
style_url = etree.SubElement(placemark, 'styleUrl')
style_url.text = '#redLine'

# Serialize to KML string
kml_string = etree.tostring(kml, pretty_print=True, xml_declaration=True, encoding='UTF-8')


# Save to file
file_path = r'C:\Users\user\Desktop\Camille\Perso\website\japan\Shikoku_track.kml'
with open(file_path, 'wb') as f:
    f.write(kml_string)

print("✅ KML successfully written.")

# ================================================================================
# NOW MAKE THE ANIMATION
# ================================================================================
import gpxpy
from datetime import datetime, timedelta
import folium
from folium.plugins import TimestampedGeoJson

# Load GPX file
with open(r"C:\Users\user\Desktop\Camille\Perso\website\japan\shikoku_track.gpx", 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)

# Extract and cut at point 15052
coords = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            coords.append((point.latitude, point.longitude))
coords = coords[:15052]

# Define start time
start_time = datetime(2023, 1, 1, 0, 0, 0)

# Create timestamps
timestamps = [(start_time + timedelta(seconds=i)).isoformat() + "Z" for i in range(len(coords))]

# Create animated trail line only
features = [{
    "type": "Feature",
    "geometry": {
        "type": "LineString",
        "coordinates": [[lon, lat] for lat, lon in coords]
    },
    "properties": {
        "times": timestamps,
        "style": {"color": "#FF4500", "weight": 3}
    }
}]

# Create map with satellite tiles
m = folium.Map(
    location=coords[0],
    zoom_start=8,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri Satellite"
)

# Add animated trail line only (no icon)
TimestampedGeoJson(
    {"type": "FeatureCollection", "features": features},
    period="PT1M",           # 1-second intervals
    transition_time=50,     # Smooth transition
    auto_play=True,
    loop=False,
    add_last_point=False,
    max_speed=10,
    date_options="YYYY/MM/DD HH:mm:ss"
).add_to(m)

# Save to file
m.save(r"C:\Users\user\Desktop\Camille\Perso\website\japan\shikoku_track_ref.html")
print("✅ Clean map with animated trail saved!")
