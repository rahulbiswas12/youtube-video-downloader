import streamlit as st
import yt_dlp
import os
from pathlib import Path
import re
import tempfile
import subprocess
import json

# Define user agent and other common options
YDL_OPTIONS = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Sec-Fetch-Mode': 'navigate',
    },
    'cookiefile': None,  # Will be set in initialize_ydl
}

def initialize_ydl():
    """Initialize yt-dlp with cookies if provided"""
    cookie_file = None
    if 'cookie_data' in st.session_state:
        # Create temporary cookie file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(st.session_state.cookie_data)
            cookie_file = f.name
        YDL_OPTIONS['cookiefile'] = cookie_file
    return cookie_file

def check_ffmpeg():
    """Check FFmpeg installation"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
        return True
    except FileNotFoundError:
        st.error("FFmpeg is not installed. Please contact the administrator.")
        return False

def sanitize_filename(title):
    """Remove invalid characters from filename"""
    return re.sub(r'[<>:"/\\|?*]', '', title)

def get_video_info(url):
    """Get video information from URL"""
    try:
        cookie_file = initialize_ydl()
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Clean up temporary cookie file if it exists
            if cookie_file and os.path.exists(cookie_file):
                os.unlink(cookie_file)
                
            return {
                'title': info.get('title', 'Unknown'),
                'author': info.get('uploader', 'Unknown'),
                'length': f"{info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}",
                'views': info.get('view_count', 0),
                'thumbnail': info.get('thumbnail', None)
            }
    except Exception as e:
        if "Sign in to confirm you're not a bot" in str(e):
            st.error("YouTube is requesting verification. Please provide your cookies from youtube.com")
            show_cookie_instructions()
        else:
            st.error(f"Error fetching video info: {str(e)}")
        return None

def show_cookie_instructions():
    """Show instructions for getting YouTube cookies"""
    with st.expander("How to provide YouTube cookies"):
        st.markdown("""
        To bypass YouTube's verification:
        
        1. Go to [YouTube](https://www.youtube.com) and sign in
        2. Install the "Cookie-Editor" extension for your browser:
           - [Chrome](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
           - [Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)
        3. Click on the Cookie-Editor extension while on YouTube
        4. Click "Export" -> "Export as JSON" (This copies the cookies to your clipboard)
        5. Paste the cookies in the text area below
        """)

def download_video(url, quality, download_type):
    """Download video or audio from YouTube"""
    if not check_ffmpeg():
        return None
        
    try:
        # Create temporary directory for download
        with tempfile.TemporaryDirectory() as temp_dir:
            # Get video info first
            info = get_video_info(url)
            if not info:
                return None
                
            filename = sanitize_filename(info['title'])
            
            # Configure yt-dlp options
            download_opts = YDL_OPTIONS.copy()
            download_opts.update({
                'paths': {'home': temp_dir},
                'outtmpl': os.path.join(temp_dir, f'{filename}.%(ext)s'),
                'progress_hooks': [progress_hook],
                'ffmpeg_location': 'ffmpeg',
            })
            
            if download_type == "Audio":
                download_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
                final_extension = '.mp3'
            else:  # Video
                if quality == "Highest":
                    download_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    download_opts['format'] = 'best[height<=720][ext=mp4]'
                final_extension = '.mp4'
            
            cookie_file = initialize_ydl()
            
            # Download the video
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                error_code = ydl.download([url])
                
                # Clean up temporary cookie file
                if cookie_file and os.path.exists(cookie_file):
                    os.unlink(cookie_file)
                
                if error_code == 0:
                    # Find the downloaded file
                    downloaded_file = None
                    for file in os.listdir(temp_dir):
                        if file.startswith(filename):
                            downloaded_file = os.path.join(temp_dir, file)
                            break
                    
                    if downloaded_file and os.path.exists(downloaded_file):
                        # Read the file and return it as bytes
                        with open(downloaded_file, 'rb') as f:
                            file_bytes = f.read()
                            return {
                                'bytes': file_bytes,
                                'filename': filename + final_extension
                            }
                    
                st.error("Download failed!")
                return None
                    
    except Exception as e:
        st.error(f"Error downloading: {str(e)}")
        return None

def progress_hook(d):
    """Progress hook for download progress"""
    if d['status'] == 'downloading':
        try:
            total_bytes = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            
            if total_bytes:
                progress = (downloaded_bytes / total_bytes) * 100
                progress_bar.progress(int(progress))
                
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

# Cookie input section
with st.expander("YouTube Cookie Settings (Required if verification is requested)"):
    cookie_data = st.text_area(
        "Paste your YouTube cookies here (JSON format)",
        height=100,
        help="Paste the cookies exported from Cookie-Editor extension"
    )
    if cookie_data:
        try:
            # Validate JSON format
            json.loads(cookie_data)
            st.session_state.cookie_data = cookie_data
            st.success("Cookies loaded successfully!")
        except json.JSONDecodeError:
            st.error("Invalid cookie format. Please make sure to export as JSON.")

# Check FFmpeg at startup
if not check_ffmpeg():
    st.stop()

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
        
        with col1:
            download_type = st.radio("Download Type:", ["Video", "Audio"])
        
        with col2:
            if download_type == "Video":
                quality = st.radio("Video Quality:", ["Highest", "Standard"])
            else:
                quality = "Standard"  # Not used for audio
        
        # Download button and progress bar
        if st.button("Download"):
            progress_bar = st.progress(0)
            
            result = download_video(url, quality, download_type)
            
            if result:
                st.success("Download completed! Click below to save the file.")
                st.download_button(
                    label="Save File",
                    data=result['bytes'],
                    file_name=result['filename'],
                    mime='video/mp4' if download_type == "Video" else 'audio/mp3'
                )

# Footer
st.markdown("---")
st.markdown(
    "Made with ❤️ using Streamlit and yt-dlp. "
    "Note: This tool is for personal use only. "
    "Please respect copyright laws and YouTube's terms of service."
)
