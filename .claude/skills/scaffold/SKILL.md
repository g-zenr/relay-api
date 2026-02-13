---
name: scaffold
description: Generate boilerplate for a new module, package, or component following project architecture
disable-model-invocation: true
---

Scaffold a new module or component: $ARGUMENTS

## Step 1 — Determine Type
What are we scaffolding?
- **New API router** → `app/api/v1/<name>.py` + tests
- **New service** → `app/services/<name>.py` + tests
- **New device implementation** → addition to `app/core/device.py` + tests
- **New middleware** → `app/middleware.py` (extend) or `app/middleware/<name>.py` + tests
- **New model package** → `app/models/<name>.py` + tests

## Step 2 — Generate Files
Every new Python file MUST include:
```python
from __future__ import annotations
```

### For a new API router:
```python
# app/api/v1/<name>.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_relay_service
from app.core.exceptions import DeviceConnectionError, InvalidChannelError
from app.models.schemas import ErrorResponse
from app.services.relay_service import RelayService

router = APIRouter(tags=["<Name>"])
```

Then in `app/main.py`:
```python
from app.api.v1.<name> import router as <name>_router
app.include_router(<name>_router, prefix="/api/v1")
```

### For a new service:
```python
# app/services/<name>.py
from __future__ import annotations

import logging
import threading

logger = logging.getLogger(__name__)
```

### For new tests:
```python
# tests/test_<layer>_<name>.py
from __future__ import annotations

from typing import Generator

import pytest
from fastapi.testclient import TestClient
```

## Step 3 — Register
- Add imports to relevant `__init__.py` files
- Wire into `app/main.py` if it's a router or middleware
- Add DI functions to `app/api/dependencies.py` if needed

## Step 4 — Verify Structure
```bash
python -m mypy app/
python -m pytest tests/ -v --tb=short
```

## Rules
- Follow existing naming conventions (snake_case files, PascalCase classes)
- Mirror `app/` structure in `tests/`
- Every new file gets `from __future__ import annotations`
- Every new module gets a corresponding test file
- Never create empty files — include at minimum the imports and a class/function stub
