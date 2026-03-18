from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path

import yaml

from car_tracker.config import BookingConfig


def remove_expired_bookings(config_path: Path, today: date) -> list[BookingConfig]:
    """Remove bookings whose pickup_date is strictly before today.

    Writes the updated config.yaml back to disk and runs git add/commit/push
    if any bookings were removed. Returns the list of removed BookingConfig
    objects.
    """
    with config_path.open() as f:
        raw = yaml.safe_load(f)

    bookings_raw: list[dict] = raw.get("bookings") or []

    kept: list[dict] = []
    removed_raw: list[dict] = []

    for b in bookings_raw:
        pickup = date.fromisoformat(b["pickup_date"])
        if today > pickup:
            removed_raw.append(b)
        else:
            kept.append(b)

    if not removed_raw:
        return []

    # Write updated config back to disk
    raw["bookings"] = kept
    with config_path.open("w") as f:
        yaml.dump(raw, f, default_flow_style=False, allow_unicode=True)

    # Git: add → commit → pull --rebase --autostash → push
    repo_dir = config_path.parent
    subprocess.run(["git", "add", str(config_path)], cwd=repo_dir, check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            f"chore(config): remove {len(removed_raw)} expired booking(s)",
        ],
        cwd=repo_dir,
        check=True,
    )
    subprocess.run(["git", "pull", "--rebase", "--autostash"], cwd=repo_dir, check=True)
    subprocess.run(["git", "push"], cwd=repo_dir, check=True)

    # Construct BookingConfig objects for the removed bookings
    removed: list[BookingConfig] = []
    for b in removed_raw:
        holding_raw = b.get("holding_price")
        holding_type_raw = b.get("holding_vehicle_type")
        if holding_raw is not None and holding_type_raw is not None:
            holding_price: float | None = float(holding_raw)
            holding_vehicle_type: str | None = str(holding_type_raw)
        else:
            holding_price = None
            holding_vehicle_type = None

        removed.append(
            BookingConfig(
                name=str(b.get("name", "")),
                pickup_location=str(b.get("pickup_location", "")),
                pickup_date=str(b.get("pickup_date", "")),
                pickup_time=str(b.get("pickup_time", "")),
                dropoff_date=str(b.get("dropoff_date", "")),
                dropoff_time=str(b.get("dropoff_time", "")),
                holding_price=holding_price,
                holding_vehicle_type=holding_vehicle_type,
            )
        )

    return removed
