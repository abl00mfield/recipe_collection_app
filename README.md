# 🥘 Recipe Box

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://docs.djangoproject.com/en/5.0/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Deployed on Heroku](https://img.shields.io/badge/Deployed-Heroku-7056bf?logo=heroku)](https://recipe-box-ga-0400572de56c.herokuapp.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://opensource.org/licenses/MIT)

**Recipe Box** is a full-featured Django web application that allows users to create, manage, and share recipes, organize them into collections, and leave reviews. With a clean UI and thoughtful UX design, the app supports both casual users and passionate home cooks alike.

🔗 **Live Demo**: [https://recipe-box-ga-0400572de56c.herokuapp.com/](https://recipe-box-ga-0400572de56c.herokuapp.com/)

---

## 📸 Screenshots

![Landing Page](<main_app/static/img/screenshots/Screenshot 2025-05-05 at 2.28.37 PM.png>)
![Recipe Index](<main_app/static/img/screenshots/Screenshot 2025-05-05 at 2.28.56 PM.png>)
![Collection Index](<main_app/static/img/screenshots/Screenshot 2025-05-05 at 2.30.14 PM.png>)
![Create a recipe](<main_app/static/img/screenshots/Screenshot 2025-05-05 at 2.30.25 PM.png>)

## 🚀 Features

- **User Authentication**

  - Sign up, sign in, sign out
  - Profile view and edit
  - Change password

- **Recipe Management**

  - Add, edit, and delete personal recipes
  - Include descriptions, ingredients, instructions, and photos
  - Tag recipes for easy filtering
  - Optional attribution to the original recipe source

- **Recipe Collections**

  - Organize recipes into custom collections
  - Set cover images for collections
  - Add and remove recipes from collections via dropdown or modal interface
  - Create collections on the fly while browsing recipes

- **Recipe Discovery**

  - View all user-submitted recipes
  - Search by title, description & ingredients
  - Sort alphabetically, most recent, most reviewed, most popular
  - Filter by tags

- **Feedback System**

  - Leave star ratings and comments on recipes
  - View average rating and reviews per recipe

- **Responsive UI/UX**
  - Styled with modular CSS and mobile-friendly design
  - Toast notifications, loading spinners, and modal forms enhance user experience

---

## 🛠 Technologies Used

### Back-End

- **Python 3.11**
- **Django 5.0**
  - Class-based and function-based views
  - Custom forms and widgets
  - Built-in authentication
- **PostgreSQL** – primary database for both development and production

### Front-End

- **HTML5** with Django templating
- **CSS3** (custom styles, no CSS framework)
- **JavaScript**
  - DOM manipulation
  - Modal & dropdown behavior
  - Timestamp formatting

### Deployment

- **Heroku** (PostgreSQL-backed deployment)

---

## 🌐 External Resources

- **Google Fonts** – _Lato_, _Delius Swash Caps_  
  _[fonts.google.com](https://fonts.google.com)_
- **Font Awesome 6** – for icons like trash, plus, stars, etc.  
  _[cdnjs.cloudflare.com](https://cdnjs.com/libraries/font-awesome)_
- **Image Credits**
  - Landing photo: [Anna Pelzer on Unsplash](https://unsplash.com/photos/bowl-of-vegetable-salads-IGfIGP5ONV0)
  - Default recipe photo: [macrovector / Freepik](https://www.freepik.com)
  - Favicon: [Freepik on Flaticon](https://www.flaticon.com/free-icons/dinner)

---

## 💡 Development Highlights

- Custom file widget template (`clearable_file_input.html`) for handling image removal and replacement
- JavaScript enhancements:
  - Modal overlay for new collections
  - Star rating widget
  - Hidden dropdowns and form submission
  - Spinner overlay for form submission UX
- Inline collection creation from recipe views
- Modular and scoped CSS files for different pages

---

## 🧪 Future Enhancements

- Social features (e.g. share collections with friends)
- A community page with links to user profiles
- Quick recipe import
- Improved accessibility (ARIA support, keyboard nav)
- Improved mobile navigation
- RESTful API for mobile clients

---

## 📝 License

This project is for educational and portfolio use. Attribution for icons and images provided above.
