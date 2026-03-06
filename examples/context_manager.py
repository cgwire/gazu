"""
Using gazu with context managers (with statement) for automatic session
cleanup. Also shows multi-client usage for working with two Kitsu instances.

Note: create_session uses email/password login internally. For bot
authentication (token-based), use create_client + set_token instead
(see the last section of this example).

Run:
    python examples/context_manager.py
"""

import gazu
from gazu.client import create_client

# --- Single session with automatic logout (email/password) ---

# create_session returns a KitsuClient that can be used as a context manager.
# On exit, it automatically logs out and closes the HTTP session.

with gazu.create_session(
    "https://kitsu.example.com/api",
    "user@example.com",
    "password",
) as client:
    projects = gazu.project.all_open_projects(client=client)
    print(f"Found {len(projects)} open projects")

    for project in projects:
        assets = gazu.asset.all_assets_for_project(
            project, client=client
        )
        shots = gazu.shot.all_shots_for_project(project, client=client)
        print(f"  {project['name']}: {len(assets)} assets, {len(shots)} shots")

# No need to call gazu.log_out() -- it was done automatically.
print("Session closed automatically\n")


# --- Multiple clients for different instances ---

# You can work with several Kitsu instances at the same time by creating
# separate clients.

with gazu.create_session(
    "https://kitsu-studio-a.example.com/api",
    "artist@studio-a.com",
    "password_a",
) as client_a, gazu.create_session(
    "https://kitsu-studio-b.example.com/api",
    "artist@studio-b.com",
    "password_b",
) as client_b:
    projects_a = gazu.project.all_open_projects(client=client_a)
    projects_b = gazu.project.all_open_projects(client=client_b)
    print(f"Studio A: {len(projects_a)} projects")
    print(f"Studio B: {len(projects_b)} projects")


# --- Bot authentication (token-based) ---

# create_session does NOT support bot tokens. For bots, use create_client
# and set_token directly. The client still works as a context manager for
# automatic session cleanup (but won't call log_out on exit since
# bot tokens are long-lived).

client = create_client("https://kitsu.example.com/api")
gazu.set_token("your-bot-access-token-here", client=client)

projects = gazu.project.all_open_projects(client=client)
print(f"\nBot client: {len(projects)} projects")


# --- Using create_client for manual control ---

# When you need finer control (e.g. custom SSL settings or token refresh),
# create a client manually with email/password.

client = create_client(
    "https://kitsu.example.com/api",
    ssl_verify=False,           # disable SSL verification
    use_refresh_token=True,     # auto-refresh expired tokens
)
gazu.log_in("user@example.com", "password", client=client)

projects = gazu.project.all_open_projects(client=client)
print(f"\nManual client: {len(projects)} projects")

gazu.log_out(client=client)
print("Manual client logged out.")
