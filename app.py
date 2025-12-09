import streamlit as st
from datetime import datetime
from PIL import Image
import io
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
            return []
    return []

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

# Initialize session state
if 'media_data' not in st.session_state:
    st.session_state.media_data = load_media_data()
    
if 'viewing_story' not in st.session_state:
    st.session_state.viewing_story = None

# Custom CSS - SIMPLE AND CLEAN
st.markdown("""
<style>
    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #000;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .snap-badge {
        background: #FFFC00;
        color: #000;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
    }
    
    .story-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 2px solid #FFFC00;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .story-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .media-preview {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    
    .story-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 8px;
        color: #000;
    }
    
    .story-info {
        font-size: 12px;
        color: #666;
        margin-bottom: 10px;
    }
    
    .type-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .type-photo {
        background: #00C853;
        color: white;
    }
    
    .type-video {
        background: #FF6D00;
        color: white;
    }
    
    .location-badge {
        background: #2962FF;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        display: inline-block;
    }
    
    .story-viewer-container {
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
        padding: 20px;
    }
    
    .story-viewer {
        background: #000;
        border-radius: 20px;
        width: 100%;
        max-width: 600px;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }
    
    .story-header {
        padding: 20px;
        background: rgba(0,0,0,0.8);
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .story-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(45deg, #FFFC00, #FF6B6B);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        color: white;
    }
    
    .close-btn {
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
    }
    
    .close-btn:hover {
        background: rgba(255,255,255,0.2);
    }
    
    .nav-btn {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: rgba(0,0,0,0.5);
        border: 2px solid white;
        color: white;
        font-size: 24px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .nav-btn:hover {
        background: rgba(0,0,0,0.8);
    }
    
    .prev-btn {
        left: 20px;
    }
    
    .next-btn {
        right: 20px;
    }
    
    .upload-section {
        background: #f8f9fa;
        padding: 30px;
        border-radius: 16px;
        border: 2px dashed #FFFC00;
    }
    
    .stats-box {
        background: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .stats-number {
        font-size: 32px;
        font-weight: 700;
        color: #000;
        margin-bottom: 5px;
    }
    
    .stats-label {
        font-size: 14px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-title">
    👻 Drone Media Map
    <span class="snap-badge">SNAP STYLE</span>
</div>
""", unsafe_allow_html=True)

# SIMPLE STORY VIEWER - This will actually work
if st.session_state.viewing_story is not None:
    story_id = st.session_state.viewing_story
    
    # Find the story
    current_story = None
    current_index = 0
    for idx, story in enumerate(st.session_state.media_data):
        if story['id'] == story_id:
            current_story = story
            current_index = idx
            break
    
    if current_story:
        # Create a container for the story viewer
        with st.container():
            col1, col2, col3 = st.columns([1, 8, 1])
            
            with col2:
                # Close button at the top
                if st.button("✕ Close", key="close_viewer", type="secondary", use_container_width=True):
                    st.session_state.viewing_story = None
                    st.rerun()
                
                # Story header
                st.markdown(f"""
                <div style="background: #000; padding: 20px; border-radius: 20px 20px 0 0; margin-bottom: 0;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <div class="story-avatar">
                            {'🎬' if current_story['type'] == 'video' else '📷'}
                        </div>
                        <div>
                            <div style="color: white; font-weight: 600; font-size: 20px;">{current_story['title']}</div>
                            <div style="color: rgba(255,255,255,0.7); font-size: 14px;">
                                {current_story['timestamp'][:10]} • {current_story['altitude']}m
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the media - THIS IS WHAT WAS MISSING
                if current_story.get('filepath') and os.path.exists(current_story['filepath']):
                    if current_story['type'] == 'image':
                        st.image(current_story['filepath'], use_container_width=True)
                    else:
                        st.video(current_story['filepath'])
                else:
                    # Placeholder if file doesn't exist
                    icon = '🎬' if current_story['type'] == 'video' else '📷'
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                        height: 400px;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        border-radius: 0;
                    ">
                        <div style="font-size: 64px; margin-bottom: 20px;">{icon}</div>
                        <div style="font-size: 24px; margin-bottom: 10px;">
                            {'Video' if current_story['type'] == 'video' else 'Photo'}
                        </div>
                        <div style="font-size: 16px; opacity: 0.8;">{current_story['description'][:100]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Story info
                st.markdown(f"""
                <div style="background: #111; padding: 20px; border-radius: 0 0 20px 20px; margin-top: 0;">
                    <div style="color: white; font-size: 16px; margin-bottom: 15px;">
                        {current_story['description']}
                    </div>
                    <div style="display: flex; justify-content: space-between; color: rgba(255,255,255,0.7); font-size: 14px;">
                        <div>
                            <div>📍 Location</div>
                            <div style="font-family: monospace; font-weight: 600;">{current_story['lat']:.4f}, {current_story['lon']:.4f}</div>
                        </div>
                        <div>
                            <div>🕒 Time</div>
                            <div>{current_story['timestamp'][11:]}</div>
                        </div>
                        <div>
                            <div>⬆️ Altitude</div>
                            <div>{current_story['altitude']}m</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Navigation buttons
                nav_col1, nav_col2, nav_col3 = st.columns([1, 8, 1])
                with nav_col1:
                    if st.button("‹ Prev", key="nav_prev", use_container_width=True):
                        # Find previous story
                        prev_index = (current_index - 1) % len(st.session_state.media_data)
                        st.session_state.viewing_story = st.session_state.media_data[prev_index]['id']
                        st.rerun()
                
                with nav_col3:
                    if st.button("Next ›", key="nav_next", use_container_width=True):
                        # Find next story
                        next_index = (current_index + 1) % len(st.session_state.media_data)
                        st.session_state.viewing_story = st.session_state.media_data[next_index]['id']
                        st.rerun()

# Main tabs
tab1, tab2, tab3 = st.tabs(["🗺️ Map View", "📤 Add Media", "📱 Stories"])

with tab1:
    st.markdown("### 📍 Media Locations")
    
    if st.session_state.media_data:
        # Display media as cards on a grid
        cols = st.columns(3)
        
        for idx, story in enumerate(st.session_state.media_data):
            with cols[idx % 3]:
                # Story card
                with st.container():
                    st.markdown(f"""
                    <div class="story-card" onclick="alert('Click handled by Streamlit button')">
                        <div class="story-title">{story['title']}</div>
                        <div class="story-info">
                            {story['timestamp'][:10]} • {story['altitude']}m
                        </div>
                        <div style="margin-bottom: 10px;">
                            <span class="type-badge {'type-photo' if story['type'] == 'image' else 'type-video'}">
                                {story['type'].upper()}
                            </span>
                            <span class="location-badge">
                                📍 {story['lat']:.2f}, {story['lon']:.2f}
                            </span>
                        </div>
                        <div style="font-size: 14px; color: #555;">
                            {story['description'][:80]}...
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show preview if available
                    if story.get('filepath') and os.path.exists(story['filepath']):
                        if story['type'] == 'image':
                            try:
                                # Create thumbnail
                                with Image.open(story['filepath']) as img:
                                    img.thumbnail((300, 200))
                                    st.image(img, use_container_width=True)
                            except:
                                pass
                    
                    # View button - THIS TRIGGERS THE STORY VIEWER
                    if st.button(f"👁️ View Story", key=f"view_{story['id']}", use_container_width=True):
                        st.session_state.viewing_story = story['id']
                        st.rerun()
    else:
        st.info("No media yet. Upload some photos or videos!")

with tab2:
    st.markdown("### 📤 Upload New Media")
    
    with st.container():
        st.markdown("""
        <div class="upload-section">
            <h3 style="color: #000; margin-bottom: 20px;">Add your drone media to the map</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Location Details")
            lat = st.number_input("Latitude", value=34.0522, format="%.6f")
            lon = st.number_input("Longitude", value=-118.2437, format="%.6f")
            altitude = st.slider("Altitude (meters)", 0, 500, 100)
            
            st.markdown("#### Media Info")
            title = st.text_input("Story Title", placeholder="e.g., Sunset over the beach")
            description = st.text_area("Description", placeholder="Describe your shot...", height=100)
        
        with col2:
            st.markdown("#### Upload File")
            uploaded_file = st.file_uploader(
                "Choose a photo or video",
                type=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi'],
                key="uploader"
            )
            
            if uploaded_file:
                file_type = 'video' if uploaded_file.type.startswith('video') else 'image'
                
                st.markdown(f"**Preview** ({file_type})")
                if file_type == 'image':
                    st.image(uploaded_file, use_container_width=True)
                else:
                    st.video(uploaded_file)
                
                # Submit button
                if st.button("🚀 Add to Map", type="primary", use_container_width=True):
                    if not title or not description:
                        st.warning("Please add a title and description!")
                    else:
                        # Save file
                        filepath = save_uploaded_file(uploaded_file)
                        
                        # Create new story
                        new_id = max([s.get('id', 0) for s in st.session_state.media_data], default=0) + 1
                        new_story = {
                            'id': new_id,
                            'type': file_type,
                            'title': title,
                            'lat': lat,
                            'lon': lon,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'altitude': altitude,
                            'description': description,
                            'filepath': filepath
                        }
                        
                        st.session_state.media_data.append(new_story)
                        save_media_data(st.session_state.media_data)
                        
                        st.success(f"✅ '{title}' added successfully!")
                        st.balloons()
                        st.rerun()
            else:
                st.info("👆 Select a photo or video file")

with tab3:
    # Stats
    total = len(st.session_state.media_data)
    images = sum(1 for s in st.session_state.media_data if s['type'] == 'image')
    videos = total - images
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stats-box">
            <div class="stats-number">{total}</div>
            <div class="stats-label">Total Stories</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stats-box">
            <div class="stats-number">{images}</div>
            <div class="stats-label">Photos</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stats-box">
            <div class="stats-number">{videos}</div>
            <div class="stats-label">Videos</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Filter
    filter_type = st.selectbox("Filter by type", ["All", "Photos", "Videos"])
    
    # Display stories
    filtered_stories = st.session_state.media_data.copy()
    if filter_type == "Photos":
        filtered_stories = [s for s in filtered_stories if s['type'] == 'image']
    elif filter_type == "Videos":
        filtered_stories = [s for s in filtered_stories if s['type'] == 'video']
    
    # Sort by date (newest first)
    filtered_stories.sort(key=lambda x: x['timestamp'], reverse=True)
    
    if filtered_stories:
        for story in filtered_stories:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Story info
                st.markdown(f"""
                <div style="background: white; padding: 20px; border-radius: 12px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                        <div style="font-size: 18px; font-weight: 600;">{story['title']}</div>
                        <span class="type-badge {'type-photo' if story['type'] == 'image' else 'type-video'}"
                              style="font-size: 12px;">
                            {story['type'].upper()}
                        </span>
                    </div>
                    
                    <div style="color: #666; font-size: 14px; margin-bottom: 10px;">
                        📅 {story['timestamp']} • 📍 {story['lat']:.4f}, {story['lon']:.4f} • ⬆️ {story['altitude']}m
                    </div>
                    
                    <div style="color: #444; font-size: 15px; line-height: 1.5;">
                        {story['description']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Media preview and actions
                if story.get('filepath') and os.path.exists(story['filepath']):
                    if story['type'] == 'image':
                        try:
                            with Image.open(story['filepath']) as img:
                                img.thumbnail((200, 150))
                                st.image(img, use_container_width=True)
                        except:
                            pass
                
                # Action buttons
                if st.button("👁️ View", key=f"view_story_{story['id']}", use_container_width=True):
                    st.session_state.viewing_story = story['id']
                    st.rerun()
                
                if st.button("🗑️ Delete", key=f"del_{story['id']}", use_container_width=True):
                    # Delete file
                    if story.get('filepath') and os.path.exists(story['filepath']):
                        try:
                            os.remove(story['filepath'])
                        except:
                            pass
                    
                    # Remove from data
                    st.session_state.media_data = [s for s in st.session_state.media_data if s['id'] != story['id']]
                    save_media_data(st.session_state.media_data)
                    st.rerun()
            
            st.markdown("---")
    else:
        st.info("No stories found. Upload some media!")

# Footer
st.markdown("""
<div style="text-align: center; color: #999; font-size: 12px; padding: 30px 0; margin-top: 30px;">
    👻 Drone Media Map • Click "View" on any story to see it fullscreen!
</div>
""", unsafe_allow_html=True)
