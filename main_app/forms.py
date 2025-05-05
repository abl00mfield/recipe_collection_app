from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import Recipe, Collection, Feedback, UserProfile
from cloudinary.uploader import destroy
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
        help_text='Enter tags separated by spaces, multi word tags in quotes (e.g dessert chocolate "peanut butter")',
    )

    class Meta:
        model = Recipe
        fields = [
            "title",
            "source",
            "description",
            "ingredients",
            "instructions",
            "photo",
            "photo_credit",
        ]
        widgets = {
            "photo": forms.ClearableFileInput(attrs={"class": "custom-file-input"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields["photo"].widget.attrs.update({"class": "custom-file-input"})

        # self.fields["photo"].widget.clear_checkbox_label = ""
        self.fields["photo"].widget.template_name = "widgets/clearable_file_input.html"
        # pre fill custom tags if editing
        if self.instance.pk:
            existing_tags = self.instance.tags.values_list("name", flat=True)
            formatted_tags = [
                f'"{tag}"' if " " in tag else tag for tag in existing_tags
            ]
            self.fields["custom_tags"].initial = " ".join(formatted_tags)

        if self.instance and self.instance.pk and self.instance.photo:
            self.fields["photo"].widget.attrs.update(
                {"data-has-photo": "true", "data-photo-url": self.instance.photo.url}
            )

    def clean_source(self):
        url = self.cleaned_data.get("source")
        if url:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            validator = URLValidator()
            try:
                validator(url)
            except ValidationError:
                raise forms.ValidationError("Please enter a valid URL")
        return url

    def clean_custom_tags(self):
        tag_string = self.cleaned_data.get("custom_tags", "").strip().lower()
        # Split on spaces except within quotes
        raw_tags = re.findall(r'"(.*?)"|(\S+)', tag_string)

        # Flatten the list of tuples from re.findall
        flat_tags = [tag[0] or tag[1] for tag in raw_tags]

        # clean data - remove foreign characters
        tag_names = []
        for tag in flat_tags:
            cleaned = re.sub(r"[^a-z0-9\- ]", "", tag)  # allow a-z, 0–9, dash, space
            if cleaned:
                tag_names.append(cleaned)

        return list(set(tag_names))

    def save(self, commit=True):
        recipe = super().save(commit=False)

        # detect if the photo was replaced
        if self.instance.pk:
            old_photo = Recipe.objects.get(pk=self.instance.pk).photo
            new_photo = self.cleaned_data.get("photo")

            # case 1: user uploads a new photo, old photo should be deleletd
            if new_photo and old_photo and new_photo != old_photo:
                try:
                    destroy(old_photo.public_id)

                except Exception as e:
                    print(f"Error deleting replaced Cloudinary image: {e}")

            # case 2: user cleared the image (checked "remove photo")
            elif not new_photo and old_photo:
                try:
                    destroy(old_photo.public_id)

                except Exception as e:
                    print(f"Error deleting replaced Cloudinary image: {e}")
                self.instance.photo = None

        if commit:
            recipe.save()
            self.save_m2m()
        return recipe


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


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "bio", "location", "profile_picture"]
