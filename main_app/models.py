from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField
from cloudinary.uploader import destroy
from django.urls import reverse


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=255)
    source = models.URLField(blank=True, null=True)
    description = models.TextField()
    ingredients = models.TextField()
    instructions = models.TextField()
    photo = CloudinaryField("image", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    tags = models.ManyToManyField(Tag, blank=True, related_name="recipes")
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse("recipe_detail", kwargs={"recipe_id": self.pk})

    # delete image from cloudinary
    def delete(self, *args, **kwargs):
        if self.photo:
            try:
                destroy(self.photo.public_id)
            except Exception as e:
                print(f"Error deleting Cloudinary image: {e}")

        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title


class Collection(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collections")
    recipes = models.ManyToManyField(Recipe, related_name="collections", blank=True)

    def get_absolute_url(self):
        return reverse("collection_detail", kwargs={"collection_id": self.pk})

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Feedback(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="feedbacks"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("recipe", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.score}⭐ by {self.user.username} on {self.recipe.title}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_picture = CloudinaryField("image", blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
