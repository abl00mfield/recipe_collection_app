from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models, IntegrityError
from django.db.models import Q, Avg, Count
from django.db.models.functions import Coalesce
from recipe_scrapers import scrape_me
from recipe_scrapers._exceptions import WebsiteNotImplementedError
import requests
from cloudinary.uploader import upload as cloudinary_upload


from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Recipe, Collection, Feedback, Tag, UserProfile
from .forms import (
    RecipeForm,
    CollectionForm,
    SignUpForm,
    FeedbackForm,
    UserProfileForm,
    ImportRecipeForm,
)


def landing(request):
    return render(request, "landing.html")


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(
                request, "Account created succesfully!, Let's finish your profile!"
            )
            return redirect("edit_profile")
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


class RecipeList(ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
    context_object_name = "recipes"
    # ordering = ["-created_at"]
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["page_title"] = "All Recipes"
        context["search_query"] = self.request.GET.get("q", "")

        # Clean the querystring for pagination links (remove page param)
        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        context["querystring"] = querydict.urlencode()

        collection_id = self.request.GET.get("collection_id")
        if collection_id and user.is_authenticated:
            try:
                target_collection = Collection.objects.get(id=collection_id, user=user)
                context["target_collection"] = target_collection

                context["target_collection_recipe_ids"] = set(
                    target_collection.recipes.values_list("id", flat=True)
                )
            except Collection.DoesNotExist:
                context["target_collection"] = None
                context["target_collection_recipe_ids"] = set()

        if user.is_authenticated:
            user_collections = (
                Collection.objects.filter(user=self.request.user)
                .prefetch_related("recipes")
                .order_by("name")
            )
            saved_recipe_ids = set()

            for collection in user_collections:
                saved_recipe_ids.update(collection.recipes.values_list("id", flat=True))

            context["user_collections"] = user_collections
            context["saved_recipe_ids"] = saved_recipe_ids
        else:
            context["user_collections"] = None

        context["selected_sort"] = self.request.GET.get("sort", "-created_at")
        context["selected_tag"] = self.request.GET.get("tag", "")
        context["all_tags"] = Tag.objects.all().order_by("name")
        return context

    def get_queryset(self):
        queryset = Recipe.objects.all().annotate(
            avg_rating=Coalesce(Avg("feedbacks__score"), 0.0),
            num_ratings=Count("feedbacks", filter=Q(feedbacks__score__isnull=False)),
        )

        # filter by tag
        tag_name = self.request.GET.get("tag")
        if tag_name:
            queryset = queryset.filter(tags__name__iexact=tag_name)

        # filter by search keyword
        query = self.request.GET.get("q")
        if query:
            terms = query.strip().split()
            q_objects = Q()
            for term in terms:
                q_objects &= (
                    Q(title__icontains=term)
                    | Q(description__icontains=term)
                    | Q(tags__name__icontains=term)
                    | Q(ingredients__icontains=term)
                )
            queryset = queryset.filter(q_objects).distinct()

        # sort
        sort = self.request.GET.get("sort", "-created_at")
        if sort == "title":
            queryset = queryset.order_by("title")
        elif sort == "-title":
            queryset = queryset.order_by("-title")
        elif sort == "most_popular":
            queryset = queryset.order_by("-avg_rating", "-created_at")
        elif sort == "most_rated":
            queryset = queryset.order_by("-num_ratings", "-created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset


class UserRecipeList(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
    context_object_name = "recipes"
    ordering = ["title"]
    paginate_by = 15

    def get_queryset(self):
        sort = self.request.GET.get("sort", "title")  # default sort
        queryset = Recipe.objects.filter(author=self.request.user).order_by(sort)

        tag_name = self.request.GET.get("tag")
        if tag_name:
            queryset = queryset.filter(tags__name__iexact=tag_name)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "My Recipes"

        user_collections = (
            Collection.objects.filter(user=self.request.user)
            .prefetch_related("recipes")
            .order_by("name")
        )
        saved_recipe_ids = set()

        for collection in user_collections:
            saved_recipe_ids.update(collection.recipes.values_list("id", flat=True))

        context["user_collections"] = user_collections
        context["saved_recipe_ids"] = saved_recipe_ids
        context["selected_sort"] = self.request.GET.get("sort", "title")
        context["user_tags"] = (
            Tag.objects.filter(recipes__author=self.request.user)
            .distinct()
            .order_by("name")
        )
        context["selected_tag"] = self.request.GET.get("tag", "All")

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

            user_collections = (
                Collection.objects.filter(user=self.request.user)
                .prefetch_related("recipes")
                .order_by("name")
            )

            context["user_collections"] = user_collections
            context["collections"] = recipe.collections.filter(user=user)

            if not existing_feedback:
                context["feedback_form"] = FeedbackForm()
            else:
                context["feedback_form"] = FeedbackForm(instance=existing_feedback)
        else:
            context["feedback_form"] = None

        context["feedbacks"] = recipe.feedbacks.select_related("user")
        feedbacks = recipe.feedbacks.all()
        avg = feedbacks.aggregate(models.Avg("score"))["score__avg"]
        total_ratings = feedbacks.count()
        context["average_score"] = round(avg or 0, 1)
        context["total_ratings"] = total_ratings

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


@login_required
def recipe_create_choice(request):
    return render(request, "recipes/recipe_create_choice.html")


def clean_scraper_tags(*args):
    """
    Takes any number of tag strings (comma-separated or single)
    and returns a clean space-separated string of quoted tags.
    """
    tag_list = []
    for raw in args:
        if not raw:
            continue
        # if isinstance(raw, (list, tuple)):
        #     raw = ", ".join(raw)

        for tag in raw.split(","):
            cleaned = tag.strip().replace('"', "")
            if not cleaned:
                continue
            if " " in cleaned:
                tag_list.append(f'"{cleaned}"')
            elif tag.lower() == "american":
                continue
            else:
                tag_list.append(cleaned)
    return " ".join(tag_list)


def safe_scrape(method_name, scraper):
    try:
        method = getattr(scraper, method_name, None)
        if callable(method):
            return method()
    except Exception:
        pass
    return ""


@login_required
def recipe_import(request):
    if request.method == "POST":
        form = ImportRecipeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data["url"]

            existing = Recipe.objects.filter(source=url).first()
            if existing:
                messages.error(
                    request, "This recipe already exists - redirecting you to it!"
                )
                return redirect("recipe_detail", recipe_id=existing.id)

            try:
                scraper = scrape_me(url)
                category = safe_scrape("category", scraper)
                cuisine = safe_scrape("cuisine", scraper)

                generated_tags = clean_scraper_tags(category, cuisine)

                author = safe_scrape("author", scraper)
                host = scraper.host()
                scraped_photo_credit = f"{author} via {host}" if author else host

                description = safe_scrape("description", scraper)

                scraped_description = description or f"Imported from {scraper.host()}"

                # ingredient groups
                try:
                    ingredient_groups = scraper.ingredient_groups()
                    grouped_lines = []
                    for group in ingredient_groups:
                        if group.purpose:
                            grouped_lines.append(f"[{group.purpose}]")
                        grouped_lines.extend(group.ingredients)
                    ingredients_text = "\n".join(grouped_lines)
                except Exception:
                    ingredients_text = "\n".join(scraper.ingredients())

                request.session["scraped_recipe"] = {
                    "title": scraper.title(),
                    "description": scraped_description,
                    "ingredients": ingredients_text,
                    "instructions": scraper.instructions(),
                    "source": form.cleaned_data["url"],
                    "photo_credit": scraped_photo_credit,
                    "custom_tags": generated_tags,
                }

                image_url = scraper.image()

                if image_url:
                    request.session["scraped_image_url"] = image_url
                return redirect("recipe_create")
            except WebsiteNotImplementedError:
                # Site not supported — send to manual form with message
                messages.error(
                    request,
                    "That site isn't supported for import, but you can enter the recipe manually.",
                )
                request.session["scraped_recipe"] = {
                    "source": url,
                }
                return redirect("recipe_create")
            except Exception as e:
                form.add_error(None, f"Failed to import: {e}")
    else:
        form = ImportRecipeForm()
    return render(request, "recipes/import_recipe.html", {"form": form})


class RecipeCreate(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    # success_url = "/recipes/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image_url = self.request.session.get("scraped_image_url")
        if image_url:
            context["scraped_image_url"] = image_url
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("signin")
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        # prefill form if scraped data is in session
        initial = super().get_initial()
        scraped_data = self.request.session.pop("scraped_recipe", None)
        if scraped_data:
            initial.update(scraped_data)
        return initial

    def form_valid(self, form):
        source = form.cleaned_data.get("source")
        if source:
            existing = Recipe.objects.filter(source=source).first()
            if existing:
                messages.error(
                    self.request, "This recipe already exists - here's the original"
                )
                return redirect("recipe_detail", recipe_id=existing.id)

        form.instance.author = self.request.user

        # check for scraped img URL in session
        image_url = self.request.session.pop("scraped_image_url", None)

        if image_url:
            headers = {"User-Agent": "Mozilla/5.0", "Referer": image_url}
            try:
                response = requests.get(image_url, headers=headers)

                if response.status_code == 200:
                    upload_result = cloudinary_upload(
                        response.content, resource_type="image", folder="recipe-box"
                    )
                    form.instance.photo = upload_result["public_id"]
            except Exception as e:
                messages.error(self.request, f"Could not fetch image: {e}")

        response = super().form_valid(form)

        tag_names = form.cleaned_data.get("custom_tags", [])
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name)
            self.object.tags.add(tag)

        messages.success(self.request, "Recipe created successfully!")
        return response

    def get_success_url(self):
        return reverse("recipe_detail", kwargs={"recipe_id": self.object.pk})


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

    def form_valid(self, form):
        messages.success(self.request, "Recipe deleted successfully!")
        return super().form_valid(form)


class CollectionList(LoginRequiredMixin, ListView):
    model = Collection
    template_name = "collections/collection_list.html"
    context_object_name = "collections"

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user).order_by("name")


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

        # check if the collection already exists for the user
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Collection created successfully!")
            return response
        except IntegrityError:
            form.add_error("name", "You already have a collection with this name.")
            return self.form_invalid(form)


class CollectionUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Collection
    form_class = CollectionForm
    template_name = "collections/collection_form.html"
    pk_url_kwarg = "collection_id"

    def test_func(self):
        collection = self.get_object()
        return self.request.user == collection.user

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            messages.success(self.request, "Collection updated successfully!")
            return super().form_valid(form)
        except IntegrityError:
            form.add_error("name", "You already have a collection with this name.")
            return self.form_invalid(form)


class CollectionDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Collection
    template_name = "collections/collection_confirm_delete.html"
    success_url = "/collections/"
    pk_url_kwarg = "collection_id"

    def test_func(self):
        collection = self.get_object()
        return self.request.user == collection.user

    def form_valid(self, form):
        messages.success(self.request, "Collection deleted successfully!")
        return super().form_valid(form)


# Custom FBV for adding/removing recipes from collections
@login_required
def collection_add_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == "POST":
        collection_id = request.POST.get("collection_id")
        next_url = request.POST.get("next")
        if not collection_id:
            messages.error(request, "Please select a collection")
            return redirect("recipe_list")

        collection = get_object_or_404(Collection, id=collection_id, user=request.user)

        if recipe not in collection.recipes.all():
            collection.recipes.add(recipe)
            messages.success(request, f'"{recipe.title}" was added to your collection.')
        else:
            messages.info(request, f'"{recipe.title}" is already in this collection.')

        if next_url:
            return redirect(next_url)

    return redirect("collection_detail", collection_id=collection.id)


@login_required
def create_collection_inline(request):
    if request.method == "POST":
        name = request.POST.get("name")
        recipe_id = request.POST.get("recipe_id")
        collection = None

        if name:
            try:
                collection = Collection.objects.create(name=name, user=request.user)
                messages.success(request, f"Collection {name} created!")
            except IntegrityError:
                collection = Collection.objects.filter(
                    name__iexact=name.title(), user=request.user
                ).first()
                messages.info(
                    request, f"You already have a collection named '{collection.name}'."
                )
                return redirect("recipe_list")

            # Add recipe to collection if provided
            if recipe_id and collection:
                recipe = get_object_or_404(Recipe, id=recipe_id)
                if recipe not in collection.recipes.all():
                    messages.success(request, f"{recipe.title} added!")
                    collection.recipes.add(recipe)

        else:
            messages.error(request, "Collection name is required")

        if collection:
            return redirect("collection_detail", collection_id=collection.id)

    return redirect("recipe_list")


@login_required
def collection_remove_recipe(request, collection_id, recipe_id):
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == "POST":
        collection.recipes.remove(recipe)
        messages.success(request, f'"{recipe.title}" removed from "{collection.name}".')

    return redirect("collection_detail", collection_id=collection.id)


@login_required
def set_collection_cover(request, collection_id, recipe_id):
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if recipe not in collection.recipes.all():
        messages.error(request, "That recipe is not part of the collection")
        return redirect("collection_detail", collection_id=collection.id)

    collection.cover_recipe = recipe
    collection.save()
    messages.success(request, f'"{recipe.title}" set as cover photo')
    return redirect("collection_detail", collection_id=collection.id)


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "users/profile.html", {"profile": profile})
