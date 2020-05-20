# web_app/routes/twitter_routes.py

from flask import Blueprint, jsonify, render_template, request, redirect

from web_app.models import User, Tweet, db, parse_records
from web_app.services.twitter_service import api_client
from web_app.services.basilica_service import connection as basilica_connection

twitter_routes = Blueprint("twitter_routes", __name__)

@twitter_routes.route("/users/<screen_name>/fetch")
def fetch_user_data(screen_name=None):
    print(screen_name)

    api = api_client()
    twitter_user = api.get_user(screen_name)
    statuses = api.user_timeline(screen_name, tweet_mode="extended", count=150)
    print("STATUSES COUNT:", len(statuses))

    #new_book = Book(title=request.form["book_title"], author_id=request.form["author_name"])
    #db.session.add(new_book)
    #db.session.commit()

    #
    # STORE USER
    #

    # get existing user from the db or initialize a new one:
    db_user = User.query.get(twitter_user.id) or User(id=twitter_user.id)
    db_user.screen_name = twitter_user.screen_name
    db_user.name = twitter_user.name
    db_user.location = twitter_user.location
    db_user.followers_count = twitter_user.followers_count
    db.session.add(db_user)
    db.session.commit()
    #breakpoint()

    #
    # STORE TWEETS
    #

    all_tweet_texts = [status.full_text for status in statuses]
    embeddings = list(basilica_connection.embed_sentences(all_tweet_texts, model="twitter"))
    print("NUMBER OF EMBEDDINGS", len(embeddings))

    # TODO: explore using the zip() function maybe...
    counter = 0

    for status in statuses:
        print(status.full_text)
        print("----")
        #print(dir(status))
        # get existing tweet from the db or initialize a new one:
        db_tweet = Tweet.query.get(status.id) or Tweet(id=status.id)
        db_tweet.user_id = status.author.id # or db_user.id
        db_tweet.full_text = status.full_text
        #embedding = basilica_connection.embed_sentence(status.full_text, model="twitter") # todo: prefer to make a single request to basilica with all the tweet texts, instead of a request per tweet
        embedding = embeddings[counter]
        print(len(embedding))
        db_tweet.embedding = embedding
        db.session.add(db_tweet)
        counter+=1
    db.session.commit()

    return render_template("users.html", users=User.query.all(), tweets=statuses) # tweets=db_tweets



@twitter_routes.route("/users")
def list_users_human_friendly():
    db_users = User.query.all()
    return render_template("users.html", users=db_users)

@twitter_routes.route("/users.json")
def list_users():
    db_users = User.query.all()
    users_response = parse_records(db_users)
    return jsonify(users_response)

@twitter_routes.route("/users/<screen_name>")
def get_user(screen_name=None):
    print(screen_name)
    db_user = User.query.filter(User.screen_name == screen_name).one()
    return render_template("user.html", user=db_user, tweets=db_user.tweets)


@twitter_routes.route("/tweets.json")
def list_tweets():
    tweet_records = Twitter.query.all()
    print(tweet_records)
    tweets = parsed_records(tweet_records)
    return jsonify(tweets)

@twitter_routes.route("/tweets")
def list_tweets_for_humans():
    tweet_records = Twitter.query.all()
    print(tweet_records)
    return render_template("tweets.html", message="Here's some tweets", tweets=tweet_records)

@twitter_routes.route("/tweets/new")
def new_tweet():
    return render_template("new_tweets.html", users=User.query.all())

@twitter_routes.route("/")
def tweets_for_a_loop():
    return render_template("prediction_form.html", users=User.query.all())

@twitter_routes.route("/tweets/create", methods=["POST"])
def create_book():
    print("FORM DATA:", dict(request.form))

    new_tweet = request.form["User_Name"]
    
    #return jsonify({
    #    "message": "BOOK CREATED OK (TODO)",
    #    "book": dict(request.form)
    #})
    #flash(f"Book '{new_book.title}' created successfully!", "success")
    return redirect(f"/users/{new_tweet}/fetch")

