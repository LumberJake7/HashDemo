from flask import Flask, request, render_template, redirect, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import User, db, connect_db, Feedback
from forms import UserForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///users"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home():
    user = None
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
    return render_template("homepage.html", user=user)

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = UserForm()
    user = None

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_user = User.register(username, password)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another')
            return render_template('signup.html', form=form, user=user)

        session['user_id'] = new_user.id
        flash('Registration successful!', 'success')
        return redirect('/')

    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

    return render_template('signup.html', form=form, user=user)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = UserForm()
    user = None

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        return_user = User.authenticate(username, password)

        if return_user:
            flash(f"Hello, you're back {return_user.username}")
            session['user_id'] = return_user.id
            return redirect(url_for('user_profile', username=return_user.username))
        else:
            form.username.errors.append("Invalid username/password")

    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

    return render_template("login.html", form=form, user=user)

@app.route("/users/<username>")
def user_profile(username):
    user = None

    if 'user_id' not in session:
        flash("Please log in to view user profiles.")
        return redirect("/login")

    profile_user = User.query.filter_by(username=username).first()

    if not profile_user:
        flash("User not found.")
        return redirect('/')

    logged_in_user_id = session['user_id']
    if profile_user.id != logged_in_user_id:
        flash("You are not authorized to view this profile.")
        return redirect('/')

    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

    return render_template('user_profile.html', profile_user=profile_user, user=user)

@app.route("/users/<username>/delete", methods=['POST'])
def delete_user(username):
    if 'user_id' not in session:
        flash("Please log in to delete your account.")
        return redirect("/login")

    profile_user = User.query.filter_by(username=username).first()

    if not profile_user:
        flash("User not found.")
        return redirect('/')

    logged_in_user_id = session['user_id']
    if profile_user.id != logged_in_user_id:
        flash("You are not authorized to delete this account.")
        return redirect('/')

    db.session.delete(profile_user)
    db.session.commit()

    session.pop('user_id')
    flash("Your account has been deleted. Goodbye!")
    return redirect('/')

@app.route("/users/<username>/feedback/add", methods=['GET', 'POST'])
def add_feedback(username):
    user = None

    if 'user_id' not in session:
        flash("Please log in to view user profiles.")
        return redirect("/login")

    profile_user = User.query.filter_by(username=username).first()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title, content=content, username=profile_user.username)
        db.session.add(new_feedback)
        db.session.commit()
        flash('Feedback has been registered')
        return redirect("/feedback")
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
    return render_template("add_feedback.html", form=form, user=user)

@app.route("/feedback/<int:feedback_id>/update", methods=['GET', 'POST'])
def feedback_update(feedback_id):
    
    user = None
    feedback = Feedback.query.get(feedback_id)
    form = FeedbackForm(obj=feedback)
    
    if 'user_id' not in session:
        flash("Please log in to view user profiles.")
        return redirect("/login")

    

    if feedback is None:
        flash("Feedback not found.")
        return redirect("/")

    user_id = session['user_id']
    profile_user = User.query.get(user_id)

    if profile_user.username != feedback.username:
        flash('You are not the owner of this post')
        return redirect('/')

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback.title = title
        feedback.content = content

        db.session.commit()
        flash('Feedback updated successfully.')
        return redirect("/feedback")

    user = User.query.get(user_id)
    return render_template("edit.html", form=form, user=user, feedback=feedback)  


@app.route("/feedback", methods = ['GET'])
def feedback_display():
    feedback = Feedback.query.all()
    user = None
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
    return render_template("feedback.html", feedback=feedback, user=user)


@app.route("/feedback/<int:feedback_id>/delete", methods=['POST'])
def feedback_delete(feedback_id):

    if 'user_id' not in session:
        flash("Please log in to view user profiles.")
        return redirect("/login")

    feedback = Feedback.query.get(feedback_id)

    if feedback is None:
        flash("Feedback not found.")
        return redirect("/feedback") 

    user_id = session['user_id']
    profile_user = User.query.get(user_id)

    if profile_user.username != feedback.username:
        flash('You are not the owner of this post')
        return redirect('/feedback')  

    db.session.delete(feedback)
    db.session.commit()
    flash('Feedback deleted successfully.')
    
    return redirect("/feedback")



@app.route("/secret", methods=['GET'])
def secret():
    user = None

    if "user_id" not in session:
        flash("Hey! Get out of here >:( ")
        return redirect("/")
    
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

    return render_template("secret.html", user=user)

@app.route("/logout")
def logout():
    session.pop('user_id')
    flash("Goodbye!")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
