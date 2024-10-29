import streamlit as st
import yt_dlp
import os
from pathlib import Path
import re

def sanitize_filename(title):
    """Remove invalid characters from filename"""
    return re.sub(r'[<>:"/\\|?*]', '', title)

def get_video_info(url):
    """Get video information from URL"""
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

def download_video(url, quality, download_type, output_path):
    """Download video or audio from YouTube"""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Get video info first
        info = get_video_info(url)
        if not info:
            return None
            
        filename = sanitize_filename(info['title'])
        
        # Configure yt-dlp options based on download type and quality
        ydl_opts = {
            'paths': {'home': output_path},
            'outtmpl': os.path.join(output_path, f'{filename}.%(ext)s'),
            'progress_hooks': [progress_hook],
        }
        
        if download_type == "Audio":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:  # Video
            if quality == "Highest":
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            else:
                ydl_opts['format'] = 'best[height<=720][ext=mp4]'
        
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download([url])
            
            if error_code == 0:
                st.success("Download completed!")
                if download_type == "Audio":
                    return os.path.join(output_path, f"{filename}.mp3")
                else:
                    return os.path.join(output_path, f"{filename}.mp4")
            else:
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
st.set_page_config(page_title="YouTube Downloader", page_icon="📺")

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
        col1, col2 = st.columns(2)
        
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
            download_path = str(Path.home() / "Downloads")
            
            output_file = download_video(url, quality, download_type, download_path)
            
            if output_file:
                st.write(f"File saved to: {output_file}")

# Footer
st.markdown("---")
st.markdown(
    "Made with ❤️ by Rahul "
)