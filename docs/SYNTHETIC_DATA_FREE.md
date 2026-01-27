# Generación de Datos Sintéticos GRATUITOS

Este documento describe las diferentes formas de generar datos sintéticos **SIN COSTO** para entrenar tu modelo de traducción, evitando el uso de APIs de pago como OpenAI.

## 🎯 Soluciones Gratuitas Disponibles

### 1. Ollama (Recomendado) ⭐

**LLMs locales completamente gratuitos y sin límites**

- ✅ **Costo:** $0.00 (100% gratis)
- ✅ **Calidad:** Excelente (similar a GPT-3.5)
- ✅ **Velocidad:** Rápida (depende de tu hardware)
- ✅ **Límites:** Sin límites de uso
- ✅ **Privacidad:** Total (todo local)
- ✅ **Internet:** No requiere conexión después de la instalación

**Instalación:**

```bash
# 1. Instalar Ollama desde https://ollama.ai/
# Windows: Descargar instalador
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# 2. Descargar un modelo (solo una vez)
ollama pull llama2        # 3.8GB - Modelo general
# o
ollama pull mistral       # 4.1GB - Alternativa excelente
# o
ollama pull codellama     # 3.8GB - Para contenido técnico

# 3. Iniciar Ollama
ollama serve
```

**Uso:**

```bash
# Generar 1000 pares de traducción
python scripts/generate_synthetic_data_free.py -n 1000 -m ollama --ollama-model llama2

# Para un dataset grande (10,000 pares)
python scripts/generate_synthetic_data_free.py -n 10000 -m ollama --ollama-model mistral -b 500
```

**Modelos disponibles:**
- `llama2` - Modelo general de Meta (recomendado)
- `mistral` - Excelente calidad
- `codellama` - Para contenido técnico
- `llama2:13b` - Mejor calidad, requiere más RAM
- Ver más en: https://ollama.ai/library

---

### 2. Rule-Based (Más Rápido) 🚀

**Generación basada en plantillas, completamente offline**

- ✅ **Costo:** $0.00 (100% gratis)
- ✅ **Calidad:** Buena (para datasets grandes)
- ✅ **Velocidad:** Muy rápida (miles por minuto)
- ✅ **Límites:** Sin límites
- ✅ **Privacidad:** Total
- ✅ **Internet:** No requiere
- ⚠️ **Nota:** Menos variedad que LLMs, pero excelente para cantidad

**Uso:**

```bash
# Sin configuración previa necesaria
python scripts/generate_synthetic_data_free.py -n 10000 -m rulebased

# Ideal para datasets muy grandes
python scripts/generate_synthetic_data_free.py -n 100000 -m rulebased -b 1000
```

**Ventajas:**
- No requiere instalación adicional
- Extremadamente rápido
- Perfecto para generar grandes volúmenes de datos
- Usa modelos de traducción gratuitos de Hugging Face

---

### 3. Back-Translation (Buena Calidad) 🔄

**Técnica de back-translation con modelos gratuitos**

- ✅ **Costo:** $0.00 (100% gratis)
- ✅ **Calidad:** Muy buena
- ✅ **Velocidad:** Media
- ✅ **Límites:** Sin límites
- ✅ **Privacidad:** Total (todo local)
- ✅ **Internet:** Solo para primera descarga de modelos

**Cómo funciona:**
1. Toma oraciones base en inglés
2. Las traduce al español
3. Las traduce de vuelta al inglés (creando variación)
4. Usa ambas versiones como par de entrenamiento

**Uso:**

```bash
# Primera vez: descarga modelos automáticamente (~1GB)
python scripts/generate_synthetic_data_free.py -n 5000 -m backtranslation

# Generar más datos
python scripts/generate_synthetic_data_free.py -n 20000 -m backtranslation -b 500
```

---

### 4. Hugging Face (Recomendado para Calidad) 🤗

**API gratuita con excelentes modelos de IA**

- ✅ **Costo:** $0.00 (tier gratuito, sin tarjeta)
- ✅ **Calidad:** Excelente (comparable a GPT-3.5/4)
- ✅ **Variedad:** Múltiples modelos disponibles
- ⚠️ **Velocidad:** Media (rate limits manejables)
- ⚠️ **Límites:** ~1000 requests/hora con token
- ⚠️ **Internet:** Requiere conexión

**📖 Ver guía completa:** [HUGGINGFACE_GUIDE.md](HUGGINGFACE_GUIDE.md)

**Configuración rápida:**

```bash
# 1. Crear cuenta gratuita en https://huggingface.co/join (¡sin tarjeta!)
# 2. Obtener token GRATIS: https://huggingface.co/settings/tokens
# 3. Exportar token
export HUGGINGFACE_TOKEN="tu_token_aqui"
```

**Modelos disponibles:**
- `flan-t5` - Excelente equilibrio (recomendado)
- `flan-t5-xl` - Máxima calidad
- `mistral` - Última generación
- `bloom` - Multilingüe
- `gpt2`, `gpt2-large` - Clásico de OpenAI (open source)

**Uso:**

```bash
# Básico con FLAN-T5 (recomendado)
python scripts/generate_synthetic_data_free.py -n 500 -m huggingface

# Con modelo específico
python scripts/generate_synthetic_data_free.py -n 500 -m huggingface --hf-text-model flan-t5-xl

# Con token para más límites
python scripts/generate_synthetic_data_free.py -n 1000 -m huggingface --hf-token TU_TOKEN
```

---

### 5. Open Source Models (GPT-2, BLOOM, etc.) 🆓

**Modelos open source ejecutándose localmente**

- ✅ **Costo:** $0.00 (100% gratis)
- ✅ **Calidad:** Buena a excelente (según modelo)
- ✅ **Velocidad:** Media (depende de hardware)
- ✅ **Límites:** Sin límites
- ✅ **Privacidad:** Total (todo local)
- ✅ **Internet:** Solo para primera descarga

**Modelos disponibles:**
- `gpt2` - GPT-2 de OpenAI (open source)
- `gpt2-medium`, `gpt2-large` - Versiones más grandes
- `bloom-560m`, `bloom-1b7` - BLOOM multilingüe
- `distilgpt2` - Versión compacta y rápida

**Uso:**

```bash
# Con GPT-2 (recomendado para empezar)
python scripts/generate_synthetic_data_free.py -n 1000 -m opensource --os-model gpt2

# Con GPT-2 Large (mejor calidad)
python scripts/generate_synthetic_data_free.py -n 1000 -m opensource --os-model gpt2-large

# Con BLOOM (multilingüe)
python scripts/generate_synthetic_data_free.py -n 1000 -m opensource --os-model bloom-560m
```

---

## 📊 Comparación de Métodos

| Método | Costo | Calidad | Velocidad | Límites | Setup | Internet |
|--------|-------|---------|-----------|---------|-------|----------|
| **HuggingFace** 🤗 | $0 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ~1k/hr | ⭐⭐⭐⭐⭐ | Sí |
| **Ollama** | $0 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ∞ | ⭐⭐⭐ | No* |
| **Open Source** | $0 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ∞ | ⭐⭐⭐⭐ | No* |
| **Rule-based** | $0 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ∞ | ⭐⭐⭐⭐⭐ | No* |
| **Back-translation** | $0 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ∞ | ⭐⭐⭐⭐ | No* |
| *OpenAI* | *$$* | *⭐⭐⭐⭐⭐* | *⭐⭐⭐⭐⭐* | *Pago* | *Fácil* | *Sí* |

\* Después de la instalación inicial

---

## 🎯 Recomendaciones por Caso de Uso

### Para la Mejor Calidad:
```bash
# Usa Ollama con Mistral
python scripts/generate_synthetic_data_free.py -n 10000 -m ollama --ollama-model mistral
```

### Para la Mayor Velocidad:
```bash
# Usa rule-based
python scripts/generate_synthetic_data_free.py -n 100000 -m rulebased -b 1000
```

### Para Equilibrio (Calidad/Velocidad):
```bash
# Usa back-translation
python scripts/generate_synthetic_data_free.py -n 20000 -m backtranslation -b 500
```

### Para Probar Sin Instalar Nada:
```bash
# Usa rule-based (incluido por defecto)
python scripts/generate_synthetic_data_free.py -n 1000 -m rulebased
```

---

## 💡 Estrategia Combinada (Recomendado)

Para obtener el mejor dataset, **combina varios métodos**:

```bash
# 1. Generar base grande con rule-based (rápido)
python scripts/generate_synthetic_data_free.py -n 50000 -m rulebased -b 1000

# 2. Agregar datos de calidad con back-translation
python scripts/generate_synthetic_data_free.py -n 20000 -m backtranslation -b 500

# 3. Agregar datos variados con Ollama
python scripts/generate_synthetic_data_free.py -n 10000 -m ollama --ollama-model llama2

# 4. Combinar todos los archivos Parquet en synthetic_data/
# El script de entrenamiento los usará todos automáticamente
```

Resultado: **80,000 pares de traducción con diversidad y calidad, $0.00 de costo**

---

## 🔧 Instalación de Dependencias

Todas las dependencias están incluidas en `requirements.txt`:

```bash
pip install -r requirements.txt
```

Para back-translation (modelos de traducción):
```bash
# Ya incluido en requirements.txt
pip install transformers sentencepiece
```

---

## 📝 Ejemplos Completos

### Ejemplo 1: Pipeline Completo con Ollama

```bash
# 1. Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Descargar modelo
ollama pull llama2

# 3. Iniciar Ollama (en otra terminal)
ollama serve

# 4. Generar datos
python scripts/generate_synthetic_data_free.py -n 5000 -m ollama --ollama-model llama2

# 5. Entrenar modelo
python scripts/train_model_hpc.py -d synthetic_data

# 6. Traducir PDF
python src/translate_pdf.py "documento.pdf"
```

### Ejemplo 2: Pipeline Rápido con Rule-Based

```bash
# 1. Generar datos (sin configuración previa)
python scripts/generate_synthetic_data_free.py -n 20000 -m rulebased

# 2. Entrenar modelo
python scripts/train_model_hpc.py -d synthetic_data

# 3. Traducir PDF
python src/translate_pdf.py "documento.pdf"
```

### Ejemplo 3: Dataset Mixto de Alta Calidad

```bash
# Generar datos con múltiples métodos
python scripts/generate_synthetic_data_free.py -n 30000 -m rulebased
python scripts/generate_synthetic_data_free.py -n 10000 -m backtranslation
python scripts/generate_synthetic_data_free.py -n 5000 -m ollama --ollama-model mistral

# Entrenar con todos los datos (se combinan automáticamente)
python scripts/train_model_hpc.py -d synthetic_data

# El modelo entrenará con 45,000 pares de traducción
```

---

## ❓ Preguntas Frecuentes

### ¿Cuál método debo usar?

- **Tienes buena CPU/RAM?** → Ollama (mejor calidad)
- **Quieres rapidez?** → Rule-based (más rápido)
- **Quieres equilibrio?** → Back-translation
- **Sin hardware potente?** → Rule-based o HuggingFace

### ¿Cuántos datos necesito?

- **Mínimo:** 1,000 pares (pruebas)
- **Recomendado:** 10,000 - 50,000 pares
- **Óptimo:** 100,000+ pares (mejor calidad de traducción)

### ¿Los datos son de buena calidad?

- **Ollama:** Calidad comparable a GPT-3.5
- **Back-translation:** Muy buena calidad, variación natural
- **Rule-based:** Buena calidad, menos variación
- **HuggingFace:** Excelente calidad, limitado por rate limits

### ¿Puedo combinar métodos?

**¡Sí!** De hecho, es recomendado. Usar múltiples métodos crea un dataset más diverso y robusto.

### ¿Necesito GPU?

- **Para generar datos:** No requerida (pero Ollama es más rápido con buena CPU)
- **Para entrenar:** GPU recomendada (pero no requerida)

### ¿Cuánto espacio en disco necesito?

- **1,000 pares:** ~1-2 MB
- **10,000 pares:** ~10-20 MB
- **100,000 pares:** ~100-200 MB
- **Modelos de Ollama:** 3-7 GB (descarga una sola vez)

---

## 🆘 Solución de Problemas

### Ollama: "Connection refused"

```bash
# Asegúrate de que Ollama está corriendo
ollama serve

# O en Windows: abrir Ollama app
```

### "Translation model not found"

```bash
# Instalar transformers
pip install transformers sentencepiece
```

### "Out of memory"

```bash
# Reducir batch size
python scripts/generate_synthetic_data_free.py -n 1000 -b 50

# O usar rule-based (menos memoria)
python scripts/generate_synthetic_data_free.py -n 10000 -m rulebased
```

### Generación muy lenta

```bash
# Usa rule-based para velocidad
python scripts/generate_synthetic_data_free.py -n 10000 -m rulebased

# O reduce el tamaño del batch
python scripts/generate_synthetic_data_free.py -n 1000 -b 50
```

---

## 📚 Recursos Adicionales

- **Ollama:** https://ollama.ai/
- **Modelos Ollama:** https://ollama.ai/library
- **Hugging Face:** https://huggingface.co/
- **MarianMT:** https://huggingface.co/Helsinki-NLP
- **Documentación del proyecto:** README.md

---

## 💰 Comparación de Costos

| Método | 10k pares | 100k pares | 1M pares |
|--------|-----------|------------|----------|
| OpenAI GPT-3.5 | ~$2-5 | ~$20-50 | ~$200-500 |
| OpenAI GPT-4 | ~$30-60 | ~$300-600 | ~$3000-6000 |
| **Ollama** | **$0** | **$0** | **$0** |
| **Rule-based** | **$0** | **$0** | **$0** |
| **Back-translation** | **$0** | **$0** | **$0** |
| **HuggingFace** | **$0** | **$0** | **$0** |

---

## ✅ Conclusión

Ya no necesitas pagar por APIs para generar datos sintéticos. Con estas soluciones gratuitas puedes:

1. ✅ Generar datos ilimitados sin costo
2. ✅ Mantener privacidad total (todo local)
3. ✅ Trabajar offline (después de setup inicial)
4. ✅ Obtener calidad comparable o superior
5. ✅ Escalar sin preocuparte por costos

**Comienza ahora:**

```bash
# Opción más fácil (sin setup)
python scripts/generate_synthetic_data_free.py -n 1000 -m rulebased

# Opción mejor calidad (con Ollama)
ollama pull llama2
python scripts/generate_synthetic_data_free.py -n 1000 -m ollama
```

¡Empieza a generar tus datos sintéticos gratis ahora! 🚀
