# **Desafío 2: Modelamiento de Datos para BI (Northwind)**

## **1. Descripción general**

Este módulo desarrolla la solución correspondiente al segundo desafío del proyecto técnico, orientado al diseño de un modelo analítico basado en la base de datos Northwind y la construcción de un reporte interactivo en Power BI.

El objetivo es diseñar un **modelo dimensional optimizado**, estructurar indicadores clave mediante medidas DAX y elaborar un **dashboard ejecutivo** que permita evaluar el comportamiento de ventas, órdenes, costos y márgenes. La solución cumple con las buenas prácticas de modelado para BI, integra una página oculta con notas técnicas y presenta un archivo PDF exportado desde Power BI.

## **2. Fuente de datos**

La información utilizada corresponde a una versión relacional de **Northwind**, previamente descargada y preparada para uso analítico. Las tablas incluidas cubren los componentes principales del dominio:

* Facturas (tabla de hechos)
* Products
* Categories
* Customers
* Cities
* Countries
* Shippers
* Calendario (tabla generada para inteligencia de tiempo)

## **3. Modelo dimensional**

El modelo adopta la estructura de un **esquema en estrella**, con la tabla **Facturas** como tabla de hechos y dimensiones normalizadas para productos, clientes, categorías, geografía, transportistas y fechas.

Las relaciones se establecen en modo **1:* con dirección de filtro único**, garantizando:

* flujo de filtros desde dimensiones hacia la tabla de hechos,
* ausencia de ambigüedades,
* reducción de redundancia,
* mejor rendimiento en consultas y visualizaciones.

La tabla Calendario se marca explícitamente como tabla de fechas y soporta las medidas de inteligencia temporal.

## **4. Medidas DAX**

El modelo incorpora medidas agrupadas en carpetas temáticas para facilitar su gobernanza y uso dentro del reporte:

* **Ventas:** indicadores de valor neto, comparación interanual y variaciones porcentuales.
* **Órdenes:** conteos distintos de pedidos y sus variaciones.
* **Costo:** estimaciones basadas en el costo estándar del producto.
* **Margen:** cálculo de rentabilidad absoluta y relativa.
* **Margen %:** análisis de eficiencia comercial a través de porcentajes y variaciones.

Estas medidas permiten analizar desempeño, evolución temporal, rentabilidad y comportamiento por categoría, producto, empleado y país.

---

## **5. Diseño del reporte**

El archivo Power BI contiene múltiples páginas orientadas a distintos niveles de análisis:

* **Página principal:** visión ejecutiva con los indicadores clave y visualizaciones principales.
* **Páginas de análisis detallado:** gráficos por categoría, producto, geografía, cliente y transportista.
* **Páginas de interacción:** elementos de navegación y alternancia de vistas.
* **Página tooltip:** información contextual para enriquecer la experiencia del usuario.

El reporte incorpora segmentadores, un tema visual consistente y una estructura organizada para facilitar su uso por parte de analistas y tomadores de decisión.

## **6. Página oculta de notas técnicas**

Se incluye una página oculta llamada **_Notas Técnicas**, en la cual se documentan:

* estructura del modelo,
* decisiones de diseño dimensional,
* relaciones establecidas,
* organización de medidas DAX,
* criterios aplicados para optimización de rendimiento,
* justificación del esquema adoptado.

Esta página forma parte del PBIX y está disponible únicamente para revisores técnicos.

## **7. Archivos entregados**

La carpeta contiene:

```text
02_bi_northwind/
│
├── pbix/
│   └── MVM_BI.pbix
│
├── docs/
│   └── MVM_BI.pdf
│
└── README.md
```

* **MVM_BI.pbix**: archivo original del reporte, modelo dimensional y medidas DAX.
* **nMVM_BI.pdf**: exportación del reporte en formato PDF.
* **README.md**: documentación del módulo y su diseño técnico.

## **8. Consideraciones finales**

El desarrollo aplicado en este módulo responde a criterios de diseño dimensional, higiene del modelo, organización de medidas, prácticas de rendimiento y claridad visual del reporte. El enfoque adoptado permite su extensión a volúmenes mayores de datos o a distintos dominios empresariales sin modificar la estructura base.

## **9. Autor**

Carlos Alberto Álvarez Henao
Data Scientist – M.Sc., Ph.D.
Repositorio: `carlosalvarezh/mvm-technical-challenge`
