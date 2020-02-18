from django.shortcuts import render, redirect
from django.contrib import messages

from django.views import generic
import json
from ast import literal_eval
import base64
import xml.etree.cElementTree as et
from data_load.services import get_photos_by_group_id, download_images, create_table, insert_into_db
from rest_framework.decorators import action, permission_classes, authentication_classes
from django.contrib.auth.decorators import login_required
@login_required
def get(request):
    '''
    Note: Login first, as the Model requires a userId.
    The function, on post request, will perform a series of operations. 
    => get_photos_by_group will return the XML file similar to 
        what "https://www.flickr.com/services/api/explore/flickr.groups.pools.getPhotos" would output

    => create_table would parse through the XML file obtained in the previous step and returns a list 
        of tuples. Where each tuple represents a row/sample in our FlickrModel. But data is not inserted yet.

    => download_images will once again parse through a separate link unique to every photoId and download the
        image and store it in media/pics folder.

    => insert_into_db, as the name suggests, finally inserts these tuples into the database.

    Three separate group Id's (Note: api_key may not work, use a new one. ).
    I. api_key: 626aa4f12aa5ed78ba8ac28d88b2963e, group_id: 16978849%40N00
    II. api_key: da6b8b4aedca7a12e6f08cea12dc968a, group_id: 34427469792%40N01
    III. api_key: 626aa4f12aa5ed78ba8ac28d88b2963e, group_id: 52239733174%40N01
    '''
    if request.method == "POST":
        photos_list = get_photos_by_group_id(
            request.POST["api_key"], request.POST["group_id"])
        table = create_table(
            photos_list, request.POST["group_id"], request.user.id)
        print(table)
        download_images(table, request.POST["api_key"])
        insert_into_db(table)
        messages.info(request, 'obtained')
        return redirect("get")
    else:
        return render(request, "getPhotosByGroups.html")
