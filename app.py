from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
from bson import ObjectId
import pymongo
import datetime
import math

# load in the variable in the .env file into our operating system environment
load_dotenv()

app = Flask(__name__)

# connect to Mongo
MONGO_URI = os.environ.get('MONGO_URL')
client = pymongo.MongoClient(MONGO_URI)

# connect to Cloudinary for uploading files
CLOUD_NAME = os.environ.get('CLOUD_NAME')
UPLOAD_PRESET = os.environ.get('UPLOAD_PRESET')

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
    all_cuisines = client[DB_NAME].cuisines.find()

    return render_template('submit_recipe.template.html',
                           cloud_name=CLOUD_NAME,
                           upload_preset=UPLOAD_PRESET,
                           all_cuisines=all_cuisines
                           )


@app.route('/recipe/submit', methods=['POST'])
def process_submit_recipe():
    print(request.form)

    recipe_title = request.form.get('recipe-title')
    about_recipe = request.form.get('about-recipe')
    ingredients = request.form.get('ingredients')
    prep_time = request.form.get('prep-time')
    cook_time = request.form.get('cook-time')
    servings = request.form.get('servings')
    cuisine_names = request.form.get('cuisines')
    directions = request.form.get('directions')
    uploaded_file_url = request.form.get('uploaded_file_url')

    cuisines_dropdown = client[DB_NAME].cuisines.find_one({
        "_id": ObjectId(cuisine_names)
    })

    submission = client[DB_NAME].submittedRecipes.insert_one({
        "title": recipe_title,
        "about": about_recipe,
        "ingredients": ingredients,
        "prep_time": prep_time,
        "cook_time": cook_time,
        "servings": servings,
        "cuisine": {
            "_id": cuisines_dropdown["_id"],
            "name": cuisines_dropdown["cuisine_name"],
        },
        "directions": directions,
        "uploaded_file_url": uploaded_file_url
    })
    return redirect(url_for('board_view', recipe_id=submission.inserted_id))


@app.route('/view/<recipe_id>')
def board_view(recipe_id):

    # get the page number
    page = request.args.get('page', 1, type=int)
    # extract out the search term
    search_terms = request.args.get('search-terms')

    recipe = client[DB_NAME].submittedRecipes.find_one({
        "_id": ObjectId(recipe_id)
    })
    return render_template('board_view.template.html',
                           recipe=recipe,
                           page=page,
                           search_terms=search_terms
                           )


@app.route('/recipes')
def show_all_recipes():

    # get the page number
    page = request.args.get('page', 1, type=int)
    # how many pages to present
    limit = request.args.get('limit', 12, type=int)
    # total number of post
    tot_count = client[DB_NAME].submittedRecipes.find().count()
    # get the last page number
    last_page_num = math.ceil(tot_count / limit)

    # To show five in a block
    block_size = 5
    # to find the current location of block
    block_num = int((page - 1) / block_size)
    # start location of block
    block_start = int((block_size * block_num) + 1)
    # end location of block
    block_last = math.ceil(block_start + (block_size - 1))

    # extract out the search term
    search_terms = request.args.get('search-terms')
    print(search_terms)

    # dictinery to store all the criteria
    criteria = {}

    if search_terms != "" and search_terms is not None:
        criteria['title'] = {
            "$regex": search_terms,
            "$options": "i"
        }

    all_recipes = client[DB_NAME].submittedRecipes.find(criteria).skip(
        (page-1)*limit).limit(limit)
    return render_template('show_all_recipes.template.html',
                           all_recipes=all_recipes,
                           page=page,
                           limit=limit,
                           last_page_num=last_page_num,
                           block_start=block_start,
                           block_last=block_last,
                           search_terms=search_terms
                           )


@app.route('/recipe/update/<recipe_id>')
def update_recipe(recipe_id):

    # get the page number
    page = request.args.get('page', 1, type=int)
    # extract out the search term
    search_terms = request.args.get('search-terms')

    recipe = client[DB_NAME].submittedRecipes.find_one({
        "_id": ObjectId(recipe_id)
    })
    all_cuisines = client[DB_NAME].cuisines.find()
    return render_template('update_recipe.teplate.html',
                           recipe=recipe,
                           cloud_name=CLOUD_NAME,
                           upload_preset=UPLOAD_PRESET,
                           all_cuisines = all_cuisines,
                           page=page,
                           search_terms=search_terms
                           )


@app.route('/recipe/update/<recipe_id>', methods=['POST'])
def process_update_recipe(recipe_id):
    print(request.form)

    recipe_title = request.form.get('recipe-title')
    about_recipe = request.form.get('about-recipe')
    ingredients = request.form.get('ingredients')
    prep_time = request.form.get('prep-time')
    cook_time = request.form.get('cook-time')
    servings = request.form.get('servings')
    cuisine_names = request.form.get('cuisines')
    directions = request.form.get('directions')
    uploaded_file_url = request.form.get('uploaded_file_url')

    cuisines_dropdown = client[DB_NAME].cuisines.find_one({
        "_id": ObjectId(cuisine_names)
    })

    client[DB_NAME].submittedRecipes.update_one({
        "_id": ObjectId(recipe_id),

    }, {
        "$set": {
            "title": recipe_title,
            "about": about_recipe,
            "ingredients": ingredients,
            "prep_time": prep_time,
            "cook_time": cook_time,
            "servings": servings,
            "cuisine": {
            "_id": cuisines_dropdown["_id"],
            "name": cuisines_dropdown["cuisine_name"],
            },
            "directions": directions,
            "uploaded_file_url": uploaded_file_url
        }
    })
    print(recipe_id)
    print(ObjectId(recipe_id))
    return redirect(url_for('board_view', recipe_id=ObjectId(recipe_id)))


@ app.route('/recipe/delete/<recipe_id>')
def delete_recipe(recipe_id):
    recipe = client[DB_NAME].submittedRecipes.find_one({
        "_id": ObjectId(recipe_id)
    })
    return render_template('confirm_to_delete.template.html',
                           recipe=recipe
                           )


@ app.route('/recipe/delete/<recipe_id>', methods=['POST'])
def process_delete_recipe(recipe_id):
    client[DB_NAME].submittedRecipes.remove({
        "_id": ObjectId(recipe_id)
    })
    return redirect(url_for('show_all_recipes'))


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
