import pulumi
import pulumi_aws as aws
import pulumi_docker as docker

import config


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
