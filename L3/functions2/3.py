def filter (movies, category):
    result = []
    for film in movies:
        if film["category"] == category:
            result.append(film)
    return result

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

print(filter(movies, "Action"))