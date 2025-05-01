from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Recipe, Collection, Feedback, Tag
from .forms import (
    RecipeForm,
    CollectionForm,
    SignUpForm,
    FeedbackForm,
)


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
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["page_title"] = "All Recipes"

        if user.is_authenticated:
            context["user_collections"] = Collection.objects.filter(
                user=self.request.user
            )
        else:
            context["user_collections"] = None
        return context


class UserRecipeList(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
    context_object_name = "recipes"
    ordering = ["title"]

    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "My Recipes"
        context["user_collections"] = Collection.objects.filter(user=self.request.user)
        return context


class RecipeDetail(DetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    context_object_name = "recipe"
    pk_url_kwarg = "recipe_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.object
        user = self.request.user

        if user.is_authenticated:
            existing_feedback = Feedback.objects.filter(
                recipe=recipe, user=user
            ).first()
            context["user_collections"] = Collection.objects.filter(user=user)
            context["collections"] = recipe.collections.all()

            if not existing_feedback:
                context["feedback_form"] = FeedbackForm()
            else:
                context["feedback_form"] = FeedbackForm(instance=existing_feedback)
        else:
            context["feedback_form"] = None

        context["feedbacks"] = recipe.feedbacks.select_related("user")
        avg = recipe.feedbacks.aggregate(models.Avg("score"))["score__avg"]
        context["average_score"] = round(avg or 0, 1)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not request.user.is_authenticated:
            return redirect("signin")

        existing_feedback = Feedback.objects.filter(
            recipe=self.object, user=request.user
        ).first()
        form = FeedbackForm(request.POST, instance=existing_feedback)

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.recipe = self.object
            feedback.save()

        return redirect("recipe_detail", recipe_id=self.object.pk)


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


class RecipeUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    pk_url_kwarg = "recipe_id"

    def form_valid(self, form):
        form.instance.author = self.request.user

        self.object.tags.clear()
        tag_names = form.cleaned_data.get("custom_tags", [])
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name)
            self.object.tags.add(tag)

        messages.success(self.request, "Recipe updated successfully!")
        return super().form_valid(form)

    def test_func(self):
        recipe = self.get_object()
        return self.request.user == recipe.author


class RecipeDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipe
    template_name = "recipes/recipe_confirm_delete.html"
    success_url = "/recipes/"
    pk_url_kwarg = "recipe_id"

    def test_func(self):
        recipe = self.get_object()
        return self.request.user == recipe.author

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, "Recipe Deleted")
        return response


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


class CollectionUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Collection
    form_class = CollectionForm
    template_name = "collections/collection_form.html"
    pk_url_kwarg = "collection_id"

    def test_func(self):
        collection = self.get_object()
        return self.request.user == collection.user


class CollectionDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Collection
    template_name = "collections/collection_confirm_delete.html"
    success_url = "/collections/"
    pk_url_kwarg = "collection_id"

    def test_func(self):
        collection = self.get_object()
        return self.request.user == collection.user

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, "Collection Deleted")
        return response


# Custom FBV for adding/removing recipes from collections
@login_required
def collection_add_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == "POST":
        collection_id = request.POST.get("collection_id")
        if not collection_id:
            messages.error(request, "Please select a collection")
            return redirect("recipe_list")

        collection = get_object_or_404(Collection, id=collection_id, user=request.user)

        if recipe not in collection.recipes.all():
            collection.recipes.add(recipe)
            messages.success(request, f'"{recipe.title}" was added to your collection.')
        else:
            messages.info(request, f'"{recipe.title}" is already in this collection.')

    return redirect("collection_detail", collection_id=collection.id)


@login_required
def create_collection_inline(request):
    if request.method == "POST":
        name = request.POST.get("name")
        recipe_id = request.POST.get("recipe_id")
        if name:
            collection = Collection.objects.create(name=name, user=request.user)
            if recipe_id:
                recipe = get_object_or_404(Recipe, id=recipe_id)
                collection.recipes.add(recipe)
            messages.success(request, f"Collection '{name}' created!")
        else:
            messages.error(request, "Collection name is required")
    if collection:
        return redirect("collection_detail", collection_id=collection.id)
    else:
        return redirect("recipe_list")


@login_required
def collection_remove_recipe(request, collection_id, recipe_id):
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == "POST":
        collection.recipes.remove(recipe)
        messages.success(request, f'"{recipe.title}" removed from "{collection.name}".')

    return redirect("collection_detail", collection_id=collection.id)
