import streamlit as st
import yt_dlp
import os
from pathlib import Path
import re
import tempfile
from typing import Dict, Optional, Union

def sanitize_filename(title: str) -> str:
    """Remove invalid characters from filename."""
    return re.sub(r'[<>:"/\\|?*]', '', title)

def get_video_info(url: str) -> Optional[Dict[str, Union[str, int]]]:
    """
    Fetch video metadata from YouTube URL.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Dictionary containing video metadata or None if error
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown'),
                'author': info.get('uploader', 'Unknown'),
                'length': f"{info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}",
                'views': info.get('view_count', 0),
                'thumbnail': info.get('thumbnail', None)
            }
    except Exception as e:
        st.error(f"Error fetching video info: {str(e)}")
        return None

def download_file(url: str, quality: str) -> Optional[bytes]:
    """
    Download video/audio file from YouTube URL.
    
    Args:
        url: YouTube video URL
        quality: Video quality (e.g., 144p, 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p, 4k)
        
    Returns:
        File bytes if successful, None if error
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s')
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                for file in os.listdir(temp_dir):
                    if file.endswith(('.mp4', '.mp3', '.webm')):
                        downloaded_file = os.path.join(temp_dir, file)
                        with open(downloaded_file, 'rb') as f:
                            return f.read()
    except Exception as e:
        st.error(f"Error downloading: {str(e)}")
        return None

def progress_hook(d: Dict) -> None:
    """Update progress bar during download."""
    if not hasattr(st.session_state, 'progress_bar'):
        return
        
    try:
        total_bytes = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
        downloaded_bytes = d.get('downloaded_bytes', 0)
        if total_bytes:
            progress = (downloaded_bytes / total_bytes) * 100
            st.session_state.progress_bar.progress(int(progress))
    except Exception:
        pass

# Set page config
st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="📺",
    layout="centered"
)

# Add custom CSS
st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
            background-color: #FF0000;
            color: white;
        }
        .stButton>button:hover {
            background-color: #CC0000;
            color: white;
        }
        .reportview-container {
            background: #FAFAFA
        }
    </style>
""", unsafe_allow_html=True)

# Main UI
st.title("📺 YouTube Video Downloader")
st.write("Download videos and audio from YouTube")

# Input fields
url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    # Get video information
    info = get_video_info(url)
    
    if info:
        # Display video information
        col1, col2 = st.columns([2, 3])
        
        with col1:
            if info['thumbnail']:
                st.image(info['thumbnail'], use_column_width=True)
        
        with col2:
            st.write(f"**Title:** {info['title']}")
            st.write(f"**Author:** {info['author']}")
            st.write(f"**Duration:** {info['length']}")
            st.write(f"**Views:** {info['views']:,}")
        
        # Download options
        col1, col2 = st.columns(2)
        
        download_type = st.radio("Download Type:", ["Video", "Audio"])
        if download_type == "Video":
            quality = st.selectbox("Video Quality:", ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4k"])
        else:
            quality = "Standard"  # Not used for audio
        
        # Download button and progress bar
        if st.button("Download"):
            st.session_state.progress_bar = st.progress(0)
            
            # Configure download options
            ydl_opts = {
                'outtmpl': '%(title)s.%(ext)s',
                'progress_hooks': [progress_hook],
            }
            
            if download_type == "Video":
                if quality == "144p":
                    ydl_opts['format'] = 'best[height<=144][ext=mp4]'
                elif quality == "240p":
                    ydl_opts['format'] = 'best[height<=240][ext=mp4]'
                elif quality == "360p":
                    ydl_opts['format'] = 'best[height<=360][ext=mp4]'
                elif quality == "480p":
                    ydl_opts['format'] = 'best[height<=480][ext=mp4]'
                elif quality == "720p":
                    ydl_opts['format'] = 'best[height<=720][ext=mp4]'
                elif quality == "1080p":
                    ydl_opts['format'] = 'best[height<=1080][ext=mp4]'
                elif quality == "1440p":
                    ydl_opts['format'] = 'best[height<=1440][ext=mp4]'
                elif quality == "2160p":
                    ydl_opts['format'] = 'best[height<=2160][ext=mp4]'
                else:  # 4k
                    ydl_opts['format'] = 'best[height<=3840][ext=mp4]'
            else:
                ydl_opts['format'] = 'bestaudio[ext=m4a]'
            
            result = download_file(url, quality)
            
            if result:
                st.success("Download completed! Click below to save the file.")
                filename = sanitize_filename(info['title']) + ('.mp4' if download_type == "Video" else '.m4a')
                st.download_button(
                    label="Save File",
                    data=result,
                    file_name=filename,
                    mime='video/mp4' if download_type == "Video" else 'audio/x-m4a'
                )

# Footer
st.markdown("---")
st.markdown(
    "Made with ❤️ by Rahul"
)
