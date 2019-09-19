from wordpress_xmlrpc import Client, WordPressPost , WordPressComment
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts  ,comments
import urllib.request
import http.client
import json
import mimetypes
import genres
import details
from json2html import *
from multiprocessing import Pool
from itertools import repeat




def add_movies(page_num , choice):
   

    while True :
    
        if(choice == 'a' or choice == 'upcoming'):
            term_tag = 'upcoming'
            term_cat = 'upcoming'
            get_url = "/3/movie/upcoming?page="+ str(page_num) + "&language=en-US&api_key=eedcd0a42e1921c7f3da84ad5fdeaa2a"

        if(choice == 'b' or choice == 'nowplaying'):
            term_tag = 'Now playing'
            term_cat = 'now_playing'
            get_url = "/3/movie/now_playing?page="+ str(page_num) + "&language=en-US&api_key=eedcd0a42e1921c7f3da84ad5fdeaa2a"

        if(choice == 'c' or choice == 'archives' or choice == 'archive'):
        
            term_tag = 'archives'
            term_cat = 'archives'
            get_url = "/3/discover/movie?page="+ str(page_num) + "&language=en-US&primary_release_date.lte=" + str(date) + "&api_key=eedcd0a42e1921c7f3da84ad5fdeaa2a"
        try:
            #making the connection to the api 
            print("making the connection")
            conn = http.client.HTTPSConnection("api.themoviedb.org")
            payload = "{}"
            print("getting all the movies from page " + str(page_num))
            
            
            #getting the movies data , key = now playing 
            print("making the api req")
            #print(get_url , term_cat , term_tag)
                
            conn.request("GET", get_url , payload)
            res = conn.getresponse()
            data = res.read()
            response = json.loads(data.decode("utf-8"))

            #connecting to wordpress
            wp = Client('http://172.104.189.102/xmlrpc.php', 'octraves', 'octraves')

            # THE MAIN LOOP FOR ADDING ALL THE MOVIES TO THE WP DATABASE
            counter = 1
            for movie in response['results']:
                try:
                    
                    print("Adding movie number = " + str(counter) +"id :  " + str(movie['id'] ) ) 
                    #download and upload the image to wordpress
                    url = "http://image.tmdb.org/t/p/w200" + movie['poster_path'] 
                    image_name = str(movie['id']) + '.jpg'
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

                    img_response = wp.call(media.UploadFile(img_data))   
                    attachment_id = img_response['id'] # id to be appended in post

                    #getting the trailer
                    try:
                        link = details.get_trailer(movie['id'])
                    except:
                        link = ""
                        pass
                    

                    

                    # Creating custom fields 
                    fields = [ ['Languages', movie['original_language'] ], ['Release Date', movie['release_date'] ] ]

                    # Creating the post
                    post = WordPressPost()
                    post.title = movie['title']
                    post.post_type = 'post'
                    post.mime_type = "text/html"
                    post.content =genres.get_primary_info(movie['id']) +  """<h3> Overview </h3> """ + movie['overview'] +  """<h3> Trailer </h3> """ + " \n" + link + " \n" + " \n"  + " \n" +"""<h3> Credits </h3> """ + " \n" + " \n" + " \n"  + str(details.get_credits(movie['id'], 'cast')) + details.get_poster(movie['id'])
                    
                    
                    post.thumbnail = attachment_id
                    post.terms_names = {
                        'post_tag': [term_tag],
                            term_cat :  genres.get_genres(movie['genre_ids']),
                        'category':  genres.get_genres(movie['genre_ids'])
                                        }
                    
                    post.custom_fields = [] 
                    for field in fields:
                        post.custom_fields.append(
                        {'key' : field[0], 'value' : field[1]}
                                                )
                    post.post_status = 'publish'
                    post.comment_status = 'open'

                    #finally publish the post !!
                    post.id = wp.call(posts.NewPost(post))
                    
                    
                    #add comments
                    reviews = details.get_reviews(movie['id'])
                    for review in reviews :
                        comment =  WordPressComment()
                        comment.author = review['author']
                        comment.content = review['content']
                        wp.call(comments.NewComment(post.id , comment))
                    

                    counter+=1
                
                except Exception as e:
                    print ("All the pages have been processed or there is a error!!  " + str(e))
                    pass

                
            print("Page number " + str(page_num) + " is completed ! Loading another page.")
                
            page_num+=1
                
                

            
        except Exception as e :
            print(str(e))




    
   
if __name__ == '__main__':
    stra = str(input("Enter the category you want to upload \n A) Upcoming \n B) Now playing  \n C) Archives \n "))
    strb = stra.replace(" ", "")
    choice =strb.lower()

    if(choice == 'c' or choice == 'archives' or choice == 'archive'):
          date = input("please specify the date you need archives from : \n for example 2017-01-01 means archives from 2017 January and backwards \n ")

    p = Pool(5)
    p.starmap(add_movies,zip( [25, 27, 30] , repeat(choice) )) 