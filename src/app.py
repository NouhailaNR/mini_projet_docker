from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
import ollama
import os
from flask_sqlalchemy import SQLAlchemy

# on peut creer la base de données par deux methodes differentes :
#1- SQLAlchemy : wrapper autour de sqlchemy , la session déja integre qui tourne les requetes Flask
#2- declarative_base() : c'est la version indepedante de Flask, on import session colum ..

app= Flask(__name__,static_folder='static')
UPLOAD_FOLDER = os.path.join('src/static', 'uploads')
app.config['UPLOAD'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'postgresql://postgres:postgres@postgres:5432/db'
)

db=SQLAlchemy(app)

class StoriesIMg(db.Model):
    __tablename__= 'storiesimg' # le nom de tableau
    id = db.Column(db.Integer, primary_key=True) # creer une colonne id , chaque histoire aura un identifiant unique via la clé primaire
    image_path = db.Column(db.String(255), nullable=False)   # <-- colonne 1: Image : chemin ou nom de fichier
    story_text = db.Column(db.Text, nullable=False) # colonne 2: histoire 
    created_at = db.Column(db.DateTime, server_default=db.func.now()) # ajouter la date de creation 
   
# Créer toutes les tables de la base de données (si elles n'existent pas déjà)
with app.app_context():
    db.create_all()

@app.route('/') # permet que la fonction home sera exécutée dans le serveur web 
def home():
    return render_template('index.html')

@app.route('/upload', methods=["GET","POST"])
def upload_img():
    if request.method == 'POST':
        file = request.files['img']
        filename = secure_filename(file.filename)
        mimetype=file.mimetype
        filepath = os.path.join(app.config['UPLOAD'], filename)
        file.save(filepath)
        # Vérifier si une histoire existe déjà pour cette image
        existing_story_img = StoriesIMg.query.filter_by(image_path=filepath).first()
        
        if existing_story_img:
            story = existing_story_img.story_text
        else:
            story = generate_hist(filepath)

        story_img=StoriesIMg(image_path=filepath, story_text=story)
        db.session.add(story_img)
        db.session.commit()
        return render_template("gallery.html", image=f"uploads/{filename}", story=story)
    return render_template("index.html")

def generate_hist(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, 'rb') as file:
        response = ollama.chat(
            model='qwen2.5vl:7b',
            messages=[
                {
                    'role': 'user',
                    'content': (
                        "Fais une histoire courte, max 150 mots, Invente une histoire vraiment drôle, imaginative et totalement fictive, inspirée de ces images. Ne décris pas les images : utilise-les comme source d’inspiration, Ton récit doit être humoristique, surprenant et raconter une aventure cohérente."
                    ),
                    'images': [file.read()],
                },
            ],
        )
    
    return response['message']['content']


if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000)