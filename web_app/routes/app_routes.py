
from flask import Blueprint, jsonify, request, flash, redirect

from web_app.models import db, User, Tweet

app_routes = Blueprint("app_routes", __name__)

@app_routes.route('/')
def root():
    return render_template('base.html', title='Home', users=User.query.all(),
                               comparisons=CACHED_COMPARISONS)
