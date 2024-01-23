from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
import random
import concurrent.futures
import time

executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

CALLBACK_URL = "http://127.0.0.1:8080"

def get_group_availability(pk, token):
    time.sleep(5)
    return {
        "id": pk,
        "token": token,
        "availability": random.choice(["Доступен", "Недоступен"])
    }

def group_availability_callback(task):
    try:
        result = task.result()
    except concurrent.futures._base.CancelledError:
        return

    if (random.randint(1, 5) == 3):
        result["availability"] = "error"

    nurl = str(CALLBACK_URL + '/enrollment_to_group/set_group_availability?id=' + result["id"] + '&availability=' + result["availability"])
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + str(result["token"])}

    requests.put(nurl, json={}, timeout=3, headers=headers)

@api_view(['POST'])
def set_group_availability(request):
    print(request.data)
    if "token" not in request.data.keys():
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if "token" in request.data.keys() and "pk" in request.data.keys():
        id = request.data["pk"]
        token = request.data["token"]
        task = executor.submit(get_group_availability, id, token)
        task.add_done_callback(group_availability_callback)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)
