"""
Command-line interface for the Kitsu API (via Gazu).

Usage:
    gazu-cli login --host https://kitsu.example.com/api
    gazu-cli status
    gazu-cli projects
    gazu-cli assets --project "My Project"
    gazu-cli my-tasks
"""

import json
import os
import uuid

import click

import gazu
from gazu import (
    asset as gazu_asset,
    casting as gazu_casting,
    client as raw,
    person as gazu_person,
    project as gazu_project,
    search as gazu_search,
    shot as gazu_shot,
    task as gazu_task,
    user as gazu_user,
)
from gazu.exception import (
    AuthFailedException,
    NotAuthenticatedException,
    NotAllowedException,
    RouteNotFoundException,
    ServerErrorException,
)

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".gazu")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


# --- Config management ---


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(data):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(CONFIG_FILE, 0o600)


def clear_config():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)


# --- Output helpers ---


def print_table(rows, columns):
    """Print a list of dicts as aligned columns.

    Args:
        rows: list of dicts
        columns: list of (header, key) tuples
    """
    if not rows:
        click.echo("No results.")
        return

    headers = [h for h, _ in columns]
    values = []
    for row in rows:
        values.append(
            [_truncate(str(row.get(k, "") or ""), 60) for _, k in columns]
        )

    widths = [len(h) for h in headers]
    for row_vals in values:
        for i, val in enumerate(row_vals):
            widths[i] = max(widths[i], len(val))

    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    click.echo(fmt.format(*headers))
    click.echo(fmt.format(*["-" * w for w in widths]))
    for row_vals in values:
        click.echo(fmt.format(*row_vals))


def _truncate(text, max_len):
    text = text.replace("\n", " ").strip()
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def output(ctx, data, columns):
    """Output data as JSON or table depending on context flag."""
    if ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if isinstance(data, list):
            print_table(data, columns)
        else:
            for header, key in columns:
                click.echo(f"{header}: {data.get(key, '')}")


# --- Resolution helpers ---


def _is_uuid(value):
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def resolve_project(name_or_id):
    if _is_uuid(name_or_id):
        return gazu_project.get_project(name_or_id)
    result = gazu_project.get_project_by_name(name_or_id)
    if result is None:
        click.echo(f"Project not found: {name_or_id}", err=True)
        raise SystemExit(1)
    return result


def get_project_from_option(project_opt):
    """Resolve project from CLI option or GAZU_PROJECT env var."""
    name_or_id = project_opt or os.environ.get("GAZU_PROJECT")
    if not name_or_id:
        click.echo(
            "Project required: use --project or set GAZU_PROJECT.",
            err=True,
        )
        raise SystemExit(1)
    return resolve_project(name_or_id)


# --- Auth bootstrap ---


def setup_client():
    """Load config and configure the gazu default client."""
    config = load_config()
    host = config.get("host")
    tokens = config.get("tokens")
    if not host or not tokens:
        click.echo("Not logged in. Run: gazu-cli login --host <URL>", err=True)
        raise SystemExit(1)
    gazu.set_host(host)
    gazu.set_token(tokens)


# --- Error handling ---


def handle_errors(fn):
    """Decorator to catch common gazu exceptions."""

    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except AuthFailedException:
            click.echo("Authentication failed.", err=True)
            raise SystemExit(1)
        except NotAuthenticatedException:
            click.echo("Session expired. Run: gazu-cli login", err=True)
            raise SystemExit(1)
        except NotAllowedException:
            click.echo("Permission denied.", err=True)
            raise SystemExit(1)
        except RouteNotFoundException as e:
            click.echo(f"Not found: {e}", err=True)
            raise SystemExit(1)
        except ServerErrorException:
            click.echo("Server error. Check your Kitsu instance.", err=True)
            raise SystemExit(1)

    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


# --- CLI definition ---


@click.group()
@click.option("--json", "use_json", is_flag=True, help="Output as JSON.")
@click.version_option(version=gazu.__version__, prog_name="gazu-cli")
@click.pass_context
def cli(ctx, use_json):
    """Gazu CLI - Command-line client for the Kitsu API."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = use_json


# --- Auth commands ---


@cli.command()
@click.option("--host", prompt=True, help="Kitsu API URL.")
@click.option("--email", prompt=True, help="User email.")
@click.option(
    "--password", prompt=True, hide_input=True, help="User password."
)
@handle_errors
def login(host, email, password):
    """Log in to a Kitsu instance and store credentials."""
    if not host.endswith("/api"):
        host = host.rstrip("/") + "/api"
    gazu.set_host(host)
    tokens = gazu.log_in(email, password)
    save_config({"host": host, "tokens": tokens})
    click.echo(f"Logged in to {host}")


@cli.command()
@handle_errors
def logout():
    """Log out and clear stored credentials."""
    try:
        setup_client()
        gazu.log_out()
    except SystemExit:
        pass
    clear_config()
    click.echo("Logged out.")


@cli.command()
@click.pass_context
@handle_errors
def status(ctx):
    """Show current connection status."""
    setup_client()
    user = raw.get_current_user()
    version = raw.get_api_version()
    config = load_config()
    if ctx.obj["json"]:
        click.echo(
            json.dumps(
                {
                    "host": config.get("host"),
                    "api_version": version,
                    "user": user,
                },
                indent=2,
                default=str,
            )
        )
    else:
        click.echo(f"Host:    {config.get('host')}")
        click.echo(f"API:     {version}")
        click.echo(
            f"User:    {user.get('first_name')} "
            f"{user.get('last_name')} ({user.get('email')})"
        )


# --- Project commands ---


@cli.command()
@click.option("--all", "show_all", is_flag=True, help="Include closed.")
@click.pass_context
@handle_errors
def projects(ctx, show_all):
    """List projects."""
    setup_client()
    if show_all:
        data = gazu_project.all_projects()
    else:
        data = gazu_project.all_open_projects()
    output(
        ctx,
        data,
        [
            ("NAME", "name"),
            ("TYPE", "production_type"),
            ("STYLE", "production_style"),
            ("ID", "id"),
        ],
    )


@cli.command()
@click.argument("name_or_id")
@click.pass_context
@handle_errors
def project(ctx, name_or_id):
    """Show details for a project."""
    setup_client()
    data = resolve_project(name_or_id)
    output(
        ctx,
        data,
        [
            ("NAME", "name"),
            ("TYPE", "production_type"),
            ("STYLE", "production_style"),
            ("STATUS", "project_status_name"),
            ("ID", "id"),
        ],
    )


# --- Asset commands ---


@cli.command()
@click.option("--project", "-p", "project_opt", help="Project name/ID.")
@click.option("--type", "-t", "asset_type", help="Filter by asset type.")
@click.pass_context
@handle_errors
def assets(ctx, project_opt, asset_type):
    """List assets for a project."""
    setup_client()
    proj = get_project_from_option(project_opt)
    if asset_type:
        at = gazu_asset.get_asset_type_by_name(asset_type)
        if at is None:
            click.echo(f"Asset type not found: {asset_type}", err=True)
            raise SystemExit(1)
        data = gazu_asset.all_assets_for_project_and_type(proj, at)
    else:
        data = gazu_asset.all_assets_for_project(proj)
    output(
        ctx,
        data,
        [
            ("NAME", "name"),
            ("TYPE", "asset_type_name"),
            ("DESCRIPTION", "description"),
            ("ID", "id"),
        ],
    )


@cli.command()
@click.argument("name_or_id")
@click.option("--project", "-p", "project_opt", help="Project name/ID.")
@click.pass_context
@handle_errors
def asset(ctx, name_or_id, project_opt):
    """Show details for an asset."""
    setup_client()
    if _is_uuid(name_or_id):
        data = gazu_asset.get_asset(name_or_id)
    else:
        proj = get_project_from_option(project_opt)
        data = gazu_asset.get_asset_by_name(proj, name_or_id)
        if data is None:
            click.echo(f"Asset not found: {name_or_id}", err=True)
            raise SystemExit(1)
    output(
        ctx,
        data,
        [
            ("NAME", "name"),
            ("TYPE", "asset_type_name"),
            ("DESCRIPTION", "description"),
            ("PROJECT", "project_name"),
            ("ID", "id"),
        ],
    )


# --- Shot commands ---


@cli.command()
@click.option("--project", "-p", "project_opt", help="Project name/ID.")
@click.option("--sequence", "-s", help="Filter by sequence name.")
@click.option("--episode", "-e", help="Filter by episode name.")
@click.pass_context
@handle_errors
def shots(ctx, project_opt, sequence, episode):
    """List shots for a project."""
    setup_client()
    proj = get_project_from_option(project_opt)
    if sequence:
        seq = gazu_shot.get_sequence_by_name(proj, sequence)
        if seq is None:
            click.echo(f"Sequence not found: {sequence}", err=True)
            raise SystemExit(1)
        data = gazu_shot.all_shots_for_sequence(seq)
    elif episode:
        ep = gazu_shot.get_episode_by_name(proj, episode)
        if ep is None:
            click.echo(f"Episode not found: {episode}", err=True)
            raise SystemExit(1)
        data = gazu_shot.all_shots_for_episode(ep)
    else:
        data = gazu_shot.all_shots_for_project(proj)
    output(
        ctx,
        data,
        [
            ("SEQUENCE", "sequence_name"),
            ("NAME", "name"),
            ("FRAMES", "nb_frames"),
            ("DESCRIPTION", "description"),
            ("ID", "id"),
        ],
    )


@cli.command()
@click.option("--project", "-p", "project_opt", help="Project name/ID.")
@click.option("--episode", "-e", help="Filter by episode name.")
@click.pass_context
@handle_errors
def sequences(ctx, project_opt, episode):
    """List sequences for a project."""
    setup_client()
    proj = get_project_from_option(project_opt)
    if episode:
        ep = gazu_shot.get_episode_by_name(proj, episode)
        if ep is None:
            click.echo(f"Episode not found: {episode}", err=True)
            raise SystemExit(1)
        data = gazu_shot.all_sequences_for_episode(ep)
    else:
        data = gazu_shot.all_sequences_for_project(proj)
    output(
        ctx,
        data,
        [
            ("NAME", "name"),
            ("EPISODE", "episode_name"),
            ("ID", "id"),
        ],
    )


@cli.command()
@click.option("--project", "-p", "project_opt", help="Project name/ID.")
@click.pass_context
@handle_errors
def episodes(ctx, project_opt):
    """List episodes for a project."""
    setup_client()
    proj = get_project_from_option(project_opt)
    data = gazu_shot.all_episodes_for_project(proj)
    output(
        ctx,
        data,
        [("NAME", "name"), ("ID", "id")],
    )


# --- Task commands ---


@cli.command()
@click.option("--project", "-p", "project_opt", help="Project name/ID.")
@click.option("--type", "-t", "task_type", help="Filter by task type.")
@click.option("--status", "-s", "task_status", help="Filter by status.")
@click.pass_context
@handle_errors
def tasks(ctx, project_opt, task_type, task_status):
    """List tasks for a project."""
    setup_client()
    proj = get_project_from_option(project_opt)
    if task_type and task_status:
        tt = gazu_task.get_task_type_by_name(task_type)
        ts = gazu_task.get_task_status_by_short_name(task_status)
        if tt is None:
            click.echo(f"Task type not found: {task_type}", err=True)
            raise SystemExit(1)
        if ts is None:
            click.echo(f"Task status not found: {task_status}", err=True)
            raise SystemExit(1)
        data = gazu_task.all_tasks_for_task_status(proj, tt, ts)
    elif task_type:
        tt = gazu_task.get_task_type_by_name(task_type)
        if tt is None:
            click.echo(f"Task type not found: {task_type}", err=True)
            raise SystemExit(1)
        data = gazu_task.all_tasks_for_task_type(proj, tt)
    else:
        data = raw.fetch_all(
            "tasks", {"project_id": proj["id"]}, client=raw.default_client
        )
    output(
        ctx,
        data,
        [
            ("ENTITY", "entity_name"),
            ("TYPE", "task_type_name"),
            ("STATUS", "task_status_name"),
            ("ASSIGNEES", "assignees"),
            ("ID", "id"),
        ],
    )


@cli.command()
@click.argument("task_id")
@click.pass_context
@handle_errors
def task(ctx, task_id):
    """Show details for a task (by ID)."""
    setup_client()
    data = gazu_task.get_task(task_id)
    output(
        ctx,
        data,
        [
            ("ENTITY", "entity_name"),
            ("TYPE", "task_type_name"),
            ("STATUS", "task_status_name"),
            ("ASSIGNEES", "assignees"),
            ("PROJECT", "project_name"),
            ("DESCRIPTION", "description"),
            ("ID", "id"),
        ],
    )


@cli.command()
@click.option("--task", "-t", "task_id", required=True, help="Task ID.")
@click.option(
    "--status",
    "-s",
    "status_short",
    required=True,
    help="Task status short name (e.g. wip, done, todo).",
)
@click.option("--message", "-m", default="", help="Comment text.")
@handle_errors
def comment(task_id, status_short, message):
    """Post a comment on a task (with status change)."""
    setup_client()
    ts = gazu_task.get_task_status_by_short_name(status_short)
    if ts is None:
        click.echo(f"Task status not found: {status_short}", err=True)
        raise SystemExit(1)
    result = gazu_task.add_comment(task_id, ts, comment=message)
    click.echo(f"Comment posted (ID: {result.get('id')})")


# --- Person commands ---


@cli.command()
@click.pass_context
@handle_errors
def persons(ctx):
    """List all persons."""
    setup_client()
    data = gazu_person.all_persons()
    output(
        ctx,
        data,
        [
            ("FIRST NAME", "first_name"),
            ("LAST NAME", "last_name"),
            ("EMAIL", "email"),
            ("ROLE", "role"),
            ("ID", "id"),
        ],
    )


# --- User commands ---


@cli.command("my-tasks")
@click.option("--done", is_flag=True, help="Show done tasks instead.")
@click.pass_context
@handle_errors
def my_tasks(ctx, done):
    """List tasks assigned to current user."""
    setup_client()
    if done:
        data = gazu_user.all_done_tasks()
    else:
        data = gazu_user.all_tasks_to_do()
    output(
        ctx,
        data,
        [
            ("PROJECT", "project_name"),
            ("ENTITY", "entity_name"),
            ("TYPE", "task_type_name"),
            ("STATUS", "task_status_name"),
            ("ID", "id"),
        ],
    )


# --- Search ---


@cli.command()
@click.argument("query")
@click.option("--project", "-p", "project_opt", help="Project name/ID.")
@click.pass_context
@handle_errors
def search(ctx, query, project_opt):
    """Search for entities across the Kitsu instance."""
    setup_client()
    proj = None
    if project_opt:
        proj = resolve_project(project_opt)
    data = gazu_search.search_entities(query, project=proj)
    if ctx.obj["json"]:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        for entity_type, entities in data.items():
            if entities:
                click.echo(f"\n{entity_type.upper()} ({len(entities)})")
                click.echo("-" * 40)
                for entity in entities:
                    name = entity.get("name", entity.get("full_name", ""))
                    click.echo(f"  {name}  ({entity.get('id', '')})")


# --- Casting ---


@cli.command("shot-casting")
@click.argument("shot_id")
@click.pass_context
@handle_errors
def shot_casting(ctx, shot_id):
    """Show casting (assets linked) for a shot."""
    setup_client()
    data = gazu_casting.get_shot_casting(shot_id)
    if ctx.obj["json"]:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if not data:
            click.echo("No casting for this shot.")
            return
        for entry in data:
            name = entry.get("asset_name", entry.get("name", str(entry)))
            nb = entry.get("nb_occurences", 1)
            click.echo(f"  {name} (x{nb})")


# --- Asset types / Task types / Task statuses ---


@cli.command("asset-types")
@click.option("--project", "-p", "project_opt", help="Project name/ID.")
@click.pass_context
@handle_errors
def asset_types(ctx, project_opt):
    """List asset types."""
    setup_client()
    if project_opt:
        proj = resolve_project(project_opt)
        data = gazu_asset.all_asset_types_for_project(proj)
    else:
        data = gazu_asset.all_asset_types()
    output(ctx, data, [("NAME", "name"), ("ID", "id")])


@cli.command("task-types")
@click.option("--project", "-p", "project_opt", help="Project name/ID.")
@click.pass_context
@handle_errors
def task_types(ctx, project_opt):
    """List task types."""
    setup_client()
    if project_opt:
        proj = resolve_project(project_opt)
        data = gazu_task.all_task_types_for_project(proj)
    else:
        data = gazu_task.all_task_types()
    output(
        ctx,
        data,
        [("NAME", "name"), ("FOR", "for_entity"), ("ID", "id")],
    )


@cli.command("task-statuses")
@click.option("--project", "-p", "project_opt", help="Project name/ID.")
@click.pass_context
@handle_errors
def task_statuses(ctx, project_opt):
    """List task statuses."""
    setup_client()
    if project_opt:
        proj = resolve_project(project_opt)
        data = gazu_task.all_task_statuses_for_project(proj)
    else:
        data = gazu_task.all_task_statuses()
    output(
        ctx,
        data,
        [
            ("NAME", "name"),
            ("SHORT", "short_name"),
            ("ID", "id"),
        ],
    )


def main():
    cli()


if __name__ == "__main__":
    main()
