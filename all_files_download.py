import pytube
video_url = input("\nenter your url: \n".upper())
youtube = pytube.YouTube(video_url)
video = youtube.streams.all()
i = 1
for stream in video:
    print(f"{str(i)} -> {str(stream)}")
    i += 1

stream_number = int(input("\nEnter number : "))
download_stream_number = video[stream_number-1]

download_stream_number.download('H:\\Web Series')
print("\nfile downloaded".upper())
