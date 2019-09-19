import http.client
import json

def get_genres(genre_array):
    name_array=[]
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    payload = "{}"
    conn.request("GET", "/3/genre/movie/list?language=en-US&api_key=eedcd0a42e1921c7f3da84ad5fdeaa2a", payload)
    res = conn.getresponse()
    data = res.read()
    json_data = json.loads(data.decode("utf-8"))
    for genre in json_data['genres']:
        for key in genre_array:
           if genre['id']== key: 
               name_array.append(genre['name'])



    return name_array


#print(get_genres([28 , 12]))    

def get_primary_info(movie_id):
    details_array = {}
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    payload = "{}"
    conn.request("GET", "/3/movie/"+str(movie_id)+"?page=1&language=en-US&api_key=eedcd0a42e1921c7f3da84ad5fdeaa2a", payload)
    res = conn.getresponse()
    data = res.read()
    movie = json.loads(data.decode("utf-8"))
    genre_arr = []
    for genre in movie['genres']:
        genre_arr .append(genre['name'] )
    genre_string = " ,  ".join(genre_arr)
    details_array.update( {'status' : movie['status']} )
    details_array.update( {'budget' : movie['budget'] } ) 
    details_array.update(  {'genres' : genre_string } ) 
    details_array.update( { 'release_date' : movie['release_date'] } )
    details_array.update( { 'language' : movie['spoken_languages'][0]['name'] }  )
    details_array.update(  {'revenue' : movie['revenue']} )
    details_array.update(  {'runtime' : movie['runtime']} )      
    
    html = "<h3>Facts</h3>" + "<dl> <dt> Status  </dt>" + "<dd> - {}</dd>".format( details_array['status']) + "<dt> Budget  </dt>" + "<dd> - ${}</dd>".format( details_array['budget']) + " <dt> Genres  </dt>" + "<dd> - {}</dd>".format( details_array['genres']) + "<dt> Release Date  </dt>" + "<dd> - {}</dd>".format( details_array['release_date']) + "<dt> Languages  </dt>" + "<dd> - {}</dd>".format( details_array['language']) + "<dt> Revenue </dt>" + "<dd> - ${}</dd>".format( details_array['revenue']) + "<dt>Runtime </dt>" + "<dd> - {} min</dd>".format( details_array['runtime']) + "</dl>"


    return html



#print(get_primary_info(157336))
