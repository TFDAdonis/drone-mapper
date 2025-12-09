# Drone Media Mapping App

## Overview
A Streamlit-based drone media mapping application with a Snapchat Snap Map-inspired design. This app allows drone operators to visualize, manage, and upload geotagged drone imagery and videos on an interactive map.

## Project Structure
```
├── app.py                 # Main Streamlit application
├── .streamlit/
│   └── config.toml        # Streamlit server configuration
├── pyproject.toml         # Python dependencies
└── attached_assets/       # Design documentation
```

## Features

### Map View
- Interactive Folium map with Snapchat-inspired clean styling
- Custom circular markers: emerald green for images, orange-red for videos
- Popup overlays with media metadata (coordinates, altitude, timestamp)
- Satellite/terrain base map toggle options
- Map legend and statistics panel

### Upload Media
- Drag-and-drop upload zone for images and videos
- Real-time media preview
- GPS coordinate input with validation
- Altitude and description fields
- Toast notifications for upload feedback

### Gallery
- Media thumbnail grid view
- Filter by type (Images/Videos/All)
- Sort options (Newest, Oldest, Alphabetical)
- Quick view and delete actions
- Metadata display with coordinates

## Design System

### Color Palette
- **Light mode**: Clean whites (#fafafa) with subtle grays
- **Image markers**: Emerald green (#22c55e)
- **Video markers**: Orange-red (#f97316)
- **Interactive elements**: Vibrant blue (#2563eb)

### Typography
- **Primary font**: Inter (Google Fonts)
- **Monospace**: JetBrains Mono for coordinates/metadata

### Components
- Custom map markers with icons
- Responsive popup overlays
- Clean tab navigation
- Card-based media display

## Running the App
```bash
streamlit run app.py --server.port 5000
```

## Dependencies
- streamlit
- folium
- streamlit-folium
- Pillow
- pandas
- python-dateutil
