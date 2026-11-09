# Record-Social
Social Platform for album voting and listening groups.

## Commit conventions

This project uses [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): description`.

The scope names the **domain/feature** a change touches, not the layer (service, repository, etc.). Keep each commit to one logical change.

| Scope | Use for |
|-------|---------|
| `user` | Users |
| `group` | Groups and group membership |
| `album` | Albums and candidate pools |
| `vote` | Album voting |
| `auth` | Authentication and authorization |
| `infra` | Database, config, Docker, app setup |
| `deps` | Dependency changes |
| `ci` | CI/CD pipelines |

Add a new domain scope here when a new feature area is introduced.

Examples:

```
feat(group): add group service with create and get
test(group): add group service unit tests
fix(user): reject duplicate usernames on update
```
