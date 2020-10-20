import subprocess
import sys
import os


# checks if the required 'youtube-dl' package is available
def check():
    import importlib
    try:                            # CHECKS if AVAILABLE
        importlib.import_module('youtube_dl')

    except ModuleNotFoundError:     # if NOT AVAILABLE --> then installs 'youtube-dl' python package
        print('youtube-dl NOT FOUND in this Computer !')
        print('The SCRIPT will install youtube-dl python package . . .')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'youtube-dl'])

    finally:                        # if AVAILABLE --> then proceeds with downloading the music
        globals()['youtube_dl'] = importlib.import_module('youtube_dl')
        run()




# Returns the default downloads path for linux or windows
def get_download_path():
    if os.name == 'nt':         # for WINDOWS system
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:                       # for LINUX & MAC
        return os.path.join(os.path.expanduser('~'), 'downloads')






# gets ./ffmpeg.exe PATH 
ffmpeg_path = os.getcwd()

'''sets DEFALUT PATH for download Location'''
path = get_download_path()

''' add a CUSTOM PATH for download loaction (remove '#' from the line BELOW & add the new PATH inside ' '(quotes) '''
#path = ''

# Main Download Script
def run():
    options = {
        # PERMANENT options
        'format': 'bestaudio/best',
        'ffmpeg_location': f'{ffmpeg_path}/ffmpeg.exe',
        'keepvideo': False,
        'outtmpl': f'{path}/%(title)s.*',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320'
        }],

        #(OPTIONAL options)
        'noplaylist': True
    }

    # the 'youtube_dl' module will be imported on program run
    with youtube_dl.YoutubeDL(options) as mp3:
        mp3.download(sys.argv[1:])
        






# runs Main Download Script
if __name__ == '__main__':
    check()
