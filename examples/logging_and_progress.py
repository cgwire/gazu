"""
Logging and progress callbacks in gazu.

Gazu uses Python's standard logging module. The sync client logs to the
"gazu" logger, the async client to "gazu.aio". You can also set the
GAZU_DEBUG=true environment variable to enable debug logging at import time.

Progress callbacks are available on upload() and download() functions in
both the sync and async clients.

Run:
    python examples/logging_and_progress.py
"""

import logging
import sys

import gazu

# --- Configure logging ---

# Option 1: See all gazu HTTP requests (GET, POST, PUT, DELETE)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
gazu_logger = logging.getLogger("gazu")
gazu_logger.setLevel(logging.DEBUG)

# Option 2: Only show warnings and errors (quieter)
# gazu_logger.setLevel(logging.WARNING)

# Option 3: Log to a file instead of stdout
# handler = logging.FileHandler("gazu.log")
# handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
# gazu_logger.addHandler(handler)

# The async module uses a separate logger
gazu_aio_logger = logging.getLogger("gazu.aio")
gazu_aio_logger.setLevel(logging.DEBUG)


# --- Progress callbacks ---

# Upload and download accept a progress_callback(bytes_read, total) function.
# `total` is the sum of file sizes for uploads, or the Content-Length header
# for downloads (0 when unknown).


def print_progress(bytes_read, total):
    """Simple text progress indicator."""
    if total > 0:
        pct = bytes_read / total * 100
        bar = "#" * int(pct // 2) + "-" * (50 - int(pct // 2))
        print(f"\r  [{bar}] {pct:5.1f}%", end="", flush=True)
    else:
        mb = bytes_read / (1024 * 1024)
        print(f"\r  {mb:.1f} MB downloaded", end="", flush=True)


# --- Example: upload and download with progress ---

with gazu.create_session(
    "https://kitsu.example.com/api",
    "user@example.com",
    "password",
) as client:
    projects = gazu.project.all_open_projects(client=client)
    print(f"Found {len(projects)} open projects")

    # Upload a thumbnail with progress tracking
    if projects:
        project = projects[0]
        print(f"\nUploading thumbnail for '{project['name']}'...")
        gazu.raw.upload(
            f"pictures/thumbnails/projects/{project['id']}",
            "/path/to/thumbnail.png",
            client=client,
            progress_callback=print_progress,
        )
        print("\n  Upload complete.")

    # Download a file with progress tracking
    # (requires a valid preview_file_id)
    assets = gazu.asset.all_assets_for_project(projects[0], client=client)
    if assets:
        preview_id = assets[0].get("preview_file_id")
        if preview_id:
            print(f"\nDownloading preview for '{assets[0]['name']}'...")
            gazu.raw.download(
                f"pictures/originals/preview-files/{preview_id}.png",
                "/tmp/preview.png",
                client=client,
                progress_callback=print_progress,
            )
            print("\n  Download complete.")

print("\nDone.")
