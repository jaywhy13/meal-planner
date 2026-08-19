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
mount -t efs -o tls,iam,accesspoint={access_point_id} {file_system_id}: /mnt/data

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
# backend/meal_planner/settings.py:135-149. Exporting it system-wide makes
# that failure mode impossible instead of merely documented.
echo 'export DATABASE_URL=sqlite:////mnt/data/db.sqlite3' > /etc/profile.d/database-url.sh
chmod 644 /etc/profile.d/database-url.sh
