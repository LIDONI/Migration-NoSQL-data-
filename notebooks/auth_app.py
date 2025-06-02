# === IMPORTS ===
from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pymongo import MongoClient
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# === CONFIGURATION GLOBALE ===
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "secretjwtkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 25

# Connexion MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client[os.getenv("MONGO_DB")]
users = db["users"]

#  Utilisation de bcrypt pour hasher les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Système d'authentification avec OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Instance FastAPI
app = FastAPI()

# === FONCTIONS UTILITAIRES ===

def verify_password(plain_password, hashed_password):
    #  Comparaison sécurisée des mots de passe avec bcrypt
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    #  Hachage sécurisé des mots de passe avant stockage
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = users.find_one({"username": username})
    if user and verify_password(password, user["password"]):  #  Comparaison hachée
        return user
    return None

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    #  Génération du token JWT
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# === ROUTES DE L'API ===

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API medical-data-migration"}

@app.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...)
):
    """
     Route de création de compte avec hash du mot de passe
    """
    if users.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant")

    hashed = get_password_hash(password)  #  Hash avant stockage
    users.insert_one({"username": username, "password": hashed})

    return {"message": "Utilisateur enregistré avec succès"}

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
     Route /login : retourne un token JWT après authentification
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Identifiants invalides")

    access_token = create_access_token(data={"sub": user["username"]})  #  Création du token JWT
    return {"access_token": access_token, "token_type": "bearer"}  #  Token retourné

@app.get("/patients")
async def get_protected_data(token: str = Depends(oauth2_scheme)):
    """
    Route protégée : nécessite un token JWT valide
    """
    try:
        # Vérification et décodage du token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    return {"message": f"Données protégées accessibles pour {username}"}
