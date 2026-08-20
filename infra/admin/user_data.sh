#!/bin/bash
set -euo pipefail

# Amazon Linux 2023 ships with the Systems Manager agent preinstalled — this
# script only adds what's specific to a Django maintenance shell against the
# app's EFS volume.
dnf install -y amazon-efs-utils git python3.12

# Installed to /usr/local/bin (already on every login shell's PATH) rather than
# the default ~/.local/bin, so uv is usable regardless of which user Session
# Manager opens the shell as.
curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

mkdir -p /mnt/data

# Mounting through the access point (not the file system root) forces every
# operation to uid/gid 1001, matching AppStorage's posix_user in the app stack.
# That keeps journal and write-ahead-log files this instance creates owned by
# the same id the Lambda already uses — mounting the file system root instead
# would create root-owned files that break the Lambda after this box is gone.
#
# Written to /etc/fstab (with _netdev, so it waits for networking) rather than
# run as a one-off `mount`, so the volume remounts automatically if the
# instance reboots mid-session instead of silently staying unmounted.
echo '{file_system_id}:/ /mnt/data efs _netdev,tls,iam,accesspoint={access_point_id} 0 0' >> /etc/fstab

mount -a

# Public repository — no credentials needed to clone.
git clone https://github.com/jaywhy13/meal-planner /opt/meal-planner
cd /opt/meal-planner/backend
uv sync --frozen

# Session Manager's shell user isn't known until a session opens, so open up
# the checkout rather than chasing a specific uid — this box only exists for
# the lifetime of one maintenance session.
chmod -R a+rwX /opt/meal-planner

# Without this, an unset DATABASE_URL makes Django silently fall back to a
# brand-new empty SQLite file inside the checkout instead of erroring — see
# backend/meal_planner/settings.py:135-149.
#
# Written twice, because neither mechanism alone is reliable here: a shell
# only picks up /etc/profile.d/ if it sources it, which Session Manager isn't
# guaranteed to do, while backend/.env is read directly by python-decouple
# (backend/meal_planner/settings.py:18) regardless of shell startup behaviour.
# The .env file is the one that actually can't be skipped; the exported
# variable just makes `echo $DATABASE_URL` work as a quick sanity check.
database_url="sqlite:////mnt/data/db.sqlite3"
echo "export DATABASE_URL=${database_url}" > /etc/profile.d/database-url.sh
chmod 644 /etc/profile.d/database-url.sh
echo "DATABASE_URL=${database_url}" > /opt/meal-planner/backend/.env
chmod 644 /opt/meal-planner/backend/.env
