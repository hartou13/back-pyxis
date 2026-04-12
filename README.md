# Pyxis

# Installation et configuration de l'environnement

Suivez les étapes ci-dessous pour configurer votre environnement :

1. Installez UV, un gestionnaire de paquets Python moderne :

   **Sur macOS et Linux :**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   **Sur Windows :**

   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   ## Initialisation du projet et création de l'environnement virtuel

    **Windows (PowerShell)** — à la racine du dépôt (`back-pyxis`) :

    ```powershell
    # Uniquement si `pyproject.toml` n'existe pas encore
    uv init

    uv venv
    # Facultatif : `uv run` et `uv sync` fonctionnent sans activation
    .\.venv\Scripts\Activate.ps1
    ```

    **macOS et Linux** (équivalent) :

    ```bash
    uv init
    uv venv
    source .venv/bin/activate
    ```

2. Utilisez UV pour configurer votre environnement :

   ```bash
   # Synchronisation de l'environnement
   uv sync
   ```

3. Pour valider la mise à jour de vos modèles :

   ```bash
   alembic -c alembic.ini revision --autogenerate -m "description of your changes"
   ```

4. Executer la mise à jour de votre base de données :

   ```bash
   alembic -c alembic.ini upgrade head
   ```

5. Lancer l'application (pour le moment):

   ```bash
   uvicorn main:app --reload
   ```
