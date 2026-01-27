# 🤗 Guía Completa de Hugging Face para Datos Sintéticos

## ¿Qué es Hugging Face?

Hugging Face es la plataforma líder de código abierto para modelos de IA. Ofrece:

- ✅ **100% GRATUITO** - No requiere tarjeta de crédito
- ✅ **Miles de modelos** - Acceso a GPT, BLOOM, T5, etc.
- ✅ **API gratuita** - Inference API sin costo
- ✅ **Comunidad activa** - Millones de usuarios
- ✅ **Fácil de usar** - Sin instalación local necesaria

## 🚀 Inicio Rápido (5 minutos)

### Paso 1: Crear Cuenta Gratuita

1. Ve a https://huggingface.co/join
2. Regístrate con email (gratis, sin tarjeta)
3. Confirma tu email

### Paso 2: Obtener Token Gratuito

1. Ve a https://huggingface.co/settings/tokens
2. Click en "New token"
3. Dale un nombre (ej: "pdf-translator")
4. Selecciona "read" (suficiente para usar API)
5. Click en "Generate"
6. Copia tu token

### Paso 3: Configurar Token

**Linux/Mac:**
```bash
export HUGGINGFACE_TOKEN="tu_token_aqui"
```

**Windows CMD:**
```cmd
set HUGGINGFACE_TOKEN=tu_token_aqui
```

**Windows PowerShell:**
```powershell
$env:HUGGINGFACE_TOKEN="tu_token_aqui"
```

**Alternativa - Pasar directamente:**
```bash
python scripts/generate_synthetic_data_free.py -n 100 -m huggingface --hf-token tu_token_aqui
```

### Paso 4: Generar Datos

```bash
# Generar 100 pares (prueba inicial)
python scripts/generate_synthetic_data_free.py -n 100 -m huggingface

# Generar 1000 pares
python scripts/generate_synthetic_data_free.py -n 1000 -m huggingface -b 50
```

¡Listo! Ya estás generando datos sintéticos gratis con Hugging Face 🎉

---

## 📊 Modelos Disponibles

### Modelos de Generación de Texto

Puedes elegir diferentes modelos según tus necesidades:

#### 1. FLAN-T5 (Recomendado) ⭐

**Modelo:** `google/flan-t5-large`

- ✅ Excelente calidad para instrucciones
- ✅ Rápido y eficiente
- ✅ Buen equilibrio calidad/velocidad
- ✅ Gratis en Hugging Face

```bash
python scripts/generate_synthetic_data_free.py -n 500 -m huggingface --hf-text-model flan-t5
```

#### 2. FLAN-T5-XL (Mejor Calidad) ⭐⭐⭐

**Modelo:** `google/flan-t5-xl`

- ✅ Mejor calidad que FLAN-T5
- ✅ Excelente para textos complejos
- ⚠️ Más lento (puede tardar más)
- ✅ Gratis en Hugging Face

```bash
python scripts/generate_synthetic_data_free.py -n 500 -m huggingface --hf-text-model flan-t5-xl
```

#### 3. Mistral-7B (Alta Calidad)

**Modelo:** `mistralai/Mistral-7B-Instruct-v0.1`

- ✅ Calidad excelente
- ✅ Modelo de última generación
- ⚠️ Más lento debido a tamaño
- ✅ Gratis en Hugging Face

```bash
python scripts/generate_synthetic_data_free.py -n 300 -m huggingface --hf-text-model mistral
```

#### 4. BLOOM (Multilingüe)

**Modelo:** `bigscience/bloom-560m`

- ✅ Diseñado para múltiples idiomas
- ✅ Buena calidad
- ✅ Velocidad media
- ✅ Gratis en Hugging Face

```bash
python scripts/generate_synthetic_data_free.py -n 500 -m huggingface --hf-text-model bloom
```

#### 5. GPT-2 / GPT-2-Large

**Modelos:** `gpt2`, `gpt2-large`

- ✅ Modelo clásico de OpenAI (open source)
- ✅ Buena calidad general
- ✅ Muy rápido
- ✅ Gratis en Hugging Face

```bash
python scripts/generate_synthetic_data_free.py -n 500 -m huggingface --hf-text-model gpt2-large
```

### Modelos de Traducción

Los modelos de traducción Helsinki-NLP son usados automáticamente:

- **Inglés → Español:** `Helsinki-NLP/opus-mt-en-es`
- **Inglés → Francés:** `Helsinki-NLP/opus-mt-en-fr`
- **Inglés → Alemán:** `Helsinki-NLP/opus-mt-en-de`
- **Inglés → Italiano:** `Helsinki-NLP/opus-mt-en-it`
- **Y más...**

Todos estos modelos son **100% gratuitos** en Hugging Face.

---

## ⚙️ Configuración Avanzada

### Ejemplo Completo con Todas las Opciones

```bash
python scripts/generate_synthetic_data_free.py \
  -n 1000 \
  -b 50 \
  -m huggingface \
  --hf-token TU_TOKEN \
  --hf-text-model flan-t5-xl \
  -s English \
  -t Spanish
```

### Parámetros Explicados

- `-n 1000`: Generar 1000 pares de traducción
- `-b 50`: Procesar en lotes de 50 (reduce rate limits)
- `-m huggingface`: Usar método de Hugging Face
- `--hf-token`: Tu token de API (opcional pero recomendado)
- `--hf-text-model`: Modelo específico a usar
- `-s English`: Idioma fuente
- `-t Spanish`: Idioma objetivo

---

## 📈 Límites y Rate Limits

### Sin Token (Anónimo)

- ⚠️ ~30 requests/hora
- ⚠️ Prioridad baja en cola
- ⚠️ Puede ser más lento

**Recomendación:** Usa lotes pequeños (`-b 10`)

```bash
python scripts/generate_synthetic_data_free.py -n 100 -m huggingface -b 10
```

### Con Token Gratuito ⭐

- ✅ ~1000 requests/hora
- ✅ Prioridad media en cola
- ✅ Velocidad razonable

**Recomendación:** Usa lotes medianos (`-b 50`)

```bash
python scripts/generate_synthetic_data_free.py -n 1000 -m huggingface -b 50 --hf-token TU_TOKEN
```

### Estrategias para Maximizar Uso Gratuito

#### 1. Generar en Sesiones

En lugar de generar todo de una vez:

```bash
# Sesión 1: 500 pares
python scripts/generate_synthetic_data_free.py -n 500 -m huggingface

# Esperar 1 hora...

# Sesión 2: 500 pares más
python scripts/generate_synthetic_data_free.py -n 500 -m huggingface

# Total: 1000 pares gratis
```

#### 2. Combinar con Otros Métodos

```bash
# 80% con métodos rápidos y gratuitos
python scripts/generate_synthetic_data_free.py -n 4000 -m rulebased
python scripts/generate_synthetic_data_free.py -n 4000 -m backtranslation

# 20% con HuggingFace (máxima calidad)
python scripts/generate_synthetic_data_free.py -n 2000 -m huggingface --hf-text-model flan-t5-xl

# Total: 10,000 pares con buena calidad y variedad
```

#### 3. Usar Batch Size Óptimo

```bash
# Batch pequeño si tienes rate limits
python scripts/generate_synthetic_data_free.py -n 500 -m huggingface -b 25

# Batch mediano con token
python scripts/generate_synthetic_data_free.py -n 1000 -m huggingface -b 50 --hf-token TOKEN
```

---

## 🔍 Comparación: HuggingFace vs Otros Métodos

| Aspecto | HuggingFace | Ollama | Rule-based | Back-translation |
|---------|-------------|--------|------------|------------------|
| **Costo** | $0 | $0 | $0 | $0 |
| **Calidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Velocidad** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Setup** | Fácil | Medio | Muy fácil | Fácil |
| **Internet** | Sí | No* | No* | No* |
| **Límites** | ~1k/hr | Ilimitado | Ilimitado | Ilimitado |
| **Variedad** | Alta | Alta | Media | Alta |

\* Después de instalación inicial

### ¿Cuándo Usar HuggingFace?

**✅ Usa HuggingFace si:**
- Quieres alta calidad sin instalar nada localmente
- Tienes buena conexión a internet
- No tienes hardware potente
- Necesitas diversidad en los datos
- Quieres probar rápidamente sin setup

**❌ No uses HuggingFace si:**
- Necesitas generar >5,000 pares de una vez
- No tienes internet estable
- Prefieres trabajar 100% offline
- Ya tienes Ollama instalado (usa Ollama entonces)

---

## 💡 Casos de Uso y Ejemplos

### Caso 1: Proyecto Pequeño (1,000 pares)

```bash
# Generar todo con HuggingFace (alta calidad)
python scripts/generate_synthetic_data_free.py -n 1000 -m huggingface --hf-text-model flan-t5-xl
```

### Caso 2: Proyecto Mediano (10,000 pares)

```bash
# Estrategia mixta
python scripts/generate_synthetic_data_free.py -n 5000 -m rulebased
python scripts/generate_synthetic_data_free.py -n 3000 -m backtranslation
python scripts/generate_synthetic_data_free.py -n 2000 -m huggingface --hf-text-model flan-t5-xl
```

### Caso 3: Dataset de Alta Calidad (5,000 pares)

```bash
# Solo HuggingFace con mejor modelo
# Generar en 5 sesiones de 1000 pares
for i in {1..5}; do
    python scripts/generate_synthetic_data_free.py -n 1000 -m huggingface --hf-text-model flan-t5-xl -b 50
    echo "Sesión $i completada. Esperando 60 minutos..."
    sleep 3600
done
```

### Caso 4: Probar Diferentes Modelos

```bash
# Probar cada modelo (100 pares cada uno)
python scripts/generate_synthetic_data_free.py -n 100 -m huggingface --hf-text-model flan-t5
python scripts/generate_synthetic_data_free.py -n 100 -m huggingface --hf-text-model flan-t5-xl
python scripts/generate_synthetic_data_free.py -n 100 -m huggingface --hf-text-model mistral
python scripts/generate_synthetic_data_free.py -n 100 -m huggingface --hf-text-model bloom
python scripts/generate_synthetic_data_free.py -n 100 -m huggingface --hf-text-model gpt2-large

# Después entrenar y ver cuál da mejor calidad
```

---

## 🛠️ Troubleshooting

### Error: "Model is currently loading"

**Causa:** El modelo se está cargando en los servidores de HF (primera vez)

**Solución:** El script espera automáticamente 20 segundos y reintenta. Es normal.

```
⏳ Modelo cargándose... (primera vez puede tardar ~20 segundos)
```

### Error: "Rate limit exceeded"

**Causa:** Has alcanzado el límite de requests por hora

**Soluciones:**
1. Espera 60 minutos y continúa
2. Obtén un token gratuito (más límites)
3. Reduce batch size: `-b 25`
4. Usa otro método temporalmente

```bash
# Mientras esperas, usa rule-based
python scripts/generate_synthetic_data_free.py -n 1000 -m rulebased
```

### Generación Muy Lenta

**Causas posibles:**
- Alta demanda en HuggingFace
- Modelo grande (mistral, flan-t5-xl)
- Sin token (prioridad baja)

**Soluciones:**
1. Usar modelo más rápido: `--hf-text-model flan-t5`
2. Obtener token gratuito
3. Generar en horas de menos demanda
4. Usar lotes más pequeños: `-b 25`

### Error de Conexión

**Soluciones:**
1. Verificar conexión a internet
2. Verificar que HuggingFace está accesible: https://huggingface.co/
3. Intentar de nuevo (fallos temporales son normales)

---

## 📚 Recursos Adicionales

### Links Útiles

- **Registro gratuito:** https://huggingface.co/join
- **Obtener token:** https://huggingface.co/settings/tokens
- **Modelos disponibles:** https://huggingface.co/models
- **Documentación API:** https://huggingface.co/docs/api-inference/
- **Comunidad:** https://discuss.huggingface.co/

### Modelos Recomendados

Explora más modelos en:
- https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads
- https://huggingface.co/models?pipeline_tag=translation&sort=downloads

### Tutoriales

- [Cómo usar la Inference API](https://huggingface.co/docs/api-inference/quicktour)
- [Guía de tokens](https://huggingface.co/docs/hub/security-tokens)

---

## ❓ Preguntas Frecuentes

### ¿Es realmente gratis?

**Sí, 100% gratis.** Hugging Face ofrece:
- Inference API gratuita
- Miles de modelos open source
- Sin necesidad de tarjeta de crédito
- Sin límite de tiempo

Existe un tier "Pro" de pago ($9/mes) con más límites, pero **no es necesario** para generar datos sintéticos.

### ¿Necesito tarjeta de crédito?

**No.** La cuenta gratuita no requiere ningún método de pago.

### ¿Cuántos datos puedo generar gratis?

Con token gratuito: ~1,000 pares/hora

**Por día:** ~10,000-20,000 pares
**Por mes:** ~300,000-600,000 pares

Más que suficiente para la mayoría de proyectos.

### ¿Es legal usar HuggingFace para esto?

**Sí, completamente legal.** Los modelos en HuggingFace son:
- Open source
- Disponibles para uso comercial (la mayoría)
- Provistos específicamente para casos como este

### ¿Puedo usar esto en un proyecto comercial?

**Sí**, la mayoría de modelos permiten uso comercial. Verifica la licencia específica del modelo en su página de HuggingFace.

### ¿Qué tan buena es la calidad?

**Muy buena.** Los modelos como FLAN-T5-XL y Mistral producen texto de calidad comparable o superior a GPT-3.5.

### ¿Puedo cambiar de idiomas?

**Sí.** HuggingFace tiene modelos de traducción para muchos pares de idiomas:
- Inglés ↔ Español, Francés, Alemán, Italiano, Portugués, Ruso, Chino, Japonés, etc.

```bash
python scripts/generate_synthetic_data_free.py -n 500 -m huggingface -s English -t French
```

---

## 🎯 Mejores Prácticas

### 1. Usa Token Siempre

Obtén tu token gratuito para mejores límites:
```bash
export HUGGINGFACE_TOKEN="tu_token"
```

### 2. Empieza Pequeño

Primero genera 100 pares para probar:
```bash
python scripts/generate_synthetic_data_free.py -n 100 -m huggingface
```

### 3. Elige el Modelo Correcto

- **Velocidad:** `flan-t5` o `gpt2`
- **Calidad:** `flan-t5-xl` o `mistral`
- **Multilingüe:** `bloom`

### 4. Combina Métodos

Para máxima eficiencia y calidad:
```bash
# Base rápida
python scripts/generate_synthetic_data_free.py -n 5000 -m rulebased

# Calidad añadida
python scripts/generate_synthetic_data_free.py -n 2000 -m huggingface --hf-text-model flan-t5-xl
```

### 5. Monitorea el Progreso

El script muestra progreso en tiempo real:
```
Generating batch 0 with 50 pairs using huggingface...
  Progress: 10/50 pairs...
  Progress: 20/50 pairs...
```

---

## 🚀 Conclusión

Hugging Face es una **excelente opción gratuita** para generar datos sintéticos:

✅ **Ventajas:**
- 100% gratuito
- Alta calidad
- Fácil de usar
- Sin instalación local
- Muchos modelos disponibles

⚠️ **Consideraciones:**
- Límites de rate (manejables)
- Requiere internet
- Puede ser más lento en horas pico

**Recomendación Final:**
Usa HuggingFace para datasets de hasta ~5,000 pares o combínalo con otros métodos para datasets más grandes.

---

## 📞 Soporte

¿Problemas o preguntas?
- Revisa la sección de Troubleshooting arriba
- Consulta la documentación en el README.md
- Abre un issue en GitHub

¡Feliz generación de datos sintéticos! 🎉
