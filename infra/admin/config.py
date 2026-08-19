import pulumi

app_name = "meal-planner"

_config = pulumi.Config()
_aws_config = pulumi.Config("aws")

app_stack_name = _config.require("app_stack_name")
aws_region = _aws_config.require("region")

# StackReference reads the app stack's recorded state-file outputs — it does not
# execute the app stack's program. `pulumi up` here never touches the Lambda, EFS,
# or the container image; it only creates resources declared in this project.
#
# These outputs only exist once the app stack has been deployed since they were
# added to infra/__main__.py. If any of the values below resolve to None, that's
# the symptom — check that the app stack has been deployed since the exports
# landed, not that this project is misconfigured.
_app_stack = pulumi.StackReference(app_stack_name)

vpc_id = _app_stack.get_output("vpc_id")
subnet_id = _app_stack.get_output("subnet_id")
storage_security_group_id = _app_stack.get_output("storage_security_group_id")
file_system_id = _app_stack.get_output("file_system_id")
access_point_id = _app_stack.get_output("access_point_id")
