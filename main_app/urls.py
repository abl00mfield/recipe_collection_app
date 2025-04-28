from django.urls import path
from . import views

urlpatterns = [
    # User authentication
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin_view, name="signin"),
    path("signout/", views.signout_view, name="signout"),
    path("profile/", views.profile, name="profile"),
    # Recipe URLs
    path("recipes/", views.RecipeList.as_view(), name="recipe_list"),
    path("recipes/create/", views.RecipeCreate.as_view(), name="recipe_create"),
    path(
        "recipes/<int:recipe_id>/", views.RecipeDetail.as_view(), name="recipe_detail"
    ),
    path(
        "recipes/<int:recipe_id>/edit",
        views.RecipeUpdate.as_view(),
        name="recipe_update",
    ),
    path(
        "recipes/<int:recipe_id>/delete/",
        views.RecipeDelete.as_view(),
        name="recipe_delete",
    ),
    # Collection URLs
    path("collections/", views.CollectionList.as_view(), name="collection_list"),
    path(
        "collections/create/",
        views.CollectionCreate.as_view(),
        name="collection_create",
    ),
    path(
        "collections/<int:collection_id>/",
        views.CollectionDetail.as_view(),
        name="collection_detail",
    ),
    path(
        "collections/<int:collection_id>/edit",
        views.CollectionUpdate.as_view(),
        name="collection_update",
    ),
    path(
        "collections/<int:collection_id>/delete",
        views.CollectionDelete.as_view(),
        name="collection_delete",
    ),
    path(
        "collections/<int:collection_id>/add/<int:recipe_id>",
        views.collection_add_recipe,
        name="collection_add_recipe",
    ),
    path(
        "collections/<int:collection_id>/remove/<int:recipe_id>",
        views.collection_remove_recipe,
        name="collection_remove_recipe",
    ),
    # Comment URLS
    path("recipes/<int:recipe_id>/comment/", views.add_comment, name="add_comment"),
    path(
        "comments/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"
    ),
    path(
        "recipes/<int:recipe_id>/rate",
        views.add_or_update_rating,
        name="add_or_update_rating",
    ),
]
