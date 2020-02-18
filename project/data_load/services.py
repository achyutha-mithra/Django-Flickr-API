import requests
import shutil
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import random
import re
from .models import FlickrModel


def get_photos_by_group_id(api_key, group_id):
    '''
    XML file is obtained from the link, 
    and converted into UTF-8 equalent from Byte array format. 
    Returns the XML file.
    '''
    if "@" in group_id:
        group_id = re.sub("@", "%40", group_id)
    url = 'https://www.flickr.com/services/rest/?method=flickr.groups.pools.getPhotos&api_key=' + \
        api_key+"&group_id="+group_id

    retrieve = requests.get(url)
    fetched = retrieve._content.decode("UTF-8")
    return fetched


def create_table(xml_file, group_id, user):
    '''
    Will parse through the XML string, 
    uses regex to obtain required fields and and appends the final tuple(which will be the 
        fields representing one row) to a list.
    Returns a list of tuples. That is, a list of samples.
    '''
    final_list = []
    list_of_photos = xml_file.splitlines()
    list_of_photos = list_of_photos[3:-2]
    print(len(list_of_photos))
    for i in list_of_photos:
        intermediate_list = []
        intermediate_list.append(group_id)
        intermediate_list.append(
            int(re.search('photo id="(.+?)"', i).group(1)))
        intermediate_list.append(re.search('owner="(.+?)"', i).group(1))
        intermediate_list.append(re.search('secret="(.+?)"', i).group(1))
        intermediate_list.append(int(re.search('server="(.+?)"', i).group(1)))
        intermediate_list.append(int(re.search('farm="(.+?)"', i).group(1)))
        intermediate_list.append(re.search('title="(.+?)"', i).group(1))
        intermediate_list.append(
            bool(re.search('ispublic="(.+?)"', i).group(1)))
        intermediate_list.append(
            bool(re.search('isfriend="(.+?)"', i).group(1)))
        intermediate_list.append(
            bool(re.search('isfamily="(.+?)"', i).group(1)))
        intermediate_list.append(re.search('ownername="(.+?)"', i).group(1))
        intermediate_list.append(
            int(re.search('dateadded="(.+?)"', i).group(1)))
        intermediate_list.append(
            ("pics/"+re.search('photo id="(.+?)"', i).group(1))+".png")
        intermediate_list.append(user)
        intermediate_list = tuple(intermediate_list)
        final_list.append(intermediate_list)
    return final_list


def download_images(lst, api_key):
    '''
    This function will go to the photoId link and download the required image (.png).
    Parses the xml string once again (this time the xml belongs to a unique photoId) and 
        downloads the image (pattern to be matched "img src=") to media/pics folder.

    Note: Initial link present in photopage takes us to the flickr hosted page and using that link it  
        is not possible to download the image. So used BeautifulSoup to return all the images/gifs 
        present in that page, out of which the link present in "img src=" is of interest.
    '''
    for i in lst:
        url = 'https://www.flickr.com/services/rest/?method=flickr.photos.getInfo&api_key='+api_key+'&photo_id=' + \
            str(i[1])
        r = requests.get(url)
        f = r._content.decode("UTF-8")
        link = re.search('<url type="photopage">(.+?)<', f).group(1)
        link = link.replace(' ', '')
        link += "sizes/l"
        page = urlopen(link).read()
        soup = BeautifulSoup(page, "html.parser")
        img_tags = soup.find_all('img')
        for j in img_tags:
            if "img src" in str(j):
                link1 = re.search('img src="(.+?)"', str(j)).group(1)
                response = requests.get(link1, stream=True)
                with open("media/pics/"+str(i[1])+".png", 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response


def insert_into_db(lst):
    '''
    The list has tuples. This function will insert those tuples into the database.
    '''
    data = [

        FlickrModel(groupId=groupId, photoId=photoId, owner=owner, secret=secret, server=server, farm=farm, title=title,
                    isPublic=isPublic, isFriend=isFriend, isFamily=isFamily, ownerName=ownerName, dateAddedSeconds=dateAddedSeconds, img=img, userId=userId)
        for groupId, photoId, owner, secret, server, farm, title, isPublic, isFriend, isFamily, ownerName, dateAddedSeconds, img, userId in lst
    ]

    FlickrModel.objects.bulk_create(data)
