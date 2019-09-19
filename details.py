import http.client
import json
from json2html import *
import urllib.request
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import media
import mimetypes
import re




def get_trailer(movie_id):
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    payload = "{}"
    conn.request("GET", "/3/movie/"+str(movie_id)+"/videos?&api_key=eedcd0a42e1921c7f3da84ad5fdeaa2a", payload)
    res = conn.getresponse()
    data = res.read()
    movie_trailers = json.loads(data.decode("utf-8"))
    trailer = movie_trailers['results'][0]['key']
    link = "https://www.youtube.com/embed/" + str(trailer)
    flink = """<div style="width: 680px; height: 458px; margin: 0 auto ; padding : 30px ;"><iframe style="width: 100%; height: 100%;" src="{}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>""".format(link)

    


    return flink








def get_reviews(movie_id):
    review_array = []
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    payload = "{}"
    conn.request("GET", "/3/movie/"+str(movie_id)+"/reviews?page=1&language=en-US&api_key=eedcd0a42e1921c7f3da84ad5fdeaa2a", payload)
    res = conn.getresponse()
    data = res.read()
    json_data = json.loads(data.decode("utf-8"))
    reviews = json_data['results']
    
    for review in reviews:
         review_array.append({'author' : review['author'], 'content' : review['content']})
    
    return review_array




def get_credits(movie_id , cast_type):
    cast_json = []
    
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    payload = "{}"
    conn.request("GET", "/3/movie/" + str(movie_id) + "/credits?api_key=eedcd0a42e1921c7f3da84ad5fdeaa2a", payload)
    res = conn.getresponse()
    data = res.read()
    json_data = json.loads(data.decode("utf-8"))

    cast = json_data[cast_type]

    #connecting to wordpress
    wp = Client('http://172.104.189.102/xmlrpc.php', 'octraves', 'octraves')

    for actor in cast :
         # image 
        try:
            url = "http://image.tmdb.org/t/p/w200" + actor['profile_path']
            image_name = str(actor['id']) + '.jpg'
            image_location = '/Users/user/Desktop/wordpress_images/' + image_name
            urllib.request.urlretrieve( url , image_location) # download the image
            image = image_location
            imageType = mimetypes.guess_type(str(image))[0]
            img_data = {
                        'name': image_name,
                        'type': imageType,  
                    }
            with open(image, 'rb') as img:
                    img_data['bits'] = xmlrpc_client.Binary(img.read())
        
            img_response =   wp.call(media.UploadFile(img_data))   
            print("image uploaded :  " + image_name)
            attachment_id = img_response['id'] # id to be appended in post
        
        except:
            pass
            
        if( actor['profile_path'] == None):
            img_tag = """<img  class="text" src=""" +"/wp-content/uploads/2018/10/{}".format("default-user-image.png") +  """ width="50" """ + """height="50" """ + "/>"
        
        else:
             img_tag = """<img  class="text" src=""" +"/wp-content/uploads/2018/10/{}".format(image_name) +  """ width="50" """ + """height="50" """ + "/>"
        


        cast_json.append(

            {'Profile' :img_tag,
            'Character': actor['character'] ,
             'Name  ': actor['name']}
        )

   
    # convert json object to html and remove escape characters like &lt; and &gt;
    return json2html.convert(json = cast_json, table_attributes="id=\"info-table\" class=\"table table-bordered table-hover\"").replace('&lt;', '<').replace('&gt;', '>') 


def get_credits_mini(movie_id) :
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    payload = "{}"
    conn.request("GET", "/3/movie/" + str(movie_id) + "/credits?api_key=eedcd0a42e1921c7f3da84ad5fdeaa2a", payload)
    res = conn.getresponse()
    data = res.read()
    json_data = json.loads(data.decode("utf-8"))

    cast = json_data['crew']

    return cast



#print(get_credits_mini(157336) )

def get_poster(movie_id) :
     #connecting to wordpress
    wp = Client('http://172.104.189.102/xmlrpc.php', 'octraves', 'octraves')
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    payload = "{}"
    conn.request("GET", "/3/movie/" + str(movie_id) + "/images?api_key=eedcd0a42e1921c7f3da84ad5fdeaa2a", payload)
    res = conn.getresponse()
    data = res.read()
    json_data = json.loads(data.decode("utf-8"))
    backdrops = json_data['backdrops']
    posters = json_data['posters']
    html = ["""<h2 class="w3-center">Screens</h2><div class="w3-content w3-display-container"  >"""]

    for backdrop in backdrops :
         # image 
        try:
            url = "http://image.tmdb.org/t/p/w400" + backdrop['file_path']
            image_name = re.sub('\ |\?|\!|\/|\;|\:', "" , backdrop['file_path']  )
            image_location = '/Users/user/Desktop/wordpress_images/' + image_name
            urllib.request.urlretrieve( url , image_location) # download the image
            image = image_location
            imageType = mimetypes.guess_type(str(image))[0]
            img_data = {
                        'name': image_name,
                        'type': imageType,  
                    }
            with open(image, 'rb') as img:
                    img_data['bits'] = xmlrpc_client.Binary(img.read())
        
            img_response =   wp.call(media.UploadFile(img_data))   
            print("image uploaded :  " + image_name)
            attachment_id = img_response['id'] # id to be appended in post
            html.append("""<img class="mySlides" src="/wp-content/uploads/2018/10/{}" style =" margin-left: 40%; " >""".format(image_name))
        
        except:
            pass
    
    for poster in posters :
         # image 
        try:
            url = "http://image.tmdb.org/t/p/w400" + poster['file_path']
            image_name = re.sub('\ |\?|\!|\/|\;|\:', "" , poster['file_path']  )
            image_location = '/Users/user/Desktop/wordpress_images/' + image_name
            urllib.request.urlretrieve( url , image_location) # download the image
            image = image_location
            imageType = mimetypes.guess_type(str(image))[0]
            img_data = {
                        'name': image_name,
                        'type': imageType,  
                    }
            with open(image, 'rb') as img:
                    img_data['bits'] = xmlrpc_client.Binary(img.read())
        
            img_response =   wp.call(media.UploadFile(img_data))   
            print("image uploaded :  " + image_name)
            attachment_id = img_response['id'] # id to be appended in post
            html.append("""<img class="mySlides" src="/wp-content/uploads/2018/10/{}" style =" margin-left: 40%; " >""".format(image_name))
        
        except:
            pass
        
    html.append("""<button class="w3-button w3-black w3-display-left" onclick="plusDivs(-1)">&#10094;</button><button class="w3-button w3-black w3-display-right" onclick="plusDivs(1)">&#10095;</button></div>""")
    

    final_html = "".join(html)
    return final_html
    

#print(get_poster(60275))
