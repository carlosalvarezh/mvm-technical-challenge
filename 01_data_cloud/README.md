# **README – MVM Technical Challenge

Ingeniería de Datos + Cloud + API REST**

Este repositorio contiene la solución completa al desafío técnico propuesto por MVM, abarcando el diseño, construcción y exposición de un modelo organizacional sintético mediante un pipeline de datos end-to-end. La solución está desarrollada bajo principios de ingeniería de datos modernos, utilizando un Data Lake en Azure como núcleo de almacenamiento y una API REST como capa de acceso.

El proyecto fue diseñado con un enfoque modular, reproducible y alineado con mejores prácticas de arquitectura, versionamiento y documentación técnica.

---

## **1. Arquitectura general de la solución**

La solución implementa un flujo de datos completo compuesto por cinco etapas:

1. **Generación de datos sintéticos**
   Construcción programática de un modelo organizacional compuesto por departamentos, puestos de trabajo y empleados.
   Los datos se generan con distribuciones realistas (log-normal, categóricas sesgadas, valores truncados), manteniendo coherencia interna y sesgos propios de escenarios corporativos.

2. **Persistencia local (CSV / Parquet)**
   Los datos generados se almacenan localmente en formatos analíticos estándar.
   Parquet se utiliza como formato preferente por su eficiencia para lectura columnar.

3. **Proceso batch hacia Azure (Data Lake)**
   A través de un script idempotente en Python (FastAPI + Azure SDK), los archivos locales se migran a un **Azure Storage Account (Blob Storage / ADLS Gen2)**.
   La estructura destino utiliza un esquema versionado:

   ```text
   org_data/
     └── v1/
         ├── departments/
         ├── job_positions/
         └── employees/
   ```

4. **Vista analítica y métricas**
   Se construye una vista integrada en memoria (equivalente a una vista SQL) que unifica empleados, cargos y departamentos.
   A partir de esta vista se derivan análisis descriptivos, KPIs y visualizaciones organizacionales.

5. **API REST (FastAPI)**
   Exposición del modelo integrado mediante un servicio REST que permite consultar:

   * empleados,
   * departamentos,
   * métricas salariales agregadas.

   Los valores monetarios y numéricos relevantes se redondean a **dos decimales**, manteniendo coherencia con prácticas reales de presentación.

---

## **2. Estructura del repositorio**

```text
mvm-technical-challenge/
│
├── 01_data_cloud/
│   ├── src/
│   │   ├── data_generation/        # Scripts de generación sintética
│   │   ├── batch_etl/              # Proceso batch hacia Azure
│   │   └── api/                    # API REST (FastAPI)
│   │        └── org_api.py
│   │
│   ├── data/
│   │   └── raw/                    # Datos locales en CSV / Parquet
│   │
│   ├── docs/
│   │   ├── 01_synthetic_data_generation.ipynb
│   │   ├── 02_batch_etl.ipynb
│   │   ├── 03_org_analytics.ipynb
│   │   └── 04_api_rest.ipynb
│   │
│   ├── .env                        # Configuración de Azure (NO se sube a Git)
│   └── requirements.txt            # Dependencias del proyecto
│
└── README.md
```

---

## **3. Requisitos técnicos**

### **Lenguaje y librerías principales**

* Python 3.10+
* pandas
* numpy
* matplotlib
* fastapi
* uvicorn
* azure-storage-blob
* python-dotenv

### **Azure**

* Cuenta de almacenamiento (Storage Account) tipo **General Purpose v2**
* Contenedor analítico: `org-raw`
* Variables de entorno requeridas:

```text
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_STORAGE_CONTAINER_RAW=org-raw
AZURE_STORAGE_BASE_PREFIX=org_data/v1
```

---

## **4. Ejecución del proceso batch hacia Azure**

Desde la carpeta `01_data_cloud`, con el entorno virtual activado:

```bash
python -m pip install -r requirements.txt
```

Luego:

```bash
PYTHONPATH=src python src/batch_etl/org_batch_etl.py
```

El proceso:

* detecta los archivos CSV y Parquet generados,
* crea el contenedor en caso de no existir,
* y sube los datos organizados por entidades.

---

## **5. Ejecución de la API REST**

Desde `01_data_cloud`:

```bash
PYTHONPATH=src uvicorn api.org_api:app --reload
```

La documentación interactiva estará disponible en:

* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

### **Endpoints principales**

| Endpoint                        | Descripción                                                       |
| ------------------------------- | ----------------------------------------------------------------- |
| `GET /health`                   | Verifica estado del servicio.                                     |
| `GET /employees`                | Listado paginado de empleados. Filtros por departamento y nivel.  |
| `GET /employees/{employee_id}`  | Consulta individual por ID.                                       |
| `GET /departments`              | Departamentos con headcount.                                      |
| `GET /analytics/salary-summary` | Métricas salariales por nivel, valores redondeados a 2 decimales. |

---

## **6. Documentación en notebooks**

Cada fase del desafío está documentada en un notebook independiente:

* **01_synthetic_data_generation.ipynb**
  Diseño conceptual, generación sintética y validación estadística.

* **02_batch_etl.ipynb**
  Ejecución del proceso batch hacia Azure y verificación de carga.

* **03_org_analytics.ipynb**
  Construcción de vista integrada y análisis organizacional.

* **04_api_rest.ipynb**
  Documentación del diseño, pruebas de endpoints y validación funcional.

---

## **7. Consideraciones técnicas y decisiones de diseño**

* Se eligió **Data Lake** en lugar de un motor SQL para respetar las restricciones de la suscripción académica y mantenerse dentro de un enfoque moderno *lake-centric*.
* El uso de **Parquet** mejora desempeño en lectura y reduce costos de almacenamiento.
* La estructura versionada (`org_data/v1`) habilita evolución futura del modelo.
* El pipeline completo es **idempotente**, permitiendo regeneración y recarga sin inconsistencias.
* Los valores monetarios y numéricos se redondean a **dos decimales** en capas de presentación (notebooks y API), garantizando claridad y consistencia empresarial.
* La API REST se diseñó con un enfoque minimalista pero extensible, suficiente para demostrar comprensión de patrones de arquitectura orientados a servicios.

---

## **8. Próximos pasos (opcional)**

La solución puede evolucionarse hacia:

* Orquestación del batch con GitHub Actions o Azure Functions.
* Montaje de una capa gold mediante Spark o Synapse (si la suscripción lo permitiera).
* Implementación de endpoints adicionales para consultas cruzadas, forecast o scoring.
* Exposición del modelo en un dashboard interactivo.

---

## **9. Autor**

Carlos Alberto Álvarez Henao
Data Scientist – M.Sc., Ph.D.
Repositorio: `carlosalvarezh/mvm-technical-challenge`
