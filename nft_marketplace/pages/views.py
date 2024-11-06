import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template.defaultfilters import slugify
import json
from pydantic import ValidationError
from .models import NFTModel, NFTItemsModel, ONE_NFT_Item_Model
from dotenv import load_dotenv
from django.conf import settings
import os

server_ip = settings.SERVER_IP

def home_page_view(request):
    return render(request, "home/home.html", {'title': 'NFT Marketplace on TON'})


def about_us(request):
    data = {
    }
    return render(request, "about_us/about_us.html", context=data)

# общая страница маркетплейса с подборками
def collections(request):
    return render(request, "collections/collections.html", {'title': 'Collections'})

# страница для конкретных коллекций
def collections_items(request, collection_address):

    response_collections = requests.get(f"http://{server_ip}/nfts/collections/{collection_address}") # GET-запрос для коллекции
    # Проверка успешности запроса
    if response_collections.status_code == 200:
        data = response_collections.json()  # Получаем JSON
        title = data.get("metadata", {}).get("name", "Default Title")
        try:
            nft_data = NFTModel(**data)  # Валидируем все через модель
        except ValidationError as e:
            return HttpResponse(f"Ошибка валидации данных: {e}", status=400)
    else:
        return HttpResponse("Ошибка при запросе данных.", status=500)

    # Создание GET-запроса для итемов коллекции
    response_items_collections = requests.get(f"http://{server_ip}/nfts/collections/{collection_address}/items")
    if response_items_collections.status_code == 200:
        nfts_data = response_items_collections.json()
        try:
            nft_item_data = NFTItemsModel(**nfts_data)
            valid_nfts_data = json.loads(nft_item_data.json())
        except ValidationError as e:
            return HttpResponse(f"Ошибка валидации данных: {e}", status=400)
    else:
        return HttpResponse("Ошибка при запросе данных.", status=500)


    return render(request, "collections/collection_items.html", {
        "data": nft_data,
        "title": title,
        "nfts": valid_nfts_data,
    })


# def collections_nft_item(request, collection_address, nft_address): #принимаю нфтишки
#     # Создание GET-запроса для итемов коллекции
#     response_items_collections = requests.get(f"http://{server_ip}/nfts/collections/{collection_address}/{nft_address}")
#     if response_items_collections.status_code == 200:
#         nfts_data = response_items_collections.json()
#         title = nfts_data.get("metadata", {}).get("name", "Default Title")
#         try:
#             nft_item_data = NFTItemsModel(**nfts_data)
#             valid_nfts_data = json.loads(nft_item_data.json())
#         except ValidationError as e:
#             return HttpResponse(f"Ошибка валидации данных: {e}", status=400)
#     else:
#         return HttpResponse("Ошибка при запросе данных.", status=500)
#     return render(request, "NFT/nft_item.html",
#                   {"data": nft_item_data,
#                    'title': title},
#                   )

# страница для одиночных NFT
def nft_item(request, nft_item_address, collection_address): #принимаю нфтишки
    response = requests.get(f"http://{server_ip}/nfts/{nft_item_address}")
    if response.status_code == 200:
        data_one = response.json()
        title = data_one.get("metadata", {}).get("name", "Default Title")
        try:
            nft_data_one = ONE_NFT_Item_Model(**data_one)
        except ValidationError as e:
            return HttpResponse(f"Ошибка валидации данных: {e}", status=400)
    else:
        return HttpResponse("Ошибка при запросе данных.", status=500)

    return render(request, "NFT/nft_item.html",
                  {"data": data_one,
                   'title': title},
                  )


def feedback(request):
    return render(request, "feedback/feedback.html", {'title': 'Feedback'})


def profile(request):
    return render(request, "profile/profile.html", {'title': 'Profile'})


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


