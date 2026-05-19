# AgentLantern — Guide d'utilisation

## Vue d'ensemble

**AgentLantern** génère automatiquement une documentation complète pour les projets de systèmes d'agents LLM, la sert dans un navigateur web, et peut visualiser une exécution d'agents en direct avec `lantern play`.

La détection du framework est automatique — il n'y a rien à configurer.

## Frameworks supportés

| Framework | Analyse | Détection automatique |
| --- | --- | --- |
| **CrewAI** | Complète | `crewai` dans les dépendances ou `crew.py` avec `@CrewBase` |
| **LangGraph** | À venir | `langgraph` dans les dépendances |
| **AutoGen** | À venir | `autogen-agentchat` ou `pyautogen` dans les dépendances |
| **Smolagents** | À venir | `smolagents` dans les dépendances |
| **Google ADK** | À venir | `google-adk` dans les dépendances |

Pour les frameworks marqués "à venir", AgentLantern génère quand même un site de documentation avec les informations disponibles (`pyproject.toml`) et indique que l'analyse complète est prévue.

## Installation

```bash
pip install agentlantern
```

Ou avec `uv` :
```bash
uv tool install agentlantern
```

## Utilisation

### Générer et visualiser la documentation

```bash
# Depuis la racine d'un projet agent
lantern web

# Ou en spécifiant le chemin
lantern web /chemin/vers/votre-projet
```

### Générer la documentation uniquement

```bash
lantern docs
lantern docs /chemin/vers/votre-projet

# Dans un dossier de sortie spécifique
lantern docs /chemin/vers/votre-projet -o /chemin/vers/sortie
```

### Options utiles

```bash
# Port personnalisé (si 9000 est occupé)
lantern web --port 9001

# Servir sans régénérer
lantern web --no-generate

# Hôte personnalisé
lantern web --host 0.0.0.0 --port 9000
```

### Visualiser une exécution en direct

```bash
# Depuis la racine d'un projet agent
lantern play

# Ou en spécifiant le chemin
lantern play /chemin/vers/votre-projet

# Ports personnalisés
lantern play /chemin/vers/votre-projet --ws-port 8790 --http-port 8791
```

L'interface Play s'ouvre dans le navigateur. Si `--name` n'est pas fourni, l'UI demande un nom de run avant **START**. Utilisez **STOP** pour arrêter le run actif.

L'UI Play affiche :

- une ville pixel-art avec un layout dynamique pour 1 à 10 agents ;
- exactement `n` agents visibles pour `n` agents déclarés ;
- des couleurs distinctes jusqu'à 20 agents ;
- un **Tool Hub** central consulté visuellement lors des appels d'outils ;
- les panneaux Timeline, Thoughts, Tools, Comms et Log ;
- les noms et bulles de pensée des agents ;
- le rapport final `report.md` quand il existe à la fin du run.

Pour sauvegarder et rejouer un run :

```bash
lantern play /chemin/vers/votre-projet --name demo-run
lantern replay demo-run
```

## Ce qui est généré

AgentLantern écrit les fichiers suivants dans `<projet>/docs/` :

| Fichier | Contenu |
| --- | --- |
| `overview.md` | Snapshot du projet, entrypoints, flux haut niveau |
| `architecture.md` | Carte système, fichiers clés, dépendances, variables d'environnement |
| `agents.md` | Rôles, objectifs, tools et backstories des agents |
| `tasks.md` | Descriptions des tâches, agents assignés, outputs attendus |
| `diagrams.md` | Diagrammes Mermaid : graphe agent-task, flux d'exécution, séquence |
| `runbook.md` | Installation, configuration, exécution, vérifications statiques |
| `contact.md` | Contacts du projet depuis `pyproject.toml` |
| `index.html` | Site Docsify (publiable sur GitHub Pages) |
| `agentlantern-docs.html` | Bundle HTML autonome et partageable |

## Exemples

### Projet CrewAI

```bash
cd ~/mes-projets/mon-crew
lantern web
# → Analyse complète : agents, tasks, diagrammes, architecture
```

### Projet Google ADK (ou autre framework en cours d'implémentation)

```bash
lantern web ~/mes-projets/mon-projet-adk
# → Framework détecté automatiquement
# → Documentation de base générée depuis pyproject.toml
# → Message indiquant que l'analyse complète est à venir
```

### Plusieurs projets en parallèle

```bash
lantern web ~/projets/projet-a --port 9000
lantern web ~/projets/projet-b --port 9001   # dans un autre terminal
```

## Référence des commandes

### `lantern docs [project] [-o OUTPUT_DIR]`

Génère la documentation d'un projet agent.

| Argument / Option | Description |
| --- | --- |
| `project` | Chemin vers le projet (défaut : répertoire courant) |
| `-o`, `--output-dir` | Dossier de sortie (défaut : `<project>/docs/`) |

### `lantern web [project]`

Génère (sauf `--no-generate`) et sert la documentation dans un navigateur.

| Argument / Option | Description |
| --- | --- |
| `project` | Chemin vers le projet (défaut : répertoire courant) |
| `--host HOST` | Adresse du serveur (défaut : `0.0.0.0`) |
| `--port PORT` | Port du serveur (défaut : `9000`) |
| `--no-generate` | Ne régénère pas les docs avant de servir |

### `lantern play [project]`

Lance l'interface animée de visualisation d'un run agent.

| Argument / Option | Description |
| --- | --- |
| `project` | Chemin vers le projet (défaut : répertoire courant) |
| `--ws-port PORT` | Port WebSocket pour les événements live (défaut : `7890`) |
| `--http-port PORT` | Port HTTP de l'UI Play (défaut : `7891`) |
| `--name NAME` | Sauvegarde le run dans `.lantern_replays/<name>.jsonl` et démarre automatiquement. Sans `--name`, l'UI demande le nom avant START |

### `lantern replay NAME`

Rejoue un run sauvegardé par `lantern play --name`.

| Argument / Option | Description |
| --- | --- |
| `NAME` | Nom du replay ou chemin direct vers un fichier `.jsonl` |
| `--speed FLOAT` | Vitesse de lecture (défaut : `1.0`) |
| `--ws-port PORT` | Port WebSocket (défaut : `7890`) |
| `--http-port PORT` | Port HTTP (défaut : `7891`) |

## Dépannage

| Symptôme | Solution |
| --- | --- |
| `No framework detected` | Vérifier que `pyproject.toml` liste un framework supporté dans `dependencies` |
| Port occupé | Utiliser `--port PORT` avec un port libre |
| Documentation non mise à jour | Relancer `lantern docs` puis `lantern web --no-generate` |
| Diagrammes sans rendu | Utiliser `lantern web` (Mermaid nécessite un navigateur) |
| Ancienne version de `lantern` dans le PATH | Vérifier avec `which lantern` — réinstaller avec `uv tool install agentlantern --force` |
| START ne lance rien dans Play | Fermer l'ancien onglet, rouvrir l'URL imprimée, vérifier le port `?ws=...`, puis rafraîchir l'installation avec `uv tool install --force --refresh .` en développement local |
| Play démarre mais l'UI ne bouge pas | Vérifier le panneau Log et le terminal : le projet peut attendre une clé API, un appel modèle, une dépendance ou un outil externe |
