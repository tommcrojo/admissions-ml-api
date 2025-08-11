# Admissions ML API

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

API REST de scoring de admisiones universitarias basada en Machine Learning. Predice la probabilidad de admisión de candidatos utilizando un modelo de Random Forest entrenado con datos históricos de estudiantes.

## 🎯 Visión General

Este proyecto proporciona un servicio de inferencia ML para evaluar solicitudes de admisión universitaria en tiempo real. El sistema procesa características demográficas y académicas de los solicitantes y devuelve predicciones con niveles de confianza asociados.

**Casos de uso:**
- Evaluación automatizada de candidatos
- Priorización de solicitudes con alta probabilidad de admisión
- Análisis de patrones de admisión

## 📊 Arquitectura del Pipeline de Datos

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Datos Crudos   │ ───> │  Entrenamiento   │ ───> │ Modelo Guardado │
│  (CSV 125K)     │      │  RandomForest    │      │  (rf_model.pkl) │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                                              │
                                                              ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Respuesta     │ <─── │   Inferencia     │ <─── │  POST /predict  │
│  JSON (score)   │      │  Feature Eng.    │      │  (datos nuevos) │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

### Flujo de Datos

1. **Ingesta**: Recepción de datos del candidato vía API REST (JSON)
2. **Transformación**: Feature engineering (normalización de notas, codificación de categorías)
3. **Inferencia**: Predicción usando modelo pre-entrenado (Random Forest)
4. **Output**: Respuesta estructurada con predicción, probabilidad y confianza

[PLACEHOLDER: Insertar Diagrama de Flujo de Datos o Captura de Pantalla]

## 🛠️ Tech Stack

| Categoría | Tecnologías |
|-----------|------------|
| **Framework Web** | FastAPI, Uvicorn |
| **ML** | scikit-learn, joblib |
| **Procesamiento** | pandas, numpy |
| **Validación** | Pydantic v2 |
| **Testing** | pytest, httpx |
| **Containerización** | Docker |

## 🚀 Configuración Local

### Prerrequisitos

- Python 3.9 o superior
- pip o virtualenv

### Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/tommcrojo/admissions-ml-private.git
cd admissions-ml-private
```

2. Crear y activar entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

### Ejecución con Python

```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Ejecución con Docker

```bash
docker build -t admissions-api .
docker run -p 8000:8000 admissions-api
```

La API estará disponible en `http://localhost:8000`

## 📝 Uso

### Endpoints Disponibles

#### `GET /health`
Verifica el estado del servicio y la carga del modelo.

```bash
curl http://localhost:8000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

#### `POST /predict`
Realiza una predicción de admisión.

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "edad": 22,
    "nota_media": 8.5,
    "pais_nacimiento": "España",
    "programa": "Ingeniería Informática",
    "solicita_beca": true
  }'
```

**Respuesta:**
```json
{
  "prediction": "admitido",
  "probability": 0.847,
  "confidence": "high",
  "model_version": "1.0.0"
}
```

### Documentación Interactiva

FastAPI genera documentación automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

Ejecutar tests unitarios:

```bash
pytest tests/ -v
```

Ejecutar con cobertura:

```bash
pytest tests/ --cov=api --cov-report=html
```

## 📂 Estructura del Proyecto

```
admissions-ml-private/
├── api/
│   └── main.py              # Endpoints FastAPI y lógica de predicción
├── models/
│   ├── rf_model.pkl         # Modelo Random Forest serializado
│   └── programas.pkl        # Mapeo de programas académicos
├── tests/
│   └── test_api.py          # Tests unitarios
├── data/
│   └── raw/                 # Datos de entrenamiento (no en producción)
├── Dockerfile               # Configuración de containerización
├── requirements.txt         # Dependencias Python
└── README.md
```

## 🔧 Consideraciones de Producción

### Escalabilidad
- Implementar caching de predicciones frecuentes (Redis)
- Usar workers de Uvicorn para alta concurrencia
- Considerar despliegue con Kubernetes para auto-scaling

### Monitoreo
- Logging estructurado de todas las predicciones
- Métricas de latencia y throughput (Prometheus)
- Alertas de drift del modelo

### Seguridad
- Autenticación API (JWT/OAuth2)
- Rate limiting por IP
- Validación estricta de inputs

## 📄 Licencia

Este proyecto está licenciado bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👤 Autor

**Tomás Campoy Rojo**
- GitHub: [@tommcrojo](https://github.com/tommcrojo)
