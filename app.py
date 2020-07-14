from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
from bson import ObjectId
import pymongo
import datetime

# load in the variable in the .env file into our operating system environment
load_dotenv()

app = Flask(__name__)

# connect to Mongo
MONGO_URI = os.environ.get('MONGO_URL')
client = pymongo.MongoClient(MONGO_URI)

# define my db name
DB_NAME = "cookbooks"

# read in the SESSION_KEY variable from the operating system environment
SESSION_KEY = os.environ.get('SESSION_KEY')

# set the session key
app.secret_key = SESSION_KEY


@app.route('/')
def home():
    return render_template('home.template.html')


@app.route('/recipe/submit')
def submit_recipe():
    return render_template('submit_recipe.template.html')


@app.route('/recipe/submit', methods=['POST'])
def process_submit_recipe():
    print(request.form)

    recipe_title = request.form.get('recipe-title')
    about_recipe = request.form.get('about-recipe')
    ingredients = request.form.get('ingredients')
    directions = request.form.get('directions')
    print(recipe_title, about_recipe, ingredients, directions)

    submission = client[DB_NAME].submittedRecipes.insert_one({
        "title": recipe_title,
        "about": about_recipe,
        "ingredients": ingredients,
        "directions": directions
    })
    return redirect(url_for('board_view', recipe_id=submission.inserted_id))


@app.route('/view/<recipe_id>')
def board_view(recipe_id):
    recipe = client[DB_NAME].submittedRecipes.find_one({
        "_id": ObjectId(recipe_id)
    })
    return render_template('board_view.template.html',
                           recipe=recipe
                           )


@app.route('/recipes')
def show_all_recipes():
    all_recipes = client[DB_NAME].submittedRecipes.find().limit(10)
    return render_template('show_all_recipes.template.html',
                           all_recipes=all_recipes
                           )


@app.route('/recipe/update/<recipe_id>')
def update_recipe(recipe_id):
    recipe = client[DB_NAME].submittedRecipes.find_one({
        "_id": ObjectId(recipe_id)
    })

    return render_template('update_recipe.teplate.html',
                           recipe=recipe
                           )


@app.route('/recipe/update/<recipe_id>', methods=['POST'])
def process_update_recipe(recipe_id):
    print(request.form)

    recipe_title = request.form.get('recipe-title')
    about_recipe = request.form.get('about-recipe')
    ingredients = request.form.get('ingredients')
    directions = request.form.get('directions')
    print(recipe_title, about_recipe, ingredients, directions)

    client[DB_NAME].submittedRecipes.update_one({
        "_id": ObjectId(recipe_id),

    }, {
        "$set": {
            "title": recipe_title,
            "about": about_recipe,
            "ingredients": ingredients,
            "directions": directions
        }
    })
    print(recipe_id)
    print(ObjectId(recipe_id))
    return redirect(url_for('board_view', recipe_id=ObjectId(recipe_id)))


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)