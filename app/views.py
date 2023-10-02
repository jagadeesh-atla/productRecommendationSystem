from flask import Blueprint, request, send_from_directory, render_template, redirect, session, jsonify, flash, url_for

import bcrypt
from bson import ObjectId
from pymongo import MongoClient
import pandas

MONGO_URI = "mongodb+srv://admin:passWORD@cluster0.4iif9cc.mongodb.net/?retryWrites=true&w=majority"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['data']

from model.recommendation_model import RecommendationModel

try:
    users = list(db.users.find())
    products = list(db.products.find())
    interactions = list(db.interactions.find())

    # print(users[:2])

    for user in users:
        user['_id'] = str(user['_id'])
    for product in products:
        product['_id'] = str(product['_id'])
    for interaction in interactions:
        interaction['userId'] = str(interaction['userId'])
        interaction['productId'] = str(interaction['productId'])

    users_df = pandas.DataFrame(users)
    users_df['_id'] = users_df['_id'].astype('string')

    products_df = pandas.DataFrame(products)
    products_df['_id'] = products_df['_id'].astype('string')

    interactions_df = pandas.DataFrame(interactions)
    interactions_df['userId'] = interactions_df['userId'].astype('string')
    interactions_df['productId'] = interactions_df['productId'].astype('string')

    print('got data')
    model = RecommendationModel(users=users_df, products=products_df, interactions=interactions_df)
    print('used mongo')
except Exception as e:
    model = RecommendationModel()
    print('without mongo')

category = ['automotive', 'electronics',
            'sports', 'beauty', 'health',
            'home decor', 'clothing', 'food',
            'pets', 'books', 'toys']

views = Blueprint('views', __name__)

def retrain(users=None, products=None, interactions=None):
    try:
        y = model.retrain(new_users=users, new_products=products, new_interactions=interactions)
        return True, "Retained Successful"
    except Exception as e:
        return False, str(e)

@views.route('/')
def index():
    if 'user_id' in session:
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        return render_template('index.html', logged=True, user={
            '_id': session['user_id'],
            'username': user['username']
        })
    return render_template('index.html', logged=False)

@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'password':
            return redirect('/admin')

        user = db.users.find_one({'username': username})
        
        if user and bcrypt.checkpw(
            password.encode('utf-8'),
            user['password']):
            flash('Login successful!', 'success')
            session['user_id'] = str(user['_id'])
            return redirect('/')
        else:
            flash('Login failed. Please check your credentials.', 'danger')
    return render_template('login.html')

@views.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = db.users.find_one({'username': username})
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect('/signup')

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
            )
        selected_options = request.form.getlist('options')  
        user_data = {
            'username': username,
            'password': hashed_password,
            'preferences': selected_options
        }
        user_data_ins = db.users.insert_one(user_data)

        user_data['_id'] = str(user_data_ins.inserted_id)

        print(user_data)
        # user_data['_id'] = str(user_data['_id'])
        retrain_result = retrain(users=[user_data])[0]
        if retrain_result:
            flash('Account created successfully', 'success')
            return redirect('/login')
    return render_template('signup.html', options=category)

@views.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@views.route('/no_image')
def serve_static_image():
    return send_from_directory(
        'static/images', 'no_image.png'
        )

@views.route('/users')
def users_view():
    users1 = list(db.users.find())

    for user in users1:
        user['_id'] = str(user['_id'])
        del user['password']

    return users1

@views.route('/products')
def products_view():
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    products = db.products.find().sort('popularity', -1).skip(offset).limit(per_page)
    if 'user_id' in session:
        return render_template('products.html', user_id=session['user_id'], products=products, page=page)
    else:
        return render_template('products.html', user_id='no', products=products, page=page)

@views.route('/interact', methods=['POST'])
def interact():
    # if 'username' in session:
    data = request.json
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    score = data.get('score')
    interaction = {
        'userId': user_id,
        'productId': product_id,
        'score': score
    }
    # print(interaction)

    interaction_ins = db.interactions.insert_one(interaction)
    interaction['_id'] = interaction_ins.inserted_id

    retrain_result = retrain(interactions=[interaction])

    response = {"message": "Purchase successful"}
    return jsonify(response), 200

@views.route('/admin')
def admin():
    return render_template('admin.html') 

@views.route('/retrain', methods=['POST'])
def retrainD():
    y = retrain()[1]
    return jsonify({'message': y}), 200

@views.route('/evaluate', methods=['POST'])
def evaluate():
    from model.evaluate_model import Evaluate
    try:
        y = Evaluate(users=users_df, products=products_df, interactions=interactions_df)
        result = str(y.result)
        return jsonify({'message': result}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@views.route('/recs/<path:user_id>')
def recs(user_id):
    user = list(db.users.find(
        {'_id': ObjectId(user_id)}))[0]
    keyword = request.args.get('type', '3')
    n = int(request.args.get('n', 5))
    n = min(n, 100)
    if keyword == '0':
        userRecs = model.collaborative_recommendations(user_id, n)
        # userRecs['image'] = userRecs.apply(
        #     lambda row: image_data(row['productName']),
        #     axis=1
        # )
        userRecs = userRecs.to_dict(orient='records')
        # print(userRecs)
        # return userRecs
        return render_template('recs.html', recommendations=userRecs, user=user)
    elif keyword == '1':
        userRecs = model.preference_recommendations(user_id, n)
        # userRecs['image'] = userRecs.apply(
        #     lambda row: image_data(row['productName']),
        #     axis=1
        # )
        userRecs = userRecs.to_dict(orient='records')
        # return userRecs
        return render_template('recs.html', recommendations=userRecs, user=user)
    elif keyword == '2':
        userRecs = model.popular_recommendations(n)
        # userRecs['image'] = userRecs.apply(
        #     lambda row: image_data(row['productName']),
        #     axis=1
        # )
        userRecs = userRecs.to_dict(orient='records')
        # return userRecs
        return render_template('recs.html', recommendations=userRecs, user=user)
    elif keyword == '3':
        userRecs = model.recommendations(user_id, n)
        # userRecs['image'] = userRecs.apply(
        #     lambda row: image_data(row['productName']),
        #     axis=1
        # )
        userRecs = userRecs.to_dict(orient='records')
        # print(userRecs)
        return render_template('recs.html', recommendations=userRecs, user=user)
        # return userRecs
    else:
        return 'Give Correct Queries'
