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
    page_title="Drone Media Mapping",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Directories
UPLOAD_DIR = "uploads"
DATA_FILE = "media_data.json"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

def get_image_base64(filepath):
    """Convert image to base64 for embedding in HTML"""
    try:
        if filepath and os.path.exists(filepath):
            with Image.open(filepath) as img:
                # Create thumbnail
                img.thumbnail((300, 300))
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                return base64.b64encode(buffer.getvalue()).decode()
    except:
        pass
    return None

def get_video_preview_base64(filepath):
    """Create a preview image for video"""
    try:
        if filepath and os.path.exists(filepath):
            # Create a simple video thumbnail
            img = Image.new('RGB', (300, 200), color='#1a1a2e')
            return get_image_base64_from_pil(img)
    except:
        pass
    return None

def get_image_base64_from_pil(img):
    """Convert PIL image to base64"""
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return base64.b64encode(buffer.getvalue()).decode()

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
        },
        {
            'id': 3, 'type': 'image', 'title': 'Mountain Peak Survey',
            'lat': 34.2234, 'lon': -118.0602, 'timestamp': '2024-12-05 08:45:00',
            'altitude': 350, 'description': 'High altitude survey of mountain terrain',
            'filepath': None
        },
        {
            'id': 4, 'type': 'video', 'title': 'Beach Sunset Timelapse',
            'lat': 33.9850, 'lon': -118.4695, 'timestamp': '2024-12-07 17:20:00',
            'altitude': 80, 'description': 'Beautiful sunset timelapse over the beach',
            'filepath': None
        },
        {
            'id': 5, 'type': 'image', 'title': 'Urban Park Mapping',
            'lat': 34.0736, 'lon': -118.3951, 'timestamp': '2024-12-08 12:00:00',
            'altitude': 100, 'description': 'Detailed mapping of urban park area',
            'filepath': None
        },
        {
            'id': 6, 'type': 'video', 'title': 'Harbor Overview',
            'lat': 33.7361, 'lon': -118.2922, 'timestamp': '2024-12-09 09:30:00',
            'altitude': 150, 'description': 'Aerial overview of Long Beach Harbor',
            'filepath': None
        }
    ]

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(180deg, #FFFDE4 0%, #F5F5F5 100%);
    }
    
    .main-header {
        font-weight: 700;
        font-size: 28px;
        color: #1a1a2e;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .header-container {
        padding: 12px 0;
        margin-bottom: 16px;
    }
    
    .snapchat-yellow {
        background: #FFFC00;
        color: black;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #f0f0f0;
        padding: 6px;
        border-radius: 25px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 13px;
        padding: 10px 20px;
        border-radius: 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FFFC00 !important;
        color: black !important;
    }
    
    .coord-display {
        font-family: monospace;
        font-size: 13px;
        background-color: rgba(0,0,0,0.05);
        padding: 8px 12px;
        border-radius: 12px;
        color: #333;
    }
    
    .media-card {
        background: white;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        margin-bottom: 16px;
    }
    
    .legend-dot {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        border: 2px solid white;
    }
    
    .legend-dot.image { background: linear-gradient(135deg, #00C853 0%, #69F0AE 100%); }
    .legend-dot.video { background: linear-gradient(135deg, #FF6D00 0%, #FFAB40 100%); }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stButton > button {
        font-weight: 600;
        border-radius: 25px;
        padding: 10px 28px;
    }
    
    .upload-instruction {
        background: linear-gradient(135deg, #FFFC00 0%, #FFE082 100%);
        color: black;
        padding: 16px 24px;
        border-radius: 16px;
        text-align: center;
        font-weight: 600;
        margin-bottom: 16px;
    }
    
    .location-selected {
        background: linear-gradient(135deg, #00C853 0%, #69F0AE 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: 600;
        margin: 10px 0;
    }
    
    .story-viewer-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.95);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .story-container {
        width: 90%;
        max-width: 400px;
        background: #000;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        animation: slideUp 0.3s ease;
    }
    
    @keyframes slideUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .story-header {
        padding: 16px;
        background: linear-gradient(180deg, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.5) 100%);
        display: flex;
        align-items: center;
        gap: 12px;
        position: relative;
    }
    
    .story-progress-bar {
        height: 3px;
        background: rgba(255,255,255,0.3);
        border-radius: 3px;
        position: absolute;
        top: 8px;
        left: 16px;
        right: 16px;
    }
    
    .story-progress {
        height: 100%;
        background: #FFFC00;
        border-radius: 3px;
        width: 100%;
        animation: progress 10s linear;
    }
    
    @keyframes progress {
        from { width: 0%; }
        to { width: 100%; }
    }
    
    .story-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #FFFC00 0%, #FF6B6B 50%, #4ECDC4 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        border: 2px solid white;
    }
    
    .story-content {
        width: 100%;
        max-height: 70vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #000;
    }
    
    .story-media {
        width: 100%;
        height: auto;
        max-height: 70vh;
        object-fit: contain;
    }
    
    .story-footer {
        padding: 16px;
        background: #111;
        color: white;
    }
    
    .close-button {
        position: absolute;
        top: 20px;
        right: 20px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: rgba(255,255,255,0.1);
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        transition: all 0.2s;
    }
    
    .close-button:hover {
        background: rgba(255,255,255,0.2);
        transform: scale(1.1);
    }
    
    .story-navigation {
        position: absolute;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: space-between;
        pointer-events: none;
    }
    
    .nav-button {
        width: 60px;
        height: 100%;
        background: transparent;
        border: none;
        color: white;
        font-size: 32px;
        cursor: pointer;
        pointer-events: auto;
        opacity: 0;
        transition: opacity 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .story-container:hover .nav-button {
        opacity: 0.7;
    }
    
    .nav-button:hover {
        opacity: 1 !important;
        background: rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'media_data' not in st.session_state:
    st.session_state.media_data = load_media_data()
    
if 'selected_lat' not in st.session_state:
    st.session_state.selected_lat = None
    
if 'selected_lon' not in st.session_state:
    st.session_state.selected_lon = None

if 'last_click_lat' not in st.session_state:
    st.session_state.last_click_lat = None
    
if 'last_click_lon' not in st.session_state:
    st.session_state.last_click_lon = None

# NEW: Session state for story viewer
if 'viewing_story' not in st.session_state:
    st.session_state.viewing_story = False
    
if 'current_story_index' not in st.session_state:
    st.session_state.current_story_index = 0
    
if 'selected_story_id' not in st.session_state:
    st.session_state.selected_story_id = None

def open_story_viewer(story_id):
    """Open the story viewer for a specific story"""
    st.session_state.viewing_story = True
    st.session_state.selected_story_id = story_id
    
    # Find the index of the story
    for idx, item in enumerate(st.session_state.media_data):
        if item['id'] == story_id:
            st.session_state.current_story_index = idx
            break

def close_story_viewer():
    """Close the story viewer"""
    st.session_state.viewing_story = False
    st.session_state.selected_story_id = None

def navigate_story(direction):
    """Navigate between stories"""
    total = len(st.session_state.media_data)
    new_index = (st.session_state.current_story_index + direction) % total
    st.session_state.current_story_index = new_index
    st.session_state.selected_story_id = st.session_state.media_data[new_index]['id']

def create_story_marker(item):
    """Create Snapchat-style story marker with actual image preview"""
    filepath = item.get('filepath')
    has_image = filepath and os.path.exists(filepath) and item['type'] == 'image'
    
    if has_image:
        # Create marker with actual image thumbnail
        img_base64 = get_image_base64(filepath)
        if img_base64:
            html = f'''
            <div onclick="window.parent.document.dispatchEvent(new CustomEvent('openStory', {{detail: {{id: {item['id']}}}}}));" 
                 style="
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #FFFC00 0%, #FF6B6B 50%, #4ECDC4 100%);
                padding: 3px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                cursor: pointer;
                transition: transform 0.3s;
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
    
    # Default markers for videos or items without images
    gradient = 'linear-gradient(135deg, #FF6D00 0%, #FFAB40 100%)' if item['type'] == 'video' else 'linear-gradient(135deg, #00C853 0%, #69F0AE 100%)'
    icon_html = '''
    <div style="
        width: 0;
        height: 0;
        border-left: 14px solid white;
        border-top: 9px solid transparent;
        border-bottom: 9px solid transparent;
        margin-left: 4px;
    "></div>
    ''' if item['type'] == 'video' else '''
    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
        <circle cx="12" cy="12" r="3"/>
        <path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
    </svg>
    '''
    
    html = f'''
    <div onclick="window.parent.document.dispatchEvent(new CustomEvent('openStory', {{detail: {{id: {item['id']}}}}}));"
         style="
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: {gradient};
        padding: 3px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        cursor: pointer;
        transition: transform 0.3s;
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
            {icon_html}
        </div>
    </div>
    '''
    return folium.DivIcon(html=html, icon_size=(60, 60), icon_anchor=(30, 30))

def create_map():
    """Create the map"""
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
    
    for item in st.session_state.media_data:
        icon = create_story_marker(item)
        folium.Marker(
            location=[item['lat'], item['lon']],
            icon=icon,
            tooltip=f"👆 {item['title']}"
        ).add_to(m)
    
    folium.LayerControl(position='topright').add_to(m)
    return m

# JavaScript for handling story clicks
story_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Listen for openStory events from iframe
    window.addEventListener('message', function(event) {
        if (event.data.type === 'openStory') {
            window.parent.document.dispatchEvent(new CustomEvent('openStory', {detail: event.data.detail}));
        }
    });
    
    // Dispatch event when story is clicked
    document.addEventListener('openStory', function(event) {
        console.log('Story clicked:', event.detail);
        // This will be handled by Streamlit's session state
    });
});
</script>
"""

# Inject JavaScript
st.components.v1.html(story_js, height=0)

# Story Viewer Component
if st.session_state.viewing_story:
    current_item = st.session_state.media_data[st.session_state.current_story_index]
    filepath = current_item.get('filepath')
    
    st.markdown("""
    <div class="story-viewer-overlay">
        <div class="story-container">
            <div class="story-header">
                <div class="story-progress-bar">
                    <div class="story-progress"></div>
                </div>
                <div class="story-avatar">
                    {icon}
                </div>
                <div>
                    <div style="color: white; font-weight: 600;">{title}</div>
                    <div style="color: rgba(255,255,255,0.7); font-size: 12px;">{timestamp} • {altitude}m</div>
                </div>
            </div>
            
            <div class="story-content">
                {media_content}
            </div>
            
            <div class="story-footer">
                <div style="font-size: 14px; margin-bottom: 8px;">{description}</div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; color: rgba(255,255,255,0.6);">
                    <span>📍 {lat:.4f}, {lon:.4f}</span>
                    <span>🕒 {time}</span>
                </div>
            </div>
            
            <div class="story-navigation">
                <button class="nav-button" onclick="window.parent.document.dispatchEvent(new CustomEvent('navigateStory', {{detail: {{direction: -1}}}}));">‹</button>
                <button class="nav-button" onclick="window.parent.document.dispatchEvent(new CustomEvent('navigateStory', {{detail: {{direction: 1}}}}));">›</button>
            </div>
        </div>
        
        <button class="close-button" onclick="window.parent.document.dispatchEvent(new CustomEvent('closeStory'));">×</button>
    </div>
    """.format(
        icon='🎬' if current_item['type'] == 'video' else '📷',
        title=current_item['title'],
        timestamp=current_item['timestamp'][:10],
        altitude=current_item['altitude'],
        lat=current_item['lat'],
        lon=current_item['lon'],
        description=current_item['description'],
        time=current_item['timestamp'][11:],
        media_content=f"""
            <video class="story-media" controls autoplay>
                <source src="{filepath if filepath and os.path.exists(filepath) else ''}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            """ if current_item['type'] == 'video' and filepath and os.path.exists(filepath) else 
            f"""
            <img class="story-media" src="data:image/jpeg;base64,{get_image_base64(filepath) if filepath and os.path.exists(filepath) else ''}" alt="{current_item['title']}">
            """ if current_item['type'] == 'image' and filepath and os.path.exists(filepath) else 
            f"""
            <div style="width: 100%; height: 300px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; font-size: 24px;">
                {'🎬 Video' if current_item['type'] == 'video' else '📷 Image'}
            </div>
            """
    ), unsafe_allow_html=True)
    
    # Handle navigation and close events
    if st.session_state.get('navigate_story'):
        direction = st.session_state.navigate_story
        navigate_story(direction)
        st.session_state.navigate_story = None
        st.rerun()
    
    if st.session_state.get('close_story'):
        close_story_viewer()
        st.session_state.close_story = None
        st.rerun()

# JavaScript to handle events
event_js = """
<script>
// Listen for events from the iframe
document.addEventListener('openStory', function(event) {
    const data = event.detail;
    // Send to Streamlit via custom component
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        value: {action: 'openStory', id: data.id}
    }, '*');
});

document.addEventListener('navigateStory', function(event) {
    const direction = event.detail.direction;
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        value: {action: 'navigateStory', direction: direction}
    }, '*');
});

document.addEventListener('closeStory', function() {
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        value: {action: 'closeStory'}
    }, '*');
});
</script>
"""

# Create a component to handle JavaScript events
def create_event_handler():
    """Create a component to handle JavaScript events"""
    import streamlit.components.v1 as components
    
    # This component will listen for JavaScript events
    component_value = components.html(
        event_js,
        height=0,
        width=0,
    )
    
    return component_value

# Header
st.markdown("""
<div class="header-container">
    <h1 class="main-header">
        👻 Drone Media Map
        <span class="snapchat-yellow">SNAP STYLE</span>
    </h1>
</div>
""", unsafe_allow_html=True)

# Main tabs
tab1, tab2, tab3 = st.tabs(["🗺️ Snap Map", "📤 Add to Map", "📱 Stories"])

with tab1:
    col1, col2 = st.columns([5, 1])
    
    with col1:
        m = create_map()
        
        # Create the map with a callback
        map_data = st_folium(
            m, 
            width=None, 
            height=650, 
            key="main_map",
            returned_objects=["last_object_clicked"]
        )
        
        # Handle map clicks for stories
        if map_data and map_data.get("last_object_clicked"):
            clicked_data = map_data["last_object_clicked"]
            if clicked_data:
                # Extract the story ID from the clicked marker
                # This is a simplified approach - in a real app, you'd need to
                # better track which marker was clicked
                for item in st.session_state.media_data:
                    if (abs(item['lat'] - clicked_data['lat']) < 0.001 and 
                        abs(item['lon'] - clicked_data['lng']) < 0.001):
                        open_story_viewer(item['id'])
                        st.rerun()
                        break
        
        # Simple button-based story viewer as fallback
        st.markdown("---")
        st.markdown("### 📸 Quick Story Viewer")
        
        cols = st.columns(min(6, len(st.session_state.media_data)))
        for idx, item in enumerate(st.session_state.media_data[:6]):
            with cols[idx % len(cols)]:
                filepath = item.get('filepath')
                if filepath and os.path.exists(filepath) and item['type'] == 'image':
                    img_b64 = get_image_base64(filepath)
                    if img_b64:
                        st.markdown(f"""
                        <div style="text-align: center; cursor: pointer;" 
                             onclick="window.dispatchEvent(new CustomEvent('openStory', {{detail: {{id: {item['id']}}}}}));">
                            <div style="
                                width: 64px;
                                height: 64px;
                                border-radius: 50%;
                                background: linear-gradient(135deg, #FFFC00 0%, #FF6B6B 50%, #4ECDC4 100%);
                                padding: 3px;
                                margin: 0 auto 8px;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                            ">
                                <div style="
                                    width: 100%;
                                    height: 100%;
                                    border-radius: 50%;
                                    background-image: url('data:image/jpeg;base64,{img_b64}');
                                    background-size: cover;
                                    background-position: center;
                                    border: 2px solid white;
                                "></div>
                            </div>
                            <div style="font-size: 11px; font-weight: 500; max-width: 70px; overflow: hidden;">
                                {item['title'][:10]}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        continue
                
                gradient = 'linear-gradient(135deg, #FF6D00 0%, #FFAB40 100%)' if item['type'] == 'video' else 'linear-gradient(135deg, #00C853 0%, #69F0AE 100%)'
                icon = '🎬' if item['type'] == 'video' else '📷'
                if st.button(
                    icon,
                    key=f"story_btn_{item['id']}",
                    use_container_width=True,
                    on_click=open_story_viewer,
                    args=(item['id'],)
                ):
                    pass
    
    with col2:
        st.markdown("### 📍 Legend")
        st.markdown("""
        <div style="padding: 8px 0;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                <div class="legend-dot image"></div>
                <span style="font-size: 13px;">Photo</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div class="legend-dot video"></div>
                <span style="font-size: 13px;">Video</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📊 Stats")
        total = len(st.session_state.media_data)
        images = sum(1 for x in st.session_state.media_data if x['type'] == 'image')
        videos = sum(1 for x in st.session_state.media_data if x['type'] == 'video')
        st.metric("Total", total)
        st.metric("Photos", images)
        st.metric("Videos", videos)

with tab2:
    st.markdown("""
    <div class="upload-instruction">
        👆 Click on the map to choose where to place your media, then upload!
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("#### 📍 Step 1: Click to Select Location")
        
        # Create a separate map for upload tab
        upload_map = folium.Map(
            location=[34.0522, -118.2437],
            zoom_start=11,
            control_scale=False
        )
        
        folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
            attr='OpenStreetMap & CARTO',
            name='Map',
            max_zoom=19
        ).add_to(upload_map)
        
        # Show existing items as small dots
        for item in st.session_state.media_data:
            folium.CircleMarker(
                location=[item['lat'], item['lon']],
                radius=5,
                color='#999',
                fill=True,
                fill_color='#ccc',
                fill_opacity=0.5
            ).add_to(upload_map)
        
        # Show selected location
        if st.session_state.selected_lat is not None:
            folium.Marker(
                location=[st.session_state.selected_lat, st.session_state.selected_lon],
                icon=folium.Icon(color='green', icon='plus', prefix='fa')
            ).add_to(upload_map)
        
        map_output = st_folium(
            upload_map, 
            width=None, 
            height=400, 
            key="upload_map",
            returned_objects=["last_clicked"]
        )
        
        if map_output and map_output.get("last_clicked"):
            new_lat = map_output["last_clicked"]["lat"]
            new_lon = map_output["last_clicked"]["lng"]
            if new_lat != st.session_state.last_click_lat or new_lon != st.session_state.last_click_lon:
                st.session_state.selected_lat = new_lat
                st.session_state.selected_lon = new_lon
                st.session_state.last_click_lat = new_lat
                st.session_state.last_click_lon = new_lon
                st.rerun()
        
        if st.session_state.selected_lat is not None:
            st.markdown(f"""
            <div class="location-selected">
                ✅ Location: {st.session_state.selected_lat:.6f}, {st.session_state.selected_lon:.6f}
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 Clear Location"):
                st.session_state.selected_lat = None
                st.session_state.selected_lon = None
                st.session_state.last_click_lat = None
                st.session_state.last_click_lon = None
                st.rerun()
        else:
            st.info("👆 Click on the map to select a location")
    
    with col2:
        st.markdown("#### 📤 Step 2: Upload Your Media")
        
        uploaded_file = st.file_uploader(
            "Drop your photo or video",
            type=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi', 'webm'],
            key="uploader"
        )
        
        if uploaded_file:
            file_type = 'video' if uploaded_file.type.startswith('video') else 'image'
            
            st.markdown(f"**Preview** {'🎬' if file_type == 'video' else '📷'}")
            if file_type == 'image':
                st.image(uploaded_file, use_container_width=True)
            else:
                st.video(uploaded_file)
            
            st.markdown("---")
            st.markdown("#### Step 3: Add Details")
            
            title = st.text_input("Title", placeholder="Name your snap...")
            description = st.text_area("Description", placeholder="What's in this shot?", height=80)
            altitude = st.slider("Altitude (m)", 0, 500, 100)
            
            with st.expander("📐 Manual Coordinates"):
                mcol1, mcol2 = st.columns(2)
                with mcol1:
                    manual_lat = st.number_input("Lat", value=34.0522, format="%.6f")
                with mcol2:
                    manual_lon = st.number_input("Lon", value=-118.2437, format="%.6f")
                if st.button("Use These"):
                    st.session_state.selected_lat = manual_lat
                    st.session_state.selected_lon = manual_lon
                    st.rerun()
            
            has_location = st.session_state.selected_lat is not None
            has_details = bool(title and description)
            can_upload = has_location and has_details
            
            if not has_location:
                st.warning("👆 Select location on map")
            elif not has_details:
                st.warning("📝 Add title and description")
            
            st.markdown("")
            
            if st.button("🚀 Add to Snap Map", type="primary", use_container_width=True, disabled=not can_upload):
                # Save the file
                filepath = save_uploaded_file(uploaded_file)
                
                new_id = max([item['id'] for item in st.session_state.media_data], default=0) + 1
                new_item = {
                    'id': new_id,
                    'type': file_type,
                    'title': title,
                    'lat': st.session_state.selected_lat,
                    'lon': st.session_state.selected_lon,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'altitude': altitude,
                    'description': description,
                    'filepath': filepath
                }
                
                st.session_state.media_data.append(new_item)
                save_media_data(st.session_state.media_data)
                
                st.session_state.selected_lat = None
                st.session_state.selected_lon = None
                st.session_state.last_click_lat = None
                st.session_state.last_click_lon = None
                
                st.success(f"✅ Added '{title}' to the map!")
                st.balloons()
                st.rerun()
        else:
            st.info("📤 Upload a photo or video")

with tab3:
    st.markdown("### 📱 Your Stories")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        filter_type = st.selectbox("Filter", ["All", "Photos", "Videos"], label_visibility="collapsed")
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.media_data = load_media_data()
            st.rerun()
    
    filtered = st.session_state.media_data.copy()
    if filter_type == "Photos":
        filtered = [x for x in filtered if x['type'] == 'image']
    elif filter_type == "Videos":
        filtered = [x for x in filtered if x['type'] == 'video']
    
    filtered.sort(key=lambda x: x['timestamp'], reverse=True)
    
    if filtered:
        # Story circles
        st.markdown("#### Recent")
        story_cols = st.columns(min(len(filtered), 6))
        for idx, item in enumerate(filtered[:6]):
            with story_cols[idx]:
                filepath = item.get('filepath')
                if filepath and os.path.exists(filepath) and item['type'] == 'image':
                    img_b64 = get_image_base64(filepath)
                    if img_b64:
                        if st.button(
                            "",
                            key=f"story_{item['id']}",
                            on_click=open_story_viewer,
                            args=(item['id'],)
                        ):
                            pass
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <div style="
                                width: 64px;
                                height: 64px;
                                border-radius: 50%;
                                background: linear-gradient(135deg, #FFFC00 0%, #FF6B6B 50%, #4ECDC4 100%);
                                padding: 3px;
                                margin: 0 auto 8px;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                            ">
                                <div style="
                                    width: 100%;
                                    height: 100%;
                                    border-radius: 50%;
                                    background-image: url('data:image/jpeg;base64,{img_b64}');
                                    background-size: cover;
                                    background-position: center;
                                    border: 2px solid white;
                                "></div>
                            </div>
                            <div style="font-size: 11px; font-weight: 500; max-width: 70px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                {item['title'][:10]}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        continue
                
                # Fallback for videos or items without images
                gradient = 'linear-gradient(135deg, #00C853 0%, #69F0AE 100%)' if item['type'] == 'image' else 'linear-gradient(135deg, #FF6D00 0%, #FFAB40 100%)'
                icon = '📷' if item['type'] == 'image' else '🎬'
                if st.button(
                    icon,
                    key=f"story_simple_{item['id']}",
                    on_click=open_story_viewer,
                    args=(item['id'],)
                ):
                    pass
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="
                        width: 64px;
                        height: 64px;
                        border-radius: 50%;
                        background: {gradient};
                        margin: 0 auto 8px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        border: 3px solid white;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                    "></div>
                    <div style="font-size: 11px; font-weight: 500; max-width: 70px; overflow: hidden;">
                        {item['title'][:10]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### All Media")
        
        cols = st.columns(3)
        for idx, item in enumerate(filtered):
            with cols[idx % 3]:
                filepath = item.get('filepath')
                
                # Show actual image if available
                if filepath and os.path.exists(filepath):
                    if item['type'] == 'image':
                        st.image(filepath, use_container_width=True)
                    else:
                        st.video(filepath)
                else:
                    # Placeholder
                    icon = '📷' if item['type'] == 'image' else '🎬'
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                        height: 150px;
                        border-radius: 12px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 48px;
                    ">{icon}</div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"**{item['title']}**")
                st.caption(f"📍 {item['lat']:.4f}, {item['lon']:.4f} | {item['timestamp'][:10]}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👁️ View", key=f"view_{item['id']}", use_container_width=True):
                        open_story_viewer(item['id'])
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{item['id']}", use_container_width=True):
                        # Delete file if exists
                        if filepath and os.path.exists(filepath):
                            try:
                                os.remove(filepath)
                            except:
                                pass
                        st.session_state.media_data = [x for x in st.session_state.media_data if x['id'] != item['id']]
                        save_media_data(st.session_state.media_data)
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("No media yet! Upload some photos or videos.")

# Footer
st.markdown("""
<div style="text-align: center; color: #999; font-size: 12px; padding: 20px 0;">
    👻 Drone Media Map
</div>
""", unsafe_allow_html=True)

# Add JavaScript event handlers
create_event_handler()
