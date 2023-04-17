import flask
import pymysql
import os

# create the app object
app = flask.Flask(__name__)

# define the DB connection parameters
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='password',
                             db='Tasty_Bytes',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

# create the cursor
cursor = connection.cursor()

# define the routes
# create the index route
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    cursor.execute("SELECT * FROM recipes")
    recipes = cursor.fetchall()
    return flask.render_template('index.html', recipes=recipes)

# create the add recipe route
@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if flask.request.method == 'POST':
        # get the form data
        recipe_name = flask.request.form['name']
        recipe_description = flask.request.form['description']
        recipe_ingredients = flask.request.form['ingredients']
        recipe_instructions = flask.request.form['instructions']
        recipe_image = flask.request.files['image']

        # create  and excecute the insert query, do not insert the image
        insert_query = """INSERT INTO recipes (name, description, ingredients, instructions) VALUES ("{}", "{}", "{}", "{}")""".format(recipe_name, recipe_description, recipe_ingredients, recipe_instructions)
        cursor.execute(insert_query)
        
        # commit the changes
        connection.commit()

        # get the recipe id
        recipe_id = cursor.lastrowid

        # save the image
        recipe_image.save('static/food_pics/{}.jpg'.format(recipe_id))
        
        # redirect to the index page
        return flask.render_template('thank_you.html', recipe_id=recipe_id)
    
    return flask.render_template('add_recipe.html')

# create the thank you route
@app.route('/thank_you/<recipe_id>', methods=['GET', 'POST'])
def thank_you(recipe_id):
    return flask.render_template('thank_you.html', recipe_id=recipe_id)

# create the recipe route
@app.route('/recipe/<recipe_id>', methods = ['GET', 'POST'])
def recipe(recipe_id):
    cursor.execute("SELECT * FROM recipes WHERE id={}".format(recipe_id))
    recipe = cursor.fetchone()
    
    # split the ingredients and instructions into lists
    recipe["ingredients"] = recipe["ingredients"].split("\n")
    recipe["instructions"] = recipe["instructions"].split(".")

    # remove any empty strings from the list
    recipe["ingredients"] = [ingredient for ingredient in recipe["ingredients"] if ingredient != ""]
    recipe["instructions"] = [instruction for instruction in recipe["instructions"] if instruction != ""]    

    return flask.render_template('recipe.html', recipe=recipe)

# create an edit recipe route
@app.route("/edit_recipe/<recipe_id>", methods=['POST', 'GET'])
def edit_recipe(recipe_id):
    sql = """SELECT * FROM recipes WHERE id={}""".format(recipe_id)
    cursor.execute(sql)
    recipe = cursor.fetchone()
    
    if flask.request.method == 'POST':
        btn = flask.request.form['btn_val']
        print(btn)
        if btn == 'cancel':
            return flask.redirect(flask.url_for('recipe', recipe_id=recipe_id))
        
        if btn == 'delete':
            sql_query = """DELETE FROM recipes WHERE id={}""".format(recipe_id)
            cursor.execute(sql_query)
            connection.commit()

            # delete the image
            os.remove('static/food_pics/{}.jpg'.format(recipe_id))

            # redirect to the thank_you page, pass -1 as the recipe_id
            return flask.redirect(flask.url_for('thank_you', recipe_id=-1))
    
        # get the form data
        name = flask.request.form['name']
        description = flask.request.form['description']
        ingredients = flask.request.form['ingredients']
        instructions = flask.request.form['instructions']
        image = flask.request.files['image']

        # create and excecute the update query, do not insert the image
        update_sql = """UPDATE recipes SET name = "{}", description = "{}", ingredients = "{}", instructions = "{}" WHERE id = {}""".format(name, description, ingredients, instructions, recipe_id)
        cursor.execute(update_sql)
        connection.commit()

        # save the image
        if image.filename != "":
            image.save('static/food_pics/{}.jpg'.format(recipe_id))

        # change to the recipe page
        return flask.redirect(flask.url_for('recipe', recipe_id=recipe_id))
                                           
    return flask.render_template("edit_recipe.html", recipe=recipe)


if __name__ == '__main__':
    app.run(debug=True)