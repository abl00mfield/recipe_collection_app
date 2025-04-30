from django.contrib import admin
from .models import Recipe, Collection, Tag, Feedback

admin.site.register([Recipe, Collection, Tag, Feedback])
