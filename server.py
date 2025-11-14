import os
import httpx
import yaml
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from typing import Optional, Any, Dict, List
from fastmcp import FastMCP
from models import (
    CategoriaCreate, MovimientoCreate, MovimientoListParams,
    GastoFijoCreate, GastoFijoListParams, TendenciasMesParams
)
from dotenv import load_dotenv

load_dotenv()

def load_config() -> dict:
    cfg_path = os.environ.get("ENDPOINTS_CONFIG", "config.endpoints.yaml")
    base_url_env = os.environ.get("BASE_URL")
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    if base_url_env:
        cfg["base_url"] = base_url_env
    if "base_url" not in cfg:
        raise RuntimeError("Missing base_url in config or BASE_URL env")
    return cfg

CFG = load_config()
BASE_URL: str = CFG["base_url"].rstrip("/")
EP = CFG.get("endpoints", {})

HEADERS: Dict[str, str] = {}

TIMEOUT = httpx.Timeout(25.0, connect=10.0)

async def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=BASE_URL, headers=HEADERS, timeout=TIMEOUT)

def _path(section: str, key: str, **path_vars) -> str:
    raw = EP.get(section, {}).get(key)
    if not raw:
        raise RuntimeError(f"Missing endpoint mapping for {section}.{key}")
    return raw.format(**path_vars)

mcp = FastMCP(
    name="FinanceMCP"
)

# ------------- BALANCE -------------

@mcp.tool()
async def balance(desde: str, hasta: str) -> Dict[str, Any]:
    """
    Obtiene el balance entre dos fechas (yyyy-MM-dd).
    Contexto: resumen agregado de ingresos/egresos y neto para reportes.
    """
    async with await _client() as client:
        resp = await client.get(_path("balance", "balance"), params={"desde": desde, "hasta": hasta})
    resp.raise_for_status()
    return resp.json()

@mcp.tool()
async def balance_mensual(ano: int, mes: int) -> Dict[str, Any]:
    """
    Balance para un mes específico (ano, mes).
    Contexto: visión mensual consolidada (e.g., 2025-11).
    """
    async with await _client() as client:
        resp = await client.get(_path("balance", "mensual", ano=ano, mes=mes))
    resp.raise_for_status()
    return resp.json()

@mcp.tool()
async def balance_acumulado(categoria: Optional[str] = None) -> Dict[str, Any]:
    """
    Balance acumulado global o por categoría (si se indica).
    Contexto: evolución total para dashboards o comparativas.
    """
    params = {"categoria": categoria} if categoria else None
    async with await _client() as client:
        resp = await client.get(_path("balance", "acumulado"), params=params)
    resp.raise_for_status()
    return resp.json()

# ------------- CATEGORIAS -------------

@mcp.tool()
async def categorias_crear(nombre: str) -> Dict[str, Any]:
    """
    Crea una categoría única por 'nombre'.
    Contexto: catalogar movimientos y gastos fijos.
    """
    payload = CategoriaCreate(nombre=nombre).model_dump()
    async with await _client() as client:
        resp = await client.post(_path("categorias", "crear"), json=payload)
    resp.raise_for_status()
    return resp.json()

@mcp.tool()
async def categorias_listar() -> List[Dict[str, Any]]:
    """
    Lista todas las categorías.
    Contexto: poblar selectores, validar duplicados.
    """
    async with await _client() as client:
        resp = await client.get(_path("categorias", "listar"))
    resp.raise_for_status()
    return resp.json()

# ------------- ESTADISTICAS -------------

@mcp.tool()
async def estadisticas_tendencias_mes(desdeMes: str, hastaMes: str, categoria: Optional[str] = None) -> Dict[str, Any]:
    """
    Tendencias por mes en el rango [desdeMes, hastaMes] (formato yyyy-MM).
    Contexto: detectar patrones de gasto/ingreso y variaciones; filtrar por categoría si aplica.
    """
    params = TendenciasMesParams(desdeMes=desdeMes, hastaMes=hastaMes, categoria=categoria).model_dump(exclude_none=True)
    async with await _client() as client:
        resp = await client.get(_path("estadisticas", "tendencias_mes"), params=params)
    resp.raise_for_status()
    return resp.json()

@mcp.tool()
async def estadisticas_proyeccion_mes_siguiente() -> Dict[str, Any]:
    """
    Proyección para el próximo mes (según tu backend).
    Contexto: estimar ingreso/gasto/ahorro esperado basado en histórico y gastos fijos.
    """
    async with await _client() as client:
        resp = await client.get(_path("estadisticas", "proyeccion_mes_siguiente"))
    resp.raise_for_status()
    return resp.json()

# ------------- GASTO FIJO -------------

@mcp.tool()
async def gasto_fijo_crear(monto: float, categoria_id: int, dia_cobro: int, activo: bool = True, nota: Optional[str] = None) -> Dict[str, Any]:
    """
    Crea un gasto fijo mensual (dia_cobro 1-31).
    Contexto: registrar costos recurrentes (alquiler, servicios, suscripciones).
    """
    # Obtener el nombre de la categoría
    async with await _client() as client:
        categorias_resp = await client.get(_path("categorias", "listar"))
        categorias_resp.raise_for_status()
        categorias = categorias_resp.json()
        categoria_obj = next((c for c in categorias if c["id"] == categoria_id), None)
        if not categoria_obj:
            raise ValueError(f"Categoría con ID {categoria_id} no encontrada")
        
        # Construir el payload en el formato que espera el backend
        payload = {
            "monto": monto,
            "categoria": {
                "id": categoria_id,
            },
            "diaCobro": dia_cobro,
            "activo": activo,
            "nota": nota
        }
        # Remover campos None
        payload = {k: v for k, v in payload.items() if v is not None}
        
        resp = await client.post(_path("gasto_fijo", "crear"), json=payload)
    resp.raise_for_status()
    return resp.json()

@mcp.tool()
async def gasto_fijo_listar() -> List[Dict[str, Any]]:
    """
    Lista todos los gastos fijos.
    Contexto: evaluar costos recurrentes y optimizaciones.
    """
    async with await _client() as client:
        resp = await client.get(_path("gasto_fijo", "listar"))
    resp.raise_for_status()
    return resp.json()

@mcp.tool()
async def gasto_fijo_crear_movimientos() -> Dict[str, Any]:
    """
    Genera movimientos a partir de los gastos fijos configurados (según tu backend).
    Contexto: poblar asientos mensuales automáticamente.
    """
    async with await _client() as client:
        resp = await client.post(_path("gasto_fijo", "crear_movimientos"))
    resp.raise_for_status()
    return resp.json()

# ------------- MOVIMIENTOS -------------

@mcp.tool()
async def movimientos_crear(
    monto: float,
    categoria: Dict[str, Any],
    tipo: str,
    fecha: str,
    nota: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Crea un movimiento (INGRESO/EGRESO) en fecha yyyy-MM-dd.
    Contexto: registrar entradas/salidas para análisis y reportes.
    """

    payload = {
        "monto": monto,
        "categoria": categoria,
        "tipo": tipo,
        "fecha": fecha,
        "nota": nota
    }

    async with await _client() as client:
        resp = await client.post(_path("movimientos", "crear"), json=payload)
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
async def movimientos_buscar_por_categoria(categoria: str) -> List[Dict[str, Any]]:
    """
    Lista movimientos filtrando por nombre de categoría (exacto según backend).
    Contexto: consultas por rubro específico.
    """
    async with await _client() as client:
        resp = await client.get(_path("movimientos", "buscar_por_categoria"), params={"categoria": categoria})
    resp.raise_for_status()
    return resp.json()

@mcp.tool()
async def movimientos_buscar_por_fechas(desde: str, hasta: str) -> List[Dict[str, Any]]:
    """
    Lista movimientos entre fechas (yyyy-MM-dd).
    Contexto: obtención de asientos para un rango determinado.
    """
    params = MovimientoListParams(desde=desde, hasta=hasta).model_dump(exclude_none=True)
    async with await _client() as client:
        resp = await client.get(_path("movimientos", "buscar_por_fechas"), params=params)
    resp.raise_for_status()
    return resp.json()

@mcp.tool()
async def movimientos_actualizar(movimiento: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actualiza un movimiento existente mediante POST /movimientos/actualizar.
    Contexto: corregir importe, fecha, nota o categoría.
    """
    async with await _client() as client:
        resp = await client.post(_path("movimientos", "actualizar"), json=movimiento)
        resp.raise_for_status()
        return resp.json()

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8003,
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"]
            )
        ]
    )