def imdb(movie):
    return movie["imdb"]>5.5
        

print(imdb({"name": "Usual Suspects","imdb": 7.0,"category": "Thriller"}))