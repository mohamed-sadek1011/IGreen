from flask import Blueprint, render_template
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/aboutus')
def aboutus():
    return render_template("aboutus.html", user=current_user)

@views.route('/contactus')
def contactus():
    return render_template("contactus.html", user=current_user)