import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Configuración principal de la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta-eco-actions-2026'

# Configuración de la Base de Datos SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'eco_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configuración del Administrador de Inicios de Sesión
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# --- MODELO DE BASE DE DATOS (TABLA DE USUARIOS) ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, default=50)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- RUTAS DE NAVEGACIÓN PRINCIPALES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quienes_somos')
def quienes_somos():
    return render_template('base.html', title="Quiénes Somos")

@app.route('/lo_que_hacemos')
def lo_que_hacemos():
    return render_template('base.html', title="Lo Que Hacemos")

@app.route('/involucrate')
def involucrate():
    return render_template('base.html', title="Involúcrate")

# --- SISTEMA DE IDIOMAS ---

@app.route('/set_lang/<lang_code>')
def set_lang(lang_code):
    session['lang'] = lang_code
    return redirect(request.referrer or url_for('index'))

# --- AUTENTICACIÓN Y CUENTAS DE USUARIO ---

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('El nombre de usuario o correo ya está registrado.', 'danger')
            return redirect(url_for('registro'))

        # Crear nuevo usuario con contraseña encriptada
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password_hash=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()

        flash('¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Correo o contraseña incorrectos. Inténtalo de nuevo.', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

# --- SISTEMA DE BÚSQUEDA ---

@app.route('/search')
def search():
    query = request.args.get('query', '')
    return render_template('base.html', title=f"Resultados para: {query}")

# --- INICIALIZACIÓN DE LA APLICACIÓN ---

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea la base de datos automáticamente si no existe
    app.run(debug=True)