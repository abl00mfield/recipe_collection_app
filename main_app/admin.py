from django.contrib import admin
from .models import Recipe, Collection, Comment, Rating, Tag

admin.site.register([Recipe, Collection, Comment, Rating, Tag])
