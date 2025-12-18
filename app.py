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
    layout="wide"
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
    
if 'selected_story_id' not in st.session_state:
    st.session_state.selected_story_id = None

if 'show_upload_form' not in st.session_state:
    st.session_state.show_upload_form = False

# Title
st.title("📡 Drone Media Map")
st.markdown("View drone photos and videos on an interactive map")

# Create two columns
col1, col2 = st.columns([2, 1])

with col1:
    # Create map
    if st.session_state.media_data:
        center_lat = sum(item['lat'] for item in st.session_state.media_data) / len(st.session_state.media_data)
        center_lon = sum(item['lon'] for item in st.session_state.media_data) / len(st.session_state.media_data)
    else:
        center_lat, center_lon = 34.0522, -118.2437
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11
    )
    
    # Add markers
    for item in st.session_state.media_data:
        # Choose marker color based on type
        if item['type'] == 'image':
            color = 'green'
            icon = 'camera'
        else:
            color = 'orange'
            icon = 'film'
        
        # Create popup with a button
        popup_html = f"""
        <div style="padding: 10px;">
            <h4 style="margin: 0 0 10px 0;">{item['title']}</h4>
            <p style="margin: 0 0 10px 0; font-size: 12px;">{item['description'][:100]}...</p>
            <form action="#" method="post">
                <input type="hidden" name="story_id" value="{item['id']}">
                <button type="submit" 
                        style="background: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                    👁️ View Story
                </button>
            </form>
        </div>
        """
        
        popup = folium.Popup(popup_html, max_width=250)
        
        folium.Marker(
            location=[item['lat'], item['lon']],
            popup=popup,
            tooltip=item['title'],
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(m)
    
    # Display map
    st_folium(m, width=700, height=500)

with col2:
    st.markdown("### 📊 Statistics")
    total = len(st.session_state.media_data)
    images = sum(1 for x in st.session_state.media_data if x['type'] == 'image')
    videos = sum(1 for x in st.session_state.media_data if x['type'] == 'video')
    
    st.metric("Total Stories", total)
    st.metric("Photos", images)
    st.metric("Videos", videos)
    
    st.markdown("---")
    st.markdown("### 🗺️ Legend")
    st.markdown("- 📍 **Green markers**: Photos")
    st.markdown("- 📍 **Orange markers**: Videos")
    st.markdown("- 👆 **Click any marker** to view story")
    
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("📤 Upload New Media", use_container_width=True):
        st.session_state.show_upload_form = True
        st.rerun()

# STORY VIEWER SECTION
st.markdown("---")
st.markdown("## 📱 Story Viewer")

# Check if a story is selected
if st.session_state.selected_story_id:
    # Find the selected story
    selected_story = None
    for story in st.session_state.media_data:
        if story['id'] == st.session_state.selected_story_id:
            selected_story = story
            break
    
    if selected_story:
        # Display the story
        st.markdown(f"### {selected_story['title']}")
        
        # Create columns for story details
        col_info, col_media = st.columns([1, 2])
        
        with col_info:
            st.markdown(f"""
            **📅 Date:** {selected_story['timestamp']}
            
            **📍 Location:** {selected_story['lat']:.4f}, {selected_story['lon']:.4f}
            
            **⬆️ Altitude:** {selected_story['altitude']} meters
            
            **📁 Type:** {selected_story['type'].upper()}
            
            **📝 Description:** {selected_story['description']}
            """)
            
            # Navigation buttons
            col_prev, col_next = st.columns(2)
            with col_prev:
                if st.button("⬅️ Previous"):
                    # Find current index
                    current_idx = st.session_state.media_data.index(selected_story)
                    prev_idx = (current_idx - 1) % len(st.session_state.media_data)
                    st.session_state.selected_story_id = st.session_state.media_data[prev_idx]['id']
                    st.rerun()
            
            with col_next:
                if st.button("Next ➡️"):
                    current_idx = st.session_state.media_data.index(selected_story)
                    next_idx = (current_idx + 1) % len(st.session_state.media_data)
                    st.session_state.selected_story_id = st.session_state.media_data[next_idx]['id']
                    st.rerun()
            
            if st.button("✕ Close Viewer", type="primary"):
                st.session_state.selected_story_id = None
                st.rerun()
        
        with col_media:
            if selected_story.get('filepath') and os.path.exists(selected_story['filepath']):
                if selected_story['type'] == 'image':
                    try:
                        image = Image.open(selected_story['filepath'])
                        st.image(image, caption="Drone Photo", use_container_width=True)
                    except:
                        st.warning("Could not load image")
                else:
                    try:
                        with open(selected_story['filepath'], 'rb') as f:
                            video_bytes = f.read()
                        st.video(video_bytes)
                    except:
                        st.warning("Could not load video")
            else:
                # Show placeholder
                if selected_story['type'] == 'image':
                    st.image("https://via.placeholder.com/600x400/4CAF50/FFFFFF?text=Drone+Photo", 
                            caption="Sample Photo - Upload your own!", use_container_width=True)
                else:
                    st.video("https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4")

# ALL STORIES LIST
st.markdown("---")
st.markdown("## 📋 All Stories")

# Create a grid of stories
cols = st.columns(3)

for idx, story in enumerate(st.session_state.media_data):
    with cols[idx % 3]:
        # Create a card for each story
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-left: 4px solid {'#4CAF50' if story['type'] == 'image' else '#FF9800'};
        ">
            <div style="font-weight: bold; font-size: 16px;">{story['title']}</div>
            <div style="font-size: 12px; color: #666; margin: 5px 0;">
                📅 {story['timestamp'][:10]} • 📍 {story['lat']:.2f}, {story['lon']:.2f}
            </div>
            <div style="font-size: 14px; margin: 10px 0;">{story['description'][:80]}...</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="
                    padding: 3px 10px;
                    border-radius: 15px;
                    font-size: 11px;
                    background: {'#4CAF50' if story['type'] == 'image' else '#FF9800'};
                    color: white;
                ">{story['type'].upper()}</span>
                <span style="font-size: 12px; color: #666;">⬆️ {story['altitude']}m</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Button to view this story
        if st.button(f"View {story['title'][:15]}...", key=f"view_{story['id']}", use_container_width=True):
            st.session_state.selected_story_id = story['id']
            st.rerun()

# UPLOAD FORM
if st.session_state.show_upload_form:
    st.markdown("---")
    st.markdown("## 📤 Upload Drone Media")
    
    with st.form("upload_form"):
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
        
        # Form submission
        submitted = st.form_submit_button("🚀 Upload to Map", use_container_width=True)
        
        if submitted:
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
                    st.session_state.selected_story_id = new_id  # Auto-view the new story
                    st.rerun()
            else:
                st.error("Please fill all required fields (*)")
    
    if st.button("Cancel Upload"):
        st.session_state.show_upload_form = False
        st.rerun()

# Instructions
st.markdown("---")
st.markdown("""
### ℹ️ How to Use:
1. **Click any marker on the map** to view that story
2. **Or click any "View" button** in the stories list below
3. **Upload your own** drone media using the upload button
4. **Use Previous/Next buttons** to navigate between stories
""")
