import streamlit as st
from datetime import datetime
from PIL import Image
import io
import os
import json
import uuid
import time

# Page configuration
st.set_page_config(
    page_title="Drone Media Map",
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
    
if 'current_story_index' not in st.session_state:
    st.session_state.current_story_index = 0

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 36px;
        font-weight: 800;
        color: #000;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .snap-badge {
        background: #FFFC00;
        color: #000;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 16px;
        font-weight: 700;
    }
    
    /* Story Viewer Overlay */
    .story-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.95);
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
    
    .close-btn {
        position: absolute;
        top: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: rgba(255,255,255,0.1);
        border: none;
        color: white;
        font-size: 28px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10001;
    }
    
    .close-btn:hover {
        background: rgba(255,255,255,0.2);
    }
    
    .nav-btn {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: rgba(0,0,0,0.5);
        border: 2px solid white;
        color: white;
        font-size: 28px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10001;
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
    
    .media-thumbnail {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 10px;
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
    
    /* Stats Cards */
    .stats-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .stats-number {
        font-size: 36px;
        font-weight: 800;
        color: #000;
        margin-bottom: 5px;
    }
    
    .stats-label {
        font-size: 14px;
        color: #666;
        font-weight: 500;
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

# SIMPLE STORY VIEWER - This will actually display videos
if st.session_state.viewing_story is not None:
    current_story = st.session_state.media_data[st.session_state.current_story_index]
    
    # Create overlay using columns
    col1, col2, col3 = st.columns([1, 8, 1])
    
    with col2:
        # Story viewer container
        st.markdown(f"""
        <div class="story-viewer">
            <div class="story-header">
                <div class="story-icon">
                    {'🎬' if current_story['type'] == 'video' else '📷'}
                </div>
                <div>
                    <div style="color: white; font-weight: 600; font-size: 22px;">{current_story['title']}</div>
                    <div style="color: rgba(255,255,255,0.7); font-size: 14px;">
                        {current_story['timestamp'][:10]} • {current_story['altitude']}m
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # DISPLAY THE MEDIA - This is the key part!
        st.markdown('<div class="story-media-container">', unsafe_allow_html=True)
        
        if current_story.get('filepath') and os.path.exists(current_story['filepath']):
            if current_story['type'] == 'image':
                # Display image
                st.image(current_story['filepath'], use_container_width=True)
            else:
                # Display video - using st.video() with the file path
                try:
                    # Read the video file
                    with open(current_story['filepath'], 'rb') as f:
                        video_bytes = f.read()
                    
                    # Display video using bytes
                    st.video(video_bytes)
                except Exception as e:
                    st.error(f"Error loading video: {str(e)}")
                    # Fallback to placeholder
                    st.markdown(f"""
                    <div style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white;">
                        <div style="font-size: 64px; margin-bottom: 20px;">🎬</div>
                        <div style="font-size: 24px; margin-bottom: 10px;">Video</div>
                        <div style="font-size: 16px; opacity: 0.8;">{current_story['title']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Placeholder if file doesn't exist
            icon = '🎬' if current_story['type'] == 'video' else '📷'
            st.markdown(f"""
            <div style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white;">
                <div style="font-size: 64px; margin-bottom: 20px;">{icon}</div>
                <div style="font-size: 24px; margin-bottom: 10px;">
                    {'Video' if current_story['type'] == 'video' else 'Photo'}
                </div>
                <div style="font-size: 16px; opacity: 0.8;">{current_story['description'][:100]}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Story footer
        st.markdown(f"""
        <div class="story-footer">
            <div style="color: white; font-size: 16px; margin-bottom: 15px; line-height: 1.5;">
                {current_story['description']}
            </div>
            <div style="display: flex; justify-content: space-between; color: rgba(255,255,255,0.7); font-size: 14px;">
                <div>
                    <div style="font-weight: 600; margin-bottom: 5px;">📍 Location</div>
                    <div style="font-family: monospace;">{current_story['lat']:.4f}, {current_story['lon']:.4f}</div>
                </div>
                <div>
                    <div style="font-weight: 600; margin-bottom: 5px;">🕒 Time</div>
                    <div>{current_story['timestamp'][11:]}</div>
                </div>
                <div>
                    <div style="font-weight: 600; margin-bottom: 5px;">⬆️ Altitude</div>
                    <div>{current_story['altitude']}m</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        nav_col1, nav_col2, nav_col3 = st.columns([2, 6, 2])
        with nav_col1:
            if st.button("‹ Previous", key="nav_prev", use_container_width=True):
                prev_index = (st.session_state.current_story_index - 1) % len(st.session_state.media_data)
                st.session_state.current_story_index = prev_index
                st.rerun()
        
        with nav_col2:
            if st.button("✕ Close Story", type="secondary", key="close_story", use_container_width=True):
                st.session_state.viewing_story = None
                st.rerun()
        
        with nav_col3:
            if st.button("Next ›", key="nav_next", use_container_width=True):
                next_index = (st.session_state.current_story_index + 1) % len(st.session_state.media_data)
                st.session_state.current_story_index = next_index
                st.rerun()

# Main tabs
tab1, tab2, tab3 = st.tabs(["🗺️ Map", "📤 Upload", "📱 Stories"])

with tab1:
    st.markdown("### 📍 Media Locations")
    
    if st.session_state.media_data:
        # Display in a grid
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
                if st.button(f"👁️ View Story", key=f"view_{story['id']}", use_container_width=True):
                    st.session_state.viewing_story = story['id']
                    # Find the index
                    for i, s in enumerate(st.session_state.media_data):
                        if s['id'] == story['id']:
                            st.session_state.current_story_index = i
                            break
                    st.rerun()
    else:
        st.info("No media yet. Upload some photos or videos!")

with tab2:
    st.markdown("### 📤 Upload Media")
    
    with st.form("upload_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Location Details")
            lat = st.number_input("Latitude", value=34.0522, format="%.6f")
            lon = st.number_input("Longitude", value=-118.2437, format="%.6f")
            altitude = st.slider("Altitude (meters)", 0, 500, 100)
            
            st.markdown("#### Story Info")
            title = st.text_input("Title", placeholder="Name your story...")
            description = st.text_area("Description", placeholder="Describe your shot...", height=100)
        
        with col2:
            st.markdown("#### Upload File")
            uploaded_file = st.file_uploader(
                "Choose a photo or video",
                type=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi', 'mkv', 'webm'],
                key="uploader"
            )
            
            if uploaded_file:
                file_type = 'video' if any(x in uploaded_file.type for x in ['video', 'mp4', 'mov', 'avi']) else 'image'
                
                st.markdown(f"**Preview** ({file_type})")
                if file_type == 'image':
                    st.image(uploaded_file, use_container_width=True)
                else:
                    st.video(uploaded_file)
        
        # Submit button
        submitted = st.form_submit_button("🚀 Add to Map", type="primary", use_container_width=True)
        
        if submitted:
            if not uploaded_file:
                st.error("Please select a file!")
            elif not title or not description:
                st.error("Please add a title and description!")
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
                
                st.success(f"✅ '{title}' added to the map!")
                st.balloons()
                st.rerun()

with tab3:
    # Stats
    total = len(st.session_state.media_data)
    images = sum(1 for s in st.session_state.media_data if s['type'] == 'image')
    videos = total - images
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{total}</div>
            <div class="stats-label">TOTAL STORIES</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{images}</div>
            <div class="stats-label">PHOTOS</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{videos}</div>
            <div class="stats-label">VIDEOS</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display all stories
    st.markdown("### 📋 All Stories")
    
    if st.session_state.media_data:
        for idx, story in enumerate(st.session_state.media_data):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Story info
                st.markdown(f"""
                <div style="background: white; padding: 20px; border-radius: 15px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                        <div style="font-size: 20px; font-weight: 600; color: #000;">{story['title']}</div>
                        <span class="type-badge {'photo-badge' if story['type'] == 'image' else 'video-badge'}">
                            {story['type'].upper()}
                        </span>
                    </div>
                    
                    <div style="color: #666; font-size: 14px; margin-bottom: 10px;">
                        📅 {story['timestamp']} • 📍 {story['lat']:.4f}, {story['lon']:.4f} • ⬆️ {story['altitude']}m
                    </div>
                    
                    <div style="color: #444; font-size: 16px; line-height: 1.5;">
                        {story['description']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Show media if available
                if story.get('filepath') and os.path.exists(story['filepath']):
                    if story['type'] == 'image':
                        try:
                            with Image.open(story['filepath']) as img:
                                img.thumbnail((200, 150))
                                st.image(img, use_container_width=True)
                        except:
                            pass
                
                # Action buttons
                if st.button("👁️ View", key=f"viewall_{story['id']}", use_container_width=True):
                    st.session_state.viewing_story = story['id']
                    st.session_state.current_story_index = idx
                    st.rerun()
                
                if st.button("🗑️ Delete", key=f"delete_{story['id']}", use_container_width=True):
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
        st.info("No stories yet. Upload some media!")

# Footer
st.markdown("""
<div style="text-align: center; color: #999; font-size: 12px; padding: 30px 0; margin-top: 30px;">
    👻 Drone Media Map • Click "View" on any story to see it fullscreen!
</div>
""", unsafe_allow_html=True)
