# **MVM – Prueba Técnica de Ingeniería de Datos y BI**

Este repositorio contiene el desarrollo completo de los dos desafíos planteados en la prueba técnica para Ingeniería de Datos y Business Intelligence. La solución integra generación de datos sintéticos, procesos cloud, construcción de vistas analíticas, exposición vía API REST y un modelo BI basado en Northwind con dashboard ejecutivos en Power BI.

El proyecto mantiene una estructura modular que separa claramente los componentes de Data Engineering & Cloud y los de Business Intelligence, con el fin de garantizar orden, reproducibilidad y claridad técnica en la revisión.

## **1. Desafío 1 – Ingeniería de Datos + Cloud**

El primer desafío se centra en el diseño y ejecución de un pipeline completo que abarca:

### **1.1 Generación de datos sintéticos**

Se diseñan datos para representar una organización con:

* Departamentos
* Puestos de trabajo
* Empleados

Los datos se generan utilizando **Python (NumPy, Pandas)** y distribuciones que representan comportamientos realistas en estructuras organizacionales (tamaños de equipo, niveles jerárquicos, salarios, antigüedad, etc.).
El proceso está completamente documentado en el notebook correspondiente.

Los resultados se almacenan en múltiples formatos (CSV y Parquet) dentro de la carpeta `01_data_cloud/data/raw`.

### **1.2 Proceso Batch hacia Azure Storage**

Se implementa un proceso ETL batch en Python utilizando el **Azure SDK**, con las siguientes características:

* Lectura de datos locales en CSV/Parquet.
* Carga hacia un **Azure Blob Storage** organizado por versión mediante prefijos como:

  ```text
  org_data/v1/departments/
  org_data/v1/job_positions/
  org_data/v1/employees/
  ```

* Gestión de configuración mediante variables de entorno en `.env`.

Los scripts están ubicados en:

  ```text
  01_data_cloud/src/batch_etl/
  ```

y se validan con el notebook **02_batch_etl.ipynb**.

### **1.3 Vista analítica**

Se construye una vista consolidada (`org_view`) que integra empleados, puestos y departamentos, y permite analizar la estructura organizacional mediante indicadores como:

* Distribución salarial
* Composición por niveles
* Antigüedad
* Tamaño y distribución por departamento

Las visualizaciones y el análisis exploratorio están documentados en:

```text
01_data_cloud/docs/03_org_analytics.ipynb
```

### **1.4 API REST para consulta**

El modelo final se expone mediante una **API REST desarrollada con FastAPI**, permitiendo consultar entidades y métricas de manera programática. La API incluye documentación automática (Swagger) y puntos de acceso para:

* Departamentos
* Puestos
* Empleados
* Vista consolidada

El código se encuentra en:

```text
01_data_cloud/src/api/org_api.py
```

Las pruebas y validación se documentan en:

```text
01_data_cloud/docs/04_api_rest.ipynb
```

## **2. Desafío 2 – Modelamiento de Datos para BI (Northwind)**

El segundo desafío aborda un caso de Business Intelligence utilizando la base Northwind. La solución incluye modelamiento dimensional, creación de medidas DAX y diseño de un dashboard ejecutivo en Power BI.

### **2.1 Modelo dimensional**

Se diseña un modelo en estrella con:

* **Facturas** como tabla de hechos
* Dimensiones: Products, Categories, Customers, Cities, Countries, Shippers y Calendario

Las relaciones se definen bajo criterios de:

* dirección de filtro única,
* eliminación de redundancia,
* flujos de filtrado consistentes,
* soporte para inteligencia temporal mediante tabla de fechas marcada.

### **2.2 Medidas DAX**

Se implementan medidas estructuradas en carpetas temáticas:

* **Ventas**
* **Órdenes**
* **Costo**
* **Margen**
* **Margen %**

Incluyen variaciones interanuales, porcentajes, expresiones acumuladas y cálculos de rendimiento.

### **2.3 Dashboard en Power BI**

El archivo PBIX contiene:

* Página ejecutiva con KPIs principales
* Páginas de análisis detallado
* Interacciones (toggles)
* Página tooltip
* Página oculta de notas técnicas documentando decisiones de modelado

El PDF exportado del reporte se incluye como parte de la entrega.

## **3. Estructura del repositorio**

```text
mvm-technical-challenge/
│
├── 01_data_cloud/
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   ├── docs/
│   │   ├── 00_Ingeniería_de_Datos_Cloud.ipynb
│   │   ├── 01_datos_sinteticos.ipynb
│   │   ├── 02_batch_etl.ipynb
│   │   ├── 03_org_analytics.ipynb
│   │   └── 04_api_rest.ipynb
│   ├── src/
│   │   ├── data_generation/
│   │   ├── batch_etl/
│   │   └── api/
│   └── README.md
│
├── 02_bi_northwind/
│   ├── pbix/
│   │   └── MVM_BI.pbix
│   ├── docs/
│   │   └── MVM_BI.pdf
│   └── README.md
│
└── README.md
```

## **4. Tecnologías utilizadas**

### **Lenguaje y librerías**

* Python 3.11
* Pandas, NumPy
* Azure SDK
* FastAPI + Uvicorn

### **Cloud**

* Azure Blob Storage (cuenta académica)

### **BI**

* Power BI Desktop (modelo dimensional, DAX, dashboard)

## **5. Consideraciones técnicas finales**

* El proyecto se diseñó siguiendo principios de ingeniería de datos reproducible, componentes desacoplados y documentación transparente.
* Cada módulo incluye notebooks explicativos que detallan decisiones, supuestos, validaciones y resultados.
* Las soluciones se entregan en formato abierto (CSV, Parquet, PBIX) y con código fuente disponible.
* La arquitectura planteada facilita la escalabilidad y adaptación a escenarios empresariales más amplios.

## **6. Autor**

Carlos Alberto Álvarez Henao
Data Scientist – Ingeniería de Datos y BI
