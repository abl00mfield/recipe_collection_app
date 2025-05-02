from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    # User authentication
    path("signup/", views.signup, name="signup"),
    path("signin/", views.Signin.as_view(), name="signin"),
    path("signout/", views.signout, name="signout"),
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
        name="recipe_edit",
    ),
    path(
        "recipes/<int:recipe_id>/delete/",
        views.RecipeDelete.as_view(),
        name="recipe_delete",
    ),
    path("my-recipes/", views.UserRecipeList.as_view(), name="user_recipe_list"),
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
        "recipes/<int:recipe_id>/add-to-collection/",
        views.collection_add_recipe,
        name="collection_add_recipe",
    ),
    path(
        "collections/<int:collection_id>/remove/<int:recipe_id>",
        views.collection_remove_recipe,
        name="collection_remove_recipe",
    ),
    path(
        "collections/create-inline/",
        views.create_collection_inline,
        name="collection_create_inline",
    ),
    path(
        "collections/<int:collection_id>/set_cover/<int:recipe_id>/",
        views.set_collection_cover,
        name="set_collection_cover",
    ),
    path("profile/edit", views.edit_profile, name="edit_profile"),
    path("profile/", views.profile, name="profile"),
    path(
        "accounts/password_change/",
        auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "accounts/password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
]
