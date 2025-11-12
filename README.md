
# MCP – FastMCP wrapper for your Spring Boot Finance API

This repo gives you **a working MCP server** (Python) using `fastmcp` that wraps your Spring Boot endpoints,
plus a **tiny demo client** that invokes the MCP *tools* programmatically.

> ✅ You said you’ll send the exact endpoints later.  
> For now, the server reads them from `config.endpoints.yaml`.  
> Update that file (or environment variables) and run.

---

## Structure

```
mcp-fastmcp-finance/
├─ server.py               # MCP server (FastMCP) exposing tools
├─ client_demo.py          # Minimal client that invokes MCP tools
├─ models.py               # Pydantic models & helpers
├─ config.endpoints.yaml   # Edit with your Spring Boot endpoints
├─ requirements.txt
└─ README.md
```

## Quick start

```bash
# 1) (optional) create venv
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) install deps
pip install -r requirements.txt

# 3) edit config.endpoints.yaml with your real paths or set BASE_URL, etc.
#    Date format is yyyy-MM-dd, as requested.

# 4) run the MCP server (stdio)
python server.py
# The server runs and waits for an MCP client (e.g., Claude Desktop, Llama.cpp MCP host, etc.)

# 5) or test locally with the demo client (no external MCP host needed)
python client_demo.py
```

> Note: `client_demo.py` uses the same `fastmcp` runtime in-process to call the tools—handy for quick tests.
> When you plug this server into a real MCP host, you won't use `client_demo.py`; the host will call the tools via MCP.

---

## Configure endpoints

Edit **`config.endpoints.yaml`** to match your Spring Boot routes.  
Default assumptions (you can change them):

```yaml
base_url: "http://localhost:8080/api/v1"
endpoints:
  categorias:
    list: "/categorias"
    create: "/categorias"
    get: "/categorias/{id}"
    delete: "/categorias/{id}"
  movimientos:
    list: "/movimientos"
    create: "/movimientos"
    get: "/movimientos/{id}"
    delete: "/movimientos/{id}"
  gastos_fijos:
    list: "/gastos-fijos"
    create: "/gastos-fijos"
    get: "/gastos-fijos/{id}"
    delete: "/gastos-fijos/{id}"
```

You can also override with env vars:

- `BASE_URL` – e.g., `http://localhost:8080/api/v1`

---

## Tools (initial set)

All dates use **`yyyy-MM-dd`** (no conversion needed).

### `categorias.create(nombre: str) -> dict`
Crea una categoría única por `nombre`.

**Context:** Use when you need to register a new spending/earning category to classify movements and fixed expenses.

### `categorias.list(q: Optional[str]) -> list[dict]`
Lista categorías; `q` filtra por texto en nombre.

**Context:** Fetch available categories to validate inputs, populate dropdowns, or ensure uniqueness before creating new ones.

### `categorias.get(id: int) -> dict`
Obtiene una categoría por id.

**Context:** Retrieve category details, e.g., to show metadata before assigning it to a movement or a fixed expense.

### `categorias.delete(id: int) -> dict`
Elimina (o solicita borrado) por id.

**Context:** Use to remove obsolete categories. The underlying API may hard- or soft-delete; the tool simply forwards.

---

### `movimientos.create(monto, categoria_id, tipo, fecha, nota?) -> dict`
Crea un movimiento (INGRESO/EGRESO).

**Context:** Record a financial movement on a specific date for a category. Maintains the ledger history for projections and trends.

### `movimientos.list(desde?, hasta?, tipo?, categoria_id?) -> list[dict]`
Lista movimientos con filtros (fechas en `yyyy-MM-dd`).

**Context:** Query your ledger by date range, type, and category—for summaries, audits, or feeding analytics.

### `movimientos.delete(id: int) -> dict`
Elimina un movimiento por id.

**Context:** Remove erroneous entries; consider business rules for reconciliation on your backend.

---

### `gastos_fijos.create(monto, categoria_id, dia_cobro, activo=True, nota?) -> dict`
Crea un gasto fijo mensual.

**Context:** Register recurring fixed expenses (e.g., rent, subscriptions) for better monthly planning.

### `gastos_fijos.list(activo?, categoria_id?) -> list[dict]`
Lista gastos fijos con filtros.

**Context:** Inspect active recurring costs to adjust budget or detect inactive ones.

### `gastos_fijos.delete(id: int) -> dict`
Elimina un gasto fijo.

**Context:** Retire a fixed expense that no longer applies.

---

## Extender (Estadísticas / Tendencias)

Cuando me pases tus endpoints de *estadísticas* (`/estadisticas/proyeccion/mes-siguiente`, `/estadisticas/tendencias`, etc.), agrego herramientas MCP adicionales
con descripciones enfocadas (contextos) y validación del input. El servidor ya tiene utilidades para extender fácilmente.

---

## Security

- This repo forwards requests to your API; secure your Spring Boot with proper auth (e.g., Keycloak) and then add a bearer token to the server (see `AUTH_TOKEN` in `server.py`).

---
