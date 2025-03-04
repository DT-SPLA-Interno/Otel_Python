import json
import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
import mysql.connector
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import set_tracer_provider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import uvicorn

app = FastAPI(title="API Inventario", version="1.0.0")

# ------------------------------------------------------------------------------
# 1. Enriquecimiento con Dynatrace
# ------------------------------------------------------------------------------
enrich_attrs = {}
dt_metadata_files = [
    "dt_metadata.json",
    "/var/lib/dynatrace/enrichment/dt_metadata.json"
]

for file_path in dt_metadata_files:
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                enrich_attrs.update(data)
        except Exception as e:
            print(f"Error leyendo archivo de metadatos Dynatrace: {e}")

resource = Resource.create(enrich_attrs)

# ------------------------------------------------------------------------------
# 2. Configurar OpenTelemetry
# ------------------------------------------------------------------------------
tracer_provider = TracerProvider(resource=resource)
set_tracer_provider(tracer_provider)

otlp_exporter = OTLPSpanExporter(
    # Reemplaza "dynatrace-collector.dynatrace:4318" con la ruta/host real de tu Collector
    endpoint="http://dynatrace-collector.dynatrace:4318/v1/traces"
)

span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

FastAPIInstrumentor.instrument_app(app)

# ------------------------------------------------------------------------------
# 3. Funciones de conexión MySQL
# ------------------------------------------------------------------------------
def get_db_connection():
    """
    Retorna la conexión a la base de datos MySQL del inventario.
    Ajusta parámetros si es necesario (host, user, password, database).
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "inventario-db.pocotelpython"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "password"),
        database=os.getenv("DB_DATABASE", "inventario")
    )

# ------------------------------------------------------------------------------
# 4. Endpoints
# ------------------------------------------------------------------------------
@app.post("/items/add")
def add_item(data: Dict[str, Any]):
    """
    Agrega un ítem al inventario: { "name": "...", "quantity": ... }
    """
    name = data.get("name")
    quantity = data.get("quantity")

    if not name or quantity is None:
        raise HTTPException(status_code=400, detail="Datos inválidos para agregar item")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (name, quantity) VALUES (%s, %s)", (name, quantity))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": f"Item '{name}' agregado con cantidad {quantity}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items/all")
def get_all_items():
    """
    Retorna todos los ítems del inventario.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, quantity FROM items")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------------------
# 5. Ejecución con Uvicorn (para desarrollo local)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
