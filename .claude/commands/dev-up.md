---
description: Start (or rebuild) the dev stack and confirm services are healthy
---

Bring up the Mook dev environment and verify it's running.

1. Run `./dev.sh start` (add `--build` context if deps changed). If the user named a
   single service to rebuild, use `./dev.sh rebuild <backend|react-ui|db>` instead.
2. Confirm the backend is up: `curl -s localhost:8000/docs -o /dev/null -w '%{http_code}'`.
3. Report the URLs: backend http://localhost:8000/docs · React UI http://localhost:5173 ·
   mock SD-WAN :8081 · mock ServiceNow :8082.
4. If the backend uses the `claude` provider, confirm the container can reach the CLI
   (creds mounted from `~/.claude`). If it fell back to mock, say so and why.

$ARGUMENTS
