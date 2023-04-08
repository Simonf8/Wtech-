from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user, login_manager
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(cls, email, password):
        self.email = email
        self.password = password
        self.is_active = True
    
    def authenticate(cls, email, password):
        if email == "tes@example.com" and password == "test":
            return User(email, password)
        else:
            return None
    
    def check_password(self, password):
        return check_password_hash(self.password, password)    

class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=True, nullable=False)
    last_name = db.Column(db.String(120), nullable=False)

class Director(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=True, nullable=False)
    last_name = db.Column(db.String(120), nullable=False)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('actor.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    character_name = db.Column(db.String(120), nullable=False)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120), nullable=False)
    poster_url = db.Column(db.String(120), nullable=False)
    trailer_url = db.Column(db.String(120), nullable=False)
    director_id = db.Column(db.Integer, db.ForeignKey('director.id'), nullable=False)
    release_year = db.Column(db.Integer, nullable=False)

   

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():
    return render_template('index.html', show_movie_trailer=current_user.is_authenticated)

@app.route('/login', methods=['GET', 'POST'])
def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            next_page = request.args.get('next')

            user = User.query.filter_by(email=email).first()


            if user is None or not user.is_active:
                flash('Invalid username or password', 'error')
                return redirect(url_for('login'))
            
            if user and user.check_password(password):
                login_user(user)
                flash('Logged in successfully.' , 'success')

                if next_page:
                    return redirect(next_page)
                return redirect(url_for('movie_trailers'))
                
            else:
                flash('Invalid username or password', 'error')
        return render_template('movie_trailers.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')

        return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/actors')
@login_required
def actors():
    actors=Actor.query.all()
    return render_template('actors.html', actors=actors)

@app.route('/actors/new', methods=['GET', 'POST'])
@login_required
def new_actor():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        new_actor = Actor(first_name=first_name, last_name=last_name)
        db.session.add(new_actor)
        db.session.commit()

        flash('New actor added!')

        return redirect(url_for('actors'))

    return render_template('new_actor.html')
@app.route('/directors')
@login_required
def directors():
    directors = Director.query.all()
    return render_template('directors.html', directors=directors)

@app.route('/directors/new', methods=['GET', 'POST'])
@login_required
def new_director():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        new_director = Director(first_name=first_name, last_name=last_name)
        db.session.add(new_director)
        db.session.commit()

        flash('New director added!')

        return redirect(url_for('directors'))

    return render_template('new_director.html')
@app.route('/roles')
@login_required
def roles():
    roles = Role.query.all()
    return render_template('roles.html', roles=roles)

@app.route('/roles/new', methods=['GET', 'POST'])
@login_required
def new_role():
    if request.method == 'POST':
        actor_id = request.form['actor_id']
        movie_id = request.form['movie_id']
        character_name = request.form['character_name']

        new_role = Role(actor_id=actor_id, movie_id=movie_id, character_name=character_name)
        db.session.add(new_role)
        db.session.commit()

        flash('New role added!')

        return redirect(url_for('roles'))

    return render_template('new_role.html')


@app.route('/movies')
@login_required
def movies():
    movies=Movie.query.all()
    return render_template('movies.html', movies=movies)
@app.route('/movies/<int:id>')
@login_required
def movie_details(id):
    movie=Movie.query.get(id)
    return render_template('movie_details.html', movie=movie)

@app.route('/movies/new', methods=['GET', 'POST'])
@login_required
def new_movie():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        poster_url = request.form['poster_url']
        trailer_url = request.form['trailer_url']

        new_movie = Movie(title=title, description=description, poster_url=poster_url, trailer_url=trailer_url)
        db.session.add(new_movie)
        db.session.commit()

        flash('New movie added!')

        return redirect(url_for('movies'))

    return render_template('new_movie.html')

@app.route('/movies/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_movie(id):
    movie=Movie.query.get(id)
    if request.method == 'POST':
        movie.title = request.form['title']
        movie.description = request.form['description']
        movie.poster_url = request.form['poster_url']
        movie.trailer_url = request.form['trailer_url']

        db.session.commit()

        flash('Movie updated!')

        return redirect(url_for('movies'))

    return render_template('edit_movie.html', movie=movie)

@app.route('/movie_trailer')
@login_required
def movie_trailer():
    return render_template('movie_trailer.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)