from pytube import YouTube
link = input("Enter link of your video :\n")
yt = YouTube(link)
videos = yt.streams.filter(progressive=True).all()
i=1
for stream in videos:
    print(str(i)+" "+ str(stream))
    i+=1
stream_number =int(input("Enter number : "))
video=videos[stream_number-1]
video.download("H:\\Web Series")
print("\nfile downloaded".upper())
