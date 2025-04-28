from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe, Collection, Comment, Rating


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["title", "description", "ingredients", "instructions", "photo"]


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ["name"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["score"]
        widgets = {
            "score": forms.Select(
                choices=[
                    (1, "⭐ 1 Star"),
                    (2, "⭐⭐ 2 Stars"),
                    (3, "⭐⭐⭐ 3 Stars"),
                    (4, "⭐⭐⭐⭐ 4 Stars"),
                    (5, "⭐⭐⭐⭐⭐ 5 Stars"),
                ]
            )
        }
