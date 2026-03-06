"""
Basic gazu usage: authentication, querying projects, assets, shots, and tasks.

Run:
    python examples/basic_queries.py
"""

import gazu

# --- Connect and authenticate ---

gazu.set_host("https://kitsu.example.com/api")
gazu.set_event_host("https://kitsu.example.com")
gazu.set_token("your-bot-access-token-here")

# --- Projects ---

projects = gazu.project.all_open_projects()
print(f"\nOpen projects ({len(projects)}):")
for project in projects:
    print(f"  - {project['name']} ({project['id']})")

# Get a single project by name
project = projects[0] if projects else None

# --- Assets ---

assets = gazu.asset.all_assets_for_project(project)
print(f"\nAssets for '{project['name']}' ({len(assets)}):")
for asset in assets[:5]:
    print(f"  - {asset['name']}")

# Get asset types
asset_types = gazu.asset.all_asset_types()
print(f"\nAsset types: {[t['name'] for t in asset_types]}")

# Get a specific asset by name
asset_type = gazu.asset.get_asset_type_by_name("Character")
if asset_type:
    character = gazu.asset.get_asset_by_name(
        project, "Hero", asset_type=asset_type
    )
    if character:
        print(f"\nFound character: {character['name']}")

# --- Shots ---

episodes = gazu.shot.all_episodes_for_project(project)
print(f"\nEpisodes ({len(episodes)}):")
for episode in episodes[:3]:
    print(f"  - {episode['name']}")

sequences = gazu.shot.all_sequences_for_project(project)
print(f"\nSequences ({len(sequences)}):")
for seq in sequences[:5]:
    print(f"  - {seq['name']}")

if sequences:
    shots = gazu.shot.all_shots_for_sequence(sequences[0])
    print(f"\nShots in '{sequences[0]['name']}' ({len(shots)}):")
    for shot in shots[:5]:
        nb_frames = shot.get("nb_frames", "?")
        print(f"  - {shot['name']} ({nb_frames} frames)")

# --- Tasks ---

task_types = gazu.task.all_task_types()
print(f"\nTask types: {[t['name'] for t in task_types]}")

task_statuses = gazu.task.all_task_statuses()
print(f"Task statuses: {[s['name'] for s in task_statuses]}")

if assets:
    tasks = gazu.task.all_tasks_for_asset(assets[0])
    print(f"\nTasks for asset '{assets[0]['name']}':")
    for task in tasks:
        print(f"  - {task['task_type_name']}: {task['task_status_name']}")

# --- People ---

people = gazu.person.all_persons()
print(f"\nTeam members ({len(people)}):")
for person in people[:5]:
    print(f"  - {person['first_name']} {person['last_name']}")

# --- Cleanup ---
# Bot tokens don't support logout. Only call gazu.log_out() when
# authenticated via gazu.log_in() with email/password.

gazu.log_out()
print("\nDone.")
