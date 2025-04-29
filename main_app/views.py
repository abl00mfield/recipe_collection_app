from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Recipe, Collection, Comment, Rating, Tag
from .forms import RecipeForm, CollectionForm, CommentForm, RatingForm, SignUpForm


def landing(request):
    return render(request, "landing.html")


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created succesfully!")
            return redirect("recipe_list")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


class Signin(LoginView):
    template_name = "registration/signin.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)


def signout(request):
    logout(request)
    return redirect("landing")


@login_required
def profile(request):
    pass


class RecipeList(ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
    context_object_name = "recipes"
    ordering = ["-created_at"]


class RecipeDetail(DetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    context_object_name = "recipe"
    pk_url_kwarg = "recipe_id"


class RecipeCreate(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    success_url = "/recipes/"

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        tag_names = form.cleaned_data.get("custom_tags", [])

        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name)
            self.object.tags.add(tag)

        messages.success(self.request, "Recipe created successfully!")
        return response


class RecipeUpdate(LoginRequiredMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    pk_url_kwarg = "recipe_id"


class RecipeDelete(LoginRequiredMixin, DeleteView):
    model = Recipe
    template_name = "recipes/recipe_confirm_delete.html"
    success_url = "/recipes/"
    pk_url_kwarg = "recipe_id"


class CollectionList(LoginRequiredMixin, ListView):
    model = Collection
    template_name = "collections/collection_list.html"
    context_object_name = "collections"

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user)


class CollectionDetail(LoginRequiredMixin, DetailView):
    model = Collection
    template_name = "collections/collection_detail.html"
    context_object_name = "collection"
    pk_url_kwarg = "collection_id"


class CollectionCreate(LoginRequiredMixin, CreateView):
    model = Collection
    form_class = CollectionForm
    template_name = "collections/collection_form.html"
    success_url = "/collections/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CollectionUpdate(LoginRequiredMixin, UpdateView):
    model = Collection
    form_class = CollectionForm
    template_name = "collections/collection_form.html"
    pk_url_kwarg = "collection_id"


class CollectionDelete(LoginRequiredMixin, DeleteView):
    model = Collection
    template_name = "collections/collection_confirm_delete.html"
    success_url = "/collections/"
    pk_url_kwarg = "collection_id"


# Custom FBV for adding/removing recipes from collections
@login_required
def collection_add_recipe(request, collection_id, recipe_id):
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    collection.recipes.add(recipe)
    return redirect("collection_detail", collection_id=collection.id)


@login_required
def collection_remove_recipe(request, collection_id, recipe_id):
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    collection.recipes.remove(recipe)
    return redirect("collection_detail", collection_id=collection.id)


@login_required
def add_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.recipe = recipe
            comment.save()
            return redirect("recipe_detail", recipe_id=recipe.id)
    else:
        form = CommentForm()
    return render(request, "comments/comment_form.html", {"form": form})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    recipe_id = comment.recipe.id
    comment.delete()
    return redirect("recipe_detail", recipe_id=recipe_id)


@login_required
def add_or_update_rating(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    rating, created = Rating.objects.get_or_create(user=request.user, recipe=recipe)
    if request.method == "POST":
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            return redirect("recipe_detail", recipe_id=recipe.id)
    else:
        form = RatingForm(instance=rating)
    return render(request, "ratings/rating_form.html", {"form": form, "recipe": recipe})
