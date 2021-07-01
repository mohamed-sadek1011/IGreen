from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User



auth = Blueprint('auth', __name__)

def db_add():
    admin = User(username="admin", password = "admin")
    db.session.add(admin)
    db.session.commit()

@auth.route('/login', methods = ['GET' , 'POST'])
def login():

    

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user:   
            if (password == user.password):
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                pass
        else:
            pass
    return render_template("login.html", user=current_user)
              
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))