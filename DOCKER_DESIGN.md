# Docker Environment Design Document

## 1. Objective
To transform the current basic Docker setup into a robust, secure, and optimized environment for the `my_source` application. This includes improving build efficiency, enhancing security (secret management), and ensuring seamless runtime operation.

## 2. Identified Gaps
1.  **Secret Management**: `config.json` is at risk of being baked into the image.
2.  **Image Size**: Current build includes `pipenv` and build-time dependencies in the final image.
3.  **Permission Conflicts**: Hardcoded GID `134` and UID `1000` can cause "Permission Denied" errors when mounting host volumes.
4.  **Operational Friction**: `docker_start.sh` assumes host directories exist and doesn't handle configuration injection dynamically.
5.  **Build Hygiene**: `.dockerignore` is incomplete, allowing `.git` and local `__pycache__` into the image.

## 3. Proposed Architecture

### 3.1 Multi-Stage `app.dockerfile`
- **Stage 1 (Builder)**: Install `pipenv`, build-essential, and resolve dependencies into a system-wide environment or a wheelhouse.
- **Stage 2 (Runtime)**: Use `python:3.13-slim`. Copy only the installed packages and application source. No `pipenv` or build tools in the final image.

### 3.2 Volume & Secret Strategy
- **Secrets**: `config.json` will be excluded via `.dockerignore` and mounted at runtime via `-v $(pwd)/config.json:/app/config.json:ro`.
- **Persistence**: `log/`, `history/`, and `session/` will be mounted as volumes to ensure data persists across container restarts.
- **Permissions**: Standardize on UID/GID `1000:1000` for the internal `appuser`, and ensure `docker_start.sh` creates host directories with appropriate permissions before starting the container.

### 3.3 Optimized Scripts
- **`docker_build.sh`**: Use consistent tagging (e.g., `my-source:latest`) and allow caching unless explicitly disabled.
- **`docker_start.sh`**: 
    - Verify `config.json` exists.
    - Create `log`, `history`, and `session` directories if missing.
    - Inject the environment type (e.g., `prod`, `dev`) as a command-line argument or environment variable.

## 4. Action Plan

### Step 1: Security & Hygiene
Update `.dockerignore` to exclude:
- `.git/`
- `config.json`
- `__pycache__/`
- Local logs and history.

### Step 2: Refactor `app.dockerfile`
- Implement 2-stage build.
- Standardize non-root user creation.
- Set `PYTHONUNBUFFERED=1` and `PYTHONDONTWRITEBYTECODE=1`.

### Step 3: Script Modernization
- **Build**: Simplify and add tag management.
- **Run**: Add "pre-flight" checks (config check, directory creation) and mount all necessary volumes.

### Step 4: Validation
- Build the image.
- Run in `dev` mode with a test config.
- Verify logs and history are written correctly to the host machine.
