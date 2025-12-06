"""
save_org_data.py
Persistencia de datos sintéticos en formatos CSV y Parquet
para el DESAFÍO #2 de la prueba técnica MVM.
"""

import os
import pandas as pd

from generate_org_data import (
    generate_departments,
    generate_job_positions,
    generate_employees,
)

BASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "raw"
)

def ensure_directories():
    """Crea los directorios necesarios si no existen."""
    os.makedirs(BASE_PATH, exist_ok=True)


def save_as_csv(df: pd.DataFrame, name: str):
    """Guarda un DataFrame como CSV con índice deshabilitado."""
    path = os.path.join(BASE_PATH, f"{name}.csv")
    df.to_csv(path, index=False)
    print(f"Archivo CSV guardado en: {path}")


def save_as_parquet(df: pd.DataFrame, name: str):
    """Guarda un DataFrame como Parquet usando compresión Snappy."""
    path = os.path.join(BASE_PATH, f"{name}.parquet")
    df.to_parquet(path, index=False, compression="snappy")
    print(f"Archivo Parquet guardado en: {path}")


def main():
    """Genera las tablas sintéticas y las persiste en CSV y Parquet."""

    ensure_directories()

    # Generación de estructuras sintéticas
    departments_df = generate_departments()
    job_positions_df = generate_job_positions(departments_df)
    employees_df = generate_employees(departments_df, job_positions_df)

    # Persistencia en ambos formatos
    save_as_csv(departments_df, "departments")
    save_as_parquet(departments_df, "departments")

    save_as_csv(job_positions_df, "job_positions")
    save_as_parquet(job_positions_df, "job_positions")

    save_as_csv(employees_df, "employees")
    save_as_parquet(employees_df, "employees")

    print("\nPersistencia completada.")


if __name__ == "__main__":
    main()
