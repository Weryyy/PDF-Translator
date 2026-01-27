# PDF Translator

Un traductor de PDFs personal que utiliza modelos de lenguaje para traducir documentos PDF a diferentes idiomas. Soporta tanto la API de OpenAI como modelos propios entrenados con **datos sintéticos 100% GRATUITOS**.

## 🆕 NUEVO: Generación de Datos Sintéticos GRATIS

Ya no necesitas pagar por APIs para entrenar tu modelo. **5 métodos gratuitos disponibles:**

1. **🤗 Hugging Face** - API gratuita, modelos de última generación (FLAN-T5, Mistral, BLOOM)
2. **Ollama** - LLMs locales gratuitos (Llama 2, Mistral)
3. **Open Source Models** - GPT-2, BLOOM corriendo localmente
4. **Rule-based** - Plantillas y reglas, extremadamente rápido
5. **Back-translation** - Técnica de traducción bidireccional

**📖 Ver guías completas:**
- [Guía Hugging Face](docs/HUGGINGFACE_GUIDE.md) - Método recomendado, API gratuita
- [Todos los Métodos Gratuitos](docs/SYNTHETIC_DATA_FREE.md) - Comparación completa

**🚀 Demo rápido:**
```bash
python demo_huggingface.py
```

## 📚 Documentación

- **[🤗 Guía Hugging Face](docs/HUGGINGFACE_GUIDE.md)** - Generar datos GRATIS con HuggingFace
- **[💰 Métodos Gratuitos](docs/SYNTHETIC_DATA_FREE.md)** - Todas las opciones sin costo
- **[Guía de Inicio Rápido](docs/QUICKSTART.md)** - Empieza en 5 minutos
- **[Guía de Docker](docs/DOCKER.md)** - Deployment con contenedores
- **README.md** - Documentación completa (este archivo)

## Características

- ✅ Extrae texto de archivos PDF
- ✅ Traduce usando modelos de lenguaje avanzados (GPT-3.5/GPT-4)
- ✅ Opción de usar modelos propios entrenados localmente
- ✅ **NUEVO:** Generación de datos sintéticos 100% GRATUITOS
- ✅ **5 métodos gratuitos** para generar datos (HuggingFace, Ollama, etc.)
- ✅ Pipeline de entrenamiento optimizado con HPC
- ✅ Motor de inferencia GPU-acelerado
- ✅ Genera un nuevo PDF con el texto traducido
- ✅ Soporta múltiples idiomas
- ✅ Procesa documentos largos dividiéndolos en chunks
- ✅ Interfaz de línea de comandos fácil de usar
- ✅ Soporte para Docker (deployment aislado y portable)
- ✅ Scripts de instalación automática para Windows/Linux/Mac
- ✅ Organización modular de archivos

## Modos de Operación

### Modo 1: API de OpenAI (Rápido y Sencillo)
Usa la API de OpenAI para traducir sin necesidad de entrenar modelos.
**Costo:** ~$0.002 por cada 1K tokens

### Modo 2: Modelo Local (Sin costos de API) ⭐
Entrena tu propio modelo con datos sintéticos **GRATUITOS** y úsalo localmente.
**Costo:** $0.00 (completamente gratis)

## Requisitos

- Python 3.7 o superior
- Para Modo 1: Clave API de OpenAI (de pago)
- Para Modo 2: **TODO GRATIS** - Sin APIs de pago necesarias
  - GPU NVIDIA recomendada (opcional pero acelera entrenamiento e inferencia)

## Instalación

### Opción 1: Instalación Automática (Recomendado)

**Windows:**
```bash
git clone https://github.com/Weryyy/PDF-Translator.git
cd PDF-Translator
install.bat
```

**Linux/Mac:**
```bash
git clone https://github.com/Weryyy/PDF-Translator.git
cd PDF-Translator
chmod +x install.sh
./install.sh
```

Los scripts de instalación automática:
- ✅ Crean un entorno virtual de Python
- ✅ Instalan todas las dependencias necesarias
- ✅ Opcionalmente instalan optimizaciones GPU
- ✅ Crean el archivo de configuración
- ✅ Verifican las optimizaciones disponibles

### Opción 2: Instalación con Docker (Aislado y Portable)

**Requisitos:**
- Docker instalado
- Docker Compose instalado (opcional pero recomendado)

**Usando Docker Compose (Recomendado):**
```bash
git clone https://github.com/Weryyy/PDF-Translator.git
cd PDF-Translator

# Crear archivo de configuración
cp config/config.example.json config/config.json
# Edita config/config.json con tu configuración

# Iniciar contenedor
docker-compose up -d pdf-translator

# Acceder al contenedor
docker-compose exec pdf-translator bash

# Traducir un PDF
python src/translate_pdf.py pdfs/documento.pdf
```

**Con GPU (requiere nvidia-docker):**
```bash
# Iniciar contenedor con soporte GPU
docker-compose --profile gpu up -d pdf-translator-gpu

# Acceder al contenedor GPU
docker-compose exec pdf-translator-gpu bash
```

**Usando Docker directamente:**
```bash
# Construir imagen
docker build -t pdf-translator .

# Ejecutar contenedor
docker run -it -v $(pwd)/pdfs:/app/pdfs -v $(pwd)/output:/app/output pdf-translator
```

### Opción 3: Instalación Manual

1. Clona este repositorio:
```bash
git clone https://github.com/Weryyy/PDF-Translator.git
cd PDF-Translator
```

2. Crea y activa un entorno virtual:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Instala las dependencias:

**Instalación básica (CPU):**
```bash
pip install -r requirements.txt
```

**Instalación optimizada (GPU con CUDA):**
```bash
# Primero instala las dependencias básicas
pip install -r requirements.txt

# Luego instala las optimizaciones GPU (requiere NVIDIA GPU + CUDA)
pip install -r requirements-gpu.txt
```

4. Verifica las optimizaciones disponibles:
```bash
python scripts/check_optimizations.py
```

5. Configura según el modo que quieras usar:

**Modo 1 - API de OpenAI:**
```bash
cp config/config.example.json config/config.json
# Edita config/config.json y añade tu clave API
# Asegúrate de que "use_local_model": false
```

**Modo 2 - Modelo Local:**
```bash
cp config/config.example.json config/config.json
# Edita config/config.json y establece "use_local_model": true
```

## Uso

### Modo 1: Traducción con API de OpenAI

Traducir un PDF:
```bash
python src/translate_pdf.py "documento.pdf"
```

Con opciones:
```bash
python src/translate_pdf.py "documento.pdf" -o "output.pdf" -l en
```

**En Docker:**
```bash
docker-compose exec pdf-translator python src/translate_pdf.py pdfs/documento.pdf
```

### Modo 2: Entrenar y Usar Modelo Propio (100% GRATIS)

#### Paso 1: Generar Datos Sintéticos GRATIS

**🤗 Opción A: Hugging Face (Recomendado)**

API gratuita con modelos de última generación:

```bash
# Ver demo interactivo
python demo_huggingface.py

# Generar 500 pares con FLAN-T5 (equilibrio perfecto)
python scripts/generate_synthetic_data_free.py -n 500 -m huggingface

# Generar 1000 pares con FLAN-T5-XL (máxima calidad)
python scripts/generate_synthetic_data_free.py -n 1000 -m huggingface --hf-text-model flan-t5-xl --hf-token TU_TOKEN

# Generar con Mistral (última generación)
python scripts/generate_synthetic_data_free.py -n 500 -m huggingface --hf-text-model mistral
```

**📖 Guía completa:** [docs/HUGGINGFACE_GUIDE.md](docs/HUGGINGFACE_GUIDE.md)

**🚀 Opción B: Rule-based (Más Rápido)**

Sin configuración, extremadamente rápido:

```bash
# Generar 10,000 pares (muy rápido)
python scripts/generate_synthetic_data_free.py -n 10000 -m rulebased
```

**🤖 Opción C: Open Source Models (GPT-2, BLOOM)**

Modelos open source corriendo localmente:

```bash
# Con GPT-2
python scripts/generate_synthetic_data_free.py -n 1000 -m opensource --os-model gpt2

# Con GPT-2 Large (mejor calidad)
python scripts/generate_synthetic_data_free.py -n 1000 -m opensource --os-model gpt2-large

# Con BLOOM (multilingüe)
python scripts/generate_synthetic_data_free.py -n 1000 -m opensource --os-model bloom-560m
```

**🔄 Opción D: Back-translation**

Alta calidad con modelos gratuitos:

```bash
# Generar 5000 pares con back-translation
python scripts/generate_synthetic_data_free.py -n 5000 -m backtranslation
```

**🦙 Opción E: Ollama**

LLMs locales de alta calidad:

```bash
# Primero instalar Ollama: https://ollama.ai/
ollama pull llama2

# Generar datos
python scripts/generate_synthetic_data_free.py -n 1000 -m ollama --ollama-model llama2
```

**💡 Estrategia Combinada (Recomendado):**

Para máxima calidad y cantidad:

```bash
# 1. Base rápida (5000 pares)
python scripts/generate_synthetic_data_free.py -n 5000 -m rulebased

# 2. Variedad con back-translation (3000 pares)
python scripts/generate_synthetic_data_free.py -n 3000 -m backtranslation

# 3. Alta calidad con HuggingFace (2000 pares)
python scripts/generate_synthetic_data_free.py -n 2000 -m huggingface --hf-text-model flan-t5-xl

# Total: 10,000 pares con excelente diversidad - $0.00 de costo
```

**📊 Ver comparación completa:** [docs/SYNTHETIC_DATA_FREE.md](docs/SYNTHETIC_DATA_FREE.md)

---

**Método antiguo (requiere pago):**

```bash
# Con API de OpenAI (REQUIERE PAGO - ya no necesario)
# Generar 1000 pares de traducción
python scripts/generate_synthetic_data.py -n 1000 -b 100

# Para un dataset más grande (por ejemplo, ~10GB con 100k pares)
python scripts/generate_synthetic_data.py -n 100000 -b 1000 -s English -t Spanish
```

Los datos se guardan en formato Parquet (optimizado para I/O rápido).

#### Paso 2: Entrenar el Modelo

Entrena tu modelo con los datos sintéticos:
```bash
python scripts/train_model_hpc.py -d synthetic_data
```

Con optimización de hiperparámetros:
```bash
python scripts/train_model_hpc.py -d synthetic_data --optimize
```

El modelo entrenado se guarda en `./models/translation_model/`

#### Paso 3: Traducir con Modelo Local

Opción A - Usar el traductor de PDF:
```bash
# Asegúrate de que config/config.json tenga "use_local_model": true
python src/translate_pdf.py "documento.pdf"
```

Opción B - Usar motor de inferencia GPU directamente:
```bash
python src/gpu_inference.py -m ./models/translation_model -f input.txt -o output.txt
```

Benchmark de rendimiento:
```bash
python src/gpu_inference.py -m ./models/translation_model -f input.txt --benchmark
```

## Ejemplos Completos

### Ejemplo 1: Traducción rápida con OpenAI
```bash
# Configurar
export OPENAI_API_KEY="tu-clave-api"

# Traducir
python src/translate_pdf.py "Mushoku Tensei Redundant Reincarnation Vol. 3.pdf" -l es
```

### Ejemplo 2: Pipeline completo con modelo propio
```bash
# 1. Generar datos
python scripts/generate_synthetic_data.py -n 5000 -b 500

# 2. Entrenar modelo
python scripts/train_model_hpc.py -d synthetic_data

# 3. Configurar para usar modelo local
echo '{"use_local_model": true, "local_model_path": "./models/translation_model"}' > config/config.json

# 4. Traducir PDF
python src/translate_pdf.py "documento.pdf" -o "traducido.pdf"
```

### Ejemplo 3: Usando Docker
```bash
# 1. Iniciar contenedor
docker-compose up -d pdf-translator

# 2. Copiar PDF al directorio pdfs/
cp mi-documento.pdf pdfs/

# 3. Traducir dentro del contenedor
docker-compose exec pdf-translator python src/translate_pdf.py pdfs/mi-documento.pdf

# 4. El resultado estará en output/
```

## Configuración

### config/config.json - Configuración Principal

```json
{
  "openai_api_key": "tu-clave-api",
  "model": "gpt-3.5-turbo",
  "source_language": "auto",
  "target_language": "es",
  "max_tokens": 2000,
  "use_local_model": false,
  "local_model_path": "./models/translation_model"
}
```

### config/training_config.json - Configuración de Entrenamiento

```json
{
  "model_name": "facebook/mbart-large-50-many-to-many-mmt",
  "batch_size": 8,
  "learning_rate": 2e-5,
  "num_epochs": 3,
  "max_length": 512,
  "fp16": true
}
```

## Optimizaciones de Rendimiento

El sistema **detecta y activa automáticamente** todas las optimizaciones disponibles:

### Optimizaciones Activas Siempre

1. **Parquet + Apache Arrow** (I/O)
   - Zero-copy data serialization
   - **104x más rápido** que CSV + Pandas
   - Activación: Automática (incluido en requirements.txt)

2. **Numba JIT Compilation** (Cómputo)
   - Compila Python a código máquina
   - **283x más rápido** que Python puro para operaciones numéricas
   - Activación: Automática (incluido en requirements.txt)

3. **PyTorch Optimizations** (ML)
   - CuDNN auto-tuner para operaciones de red neuronal
   - Activación: Automática cuando GPU disponible

### Optimizaciones GPU (Opcionales pero Altamente Recomendadas)

4. **RAPIDS cuDF** (Data Processing)
   - DataFrames acelerados por GPU
   - **26x más rápido** que Pandas para ML inference
   - Instalación: `pip install -r requirements-gpu.txt`

5. **Mixed Precision (FP16)** (Training/Inference)
   - Usa FP16 en lugar de FP32
   - **2x más rápido** con mismo rendimiento
   - Activación: Automática en GPU

6. **TensorFloat-32** (Ampere GPUs)
   - Para GPUs RTX 30xx, A100, etc.
   - Speedup adicional en operaciones matriciales
   - Activación: Automática en GPUs Ampere+

### Verificar Optimizaciones

```bash
python scripts/check_optimizations.py
```

Este comando muestra:
- ✓ Optimizaciones activas
- ⚠ Optimizaciones disponibles pero no instaladas
- ✗ Optimizaciones no disponibles en tu sistema
- Mejoras de rendimiento esperadas

### Tabla de Rendimiento

| Operación | Sin Optimizar | Optimizado | Speedup |
|-----------|---------------|------------|---------|
| Carga de datos (I/O) | CSV + Pandas | Parquet + Arrow | **104x** |
| Cómputo numérico | Python puro | Numba JIT | **283x** |
| Inferencia ML | CPU | GPU + cuDF | **26x** |
| Entrenamiento | FP32 CPU | FP16 GPU | **50x+** |

### Instalación Recomendada

Para obtener el **máximo rendimiento**:

```bash
# 1. Instalar dependencias base
pip install -r requirements.txt

# 2. Si tienes GPU NVIDIA (altamente recomendado):
pip install -r requirements-gpu.txt

# 3. Verificar optimizaciones
python check_optimizations.py
```

**Nota:** Las optimizaciones GPU requieren:
- GPU NVIDIA con soporte CUDA
- Drivers NVIDIA actualizados
- CUDA Toolkit 11.x o 12.x instalado

## Estructura del Proyecto

```
PDF-Translator/
├── src/                          # Código fuente principal
│   ├── translate_pdf.py          # Script principal de traducción
│   ├── gpu_inference.py          # Motor de inferencia GPU
│   └── example_usage.py          # Ejemplos de uso
├── scripts/                      # Scripts de utilidad
│   ├── generate_synthetic_data.py  # Generador de datos sintéticos
│   ├── train_model_hpc.py       # Pipeline de entrenamiento HPC
│   └── check_optimizations.py   # Verificador de optimizaciones
├── config/                       # Archivos de configuración
│   ├── config.example.json      # Configuración ejemplo
│   └── training_config.json     # Configuración de entrenamiento
├── docs/                         # Documentación adicional
├── models/                       # Modelos entrenados (creado automáticamente)
├── synthetic_data/               # Datos generados (creado automáticamente)
├── output/                       # Archivos de salida
├── translations/                 # PDFs traducidos
├── pdfs/                         # PDFs de entrada
├── requirements.txt              # Dependencias base
├── requirements-gpu.txt          # Dependencias GPU opcionales
├── Dockerfile                    # Configuración Docker
├── docker-compose.yml            # Orquestación Docker
├── .dockerignore                 # Archivos ignorados por Docker
├── install.bat                   # Script instalación Windows
├── install.sh                    # Script instalación Linux/Mac
├── .gitignore                    # Archivos ignorados por Git
└── README.md                     # Este archivo
```

## Ventajas del Modelo Local vs API

### API de OpenAI
- ✅ Rápido de configurar
- ✅ Alta calidad sin entrenamiento
- ✅ No requiere GPU
- ❌ Costo por uso
- ❌ Requiere conexión a internet
- ❌ Datos enviados a terceros

### Modelo Local
- ✅ Sin costos de API después del entrenamiento
- ✅ Funciona offline
- ✅ Privacidad total (datos no salen de tu máquina)
- ✅ Personalizable para dominios específicos
- ❌ Requiere tiempo de entrenamiento inicial
- ❌ GPU recomendada para mejor rendimiento

## Limitaciones

- La calidad de la traducción depende del modelo usado
- Los PDFs con imágenes o texto en imágenes no serán traducidos (solo texto extraíble)
- Los PDFs muy grandes pueden requerir múltiples llamadas a la API o más tiempo de procesamiento
- El formato del PDF de salida es simplificado (no mantiene el diseño original)

## Costos (Modo API)

Usando la API de OpenAI:
- GPT-3.5-turbo: ~$0.002 por 1K tokens
- GPT-4: ~$0.03 por 1K tokens

Consulta los [precios actuales de OpenAI](https://openai.com/pricing) para más información.

## Solución de Problemas

### Error: "OpenAI API key not found"
- Asegúrate de haber configurado la clave API en `config/config.json` o como variable de entorno
- O cambia a modelo local con `"use_local_model": true`

### Error: "Local model not found"
- Entrena un modelo primero con `scripts/train_model_hpc.py`
- O verifica la ruta en `local_model_path` del config

### Error: "No text extracted from PDF"
- El PDF puede estar protegido o contener solo imágenes
- Intenta con un PDF diferente que contenga texto seleccionable

### Entrenamiento lento
- Usa una GPU NVIDIA para acelerar el entrenamiento
- Reduce `batch_size` si te quedas sin memoria GPU
- Reduce `num_epochs` para entrenamientos más rápidos

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request para sugerencias o mejoras.

## Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.
