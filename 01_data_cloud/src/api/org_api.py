"""
org_api.py

API REST del Desafío #5 de la prueba técnica MVM.

Expone endpoints de lectura sobre el modelo organizacional sintético
a partir de los datos almacenados en el Data Lake de Azure.
"""

import os
from io import BytesIO
from typing import List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# ---------------------------------------------------------------------
# Configuración y carga de datos
# ---------------------------------------------------------------------

# Carga de variables de entorno (archivo .env en la raíz de 01_data_cloud)
load_dotenv()

CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_RAW", "org-raw")
BASE_PREFIX = os.getenv("AZURE_STORAGE_BASE_PREFIX", "org_data/v1")

if not CONN_STR:
    raise RuntimeError(
        "AZURE_STORAGE_CONNECTION_STRING no está definido en el entorno."
    )

blob_service = BlobServiceClient.from_connection_string(CONN_STR)
container_client = blob_service.get_container_client(CONTAINER_NAME)


def _load_parquet_from_datalake(prefix: str, filename: str) -> pd.DataFrame:
    """
    Lee un archivo Parquet desde el Data Lake y lo devuelve como DataFrame.
    """
    blob_path = f"{BASE_PREFIX}/{prefix}/{filename}"
    blob_client = container_client.get_blob_client(blob_path)
    data_bytes = blob_client.download_blob().readall()
    return pd.read_parquet(BytesIO(data_bytes))


def _build_org_view() -> pd.DataFrame:
    """
    Construye la vista integrada de organización (employees + job_positions + departments)
    a partir de los archivos Parquet almacenados en el Data Lake.
    """
    departments_df = _load_parquet_from_datalake("departments", "departments.parquet")
    job_positions_df = _load_parquet_from_datalake("job_positions", "job_positions.parquet")
    employees_df = _load_parquet_from_datalake("employees", "employees.parquet")

    # Unión employees + job_positions
    employees_positions = employees_df.merge(
        job_positions_df,
        how="left",
        on="job_position_id",
        suffixes=("", "_job"),
    )

    # Unión con departments
    org_view = employees_positions.merge(
        departments_df,
        how="left",
        on="department_id",
        suffixes=("", "_dept"),
    )

    # Estandarización de tipos básicos
    if "employee_id" in org_view.columns:
        org_view["employee_id"] = org_view["employee_id"].astype(int)
    if "department_id" in org_view.columns:
        org_view["department_id"] = org_view["department_id"].astype(int)
    if "job_position_id" in org_view.columns:
        org_view["job_position_id"] = org_view["job_position_id"].astype(int)

    # Redondeo de columnas numéricas relevantes a dos decimales
    for col in ["salary", "tenure_years"]:
        if col in org_view.columns:
            org_view[col] = org_view[col].astype(float).round(2)

    return org_view


# Se construye la vista en memoria al iniciar el servicio
ORG_VIEW: pd.DataFrame = _build_org_view()


# ---------------------------------------------------------------------
# Modelos de respuesta
# ---------------------------------------------------------------------

class EmployeeItem(BaseModel):
    employee_id: int
    department_id: int
    department_name: Optional[str]
    job_position_id: int
    job_title: Optional[str]
    job_level: Optional[str]
    salary: float
    tenure_years: float
    age: Optional[int]


class DepartmentSummary(BaseModel):
    department_id: int
    department_name: Optional[str]
    headcount: int


class SalaryLevelSummary(BaseModel):
    job_level: Optional[str]
    avg_salary: float
    min_salary: float
    max_salary: float
    count: int


class SalarySummaryResponse(BaseModel):
    overall_avg_salary: float
    overall_min_salary: float
    overall_max_salary: float
    levels: List[SalaryLevelSummary]


# ---------------------------------------------------------------------
# Inicialización de la aplicación FastAPI
# ---------------------------------------------------------------------

app = FastAPI(
    title="Organizational Analytics API",
    description=(
        "API REST sobre el modelo organizacional sintético, "
        "construida como parte del Desafío #5 de la prueba técnica MVM."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------

@app.get("/health")
def health_check():
    """
    Endpoint de verificación de estado básico.
    """
    return {"status": "ok"}


@app.get("/employees", response_model=List[EmployeeItem])
def list_employees(
    department_id: Optional[int] = Query(None, description="Filtrar por ID de departamento"),
    job_level: Optional[str] = Query(None, description="Filtrar por nivel del cargo"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
):
    """
    Devuelve un listado paginado de empleados, con filtros opcionales
    por departamento y nivel de cargo.
    """
    df = ORG_VIEW.copy()

    if department_id is not None and "department_id" in df.columns:
        df = df[df["department_id"] == department_id]

    if job_level is not None and "job_level" in df.columns:
        df = df[df["job_level"] == job_level]

    df = df.sort_values("employee_id").iloc[offset : offset + limit]

    items: List[EmployeeItem] = []
    for _, row in df.iterrows():
        item = EmployeeItem(
            employee_id=int(row["employee_id"]),
            department_id=int(row["department_id"]),
            department_name=row.get("department_name"),
            job_position_id=int(row["job_position_id"]),
            job_title=row.get("job_title"),
            job_level=row.get("job_level"),
            salary=round(float(row["salary"]), 2) if "salary" in row else 0.0,
            tenure_years=round(float(row["tenure_years"]), 2) if "tenure_years" in row else 0.0,
            age=int(row["age"]) if "age" in row and not pd.isna(row["age"]) else None,
        )
        items.append(item)

    return items


@app.get("/employees/{employee_id}", response_model=EmployeeItem)
def get_employee(employee_id: int):
    """
    Devuelve la información detallada de un empleado específico.
    """
    df = ORG_VIEW
    if "employee_id" not in df.columns:
        raise HTTPException(status_code=500, detail="Columna employee_id no disponible en el modelo.")

    row = df[df["employee_id"] == employee_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Empleado no encontrado.")

    r = row.iloc[0]

    return EmployeeItem(
        employee_id=int(r["employee_id"]),
        department_id=int(r["department_id"]),
        department_name=r.get("department_name"),
        job_position_id=int(r["job_position_id"]),
        job_title=r.get("job_title"),
        job_level=r.get("job_level"),
        salary=round(float(r["salary"]), 2) if "salary" in r else 0.0,
        tenure_years=round(float(r["tenure_years"]), 2) if "tenure_years" in r else 0.0,
        age=int(r["age"]) if "age" in r and not pd.isna(r["age"]) else None,
    )


@app.get("/departments", response_model=List[DepartmentSummary])
def list_departments():
    """
    Devuelve un listado de departamentos junto con su headcount.
    """
    df = ORG_VIEW
    required_cols = {"department_id", "department_name"}
    if not required_cols.issubset(df.columns):
        raise HTTPException(status_code=500, detail="Columnas de departamentos no disponibles en el modelo.")

    headcount = (
        df.groupby(["department_id", "department_name"])
          .size()
          .reset_index(name="headcount")
          .sort_values("headcount", ascending=False)
    )

    items: List[DepartmentSummary] = []
    for _, row in headcount.iterrows():
        items.append(
            DepartmentSummary(
                department_id=int(row["department_id"]),
                department_name=row["department_name"],
                headcount=int(row["headcount"]),
            )
        )
    return items


@app.get("/analytics/salary-summary", response_model=SalarySummaryResponse)
def salary_summary():
    """
    Devuelve un resumen analítico de salarios por nivel de puesto,
    con valores agregados redondeados a dos decimales.
    """
    df = ORG_VIEW
    if "salary" not in df.columns:
        raise HTTPException(status_code=500, detail="Columna salary no disponible en el modelo.")

    # Agregados por nivel
    if "job_level" in df.columns:
        grouped = (
            df.groupby("job_level")
              .agg(
                  avg_salary=("salary", "mean"),
                  min_salary=("salary", "min"),
                  max_salary=("salary", "max"),
                  count=("salary", "size"),
              )
              .reset_index()
        )
    else:
        grouped = (
            df.assign(job_level="N/A")
              .groupby("job_level")
              .agg(
                  avg_salary=("salary", "mean"),
                  min_salary=("salary", "min"),
                  max_salary=("salary", "max"),
                  count=("salary", "size"),
              )
              .reset_index()
        )

    # Redondeo a dos decimales
    grouped["avg_salary"] = grouped["avg_salary"].astype(float).round(2)
    grouped["min_salary"] = grouped["min_salary"].astype(float).round(2)
    grouped["max_salary"] = grouped["max_salary"].astype(float).round(2)

    levels: List[SalaryLevelSummary] = []
    for _, row in grouped.iterrows():
        levels.append(
            SalaryLevelSummary(
                job_level=row["job_level"],
                avg_salary=float(row["avg_salary"]),
                min_salary=float(row["min_salary"]),
                max_salary=float(row["max_salary"]),
                count=int(row["count"]),
            )
        )

    overall_avg = round(float(df["salary"].mean()), 2)
    overall_min = round(float(df["salary"].min()), 2)
    overall_max = round(float(df["salary"].max()), 2)

    return SalarySummaryResponse(
        overall_avg_salary=overall_avg,
        overall_min_salary=overall_min,
        overall_max_salary=overall_max,
        levels=levels,
    )
