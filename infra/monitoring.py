import pulumi
import pulumi_aws as aws

import config


class AppMonitoring(pulumi.ComponentResource):
    def __init__(self):
        super().__init__("meal-planner:monitoring:AppMonitoring", "meal-planner-monitoring", {})

        # Explicitly owning the log group (rather than letting Lambda auto-create it)
        # means we control retention. Lambda-created log groups default to never expiring,
        # which accumulates cost over time.
        self.log_group = aws.cloudwatch.LogGroup(
            "meal-planner-web-server-log-group",
            name=f"/meal-planner/web-server",
            retention_in_days=30,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({
            "log_group_name": self.log_group.name,
            "log_group_arn": self.log_group.arn,
        })
