# Sistema Inteligente de Gestión Financiera Personal

Sistema backend con inteligencia artificial que ayuda a los usuarios a gestionar sus finanzas personales, evaluar gastos en tiempo real y recibir recomendaciones personalizadas basadas en su historial de pagos.

## Características Principales

- **Evaluación Inteligente de Gastos**: Analiza cada transacción considerando tu saldo, suscripciones activas y patrones de gasto
- **Recomendaciones Personalizadas**: La IA aprende de tu historial y ofrece consejos específicos para tu situación
- **Gestión de Pagos**: Registra y controla todos tus pagos con historial completo
- **Alertas Inteligentes**: Recibe advertencias cuando un gasto puede comprometer tu estabilidad financiera
- **API REST**: Endpoints completos para integración con cualquier frontend

## Tecnologías

- **Backend**: Flask (Python)
- **Base de Datos**: MySQL con SQLAlchemy ORM
- **IA**: OpenAI GPT-4o-mini (con fallback inteligente)
- **Análisis**: Sistema de evaluación basado en patrones de comportamiento

## Instalación

### Requisitos Previos

- Python 3.8 o superior
- MySQL Server instalado y en ejecución
- (Opcional) API key de OpenAI para mensajes personalizados con GPT

### Paso 1: Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd <nombre-del-proyecto>
```

### Paso 2: Crear Entorno Virtual

```bash
python -m venv venv
```

Activar el entorno virtual:
- **Windows**: `venv\Scripts\activate`
- **Linux/Mac**: `source venv/bin/activate`

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
MYSQL_USER=tu_usuario
MYSQL_PASS=tu_contraseña
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DB=bancodigital

OPENAI_API_KEY=tu_api_key_opcional
```

**Nota**: Si no configuras `OPENAI_API_KEY`, el sistema usará un generador de mensajes inteligente local que también analiza tu historial.

### Paso 5: Iniciar la Aplicación

```bash
python app.py
```

La aplicación creará automáticamente la base de datos y las tablas necesarias en el primer inicio.

El servidor estará disponible en: `http://127.0.0.1:5000`

## Uso de la API

### 1. Evaluar un Gasto (con IA)

**Endpoint**: `POST /api/evaluar`

**Body**:
```json
{
  "idUser": 1,
  "saldo": 4200.00,
  "suscripciones": 3,
  "esencial": false,
  "nuevo_gasto": 1500.00
}
```

**Respuesta con alerta**:
```json
{
  "alerta": true,
  "mensaje": "⚠️ Este gasto representa el 35.7% de tu saldo. Basándome en tus últimos pagos..."
}
```

**Respuesta sin alerta**:
```json
{
  "alerta": false
}
```

### 2. Registrar un Pago

**Endpoint**: `POST /api/pago`

**Body**:
```json
{
  "idUser": 1,
  "motivo": "Compra de supermercado",
  "monto": 250.50
}
```

**Respuesta**:
```json
{
  "mensaje": "Pago registrado con éxito",
  "nuevo_saldo": 3949.50,
  "pago_id": 15
}
```

### 3. Consultar Saldo

**Endpoint**: `GET /api/saldo/<user_id>`

**Respuesta**:
```json
{
  "idUser": 1,
  "saldo": 3949.50
}
```

## Cómo Funciona la IA

El sistema de inteligencia artificial mejora con cada pago que registras:

1. **Análisis de Patrones**: Calcula tu gasto promedio, identifica gastos similares y evalúa tendencias
2. **Evaluación Contextual**: Considera tu saldo actual, suscripciones y tipo de gasto (esencial/no esencial)
3. **Predicción de Riesgo**: Ajusta dinámicamente los umbrales de alerta según tu comportamiento histórico
4. **Recomendaciones Personalizadas**: Genera mensajes específicos basados en tus hábitos reales

**Ejemplo**: Si normalmente gastas $500 en promedio y de repente intentas gastar $1500, la IA lo detectará y te advertirá que es 3x tu promedio habitual, incluso si técnicamente tienes el saldo.

## Estructura del Proyecto

```
.
├── app.py                  # Aplicación principal Flask
├── config.py              # Configuración de base de datos
├── requirements.txt       # Dependencias del proyecto
├── models/               # Modelos de base de datos
│   ├── __init__.py
│   ├── user.py          # Usuario
│   ├── pago.py          # Pagos
│   ├── historial.py     # Historial de transacciones
│   └── dinero.py        # Saldo del usuario
└── ml/                   # Sistema de IA
    ├── model.py         # Lógica de evaluación de riesgo
    └── gpt.py           # Generación de mensajes personalizados
```

## Desarrollo

### Usuario de Prueba

Al iniciar la aplicación por primera vez, se crea automáticamente un usuario de prueba:

- **ID**: 1
- **Nombre**: Carlos Ramírez
- **Email**: carlos@example.com
- **Saldo inicial**: $4200.00

### Extender la IA

Para mejorar el sistema de evaluación, puedes modificar:

- `ml/model.py`: Ajusta los umbrales y lógica de evaluación de riesgo
- `ml/gpt.py`: Personaliza los prompts y el formato de los mensajes

## Solución de Problemas

### Error de conexión a MySQL

Verifica que MySQL esté corriendo:
```bash
mysql -u root -p
```

Y que las credenciales en `.env` sean correctas.

### La IA no genera mensajes personalizados

Si no tienes configurada la API key de OpenAI, el sistema usa un generador local inteligente. Para habilitar GPT:

1. Obtén una API key en https://platform.openai.com/api-keys
2. Agrégala a tu archivo `.env`
3. Reinicia la aplicación

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.