from pytube import YouTube

link = input("Enter link of your video :")
yt = YouTube(link)
stream =yt.streams.get_by_itag('22')
stream.download("H:\\Web Series")
print("\nfile downloaded".upper())
