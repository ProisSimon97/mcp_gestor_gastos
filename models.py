
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal

DATE_FMT = "%Y-%m-%d"  # yyyy-MM-dd
YM_FMT = "%Y-%m"       # yyyy-MM

def validate_yyyy_mm_dd(value: str) -> str:
    try:
        datetime.strptime(value, DATE_FMT)
    except ValueError as e:
        raise ValueError(f"Date '{value}' must be in yyyy-MM-dd format") from e
    return value

def validate_yyyy_mm(value: str) -> str:
    try:
        datetime.strptime(value, YM_FMT)
    except ValueError as e:
        raise ValueError(f"YearMonth '{value}' must be in yyyy-MM format") from e
    return value

class CategoriaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)

class MovimientoCreate(BaseModel):
    monto: Decimal = Field(..., gt=0)
    categoria_id: int = Field(..., ge=1)
    tipo: Literal["INGRESO", "EGRESO"]
    fecha: str  # yyyy-MM-dd
    nota: Optional[str] = Field(default=None, max_length=500)

    @field_validator("fecha")
    @classmethod
    def _check_fecha(cls, v: str) -> str:
        return validate_yyyy_mm_dd(v)

class MovimientoListParams(BaseModel):
    desde: Optional[str] = None  # yyyy-MM-dd
    hasta: Optional[str] = None  # yyyy-MM-dd
    tipo: Optional[Literal["INGRESO", "EGRESO"]] = None
    categoria_id: Optional[int] = Field(default=None, ge=1)

    @field_validator("desde")
    @classmethod
    def _check_desde(cls, v: Optional[str]) -> Optional[str]:
        return validate_yyyy_mm_dd(v) if v else v

    @field_validator("hasta")
    @classmethod
    def _check_hasta(cls, v: Optional[str]) -> Optional[str]:
        return validate_yyyy_mm_dd(v) if v else v

class GastoFijoCreate(BaseModel):
    monto: Decimal = Field(..., gt=0)
    categoria_id: int = Field(..., ge=1)
    dia_cobro: int = Field(..., ge=1, le=31)
    activo: bool = True
    nota: Optional[str] = Field(default=None, max_length=500)

class GastoFijoListParams(BaseModel):
    activo: Optional[bool] = None
    categoria_id: Optional[int] = Field(default=None, ge=1)

class TendenciasMesParams(BaseModel):
    desdeMes: str  # yyyy-MM
    hastaMes: str  # yyyy-MM
    categoria: Optional[str] = None

    @field_validator("desdeMes")
    @classmethod
    def _check_desde_mes(cls, v: str) -> str:
        return validate_yyyy_mm(v)

    @field_validator("hastaMes")
    @classmethod
    def _check_hasta_mes(cls, v: str) -> str:
        return validate_yyyy_mm(v)
