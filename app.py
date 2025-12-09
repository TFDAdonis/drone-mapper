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
                img.thumbnail((200, 200))
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                return base64.b64encode(buffer.getvalue()).decode()
    except:
        pass
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
    if item['type'] == 'video':
        html = '''
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
        html = '''
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
    return folium.DivIcon(html=html, icon_size=(60, 60), icon_anchor=(30, 30))

def create_story_popup(item):
    """Create Snapchat story-style popup with actual media preview"""
    filepath = item.get('filepath')
    type_gradient = 'linear-gradient(135deg, #00C853 0%, #69F0AE 100%)' if item['type'] == 'image' else 'linear-gradient(135deg, #FF6D00 0%, #FFAB40 100%)'
    type_icon = '📷' if item['type'] == 'image' else '🎬'
    
    # Check if we have an actual image to display
    img_content = ""
    if filepath and os.path.exists(filepath) and item['type'] == 'image':
        img_base64 = get_image_base64(filepath)
        if img_base64:
            img_content = f'''
            <div style="
                width: 100%;
                height: 220px;
                background-image: url('data:image/jpeg;base64,{img_base64}');
                background-size: cover;
                background-position: center;
            "></div>
            '''
    
    if not img_content:
        # Fallback placeholder
        img_content = f'''
        <div style="
            height: 200px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        ">
            <div style="font-size: 64px; margin-bottom: 12px;">{type_icon}</div>
            <div style="color: white; font-size: 13px; text-align: center;">
                {item['description'][:80]}{'...' if len(item['description']) > 80 else ''}
            </div>
        </div>
        '''
    
    html = f'''
    <div style="
        font-family: -apple-system, sans-serif;
        width: 280px;
        background: #000;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    ">
        <!-- Story Header -->
        <div style="
            padding: 12px 16px;
            background: linear-gradient(180deg, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.5) 100%);
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            z-index: 10;
        ">
            <div style="
                height: 2px;
                background: rgba(255,255,255,0.3);
                border-radius: 2px;
                margin-bottom: 10px;
            ">
                <div style="height: 100%; width: 100%; background: white; border-radius: 2px;"></div>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    background: {type_gradient};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 14px;
                    border: 2px solid white;
                ">{type_icon}</div>
                <div>
                    <div style="color: white; font-weight: 600; font-size: 13px;">{item['title']}</div>
                    <div style="color: rgba(255,255,255,0.7); font-size: 10px;">{item['timestamp'][:10]}</div>
                </div>
            </div>
        </div>
        
        <!-- Story Content -->
        <div style="position: relative; padding-top: 70px;">
            {img_content}
        </div>
        
        <!-- Story Footer -->
        <div style="
            padding: 12px 16px;
            background: #111;
        ">
            <div style="color: rgba(255,255,255,0.8); font-size: 12px; margin-bottom: 8px;">
                {item['description'][:100]}{'...' if len(item['description']) > 100 else ''}
            </div>
            <div style="
                display: flex;
                justify-content: space-between;
                font-family: monospace;
                font-size: 10px;
                color: rgba(255,255,255,0.5);
            ">
                <span>📍 {item['lat']:.4f}, {item['lon']:.4f}</span>
                <span>⬆️ {item['altitude']}m</span>
            </div>
        </div>
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
        for item in st.session_state.media_data:
            icon = create_story_marker(item)
            popup_html = create_story_popup(item)
            folium.Marker(
                location=[item['lat'], item['lon']],
                icon=icon,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"👆 {item['title']}"
            ).add_to(m)
    
    folium.LayerControl(position='topright').add_to(m)
    return m

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
        st_folium(m, width=None, height=650, key="main_map")
    
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
                    ">{icon}</div>
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
                
                if st.button("🗑️ Delete", key=f"del_{item['id']}", use_container_width=True):
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
