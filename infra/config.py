import pulumi

app_name = "meal-planner"

_config = pulumi.Config()
_aws_config = pulumi.Config("aws")

vpc_id = _config.require("vpc_id")
subnet_id = _config.require("subnet_id")
aws_account_id = _config.require("aws_account_id")
aws_region = _aws_config.require("region")
