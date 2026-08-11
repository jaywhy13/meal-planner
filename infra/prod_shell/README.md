# Production shell

A temporary EC2 instance for running Django management commands against a SQLite
database on Elastic File System. It is a separate Pulumi project from `infra/` so the
web server stack is never touched when the shell is created or destroyed.

## What gets created

- Elastic File System (encrypted, daily backups) with an access point scoped to
  `/meal-planner`, and a mount target in the configured subnet
- A `t3.micro` Ubuntu 22.04 instance with an instance profile granting
  `AmazonSSMManagedInstanceCore`, read access to the deploy key parameter, and client
  access to the file system
- A Systems Manager `SecureString` parameter holding the GitHub deploy key

The instance has no inbound rules: Session Manager connects through an outbound
connection the Systems Manager agent opens.

## Usage

```bash
make create-prod-shell   # pulumi up
make ssh-prod-shell      # aws ssm start-session into the instance
make destroy-prod-shell  # pulumi destroy when finished
```

Inside the instance the repository is at `/app`, the file system is mounted at
`/mnt/data`, and `manage` runs Django management commands against it:

```bash
manage shell
manage migrate
```

## Repository checkout

The instance clones the repository over SSH with a GitHub deploy key. Set it before
creating the stack:

```bash
cd infra/prod_shell
pulumi config set --secret --stack prod-shell github_deploy_key < /path/to/deploy_key
```

Without the key the instance still boots with the file system mounted and the virtual
environment in place; `/app` is then cloned by hand.

## Configuration

| Key | Default |
|---|---|
| `vpc_id` | dev VPC |
| `subnet_id` | dev subnet |
| `aws_account_id` | account the stack deploys into |
| `instance_type` | `t3.micro` |
| `repository_url` | `git@github.com:jaywhy13/meal-planner.git` |
| `github_deploy_key` | unset (secret) |
