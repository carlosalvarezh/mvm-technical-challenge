"""
Generación de datos sintéticos para el DESAFÍO #1
Prueba técnica MVM - Ingeniería de Datos + Cloud

Este script genera tres DataFrames:
- departments_df
- job_positions_df
- employees_df

siguiendo la estructura solicitada en el enunciado
(departamentos, puestos de trabajo y empleados) y
utilizando distribuciones de probabilidad sencillas
pero más realistas que un simple random uniforme.
"""

from datetime import date, timedelta
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Parámetros generales
# ---------------------------------------------------------------------------

RANDOM_SEED = 42
N_EMPLOYEES = 600  # cantidad total de empleados a simular

rng = np.random.default_rng(RANDOM_SEED)


# ---------------------------------------------------------------------------
# 1. Definición de departamentos
# ---------------------------------------------------------------------------

def generate_departments() -> pd.DataFrame:
    """
    Genera la tabla de departamentos con un peso relativo de tamaño
    para cada uno, que luego se utilizará al asignar empleados.
    """

    departments = [
        # name,                type,       size_weight
        ("Operations",         "Core",     4.0),
        ("Commercial",         "Core",     3.0),
        ("IT & Data",          "Core",     2.5),
        ("Finance",            "Corporate",1.8),
        ("Human Resources",    "Corporate",1.2),
        ("Legal & Compliance", "Support",  0.7),
        ("Strategy & Projects","Support",  0.8),
    ]

    departments_df = pd.DataFrame(
        [
            {
                "department_id": i + 1,
                "department_name": name,
                "department_type": dept_type,
                "headcount_weight": weight,
            }
            for i, (name, dept_type, weight) in enumerate(departments)
        ]
    )

    return departments_df


# ---------------------------------------------------------------------------
# 2. Definición de puestos de trabajo
# ---------------------------------------------------------------------------

def generate_job_positions(departments_df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera la tabla de puestos de trabajo por departamento y nivel
    de seniority. Cada combinación dept + seniority generará
    al menos un puesto.
    """

    seniority_levels = ["Junior", "SemiSenior", "Senior", "Lead", "Manager"]

    job_positions = []
    job_position_id = 1

    for _, dept in departments_df.iterrows():
        dept_id = dept["department_id"]
        dept_name = dept["department_name"]

        for level in seniority_levels:
            # Nombre de puesto sencillo pero legible
            position_name = f"{dept_name} {level}"

            job_positions.append(
                {
                    "job_position_id": job_position_id,
                    "department_id": dept_id,
                    "position_name": position_name,
                    "seniority_level": level,
                }
            )
            job_position_id += 1

    job_positions_df = pd.DataFrame(job_positions)
    return job_positions_df


# ---------------------------------------------------------------------------
# 3. Utilidades para generación de fechas, edades y salarios
# ---------------------------------------------------------------------------

def generate_age(size: int) -> np.ndarray:
    """
    Genera edades con una distribución aproximadamente normal,
    truncada entre 22 y 65 años.
    """
    ages = rng.normal(loc=37, scale=8, size=size)
    ages = np.clip(ages, 22, 65)
    return ages.round().astype(int)


def generate_tenure_years(ages: np.ndarray) -> np.ndarray:
    """
    Genera años de antigüedad con mayor concentración en los
    primeros años, asegurando coherencia con la edad (la
    antigüedad no puede exceder la edad laboral).
    """
    size = len(ages)

    # distribución exponencial truncada como aproximación simple
    raw = rng.exponential(scale=3, size=size)  # mayoría cerca de 0–5 años
    tenure = np.clip(raw, 0, 35)

    # Ajuste para no superar la edad - 21 (edad laboral mínima aproximada)
    max_tenure = np.maximum(0, ages - 21)
    tenure = np.minimum(tenure, max_tenure)

    return tenure.round().astype(int)

def safe_add_years(d: date, years: int) -> date:
    """
    Suma 'years' años a la fecha 'd' manejando correctamente
    el caso de fechas bisiestas (29 de febrero). Si el año
    resultante no es bisiesto, ajusta el día al 28 de febrero.
    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        # Caso típico: 29 de febrero en un año no bisiesto
        return d.replace(year=d.year + years, month=2, day=28)

def generate_dates_from_age_and_tenure(
    ages: np.ndarray,
    tenure_years: np.ndarray,
):
    """
    A partir de edad y antigüedad, genera fechas de nacimiento e ingreso.

    - La fecha de nacimiento se calcula restando la edad (en años) al año actual
      y sumando un día aleatorio dentro del año.
    - La fecha de ingreso se calcula restando la antigüedad (en años) al año
      actual y sumando un día aleatorio dentro del año.
    - Se garantiza que la fecha de ingreso no sea anterior a una edad laboral
      mínima aproximada de 18 años, usando un desplazamiento de 18*365 días
      sobre la fecha de nacimiento. Esta aproximación evita problemas con
      años bisiestos y es suficiente para el contexto de datos sintéticos.
    """
    size = len(ages)
    today = date.today()

    birth_dates = []
    hire_dates = []

    for i in range(size):
        age = int(ages[i])
        tenure = int(tenure_years[i])

        # Año aproximado de nacimiento e ingreso
        birth_year = today.year - age
        hire_year = today.year - tenure

        # Día aleatorio dentro del año
        birth_day_of_year = int(np.random.randint(1, 365))
        hire_day_of_year = int(np.random.randint(1, 365))

        birth_date = date(birth_year, 1, 1) + timedelta(
            days=birth_day_of_year
        )
        hire_date = date(hire_year, 1, 1) + timedelta(
            days=hire_day_of_year
        )

        # Edad laboral mínima aproximada: 18 años
        min_hire_date = birth_date + timedelta(days=18 * 365)

        if hire_date < min_hire_date:
            hire_date = min_hire_date

        birth_dates.append(birth_date)
        hire_dates.append(hire_date)

    return np.array(birth_dates), np.array(hire_dates)


def generate_salary(levels: np.ndarray,
                    department_ids: np.ndarray,
                    departments_df: pd.DataFrame) -> np.ndarray:
    """
    Genera salarios usando una distribución log-normal como base,
    ajustada por nivel de seniority y por departamento.
    La unidad puede interpretarse como salario mensual o anual,
    según se defina más adelante.
    """

    size = len(levels)

    # factores por nivel de seniority
    level_factor = {
        "Junior": 0.8,
        "SemiSenior": 1.0,
        "Senior": 1.3,
        "Lead": 1.6,
        "Manager": 2.0,
    }

    # factores por tipo de departamento (simple pero razonable)
    dept_type_factor = {
        "Core": 1.10,
        "Corporate": 1.00,
        "Support": 0.95,
    }

    # mapa department_id -> tipo
    dept_types = (
        departments_df.set_index("department_id")["department_type"].to_dict()
    )

    # base log-normal (no centrada en valores monetarios específicos;
    # posteriormente se puede interpretar como miles de unidades)
    base = rng.lognormal(mean=8.5, sigma=0.5, size=size)

    salaries = []
    for i in range(size):
        lvl = levels[i]
        dept_id = int(department_ids[i])

        lf = level_factor.get(lvl, 1.0)
        dt = dept_type_factor.get(dept_types.get(dept_id, "Corporate"), 1.0)

        salary_value = base[i] * lf * dt
        salaries.append(salary_value)

    return np.array(salaries)


# ---------------------------------------------------------------------------
# 4. Generación de empleados
# ---------------------------------------------------------------------------

def generate_employees(
    departments_df: pd.DataFrame,
    job_positions_df: pd.DataFrame,
    n_employees: int = N_EMPLOYEES,
) -> pd.DataFrame:
    """
    Genera la tabla de empleados asignando departamento, puesto,
    edad, antigüedad, fechas y salario con distribuciones sesgadas.
    """

    # Probabilidad de pertenencia a cada departamento según headcount_weight
    weights = departments_df["headcount_weight"].to_numpy()
    dept_probs = weights / weights.sum()

    dept_ids = departments_df["department_id"].to_numpy()

    # Distribución de niveles de seniority en la plantilla
    seniority_levels = ["Junior", "SemiSenior", "Senior", "Lead", "Manager"]
    seniority_probs = np.array([0.4, 0.3, 0.18, 0.07, 0.05])  # suma 1.0

    # 1) Departamento y nivel para cada empleado
    employee_department_ids = rng.choice(
        dept_ids, size=n_employees, p=dept_probs
    )
    employee_seniority = rng.choice(
        seniority_levels, size=n_employees, p=seniority_probs
    )

    # 2) Selección de puesto compatible con dept + nivel
    job_positions_df = job_positions_df.copy()

    # índice auxiliar para búsquedas rápidas
    grouped_positions = (
        job_positions_df.groupby(
            ["department_id", "seniority_level"]
        )["job_position_id"]
        .apply(list)
        .to_dict()
    )

    job_position_ids = []
    for dept_id, level in zip(employee_department_ids, employee_seniority):
        key = (int(dept_id), level)
        candidates = grouped_positions.get(key)

        if not candidates:
            # Si por alguna razón no hay puesto exacto, elegir cualquiera del depto
            candidates = job_positions_df[
                job_positions_df["department_id"] == dept_id
            ]["job_position_id"].tolist()

        job_position_ids.append(rng.choice(candidates))

    job_position_ids = np.array(job_position_ids)

    # 3) Edad, antigüedad y fechas
    ages = generate_age(n_employees)
    tenure_years = generate_tenure_years(ages)
    birth_dates, hire_dates = generate_dates_from_age_and_tenure(
        ages, tenure_years
    )

    # 4) Salario
    salaries = generate_salary(
        levels=employee_seniority,
        department_ids=employee_department_ids,
        departments_df=departments_df,
    )

    # 5) Nombres simples (se podrían mejorar si hiciera falta)
    first_names = [
        "Carlos", "María", "Ángela", "José", "Pedro", "Jaime", "Ana",
        "Juan", "Mauricio", "Diego"
    ]
    last_names = [
        "Álvarez", "Henao", "Rodríguez", "López", "Hernández",
        "Pérez", "Gómez", "Sánchez", "Ramírez", "Torres"
    ]

    employee_first_names = rng.choice(first_names, size=n_employees)
    employee_last_names = rng.choice(last_names, size=n_employees)

    employees = []
    for i in range(n_employees):
        employees.append(
            {
                "employee_id": i + 1,
                "first_name": employee_first_names[i],
                "last_name": employee_last_names[i],
                "department_id": int(employee_department_ids[i]),
                "job_position_id": int(job_position_ids[i]),
                "seniority_level": employee_seniority[i],
                "birth_date": birth_dates[i],
                "hire_date": hire_dates[i],
                "age": int(ages[i]),
                "tenure_years": int(tenure_years[i]),
                "salary": float(salaries[i]),
            }
        )

    employees_df = pd.DataFrame(employees)
    return employees_df


# ---------------------------------------------------------------------------
# Punto de entrada principal
# ---------------------------------------------------------------------------

def main():
    """
    Genera los tres DataFrames requeridos por el DESAFÍO #1 y
    muestra un resumen por consola. El guardado a CSV/Parquet
    se gestionará en el DESAFÍO #2.
    """

    departments_df = generate_departments()
    job_positions_df = generate_job_positions(departments_df)
    employees_df = generate_employees(departments_df, job_positions_df)

    print("Departments:")
    print(departments_df.head(), "\n")

    print("Job positions:")
    print(job_positions_df.head(), "\n")

    print("Employees:")
    print(employees_df.head(), "\n")

    print("Shapes:")
    print("  departments_df:", departments_df.shape)
    print("  job_positions_df:", job_positions_df.shape)
    print("  employees_df:", employees_df.shape)


if __name__ == "__main__":
    main()
