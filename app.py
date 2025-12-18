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
                img.thumbnail((200, 200))
                buffer = io.BytesIO()
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(buffer, format='JPEG', quality=85)
                return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        print(f"Error converting image: {e}")
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

if 'viewing_story' not in st.session_state:
    st.session_state.viewing_story = None
    
if 'current_story_index' not in st.session_state:
    st.session_state.current_story_index = 0

if 'clicked_marker_id' not in st.session_state:
    st.session_state.clicked_marker_id = None

# Custom CSS
st.markdown("""
<style>
    /* Story Viewer Overlay */
    .story-overlay {
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
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .story-viewer {
        width: 90%;
        max-width: 800px;
        background: #000;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
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
    
    .story-media-container {
        width: 100%;
        height: 500px;
        background: #000;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    
    .story-footer {
        padding: 20px;
        background: rgba(0,0,0,0.9);
        border-top: 1px solid rgba(255,255,255,0.1);
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
        cursor: pointer;
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
    
    /* Remove Streamlit default styling */
    .stButton > button {
        border-radius: 20px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

def create_story_marker(item):
    """Create Snapchat-style story marker"""
    filepath = item.get('filepath')
    has_image = filepath and os.path.exists(filepath) and item['type'] == 'image'
    
    if has_image:
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
            cursor: pointer;
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
        ">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                <circle cx="12" cy="12" r="3"/>
                <path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
            </svg>
        </div>
        '''
    
    # Add JavaScript to handle click and store in session state
    html += f'''
    <script>
        document.currentScript.parentElement.onclick = function() {{
            window.parent.postMessage({{
                type: 'marker_clicked',
                story_id: {item['id']}
            }}, '*');
        }};
    </script>
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
    
    for idx, item in enumerate(st.session_state.media_data):
        icon = create_story_marker(item)
        
        folium.Marker(
            location=[item['lat'], item['lon']],
            icon=icon,
            tooltip=f"👆 Click to view: {item['title']}"
        ).add_to(m)
    
    folium.LayerControl(position='topright').add_to(m)
    return m

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="font-size: 36px; font-weight: 800; color: #000; margin-bottom: 10px;">
        👻 Drone Media Map
        <span style="background: #FFFC00; color: #000; padding: 6px 16px; border-radius: 20px; font-size: 16px; font-weight: 700;">
            SNAP STYLE
        </span>
    </h1>
    <p style="color: #666;">Click on any map marker to view the story</p>
</div>
""", unsafe_allow_html=True)

# JavaScript to handle marker clicks
js_code = '''
<script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'marker_clicked') {
            // Store in localStorage and trigger Streamlit rerun
            localStorage.setItem('clicked_story_id', event.data.story_id);
            window.location.reload();
        }
    });
    
    // Check for stored click on page load
    window.onload = function() {
        const storyId = localStorage.getItem('clicked_story_id');
        if (storyId) {
            localStorage.removeItem('clicked_story_id');
            // Send to Streamlit
            window.parent.postMessage({
                type: 'load_story',
                story_id: parseInt(storyId)
            }, '*');
        }
    };
</script>
'''

# Inject JavaScript
st.components.v1.html(js_code, height=0)

# Check for story to view
if st.session_state.viewing_story is None:
    # Check if a marker was clicked
    query_params = st.query_params
    if 'story_id' in query_params:
        try:
            story_id = int(query_params['story_id'])
            for idx, story in enumerate(st.session_state.media_data):
                if story['id'] == story_id:
                    st.session_state.viewing_story = story_id
                    st.session_state.current_story_index = idx
                    break
        except:
            pass

# STORY VIEWER
if st.session_state.viewing_story is not None:
    current_story = st.session_state.media_data[st.session_state.current_story_index]
    
    # Create overlay
    st.markdown("""
    <div class="story-overlay">
        <div class="story-viewer">
    """, unsafe_allow_html=True)
    
    # Story header
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        st.markdown(f"""
        <div class="story-header">
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
                    {current_story['timestamp'][:10]} • {current_story['altitude']}m
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
                except:
                    st.markdown(f"""
                    <div style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white;">
                        <div style="font-size: 64px; margin-bottom: 20px;">📷</div>
                        <div style="font-size: 24px; margin-bottom: 10px;">Image</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Display video
                try:
                    with open(current_story['filepath'], 'rb') as f:
                        video_bytes = f.read()
                    st.video(video_bytes)
                except:
                    st.markdown(f"""
                    <div style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white;">
                        <div style="font-size: 64px; margin-bottom: 20px;">🎬</div>
                        <div style="font-size: 24px; margin-bottom: 10px;">Video</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Placeholder
            icon = '🎬' if current_story['type'] == 'video' else '📷'
            st.markdown(f"""
            <div style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white;">
                <div style="font-size: 64px; margin-bottom: 20px;">{icon}</div>
                <div style="font-size: 24px; margin-bottom: 10px;">{current_story['type'].title()}</div>
                <div style="font-size: 16px; opacity: 0.8; text-align: center; padding: 0 20px;">{current_story['description'][:100]}</div>
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
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Previous", key="prev_story", use_container_width=True):
            prev_index = (st.session_state.current_story_index - 1) % len(st.session_state.media_data)
            st.session_state.current_story_index = prev_index
            st.rerun()
    
    with col2:
        if st.button("✕ Close Viewer", key="close_story", type="primary", use_container_width=True):
            st.session_state.viewing_story = None
            st.rerun()
    
    with col3:
        if st.button("Next →", key="next_story", use_container_width=True):
            next_index = (st.session_state.current_story_index + 1) % len(st.session_state.media_data)
            st.session_state.current_story_index = next_index
            st.rerun()

else:
    # Main app when not viewing a story
    col1, col2 = st.columns([5, 1])
    
    with col1:
        # Create map
        m = create_map()
        map_output = st_folium(m, width=None, height=600, key="main_map")
        
        # Quick view stories
        st.markdown("### 📱 Quick View")
        cols = st.columns(3)
        for idx, story in enumerate(st.session_state.media_data[:6]):
            with cols[idx % 3]:
                # Create clickable story card
                if st.button(f"👁️ {story['title'][:15]}...", 
                           key=f"quick_view_{story['id']}",
                           use_container_width=True):
                    st.session_state.viewing_story = story['id']
                    st.session_state.current_story_index = idx
                    st.rerun()
                
                # Show thumbnail if available
                if story.get('filepath') and os.path.exists(story['filepath']) and story['type'] == 'image':
                    try:
                        with Image.open(story['filepath']) as img:
                            img.thumbnail((200, 150))
                            st.image(img, use_container_width=True)
                    except:
                        pass
    
    with col2:
        st.markdown("### 📍 Legend")
        st.markdown("""
        <div style="padding: 8px 0;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                <div style="width: 14px; height: 14px; border-radius: 50%; background: linear-gradient(135deg, #00C853 0%, #69F0AE 100%); border: 2px solid white;"></div>
                <span style="font-size: 13px;">Photo</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 14px; height: 14px; border-radius: 50%; background: linear-gradient(135deg, #FF6D00 0%, #FFAB40 100%); border: 2px solid white;"></div>
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

# Stories tab
st.markdown("---")
st.markdown("## 📱 All Stories")

if st.session_state.media_data:
    cols = st.columns(3)
    
    for idx, story in enumerate(st.session_state.media_data):
        with cols[idx % 3]:
            # Story card
            if st.button(f"👁️ View {story['title'][:20]}...", 
                        key=f"view_{story['id']}",
                        use_container_width=True,
                        help=f"Click to view this story"):
                st.session_state.viewing_story = story['id']
                st.session_state.current_story_index = idx
                st.rerun()
            
            # Story info
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 5px;">
                <div style="font-weight: 600; font-size: 16px; color: #333;">{story['title']}</div>
                <div style="font-size: 12px; color: #666; margin: 5px 0;">{story['timestamp'][:10]} • {story['altitude']}m</div>
                <div style="font-size: 14px; color: #555;">{story['description'][:80]}...</div>
                <div style="margin-top: 10px;">
                    <span style="
                        display: inline-block;
                        padding: 3px 10px;
                        border-radius: 10px;
                        font-size: 11px;
                        font-weight: 600;
                        background: {'#00C853' if story['type'] == 'image' else '#FF6D00'};
                        color: white;
                    ">{story['type'].upper()}</span>
                    <span style="
                        display: inline-block;
                        padding: 3px 10px;
                        border-radius: 10px;
                        font-size: 11px;
                        background: #2962FF;
                        color: white;
                        margin-left: 5px;
                    ">📍 {story['lat']:.2f}, {story['lon']:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #999; font-size: 12px; padding: 20px 0; margin-top: 30px;">
    👻 Drone Media Map • Click on map markers or story buttons to view!
</div>
""", unsafe_allow_html=True)
 
