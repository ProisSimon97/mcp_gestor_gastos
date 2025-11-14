import asyncio
import random
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# Datos aleatorios para el gasto fijo
montos = [250.00, 350.50, 450.00, 600.00, 750.25, 900.00, 1200.00]
categorias_ids = [1, 2, 3, 4, 5]  # Ajusta según las categorías que tengas
dias_cobro = list(range(1, 32))  # Días del mes (1-31)
notas = [
    "Alquiler mensual",
    "Servicio de internet",
    "Suscripción a streaming",
    "Gimnasio",
    "Seguro del auto",
    "Servicio de luz",
    "Agua y gas",
    "Netflix y Spotify",
    "Almacenamiento en la nube",
    "Plan de celular"
]

async def crear_gasto_fijo_random():
    """Crea un gasto fijo con datos aleatorios"""
    transport = StreamableHttpTransport(url="http://127.0.0.1:8003/mcp")
    client = Client(transport)
    
    # Generar datos aleatorios
    monto = random.choice(montos)
    categoria_id = random.choice(categorias_ids)
    dia_cobro = random.choice(dias_cobro)
    nota = random.choice(notas)
    activo = True
    
    print(f"Creando gasto fijo con los siguientes datos:")
    print(f"  - Monto: ${monto}")
    print(f"  - Categoría ID: {categoria_id}")
    print(f"  - Día de cobro: {dia_cobro}")
    print(f"  - Nota: {nota}")
    print(f"  - Activo: {activo}")
    print()
    
    try:
        async with client:
            resultado = await client.call_tool("gasto_fijo_crear", {
                "monto": monto,
                "categoria_id": categoria_id,
                "dia_cobro": dia_cobro,
                "activo": activo,
                "nota": nota
            })
            print("✅ Gasto fijo creado exitosamente:")
            print(resultado)
            return resultado
    except Exception as e:
        print(f"❌ Error al crear el gasto fijo: {e}")
        print("\nNota: Asegúrate de que:")
        print("  1. El servidor MCP esté corriendo (python server.py)")
        print("  2. El backend Spring Boot esté corriendo en http://localhost:8080")
        print("  3. El backend tenga una sesión válida o autenticación configurada")
        raise

if __name__ == "__main__":
    asyncio.run(crear_gasto_fijo_random())

