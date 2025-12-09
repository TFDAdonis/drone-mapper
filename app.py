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
import tempfile

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
                img.thumbnail((200, 200))
                buffer = io.BytesIO()
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(buffer, format='JPEG', quality=85)
                return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        st.error(f"Error converting image: {e}")
    return None

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
    
if 'selected_lat' not in st.session_state:
    st.session_state.selected_lat = None
    
if 'selected_lon' not in st.session_state:
    st.session_state.selected_lon = None

if 'last_click_lat' not in st.session_state:
    st.session_state.last_click_lat = None
    
if 'last_click_lon' not in st.session_state:
    st.session_state.last_click_lon = None

if 'viewing_story' not in st.session_state:
    st.session_state.viewing_story = None
    
if 'current_story_index' not in st.session_state:
    st.session_state.current_story_index = 0

if 'clicked_marker' not in st.session_state:
    st.session_state.clicked_marker = None

# Custom CSS with story viewer styles
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
    
    /* Story Viewer Overlay */
    .story-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.98);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .story-viewer {
        width: 95%;
        max-width: 900px;
        background: #000;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0,0,0,0.8);
        animation: slideUp 0.3s ease;
    }
    
    @keyframes slideUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .story-header {
        padding: 20px;
        background: rgba(0,0,0,0.9);
        display: flex;
        align-items: center;
        gap: 15px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .story-icon {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(45deg, #FFFC00, #FF6B6B);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: white;
    }
    
    .story-media-container {
        width: 100%;
        height: 500px;
        background: #000;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    
    .story-media {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }
    
    .story-footer {
        padding: 20px;
        background: rgba(0,0,0,0.9);
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Map Styles */
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
    
    /* Story Cards */
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
    
    .type-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .photo-badge {
        background: #00C853;
        color: white;
    }
    
    .video-badge {
        background: #FF6D00;
        color: white;
    }
    
    .location-badge {
        background: #2962FF;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
    }
    
    /* Navigation Buttons */
    .nav-btn-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10001;
        display: flex;
        gap: 10px;
    }
    
    .close-story-btn {
        background: rgba(255,255,255,0.1);
        color: white;
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 20px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    .close-story-btn:hover {
        background: rgba(255,255,255,0.2);
        border-color: rgba(255,255,255,0.5);
    }
    
    .prev-next-container {
        position: fixed;
        top: 50%;
        left: 0;
        right: 0;
        transform: translateY(-50%);
        display: flex;
        justify-content: space-between;
        padding: 0 20px;
        z-index: 10001;
    }
    
    .nav-arrow-btn {
        background: rgba(0,0,0,0.5);
        color: white;
        border: 2px solid white;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 28px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    .nav-arrow-btn:hover {
        background: rgba(0,0,0,0.8);
    }
</style>
""", unsafe_allow_html=True)

def create_story_marker(item):
    """Create Snapchat-style story marker with actual image preview"""
    filepath = item.get('filepath')
    has_image = filepath and os.path.exists(filepath) and item['type'] == 'image'
    
    if has_image:
        # Create marker with actual image thumbnail
        img_base64 = get_image_base64(filepath)
        if img_base64:
            html = f'''
            <div style="
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #FFFC00 0%, #FF6B6B 50%, #4ECDC4 100%);
                padding: 3px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                cursor: pointer;
                transition: transform 0.2s ease;
            " onclick="handleMarkerClick({item['id']})" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
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
    if item['type'] == 'video':
        html = f'''
        <div style="
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #FF6D00 0%, #FFAB40 100%);
            padding: 3px;
            box-shadow: 0 4px 15px rgba(255, 109, 0, 0.5);
            cursor: pointer;
            transition: transform 0.2s ease;
        " onclick="handleMarkerClick({item['id']})" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
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
            cursor: pointer;
            transition: transform 0.2s ease;
        " onclick="handleMarkerClick({item['id']})" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                <circle cx="12" cy="12" r="3"/>
                <path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
            </svg>
        </div>
        '''
    return folium.DivIcon(html=html, icon_size=(60, 60), icon_anchor=(30, 30))

def create_story_popup(item):
    """Create simple popup with view button"""
    html = f'''
    <div style="font-family: Arial, sans-serif; padding: 10px; max-width: 250px;">
        <h4 style="margin: 0 0 10px 0; color: #333;">{item['title']}</h4>
        <p style="margin: 0 0 10px 0; font-size: 12px; color: #666;">
            {item['timestamp'][:10]} • {item['altitude']}m
        </p>
        <p style="margin: 0 0 10px 0; font-size: 14px;">
            {item['description'][:100]}...
        </p>
        <button onclick="
            window.parent.postMessage({{
                type: 'view_story',
                story_id: {item['id']}
            }}, '*');
            return false;
        " style="
            background: #FFFC00;
            color: black;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            font-size: 14px;
        ">
            👁️ View Story
        </button>
    </div>
    '''
    return html

def create_map(click_mode=False):
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
    
    if not click_mode:
        for idx, item in enumerate(st.session_state.media_data):
            icon = create_story_marker(item)
            popup_html = create_story_popup(item)
            
            popup = folium.Popup(popup_html, max_width=300)
            
            folium.Marker(
                location=[item['lat'], item['lon']],
                icon=icon,
                popup=popup,
                tooltip=f"👆 {item['title']}"
            ).add_to(m)
    
    folium.LayerControl(position='topright').add_to(m)
    return m

# JavaScript to handle marker clicks
js_code = '''
<script>
    function handleMarkerClick(storyId) {
        window.parent.postMessage({
            type: 'view_story',
            story_id: storyId
        }, '*');
    }
    
    window.addEventListener('message', function(event) {
        if (event.data.type === 'view_story') {
            // Send to Streamlit via URL parameter
            const url = new URL(window.location);
            url.searchParams.set('story_id', event.data.story_id);
            window.history.pushState({}, '', url);
            // Trigger Streamlit rerun
            window.parent.location.reload();
        }
    });
</script>
'''

# Header
st.markdown("""
<div class="header-container">
    <h1 class="main-header">
        👻 Drone Media Map
        <span class="snapchat-yellow">SNAP STYLE</span>
    </h1>
</div>
""", unsafe_allow_html=True)

# Check URL for story parameter
query_params = st.query_params
if 'story_id' in query_params:
    try:
        story_id = int(query_params['story_id'])
        for idx, story in enumerate(st.session_state.media_data):
            if story['id'] == story_id:
                st.session_state.viewing_story = story_id
                st.session_state.current_story_index = idx
                break
        # Remove the parameter
        st.query_params.clear()
    except:
        pass

# STORY VIEWER
if st.session_state.viewing_story is not None:
    current_story = st.session_state.media_data[st.session_state.current_story_index]
    
    # Navigation buttons (outside the main viewer)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Previous", key="prev_story", use_container_width=True):
            prev_index = (st.session_state.current_story_index - 1) % len(st.session_state.media_data)
            st.session_state.current_story_index = prev_index
            st.rerun()
    
    with col2:
        if st.button("✕ Close", key="close_story", type="primary", use_container_width=True):
            st.session_state.viewing_story = None
            st.rerun()
    
    with col3:
        if st.button("Next →", key="next_story", use_container_width=True):
            next_index = (st.session_state.current_story_index + 1) % len(st.session_state.media_data)
            st.session_state.current_story_index = next_index
            st.rerun()
    
    # Story viewer container
    st.markdown("""
    <div class="story-viewer">
    """, unsafe_allow_html=True)
    
    # Story header
    st.markdown(f"""
    <div class="story-header">
        <div class="story-icon">
            {'🎬' if current_story['type'] == 'video' else '📷'}
        </div>
        <div>
            <div style="color: white; font-weight: 600; font-size: 24px;">{current_story['title']}</div>
            <div style="color: rgba(255,255,255,0.7); font-size: 14px;">
                {current_story['timestamp']} • Altitude: {current_story['altitude']}m
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Story media
    st.markdown('<div class="story-media-container">', unsafe_allow_html=True)
    
    if current_story.get('filepath') and os.path.exists(current_story['filepath']):
        if current_story['type'] == 'image':
            # Display image
            try:
                image = Image.open(current_story['filepath'])
                st.image(image, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading image: {e}")
                st.markdown(f"""
                <div style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white;">
                    <div style="font-size: 64px; margin-bottom: 20px;">📷</div>
                    <div style="font-size: 24px; margin-bottom: 10px;">Photo Preview</div>
                    <div style="font-size: 16px; opacity: 0.8;">{current_story['title']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Display video
            try:
                # Read video file
                with open(current_story['filepath'], 'rb') as f:
                    video_bytes = f.read()
                
                # Create a temporary file to hold the video
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                    tmp_file.write(video_bytes)
                    tmp_path = tmp_file.name
                
                # Display video
                st.video(tmp_path)
            except Exception as e:
                st.error(f"Error loading video: {e}")
                st.markdown(f"""
                <div style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white;">
                    <div style="font-size: 64px; margin-bottom: 20px;">🎬</div>
                    <div style="font-size: 24px; margin-bottom: 10px;">Video Preview</div>
                    <div style="font-size: 16px; opacity: 0.8;">{current_story['title']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Placeholder if no file
        icon = '🎬' if current_story['type'] == 'video' else '📷'
        st.markdown(f"""
        <div style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white;">
            <div style="font-size: 64px; margin-bottom: 20px;">{icon}</div>
            <div style="font-size: 24px; margin-bottom: 10px;">{current_story['type'].title()}</div>
            <div style="font-size: 16px; opacity: 0.8; text-align: center; padding: 0 20px;">{current_story['description']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Story footer
    st.markdown(f"""
    <div class="story-footer">
        <div style="color: white; font-size: 16px; margin-bottom: 15px; line-height: 1.6;">
            {current_story['description']}
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; color: rgba(255,255,255,0.7); font-size: 14px;">
            <div>
                <div style="font-weight: 600; margin-bottom: 5px; color: #FFFC00;">📍 Location</div>
                <div style="font-family: monospace; font-size: 13px;">{current_story['lat']:.6f}, {current_story['lon']:.6f}</div>
            </div>
            <div>
                <div style="font-weight: 600; margin-bottom: 5px; color: #FFFC00;">🕒 Time</div>
                <div>{current_story['timestamp'][11:]}</div>
            </div>
            <div>
                <div style="font-weight: 600; margin-bottom: 5px; color: #FFFC00;">⬆️ Altitude</div>
                <div>{current_story['altitude']} meters</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Navigation info
    st.info(f"Viewing story {st.session_state.current_story_index + 1} of {len(st.session_state.media_data)}. Use Previous/Next buttons to navigate.")

else:
    # Main app when not viewing a story
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🗺️ Snap Map", "📤 Add to Map", "📱 Stories"])

    with tab1:
        col1, col2 = st.columns([5, 1])
        
        with col1:
            # Inject JavaScript
            st.components.v1.html(js_code, height=0)
            
            m = create_map()
            map_output = st_folium(m, width=None, height=650, key="main_map")
            
            # Instructions
            st.info("👆 **Click on any map marker** to view the story. Click the 'View Story' button in the popup to open fullscreen viewer.")
            
            # Quick view panel
            with st.expander("📱 Quick View Stories", expanded=True):
                cols = st.columns(3)
                for idx, item in enumerate(st.session_state.media_data[:6]):  # Show first 6
                    with cols[idx % 3]:
                        # Try to show thumbnail
                        filepath = item.get('filepath')
                        if filepath and os.path.exists(filepath) and item['type'] == 'image':
                            try:
                                with Image.open(filepath) as img:
                                    img.thumbnail((150, 150))
                                    st.image(img, use_container_width=True)
                            except:
                                icon = '📷' if item['type'] == 'image' else '🎬'
                                st.markdown(f"""
                                <div style="text-align: center; padding: 20px; background: #f0f0f0; border-radius: 10px;">
                                    <div style="font-size: 32px;">{icon}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            icon = '📷' if item['type'] == 'image' else '🎬'
                            st.markdown(f"""
                            <div style="text-align: center; padding: 20px; background: #f0f0f0; border-radius: 10px;">
                                <div style="font-size: 32px;">{icon}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown(f"**{item['title'][:15]}...**")
                        st.caption(f"{item['timestamp'][:10]}")
                        
                        if st.button("View", key=f"map_view_{item['id']}", use_container_width=True):
                            st.session_state.viewing_story = item['id']
                            st.session_state.current_story_index = idx
                            st.rerun()
        
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
            
            st.markdown("---")
            st.markdown("### 🎯 Tips")
            st.info("""
            1. Click map markers
            2. Click 'View Story' in popup
            3. Use arrows to navigate
            4. Upload your own media!
            """)

    with tab2:
        st.markdown("""
        <div class="upload-instruction">
            👆 Click on the map to choose where to place your media, then upload!
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("#### 📍 Step 1: Click to Select Location")
            
            upload_map = create_map(click_mode=True)
            
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
        
        # Display all stories in a grid
        if st.session_state.media_data:
            cols = st.columns(3)
            
            for idx, story in enumerate(st.session_state.media_data):
                col_idx = idx % 3
                with cols[col_idx]:
                    # Story card
                    st.markdown(f"""
                    <div class="story-card">
                        <div style="font-size: 18px; font-weight: 600; color: #000; margin-bottom: 8px;">
                            {story['title']}
                        </div>
                        <div style="font-size: 12px; color: #666; margin-bottom: 10px;">
                            {story['timestamp'][:10]} • {story['altitude']}m
                        </div>
                        <div style="margin-bottom: 10px;">
                            <span class="type-badge {'photo-badge' if story['type'] == 'image' else 'video-badge'}">
                                {story['type'].upper()}
                            </span>
                            <span class="location-badge">
                                📍 {story['lat']:.2f}, {story['lon']:.2f}
                            </span>
                        </div>
                        <div style="font-size: 14px; color: #555; margin-bottom: 15px;">
                            {story['description'][:80]}...
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show thumbnail if available
                    if story.get('filepath') and os.path.exists(story['filepath']):
                        if story['type'] == 'image':
                            try:
                                with Image.open(story['filepath']) as img:
                                    img.thumbnail((400, 300))
                                    st.image(img, use_container_width=True)
                            except:
                                pass
                    
                    # View button
                    if st.button(f"👁️ View Story", key=f"story_view_{story['id']}", use_container_width=True):
                        st.session_state.viewing_story = story['id']
                        st.session_state.current_story_index = idx
                        st.rerun()
                    
                    # Delete button
                    if st.button(f"🗑️ Delete", key=f"story_del_{story['id']}", use_container_width=True):
                        # Delete file if exists
                        filepath = story.get('filepath')
                        if filepath and os.path.exists(filepath):
                            try:
                                os.remove(filepath)
                            except:
                                pass
                        st.session_state.media_data = [x for x in st.session_state.media_data if x['id'] != story['id']]
                        save_media_data(st.session_state.media_data)
                        st.rerun()
        else:
            st.info("No media yet. Upload some photos or videos!")

# Footer
st.markdown("""
<div style="text-align: center; color: #999; font-size: 12px; padding: 20px 0;">
    👻 Drone Media Map • Click on map markers to view stories!
</div>
""", unsafe_allow_html=True)
