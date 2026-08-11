import pulumi

app_name = "meal-planner-prod-shell"

_config = pulumi.Config()
_aws_config = pulumi.Config("aws")

vpc_id = _config.require("vpc_id")
subnet_id = _config.require("subnet_id")
aws_account_id = _config.require("aws_account_id")
aws_region = _aws_config.require("region")
instance_type = _config.get("instance_type") or "t3.micro"
repository_url = _config.get("repository_url") or "git@github.com:jaywhy13/meal-planner.git"

# Private key for a GitHub deploy key with read access to the repository. When it is
# absent the instance still boots — an operator clones the repository by hand instead.
github_deploy_key = _config.get_secret("github_deploy_key")
