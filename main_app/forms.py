from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe, Collection, Feedback
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


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["score", "comment"]
        labels = {"comment": "", "score": "Your Rating"}
        widgets = {
            "score": forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            "comment": forms.Textarea(
                attrs={"rows": 5, "placeholder": "Leave a comment..."}
            ),
        }
