"""
org_batch_etl.py

Proceso batch para el DESAFÍO #3 de la prueba técnica MVM.

Lee los archivos CSV y Parquet generados en 01_data_cloud/data/raw
y los carga a un contenedor de Azure Blob Storage (Data Lake),
organizados como capa raw versionada.
"""

import os
from pathlib import Path
from datetime import datetime

from azure.storage.blob import BlobServiceClient


# Rutas locales del proyecto
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent  # 01_data_cloud
RAW_PATH = PROJECT_ROOT / "data" / "raw"


def load_storage_config():
    """
    Carga la configuración de Azure Storage desde variables de entorno.

    Variables esperadas:
    - AZURE_STORAGE_CONNECTION_STRING
    - AZURE_STORAGE_CONTAINER_RAW (opcional, default: 'org-raw')
    - AZURE_STORAGE_BASE_PREFIX (opcional, default: 'org_data/v1')
    """
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container = os.getenv("AZURE_STORAGE_CONTAINER_RAW", "org-raw")
    base_prefix = os.getenv("AZURE_STORAGE_BASE_PREFIX", "org_data/v1")

    if not conn_str:
        raise ValueError(
            "No se encontró AZURE_STORAGE_CONNECTION_STRING en el entorno. "
            "Configurar la variable antes de ejecutar el proceso batch."
        )

    return conn_str, container, base_prefix


def get_blob_service_client(conn_str: str) -> BlobServiceClient:
    """Inicializa un BlobServiceClient a partir del connection string."""
    return BlobServiceClient.from_connection_string(conn_str)


def iter_raw_files():
    """
    Itera sobre los archivos presentes en data/raw.

    Se consideran únicamente archivos con extensión .csv o .parquet.
    """
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"El directorio de datos raw no existe: {RAW_PATH}"
        )

    for path in RAW_PATH.glob("*"):
        if path.is_file() and path.suffix.lower() in {".csv", ".parquet"}:
            yield path


def build_blob_path(base_prefix: str, file_path: Path) -> str:
    """
    Construye la ruta destino en el contenedor a partir de:

    - base_prefix: por ejemplo 'org_data/v1'
    - subcarpeta por entidad (departments, job_positions, employees)
    - nombre de archivo original
    """
    entity_name = file_path.stem.split(".")[0]
    blob_path = f"{base_prefix}/{entity_name}/{file_path.name}"
    return blob_path


def upload_file(
    blob_service: BlobServiceClient,
    container_name: str,
    local_path: Path,
    dest_blob_path: str,
    overwrite: bool = True,
):
    """
    Sube un archivo local a Azure Blob Storage.

    Crea el contenedor si no existe y utiliza overwrite=True para
    permitir ejecuciones repetidas sin duplicar blobs.
    """
    container_client = blob_service.get_container_client(container_name)

    try:
        container_client.create_container()
        print(f"Contenedor '{container_name}' creado.")
    except Exception:
        # Si el contenedor ya existe, se ignora la excepción correspondiente.
        pass

    blob_client = container_client.get_blob_client(dest_blob_path)

    with open(local_path, "rb") as f:
        blob_client.upload_blob(f, overwrite=overwrite)

    print(f"Subido: {local_path.name} -> {dest_blob_path}")


def run_batch_upload():
    """
    Ejecuta el proceso batch completo:

    - Carga la configuración de Storage.
    - Inicializa el cliente de blobs.
    - Recorre los archivos en data/raw.
    - Sube cada archivo al contenedor, siguiendo la estructura destino.
    """
    print("Iniciando proceso batch de carga a Data Lake...")

    conn_str, container_name, base_prefix = load_storage_config()
    blob_service = get_blob_service_client(conn_str)

    run_timestamp = datetime.utcnow().isoformat()
    print(f"Run timestamp (UTC): {run_timestamp}")
    print(f"Directorio local de origen: {RAW_PATH}")
    print(f"Contenedor destino: {container_name}")
    print(f"Prefijo base en el contenedor: {base_prefix}")
    print("-" * 60)

    files = list(iter_raw_files())
    if not files:
        print("No se encontraron archivos en data/raw para cargar.")
        return

    for file_path in files:
        blob_path = build_blob_path(base_prefix, file_path)
        upload_file(
            blob_service=blob_service,
            container_name=container_name,
            local_path=file_path,
            dest_blob_path=blob_path,
            overwrite=True,
        )

    print("-" * 60)
    print("Proceso batch completado.")


if __name__ == "__main__":
    run_batch_upload()
