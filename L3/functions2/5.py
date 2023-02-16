def filter (movies, category):
    result = 0
    divisor = 0
    for film in movies:
        if film["category"] == category:
            result += film["imdb"]
            divisor += 1
    return result/divisor

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
"category": "Action"
}]

print(filter(movies, "Action"))