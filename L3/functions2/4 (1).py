def averageidmb (movies):
    result = 0
    for film in movies:
        result += film["imdb"]
        return result/len(movies)

movies = [{
"name": "Usual Suspects", 
"imdb": 7.0,
"category": "Action"
},
{
"name": "Hitman",
"imdb": 5,
"category": "Action"
},
{
"name": "Dark Knight",
"imdb": 3.0,
"category": "Adventure"
}]
print(averageidmb(movies))