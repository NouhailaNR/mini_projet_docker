from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
import ollama
import os
from flask_sqlalchemy import SQLAlchemy


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
    id = db.Column(db.Integer, primary_key=True) # creer une colonne id , chaque histoire et l'image aura un identifiant unique via la clé primaire
    image_path = db.Column(db.String(255), nullable=False)   # <-- colonne 1: Image 
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
    """
    Route pour l'upload d'une image.

    Méthodes HTTP :
        GET : Affiche le formulaire d'upload.
        POST : Reçoit l'image uploadée, la sauvegarde sur le serveur,
               puis génère une histoire à partir de l'image.

    Formulaire attendu :
        - 'file' : fichier image envoyé via le formulaire HTML

    Fonction :
        1. Vérifie que le fichier est bien une image.
        2. Sauvegarde l'image dans le dossier 'static/uploads/'.
        3. Appelle le modèle Ollama pour générer une histoire à partir de l'image.
        4. Sauvegarde l'image et l'histoire dans PostgreSQL.
        5. Redirige vers une page de confirmation ou la galerie d'images.

    Templates :
        - index.html (si GET)
        - gallery.html (si redirection après upload réussi)

    Retour :
        - GET : render_template('index.html')
        - POST réussi : redirect(url_for('gallery')) ou render_template('gallery.html', ...)
        - POST échoué : flash message et render_template('index.html')
    """
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
            story = generate_story(filepath)

        story_img=StoriesIMg(image_path=filepath, story_text=story)
        db.session.add(story_img)
        db.session.commit()
        return render_template("gallery.html", image=f"uploads/{filename}", story=story)
    return render_template("index.html")

def generate_story(filepath):
    """
    Génère une histoire à partir d'une image.

    Paramètres :
        image_path (str) : chemin local vers l'image sur le serveur.

    Fonction :
        1. Charge l'image depuis le chemin fourni.
        2. Envoie l'image au modèle multimodal Ollama (qwen2.5vl:7b).
        3. Récupère le texte généré (l'histoire).
        4. Retourne l'histoire sous forme de chaîne de caractères.

    Retour :
        story (str) : l'histoire générée à partir de l'image.

    Exemple :
        >>> story = generate_story("static/uploads/image1.png")
        >>> print(story)
        "Il était une fois un petit chat curieux qui explorait un jardin enchanté..."
    """
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