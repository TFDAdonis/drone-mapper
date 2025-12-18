import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime
from PIL import Image
import io
import base64
import os
import json
import uuid

# Page configuration
st.set_page_config(
    page_title="Drone Media Map",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Directories
UPLOAD_DIR = "uploads"
DATA_FILE = "media_data.json"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file types
ALLOWED_IMAGE_TYPES = ["jpg", "jpeg", "png", "gif", "bmp", "webp"]
ALLOWED_VIDEO_TYPES = ["mp4", "mov", "avi", "mkv", "webm", "m4v"]

def load_media_data():
    """Load media data from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return get_sample_data()
    return get_sample_data()

def save_media_data(data):
    """Save media data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def save_uploaded_file(uploaded_file):
    """Save uploaded file and return path"""
    ext = uploaded_file.name.split('.')[-1].lower()
    filename = f"{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
    return filepath

def get_file_type(filename):
    """Determine if file is image or video based on extension"""
    ext = filename.split('.')[-1].lower()
    if ext in ALLOWED_IMAGE_TYPES:
        return 'image'
    elif ext in ALLOWED_VIDEO_TYPES:
        return 'video'
    return None

def get_image_base64(filepath):
    """Convert image to base64 for embedding in HTML"""
    try:
        if filepath and os.path.exists(filepath):
            with Image.open(filepath) as img:
                img.thumbnail((200, 200))
                buffer = io.BytesIO()
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(buffer, format='JPEG', quality=85)
                return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        print(f"Error converting image: {e}")
    return None

def validate_file(file):
    """Validate uploaded file"""
    filename = file.name
    file_type = get_file_type(filename)
    
    if file_type is None:
        return False, "File type not supported. Please upload images or videos only."
    
    max_size = 200 * 1024 * 1024  # 200MB
    if file.size > max_size:
        return False, f"File too large. Maximum size is 200MB. Your file is {file.size/(1024*1024):.1f}MB."
    
    return True, file_type

def get_sample_data():
    """Return sample drone media data"""
    return [
        {
            'id': 1, 'type': 'image', 'title': 'Coastal Cliff Aerial',
            'lat': 34.0195, 'lon': -118.4912, 'timestamp': '2024-12-01 14:32:00',
            'altitude': 120, 'description': 'Stunning aerial view of coastal cliffs at sunset',
            'filepath': None
        },
        {
            'id': 2, 'type': 'video', 'title': 'Downtown Flyover',
            'lat': 34.0522, 'lon': -118.2437, 'timestamp': '2024-12-03 10:15:00',
            'altitude': 200, 'description': 'Cinematic drone flyover of downtown Los Angeles',
            'filepath': None
        }
    ]

# Initialize session state
if 'media_data' not in st.session_state:
    st.session_state.media_data = load_media_data()
    
if 'viewing_story' not in st.session_state:
    st.session_state.viewing_story = None
    
if 'current_story_index' not in st.session_state:
    st.session_state.current_story_index = 0

if 'show_upload_form' not in st.session_state:
    st.session_state.show_upload_form = False

if 'upload_success' not in st.session_state:
    st.session_state.upload_success = None

if 'map_click' not in st.session_state:
    st.session_state.map_click = None

# Custom CSS
st.markdown("""
<style>
    .story-card {
        background: white;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .story-card:hover {
        border-color: #FFFC00;
        transform: translateY(-2px);
    }
    
    .upload-form {
        background: white;
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 2px solid #FFFC00;
    }
    
    .click-marker {
        background: linear-gradient(135deg, #FFFC00, #FF6B6B);
        color: black;
        padding: 10px 20px;
        border-radius: 15px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .story-viewer-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.95);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .story-viewer-content {
        background: #000;
        border-radius: 20px;
        overflow: hidden;
        width: 90%;
        max-width: 800px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }
    
    .marker-preview {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px;
        background: #f0f8ff;
        border-radius: 10px;
        margin: 5px 0;
        cursor: pointer;
    }
    
    .marker-preview:hover {
        background: #e6f7ff;
    }
</style>
""", unsafe_allow_html=True)

def create_story_marker(item):
    """Create Snapchat-style story marker"""
    filepath = item.get('filepath')
    file_type = item.get('type')
    
    if filepath and os.path.exists(filepath) and file_type == 'image':
        img_base64 = get_image_base64(filepath)
        if img_base64:
            html = f'''
            <div style="
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #00C853 0%, #69F0AE 100%);
                padding: 3px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            ">
                <div style="
                    width: 100%;
                    height: 100%;
                    border-radius: 50%;
                    background-image: url('data:image/jpeg;base64,{img_base64}');
                    background-size: cover;
                    background-position: center;
                    border: 2px solid white;
                "></div>
            </div>
            '''
            return folium.DivIcon(html=html, icon_size=(60, 60), icon_anchor=(30, 30))
    
    # Default markers
    if item['type'] == 'video':
        html = f'''
        <div style="
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #FF6D00 0%, #FFAB40 100%);
            padding: 3px;
            box-shadow: 0 4px 15px rgba(255, 109, 0, 0.5);
        ">
            <div style="
                width: 100%;
                height: 100%;
                border-radius: 50%;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                border: 2px solid white;
            ">
                <div style="
                    width: 0;
                    height: 0;
                    border-left: 14px solid white;
                    border-top: 9px solid transparent;
                    border-bottom: 9px solid transparent;
                    margin-left: 4px;
                "></div>
            </div>
        </div>
        '''
        return folium.DivIcon(html=html, icon_size=(60, 60), icon_anchor=(30, 30))
    else:
        html = f'''
        <div style="
            width: 52px;
            height: 52px;
            border-radius: 50%;
            background: linear-gradient(135deg, #00C853 0%, #69F0AE 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0, 200, 83, 0.4);
            border: 3px solid white;
        ">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                <circle cx="12" cy="12" r="3"/>
                <path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
            </svg>
        </div>
        '''
        return folium.DivIcon(html=html, icon_size=(60, 60), icon_anchor=(30, 30))

def create_map():
    """Create the map with all markers"""
    if st.session_state.media_data:
        center_lat = sum(item['lat'] for item in st.session_state.media_data) / len(st.session_state.media_data)
        center_lon = sum(item['lon'] for item in st.session_state.media_data) / len(st.session_state.media_data)
    else:
        center_lat, center_lon = 34.0522, -118.2437
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles=None,
        control_scale=False
    )
    
    # Add tile layers
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
        attr='OpenStreetMap & CARTO',
        name='Map',
        max_zoom=19
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        max_zoom=19
    ).add_to(m)
    
    # Add all story markers
    for item in st.session_state.media_data:
        icon = create_story_marker(item)
        
        folium.Marker(
            location=[item['lat'], item['lon']],
            icon=icon,
            tooltip=f"📌 {item['title']}",
            popup=folium.Popup(f"<b>{item['title']}</b><br>{item['type'].upper()} • {item['altitude']}m", max_width=200)
        ).add_to(m)
    
    # Add a marker for the user's click if exists
    if st.session_state.map_click:
        folium.Marker(
            location=[st.session_state.map_click['lat'], st.session_state.map_click['lng']],
            icon=folium.Icon(color='red', icon='info-sign'),
            popup="You clicked here!"
        ).add_to(m)
    
    folium.LayerControl(position='topright').add_to(m)
    return m

# Sidebar for story selection
with st.sidebar:
    st.title("📱 Stories")
    
    # Search/filter
    search_term = st.text_input("Search stories", "")
    
    # Filter stories based on search
    filtered_stories = st.session_state.media_data
    if search_term:
        filtered_stories = [
            story for story in st.session_state.media_data 
            if search_term.lower() in story['title'].lower() 
            or search_term.lower() in story['description'].lower()
        ]
    
    # Story type filter
    type_filter = st.selectbox(
        "Filter by type",
        ["All", "Images", "Videos"]
    )
    
    if type_filter == "Images":
        filtered_stories = [story for story in filtered_stories if story['type'] == 'image']
    elif type_filter == "Videos":
        filtered_stories = [story for story in filtered_stories if story['type'] == 'video']
    
    st.markdown(f"**Found {len(filtered_stories)} stories**")
    
    # Display stories in sidebar
    for idx, story in enumerate(filtered_stories):
        col1, col2 = st.columns([1, 4])
        
        with col1:
            icon = "📷" if story['type'] == 'image' else "🎬"
            st.markdown(f"<div style='font-size: 24px; text-align: center;'>{icon}</div>", unsafe_allow_html=True)
        
        with col2:
            if st.button(story['title'][:20] + ("..." if len(story['title']) > 20 else ""), 
                        key=f"sidebar_{story['id']}",
                        help=f"Click to view: {story['title']}",
                        use_container_width=True):
                # Find the actual index in the full media_data
                for full_idx, full_story in enumerate(st.session_state.media_data):
                    if full_story['id'] == story['id']:
                        st.session_state.viewing_story = story['id']
                        st.session_state.current_story_index = full_idx
                        st.rerun()
                        break
        
        st.markdown(f"""
        <div style="font-size: 12px; color: #666; padding: 0 10px;">
            📍 {story['lat']:.3f}, {story['lon']:.3f}<br>
            ⬆️ {story['altitude']}m • {story['timestamp'][:10]}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")

# Main App
st.title("📡 Drone Media Map")
st.markdown("Click anywhere on the map or select a story from the sidebar")

# Create two columns for the main layout
col1, col2 = st.columns([3, 1])

with col1:
    # Create and display the map
    m = create_map()
    map_data = st_folium(m, width=None, height=600, key="main_map")
    
    # Check if user clicked on the map
    if map_data and 'last_clicked' in map_data and map_data['last_clicked']:
        st.session_state.map_click = map_data['last_clicked']
        st.rerun()

with col2:
    st.markdown("### 📊 Stats")
    total = len(st.session_state.media_data)
    images = sum(1 for x in st.session_state.media_data if x['type'] == 'image')
    videos = sum(1 for x in st.session_state.media_data if x['type'] == 'video')
    st.metric("Total Stories", total)
    st.metric("Photos", images)
    st.metric("Videos", videos)
    
    st.markdown("---")
    st.markdown("### 📍 Legend")
    st.markdown("""
    <div style="margin: 10px 0;">
        <div style="display: flex; align-items: center; gap: 10px; margin: 5px 0;">
            <div style="width: 12px; height: 12px; border-radius: 50%; background: linear-gradient(135deg, #00C853 0%, #69F0AE 100%);"></div>
            <span>Photo Story</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px; margin: 5px 0;">
            <div style="width: 12px; height: 12px; border-radius: 50%; background: linear-gradient(135deg, #FF6D00 0%, #FFAB40 100%);"></div>
            <span>Video Story</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px; margin: 5px 0;">
            <div style="width: 12px; height: 12px; border-radius: 50%; background: red;"></div>
            <span>Your Click</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Show clicked location and nearby stories
if st.session_state.map_click:
    st.markdown("---")
    st.markdown(f"""
    <div class="click-marker">
        📍 You clicked at: {st.session_state.map_click['lat']:.4f}, {st.session_state.map_click['lng']:.4f}
    </div>
    """, unsafe_allow_html=True)
    
    # Find stories near the clicked location
    clicked_lat = st.session_state.map_click['lat']
    clicked_lon = st.session_state.map_click['lng']
    
    nearby_stories = []
    for idx, story in enumerate(st.session_state.media_data):
        distance = ((story['lat'] - clicked_lat) ** 2 + (story['lon'] - clicked_lon) ** 2) ** 0.5
        if distance < 0.1:  # Within ~11km
            nearby_stories.append((idx, story, distance))
    
    if nearby_stories:
        st.subheader(f"📱 Nearby Stories ({len(nearby_stories)} found)")
        
        # Sort by distance
        nearby_stories.sort(key=lambda x: x[2])
        
        for idx, story, distance in nearby_stories:
            col_n1, col_n2, col_n3 = st.columns([3, 1, 1])
            
            with col_n1:
                st.markdown(f"""
                <div style="padding: 10px; background: #f8f9fa; border-radius: 10px; margin: 5px 0;">
                    <div style="font-weight: bold;">{story['title']}</div>
                    <div style="font-size: 12px; color: #666;">
                        📍 {distance*111:.1f}km away • {story['type'].upper()} • {story['altitude']}m
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_n2:
                if st.button("👁️ View", key=f"view_nearby_{story['id']}"):
                    st.session_state.viewing_story = story['id']
                    st.session_state.current_story_index = idx
                    st.rerun()
            
            with col_n3:
                if st.button("📍 Show", key=f"show_nearby_{story['id']}"):
                    # Center map on this story
                    st.session_state.map_click = {'lat': story['lat'], 'lng': story['lon']}
                    st.rerun()
    else:
        st.info("No stories found near your click. Try clicking closer to a marker!")

# Upload Section
st.markdown("---")
st.markdown("## 📤 Upload Your Drone Media")

if st.button("➕ Upload New Media", key="toggle_upload", use_container_width=True):
    st.session_state.show_upload_form = not st.session_state.show_upload_form
    st.rerun()

if st.session_state.show_upload_form:
    st.markdown('<div class="upload-form">', unsafe_allow_html=True)
    st.markdown("### Upload Details")
    
    uploaded_file = st.file_uploader(
        "Choose drone media file",
        type=ALLOWED_IMAGE_TYPES + ALLOWED_VIDEO_TYPES,
        help="Upload photos or videos from your drone"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Title *", placeholder="Enter a descriptive title")
        
        st.markdown("**Location**")
        lat = st.number_input("Latitude *", value=34.0522, format="%.6f", step=0.0001)
        lon = st.number_input("Longitude *", value=-118.2437, format="%.6f", step=0.0001)
    
    with col2:
        description = st.text_area("Description *", placeholder="Describe your drone footage...", height=100)
        
        timestamp = st.date_input("Date", value=datetime.now())
        
        altitude = st.number_input("Altitude (meters) *", min_value=0.0, value=100.0, step=10.0)
    
    # Submit button
    if st.button("🚀 Upload to Map", key="submit_upload", use_container_width=True, type="primary"):
        if uploaded_file and title and description:
            is_valid, result = validate_file(uploaded_file)
            
            if not is_valid:
                st.error(result)
            else:
                file_type = result
                filepath = save_uploaded_file(uploaded_file)
                
                # Generate new ID
                if st.session_state.media_data:
                    new_id = max(item['id'] for item in st.session_state.media_data) + 1
                else:
                    new_id = 1
                
                # Create new media entry
                new_media = {
                    'id': new_id,
                    'type': file_type,
                    'title': title,
                    'lat': float(lat),
                    'lon': float(lon),
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'altitude': float(altitude),
                    'description': description,
                    'filepath': filepath
                }
                
                # Add to media data
                st.session_state.media_data.append(new_media)
                save_media_data(st.session_state.media_data)
                
                st.success(f"✅ {file_type.title()} uploaded successfully!")
                st.session_state.show_upload_form = False
                st.session_state.upload_success = True
                st.rerun()
        else:
            st.error("Please fill all required fields (*)")
    
    st.markdown('</div>', unsafe_allow_html=True)

# STORY VIEWER MODAL
if st.session_state.viewing_story is not None:
    current_story = st.session_state.media_data[st.session_state.current_story_index]
    
    # Create overlay
    st.markdown('<div class="story-viewer-overlay">', unsafe_allow_html=True)
    
    with st.container():
        # Main viewer content
        st.markdown('<div class="story-viewer-content">', unsafe_allow_html=True)
        
        # Header
        col_header1, col_header2, col_header3 = st.columns([1, 8, 1])
        with col_header2:
            st.markdown(f"""
            <div style="padding: 20px; background: rgba(0,0,0,0.9); display: flex; align-items: center; gap: 15px;">
                <div style="
                    width: 50px;
                    height: 50px;
                    border-radius: 50%;
                    background: linear-gradient(45deg, #FFFC00, #FF6B6B);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                    color: white;
                ">
                    {'🎬' if current_story['type'] == 'video' else '📷'}
                </div>
                <div>
                    <div style="color: white; font-weight: 600; font-size: 22px;">{current_story['title']}</div>
                    <div style="color: rgba(255,255,255,0.7); font-size: 14px;">
                        📅 {current_story['timestamp']} • 📍 {current_story['lat']:.4f}, {current_story['lon']:.4f}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Media content
        if current_story.get('filepath') and os.path.exists(current_story['filepath']):
            if current_story['type'] == 'image':
                try:
                    image = Image.open(current_story['filepath'])
                    st.image(image, use_container_width=True)
                except:
                    st.markdown(f"""
                    <div style="height: 400px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; background: #000;">
                        <div style="font-size: 64px; margin-bottom: 20px;">📷</div>
                        <div style="font-size: 24px;">Image Preview</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                try:
                    with open(current_story['filepath'], 'rb') as f:
                        video_bytes = f.read()
                    st.video(video_bytes)
                except:
                    st.markdown(f"""
                    <div style="height: 400px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; background: #000;">
                        <div style="font-size: 64px; margin-bottom: 20px;">🎬</div>
                        <div style="font-size: 24px;">Video Preview</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            icon = '🎬' if current_story['type'] == 'video' else '📷'
            st.markdown(f"""
            <div style="height: 400px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; background: #000;">
                <div style="font-size: 64px; margin-bottom: 20px;">{icon}</div>
                <div style="font-size: 24px; margin-bottom: 10px;">{current_story['type'].title()} Story</div>
                <div style="font-size: 16px; opacity: 0.8; text-align: center; padding: 0 20px;">{current_story['description']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Footer with description and metadata
        st.markdown(f"""
        <div style="padding: 20px; background: rgba(0,0,0,0.9);">
            <div style="color: white; font-size: 16px; margin-bottom: 15px; line-height: 1.6;">
                {current_story['description']}
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; color: rgba(255,255,255,0.7); font-size: 14px;">
                <div>
                    <div style="font-weight: 600; margin-bottom: 5px; color: #FFFC00;">📍 Location Coordinates</div>
                    <div style="font-family: monospace; font-size: 13px;">Lat: {current_story['lat']:.6f}<br>Lon: {current_story['lon']:.6f}</div>
                </div>
                <div>
                    <div style="font-weight: 600; margin-bottom: 5px; color: #FFFC00;">📊 Flight Details</div>
                    <div>Altitude: {current_story['altitude']}m<br>Type: {current_story['type'].upper()}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close story-viewer-content
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close overlay
    
    # Navigation buttons (outside the overlay so they're clickable)
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        if st.button("← Previous Story", key="prev_story", use_container_width=True):
            prev_index = (st.session_state.current_story_index - 1) % len(st.session_state.media_data)
            st.session_state.current_story_index = prev_index
            st.rerun()
    
    with col_nav2:
        if st.button("✕ Close Viewer", key="close_story", type="primary", use_container_width=True):
            st.session_state.viewing_story = None
            st.rerun()
    
    with col_nav3:
        if st.button("Next Story →", key="next_story", use_container_width=True):
            next_index = (st.session_state.current_story_index + 1) % len(st.session_state.media_data)
            st.session_state.current_story_index = next_index
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px; padding: 20px 0;">
    🚁 Drone Media Map • Click on the map to find stories or upload your own drone footage!
</div>
""", unsafe_allow_html=True)
