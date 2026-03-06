"""
Async usage of gazu with asyncio and aiohttp.

The async module (gazu.aio) provides the same primitives (get, post, put,
delete, fetch_all, upload, download) but as coroutines. There is no default
client -- you must always pass an explicit client.

Requirements:
    pip install gazu[async]

Run:
    python examples/async_queries.py
"""

import asyncio

import gazu.aio


async def list_project_contents(client, project):
    """Fetch assets and shots for a project concurrently."""
    assets, shots = await asyncio.gather(
        gazu.aio.fetch_all(
            f"projects/{project['id']}/assets", client=client
        ),
        gazu.aio.fetch_all(
            f"projects/{project['id']}/shots", client=client
        ),
    )
    return assets, shots


async def main():
    # --- Create an async session (auto login + auto logout) ---

    async with await gazu.aio.create_session(
        "https://kitsu.example.com/api",
        "user@example.com",
        "password",
    ) as client:

        # --- Fetch all open projects ---
        projects = await gazu.aio.get("data/projects/open", client=client)
        print(f"Open projects: {len(projects)}")

        # --- Fetch project details concurrently ---
        # asyncio.gather runs all coroutines in parallel, which is much
        # faster than fetching each project sequentially.
        results = await asyncio.gather(
            *(
                list_project_contents(client, project)
                for project in projects[:5]
            )
        )

        for project, (assets, shots) in zip(projects[:5], results):
            print(
                f"  {project['name']}: "
                f"{len(assets)} assets, {len(shots)} shots"
            )

        # --- Low-level async primitives ---

        # fetch_all supports pagination
        all_tasks = await gazu.aio.fetch_all(
            "tasks", client=client, paginated=True, limit=100
        )
        print(f"\nTotal tasks (paginated): {len(all_tasks)}")

        # fetch_one retrieves a single entity by ID
        if projects:
            project = await gazu.aio.fetch_one(
                "projects", projects[0]["id"], client=client
            )
            print(f"First project: {project['name']}")

        # fetch_first returns the first match or None
        first_asset = await gazu.aio.fetch_first("assets", client=client)
        if first_asset:
            print(f"First asset: {first_asset['name']}")

        # --- Download with progress callback ---

        def on_download_progress(bytes_read, total):
            if total > 0:
                pct = bytes_read / total * 100
                print(f"\r  Downloading: {pct:.0f}%", end="", flush=True)

        if first_asset:
            preview_id = first_asset.get("preview_file_id")
            if preview_id:
                await gazu.aio.download(
                    f"pictures/originals/preview-files/{preview_id}.png",
                    "/tmp/preview.png",
                    client=client,
                    progress_callback=on_download_progress,
                )
                print("\n  Download complete.")


asyncio.run(main())
