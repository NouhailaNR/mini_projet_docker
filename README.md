# Projet Flask déployer avec docker  - Histoire Générée à partir d'Images 

Ce mini_projet utilise Flask pour créer une application web qui permet aux utilisateurs de télécharger des images. L'application génère ensuite une histoire inspirée par l'image téléchargée, en utilisant un modele d'Ollama.

## 1- la structure de projet 

src/
│── app.py
│── templates/
│    ├── index.html
│    └── gallery.html
│── static/
│    ├── uploads/ 
|       ├── image.png
│       └── image2.png
│
docker-compose.yml
README.md
requirements.txt
Dockerfile
.gitignore

## 2- les missions 

- Upload d’image
- Génération d’une histoire fictive via Ollama
- Un modèle multimodal (qwen2.5vl:7b) traite l’image
- Sauvegarde dans PostgreSQL
- Interface simple avec deux templates HTML
- Exécution complète via Docker

## 4- lancer le projet et aussi relancer le programme apres une modification 

`docker-compose up --build`
    Cela va :
    - Construire les images Docker (Flask, Ollama…)
    - Lancer les conteneurs
    - Initialiser la base PostgreSQL
    - Rendre l'application accessible

## 5- acceder au projet : 
http://localhost:5000
