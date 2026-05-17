import requests
from django.views import View
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages


API_URL = settings.API_URL
TOKEN = settings.API_TOKEN

HEADERS = {
    "Authorization": f"Token {TOKEN}"
}


class CategoryListView(View):
    def get(self, request):
        response = requests.get(API_URL, headers=HEADERS)
        data = response.json()

        if "results" in data:
            categories = data["results"]
        else:
            categories = data

        return render(request, "categories/list.html", {
            "categories": categories
        })


class CategoryCreateView(View):
    def get(self, request):
        return render(request, "categories/form.html")

    def post(self, request):
        files = {}
        if request.FILES.get("icon"):
            files["icon"] = request.FILES["icon"]

        data = {
            "name": request.POST.get("name"),
            "description": request.POST.get("description"),
            "color": request.POST.get("color"),
            "order": request.POST.get("order"),
            "is_active": True,
        }


        requests.post(API_URL, headers=HEADERS, data=data, files=files)
        messages.success(request, "Категория создана ✅")
        return redirect("/categories/")



class CategoryUpdateView(View):
    def get(self, request, id):
        response = requests.get(f"{API_URL}{id}/", headers=HEADERS)

        return render(request, "categories/form.html", {
            "category": response.json()
        })

    def post(self, request, id):
        files = {}
        if request.FILES.get("icon"):
            files["icon"] = request.FILES["icon"]

        data = request.POST.dict()

        requests.patch(
            f"{API_URL}{id}/",
            headers=HEADERS,
            data=data,
            files=files
        )

        return redirect("/categories/")
