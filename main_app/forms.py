from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe, Collection, Comment, Rating
import re


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class RecipeForm(forms.ModelForm):
    custom_tags = forms.CharField(
        max_length=255,
        required=False,
        help_text="Enter tags separated by spaces (e.g dessert pie chocolate)",
    )

    class Meta:
        model = Recipe
        fields = ["title", "description", "ingredients", "instructions", "photo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # pre fill custom tags if editing
        if self.instance.pk:
            exisiting_tags = self.instance.tags.values_list("name", flat=True)
            self.fields["custom_tags"].initial = " ".join(exisiting_tags)

    def clean_custom_tags(self):
        tag_string = self.cleaned_data.get("custom_tags", "").strip().lower()
        raw_tags = tag_string.split()

        # clean data - remove foriegn characters
        tag_names = [
            re.sub(r"[^a-z]", "", tag) for tag in raw_tags if re.sub(r"[^a-z]", "", tag)
        ]

        return list(set(tag_names))


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
