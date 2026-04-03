# Mini RAG ESN

Un système de **Retrieval-Augmented Generation (RAG)** minimaliste permettant d'ingérer des documents (PDF, TXT, Markdown), de les indexer sous forme de chunks vectorisés, puis d'interroger leur contenu en langage naturel via Claude.

---

## Fonctionnement

1. **Ingestion** — le document est découpé en chunks, chaque chunk est converti en vecteur d'embedding via OpenAI.
2. **Stockage** — les documents et leurs chunks (avec embeddings) sont stockés dans Supabase (PostgreSQL + pgvector).
3. **Recherche** — à chaque question, l'embedding de la requête est comparé aux chunks via similarité cosinus.
4. **Génération** — les chunks les plus pertinents sont envoyés à Claude comme contexte pour générer une réponse fondée uniquement sur les documents.

---

## Stack technique

| Composant | Technologie |
|---|---|
| API backend | [FastAPI](https://fastapi.tiangolo.com/) |
| Base de données | [Supabase](https://supabase.com/) (PostgreSQL + pgvector) |
| Embeddings | OpenAI `text-embedding-3-small` (1536 dimensions) |
| Génération | Anthropic Claude (`claude-sonnet-4-6` par défaut) |
| Frontend | Vanilla HTML / CSS / JS |

---

## Installation

### 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd Mini\ RAG-ESN
```

### 2. Créer et activer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Renseigner les valeurs dans `.env` :

```env
SUPABASE_URL=https://<votre-projet>.supabase.co
SUPABASE_KEY=<votre-clé-anon>
ANTHROPIC_API_KEY=<votre-clé-anthropic>
OPENAI_API_KEY=<votre-clé-openai>
EMBEDDING_MODEL=text-embedding-3-small
CLAUDE_MODEL=claude-sonnet-4-6
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

### 5. Initialiser le schéma Supabase

Dans l'éditeur SQL de votre projet Supabase, exécuter le contenu de :

```
sql/schema.sql
```

Cela crée l'extension `pgvector`, les tables `documents` et `chunks`, ainsi que la fonction RPC `match_chunks`.

### 6. Lancer l'application

```bash
uvicorn main:app --reload
```

L'interface est accessible sur [http://localhost:8000](http://localhost:8000).

---

## Endpoints API

### `POST /upload`
Ingère un document et l'indexe dans Supabase.

- **Corps** : `multipart/form-data`
  - `file` *(requis)* — fichier PDF, TXT ou MD
  - `title` *(optionnel)* — titre personnalisé

- **Réponse** : `UploadResponse`
```json
{
  "document_id": 1,
  "title": "Mon document",
  "filename": "doc.pdf",
  "chunk_count": 42,
  "message": "Document uploaded and indexed successfully."
}
```

---

### `POST /ask`
Pose une question sur les documents indexés.

- **Corps** : `application/json`
```json
{
  "question": "Quelle est la politique de congés ?",
  "top_k": 5
}
```

- **Réponse** : `AskResponse`
```json
{
  "question": "Quelle est la politique de congés ?",
  "answer": "Selon les documents...",
  "sources": [
    {
      "document_id": 1,
      "document_title": "RH - Politique interne",
      "content_excerpt": "Les congés annuels sont...",
      "similarity": 0.91
    }
  ],
  "chunks_used": 5
}
```

---

### `GET /documents`
Retourne la liste de tous les documents indexés, triés par date d'ingestion décroissante.

- **Réponse** : liste de `DocumentOut`
```json
[
  {
    "id": 1,
    "title": "RH - Politique interne",
    "filename": "rh_politique.pdf",
    "created_at": "2026-04-03T10:00:00Z",
    "chunk_count": 42
  }
]
```

---

### `DELETE /documents/{document_id}`
Supprime un document et tous ses chunks associés.

- **Réponse** : `DeleteResponse`
```json
{
  "document_id": 1,
  "deleted_chunks": 42,
  "message": "Document and its chunks deleted successfully."
}
```

---

## Structure du projet

```
Mini RAG-ESN/
├── main.py                   # Point d'entrée FastAPI
├── requirements.txt
├── .env.example              # Variables d'environnement (modèle)
├── .gitignore
│
├── app/
│   ├── db/
│   │   └── supabase.py       # Client Supabase singleton
│   ├── models/
│   │   └── schemas.py        # Modèles Pydantic
│   ├── routes/
│   │   ├── upload.py         # POST /upload
│   │   ├── ask.py            # POST /ask
│   │   └── documents.py      # GET & DELETE /documents
│   └── services/
│       ├── chunker.py        # Extraction de texte et découpage
│       ├── embedder.py       # Embeddings OpenAI
│       ├── retriever.py      # Recherche vectorielle Supabase
│       └── generator.py      # Génération de réponse Claude
│
├── frontend/
│   └── index.html            # Interface utilisateur
│
└── sql/
    └── schema.sql            # Schéma PostgreSQL + fonction match_chunks
```
