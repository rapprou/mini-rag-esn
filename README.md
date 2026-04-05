# Mini RAG ESN

Système RAG minimaliste permettant d'interroger des documents en langage naturel via une recherche vectorielle et Claude.

---

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat&logo=supabase&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-D97757?style=flat&logo=anthropic&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)

---

## Démarrage rapide

```bash
# 1. Cloner et installer
git clone <url-du-repo> && cd Mini\ RAG-ESN
pip install -r requirements.txt

# 2. Configurer l'environnement
cp .env.example .env  # Renseigner SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY

# 3. Initialiser la base de données
# Exécuter sql/schema.sql dans l'éditeur SQL Supabase

# 4. Lancer
uvicorn main:app --reload
```

Interface disponible sur [http://localhost:8000](http://localhost:8000).

---

## API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/upload` | Ingère et indexe un document (PDF, TXT, MD) |
| `POST` | `/ask` | Pose une question sur les documents indexés |
| `GET` | `/documents` | Liste tous les documents indexés |
| `DELETE` | `/documents/{id}` | Supprime un document et ses chunks |

---

## Pourquoi ce projet

- **Recherche sémantique** — chaque document est découpé en chunks et converti en vecteurs d'embedding (OpenAI `text-embedding-3-small`), permettant une recherche par similarité cosinus bien plus pertinente qu'une recherche par mots-clés.
- **Génération ancrée** — seuls les chunks les plus proches de la question sont transmis à Claude comme contexte, ce qui réduit les hallucinations et limite les coûts d'inférence.
- **Stack production-ready** — FastAPI pour les performances async, Supabase (PostgreSQL + pgvector) pour la persistance vectorielle, architecture en couches (routes / services / db) directement déployable.
