# Pulumi Infrastructure Plan

## Philosophy

Each file represents a **capability** the app needs, not an AWS service. The infrastructure details live inside — callers work with clean interfaces. `__main__.py` reads like a deployment manifest.

---

## File Structure

```
infra/
├── __main__.py           # Wires everything together; reads like a manifest
├── Pulumi.yaml           # Project: meal-planner
├── Pulumi.dev.yaml       # Stack config: dev
├── Pulumi.prod.yaml      # Stack config: prod (future)
├── requirements.txt      # pulumi, pulumi-aws, pulumi-docker
├── config.py             # Stack config values + shared constants
├── networking.py         # VPC/subnet references + security groups
├── storage.py            # EFS + access point + mount target
├── container_image.py    # ECR repo + Docker build & push
├── web_server.py         # Lambda + Function URL
└── monitoring.py         # CloudWatch log group
```

IAM lives *inside* `web_server.py` — it's tightly coupled to the Lambda and has no independent meaning.

---

## `__main__.py` — reads like a deployment manifest

```python
from networking import AppNetworking
from storage import AppStorage
from container_image import ContainerImage
from monitoring import AppMonitoring
from web_server import WebServer

networking = AppNetworking()            # security groups, VPC refs
storage = AppStorage(networking)        # EFS + mount in the right subnet/security group
image = ContainerImage()                # ECR repo + build + push
monitoring = AppMonitoring()            # CloudWatch log group
web_server = WebServer(                 # Lambda + public URL
    image=image,
    storage=storage,
    networking=networking,
    monitoring=monitoring,
)

pulumi.export("url", web_server.url)
```

---

## `config.py`

Holds values that vary by stack or are shared across modules:

```python
# Read from Pulumi.<stack>.yaml
vpc_id          # existing VPC to deploy into
subnet_id       # existing subnet (must match EFS mount target AZ)
aws_account_id
aws_region
app_name = "meal-planner"   # prefix for all AWS resource names
```

---

## `networking.py` — `AppNetworking`

**Purpose:** Establishes the network boundary — what traffic is allowed between the web server and storage.

**Contains:**
- `vpc` — `aws.ec2.get_vpc()` lookup (reference, not created)
- `subnet` — `aws.ec2.get_subnet()` lookup
- `web_server_security_group` — security group on Lambda; allows outbound NFS (2049) to storage security group
- `storage_security_group` — security group on EFS mount target; allows inbound NFS (2049) from web server security group only

**Key design:** The two security groups reference each other, creating a locked-down NFS channel.

**Exposes:** `vpc`, `subnet`, `web_server_security_group`, `storage_security_group`

---

## `storage.py` — `AppStorage`

**Purpose:** Persistent storage for the app's SQLite database.

**Contains:**
- `file_system` — EFS, elastic throughput, KMS-encrypted, backup enabled; named `meal-planner-storage`
- `mount_target` — binds EFS into the Lambda's subnet with `storage_security_group`
- `access_point` — scoped to `/meal-planner` root dir, uid/gid 1001; named `meal-planner-storage-access-point`

**Exposes:** `access_point_arn`, `mount_path = "/mnt/data"`

---

## `container_image.py` — `ContainerImage`

**Purpose:** Packages the app as a container and makes it available to deploy.

**Contains:**
- `repository` — ECR repo named `meal-planner`; image tag mutability IMMUTABLE in prod, MUTABLE in dev
- `image` — `pulumi_docker.Image`; builds via `backend/Dockerfile-lambda`, context `./backend`, pushes to ECR with proper auth token

**Note:** Replaces the `make lambda-build` + `make lambda-push` manual steps. The `pulumi_docker.Image` resource handles ECR auth, build, and push as part of `pulumi up`.

**Exposes:** `uri` (the full image URI for Lambda)

---

## `monitoring.py` — `AppMonitoring`

**Purpose:** Observability for the web server.

**Contains:**
- `log_group` — CloudWatch log group `/meal-planner/web-server`, 30-day retention

**Exposes:** `log_group_name`

**Note:** Pulumi owning this prevents the log group from being auto-created (and therefore unmanaged) by Lambda on first invocation.

---

## `web_server.py` — `WebServer`

**Purpose:** The running web server — assembles all other capabilities into a deployable unit.

**Contains:**
- `role` — IAM role with Lambda trust policy; named `meal-planner-web-server-role`
- Three policy attachments:
  - `AWSLambdaVPCAccessExecutionRole` (managed)
  - `AmazonElasticFileSystemClientReadWriteAccess` (managed)
  - Custom inline policy for CloudWatch Logs (scoped to the log group from `monitoring`)
- `function` — Lambda; container image from `ContainerImage`, VPC + security group from `AppNetworking`, EFS mount from `AppStorage`, env var `DATABASE_URL`, log group from `AppMonitoring`; named `meal-planner`
- `url` — Lambda Function URL; `AuthType: NONE`, buffered mode; public invoke permission

**Exposes:** `url` (the public Function URL)

---

## Config values per stack (`Pulumi.dev.yaml`)

```yaml
config:
  meal-planner:vpc_id: vpc-52d59c37
  meal-planner:subnet_id: subnet-74f4565f
  meal-planner:aws_account_id: "879100528238"
  meal-planner:aws_region: us-east-1
```

---

## What this changes vs. current state

| Current | Pulumi-managed |
|---|---|
| Lambda named `meal-planner-ecr-test` | Renamed to `meal-planner` |
| Lambda security group allows all TCP in (0.0.0.0/0) | Tightened: only NFS egress to storage security group |
| Log group auto-created, unmanaged | Managed, with 30-day retention |
| Image built/pushed via `make` manually | `pulumi up` builds and pushes |
| Mount path `/mnt/app` | Renamed to `/mnt/data` |
| 3 unrelated security groups on EFS mount target | Only `storage_security_group` (Pulumi-owned) |

---

## `infra/admin/` — a separate Pulumi project

This plan covers the always-on app stack only. `infra/admin/` is its own Pulumi
project with its own state file — the on-demand maintenance instance used for
production `manage.py shell` access. It reads this stack's outputs (`vpc_id`,
`subnet_id`, `storage_security_group_id`, `file_system_id`, `access_point_id`)
via `StackReference` and structurally cannot modify anything this stack owns.
Neither `deploy.yml` nor `preview.yml` touch it — it's created and destroyed by
hand via `make start-prod-instance` / `make destroy-prod-instance`.
