import hashlib
import subprocess
from pathlib import Path

import pulumi
import pulumi_aws as aws
import pulumi_docker as docker

import config


def _compute_backend_source_hash() -> str:
    """Hash the contents of every git-known file under backend/.

    pulumi-docker v4 only diffs the declared inputs of docker.Image
    (context path, dockerfile path, platform). It computes a contextDigest
    but stores it as a state output — never as a diff input — so changes
    to source files in the build context never trigger a rebuild. Passing
    this hash through build_args adds a real, content-derived input that
    Pulumi will diff, forcing a rebuild + push whenever backend/ changes.

    Uses `git ls-files --cached --others --exclude-standard` so the hash
    matches what Docker actually sees: tracked files plus untracked files
    that aren't gitignored. Files that are gitignored (db.sqlite3, .env,
    __pycache__) are excluded — they shouldn't influence the image.
    """
    repo_root = Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
    )
    files = subprocess.check_output(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "backend",
        ],
        cwd=repo_root,
        text=True,
    ).splitlines()

    h = hashlib.sha256()
    for rel in sorted(files):
        full = repo_root / rel
        if not full.is_file():
            continue
        h.update(rel.encode())
        h.update(b"\x00")
        h.update(full.read_bytes())
        h.update(b"\x00")
    return h.hexdigest()


class ContainerImage(pulumi.ComponentResource):
    def __init__(self):
        super().__init__("meal-planner:image:ContainerImage", "meal-planner-image", {})

        self.repository = aws.ecr.Repository(
            "meal-planner-container-registry",
            name=config.app_name,
            # MUTABLE allows reusing the `latest` tag across deploys, which is fine
            # for dev. Switch to IMMUTABLE in prod to ensure every deploy is traceable
            # to a unique image digest.
            image_tag_mutability="MUTABLE",
            image_scanning_configuration=aws.ecr.RepositoryImageScanningConfigurationArgs(
                scan_on_push=True,
            ),
            # Import the existing ECR repository rather than creating a new one —
            # repository names are unique per account/region so a parallel one can't exist.
            # Remove this import_ option once the resource is successfully under management.
            opts=pulumi.ResourceOptions(parent=self, import_=config.app_name),
        )

        # ECR requires a short-lived auth token to push images — it's not a static
        # username/password. get_authorization_token_output fetches a token that's
        # valid for 12 hours and provides pre-decoded username and password fields.
        auth_token = aws.ecr.get_authorization_token_output(
            registry_id=self.repository.registry_id,
        )

        # Builds the Lambda container image from backend/Dockerfile-lambda and pushes
        # it to ECR as part of `pulumi up`. Replaces the manual `make lambda-build`
        # and `make lambda-push` steps.
        #
        # platform must match the Lambda function's architecture (x86_64 = linux/amd64).
        # This matters when building on Apple Silicon — without it, Docker would build
        # an arm64 image that Lambda can't run.
        #
        # repo_digest (not image_name) is passed to Lambda so it always references the
        # exact image built in this deploy. image_name resolves to `repo:latest` which
        # doesn't change between pushes, so Lambda would never detect an update.
        self.image = docker.Image(
            "meal-planner-container-image",
            build=docker.DockerBuildArgs(
                context="../backend",
                dockerfile="../backend/Dockerfile-lambda",
                platform="linux/amd64",
                # See _compute_backend_source_hash — feeds a content hash
                # into a diffable input so backend/ changes trigger a rebuild.
                args={"SOURCE_HASH": _compute_backend_source_hash()},
            ),
            image_name=self.repository.repository_url.apply(
                lambda url: f"{url}:latest"
            ),
            registry=docker.RegistryArgs(
                server=self.repository.repository_url,
                username=auth_token.user_name,
                password=pulumi.Output.secret(auth_token.password),
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # repo_digest is the immutable `repo@sha256:<hash>` reference. Using this
        # as the Lambda image URI ensures Pulumi detects a new image on every push
        # and triggers a Lambda update.
        self.uri = self.image.repo_digest

        self.register_outputs({
            "repository_url": self.repository.repository_url,
            "uri": self.uri,
        })
