from django.contrib import admin
from .models import Recipe, Collection, Comment, Rating

admin.site.register([Recipe, Collection, Comment, Rating])


# Register your models here.
