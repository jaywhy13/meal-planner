import pulumi


app_name = "prod-shell"

_config = pulumi.Config()
_aws_config = pulumi.Config("aws")

vpc_id = _config.require("vpc_id")
subnet_id = _config.require("subnet_id")
aws_account_id = _aws_config.require("account_id")
