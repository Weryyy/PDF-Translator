# Guía de Inicio Rápido

Esta guía te ayudará a empezar a usar PDF Translator en menos de 5 minutos.

## 🚀 Instalación Rápida

### Opción 1: Instalación Automática (Más Fácil)

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
./install.sh
```

El script automáticamente:
- ✅ Crea un entorno virtual
- ✅ Instala todas las dependencias
- ✅ Te pregunta si quieres optimizaciones GPU
- ✅ Crea el archivo de configuración

### Opción 2: Docker (Más Portable)

```bash
git clone https://github.com/Weryyy/PDF-Translator.git
cd PDF-Translator
cp config/config.example.json config/config.json
# Edita config/config.json con tu API key
docker-compose up -d pdf-translator
```

## 🔑 Configuración

### Obtener API Key de OpenAI

1. Ve a: https://platform.openai.com/api-keys
2. Crea una nueva API key
3. Cópiala

### Configurar PDF Translator

Edita `config/config.json`:
```json
{
  "openai_api_key": "sk-tu-api-key-aqui",
  "model": "gpt-3.5-turbo",
  "target_language": "es",
  "use_local_model": false
}
```

O usa variable de entorno (Linux/Mac):
```bash
export OPENAI_API_KEY="sk-tu-api-key-aqui"
```

Windows:
```cmd
set OPENAI_API_KEY=sk-tu-api-key-aqui
```

## 📝 Uso Básico

### Traducir un PDF

**Instalación Local:**
```bash
# Activar entorno virtual (si lo creaste)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Traducir
python src/translate_pdf.py mi-documento.pdf
```

**Con Docker:**
```bash
# Copiar PDF al directorio pdfs/
cp mi-documento.pdf pdfs/

# Traducir
docker-compose exec pdf-translator python src/translate_pdf.py pdfs/mi-documento.pdf
```

### Opciones de Traducción

```bash
# Especificar idioma de destino
python src/translate_pdf.py documento.pdf -l en  # Inglés
python src/translate_pdf.py documento.pdf -l fr  # Francés
python src/translate_pdf.py documento.pdf -l de  # Alemán

# Especificar archivo de salida
python src/translate_pdf.py documento.pdf -o traducido.pdf

# Todo junto
python src/translate_pdf.py documento.pdf -o salida.pdf -l en
```

## 🎯 Idiomas Soportados

| Código | Idioma |
|--------|---------|
| `es` | Español |
| `en` | Inglés |
| `fr` | Francés |
| `de` | Alemán |
| `it` | Italiano |
| `pt` | Portugués |
| `ja` | Japonés |
| `ko` | Coreano |
| `zh` | Chino |
| `ru` | Ruso |

## 📊 Modos de Operación

### Modo 1: API de OpenAI (Recomendado para empezar)

**Ventajas:**
- ✅ Configuración rápida (5 minutos)
- ✅ Alta calidad de traducción
- ✅ Sin necesidad de GPU

**Desventajas:**
- ❌ Requiere API key (costo por uso)
- ❌ Necesita internet

**Costo aproximado:**
- GPT-3.5-turbo: ~$0.002 por 1,000 tokens (~750 palabras)
- GPT-4: ~$0.03 por 1,000 tokens

**Ejemplo:** Un PDF de 50 páginas (~10,000 palabras) cuesta ~$0.03 con GPT-3.5

### Modo 2: Modelo Local (Avanzado)

**Ventajas:**
- ✅ Sin costos de API después del entrenamiento
- ✅ Funciona offline
- ✅ Privacidad total

**Desventajas:**
- ❌ Requiere tiempo de configuración inicial
- ❌ GPU recomendada para mejor rendimiento

Ver [Guía de Entrenamiento](TRAINING.md) para más detalles.

## 🔍 Verificar Instalación

```bash
# Verificar optimizaciones instaladas
python scripts/check_optimizations.py

# Ver ayuda del traductor
python src/translate_pdf.py --help

# Ver versión de Python
python --version  # Debe ser 3.7+
```

## 📂 Estructura de Directorios

```
PDF-Translator/
├── pdfs/          # 📁 Coloca aquí tus PDFs para traducir
├── output/        # 📤 PDFs traducidos aparecen aquí
├── src/           # 💻 Código fuente
├── scripts/       # 🛠️ Scripts de utilidad
├── config/        # ⚙️ Archivos de configuración
└── docs/          # 📚 Documentación
```

## 🐛 Problemas Comunes

### "OpenAI API key not found"

**Solución:**
```bash
# Opción 1: Variable de entorno
export OPENAI_API_KEY="sk-tu-key"

# Opción 2: Editar config/config.json
nano config/config.json  # Linux/Mac
notepad config\config.json  # Windows
```

### "No text extracted from PDF"

**Causas posibles:**
- PDF protegido con contraseña
- PDF de solo imágenes (sin texto seleccionable)
- PDF corrupto

**Solución:**
- Intenta con otro PDF
- Usa un PDF con texto seleccionable
- Para PDFs de imágenes, necesitarás OCR (próximamente)

### "Module not found"

**Solución:**
```bash
# Asegúrate de estar en el entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Traducción muy lenta

**Soluciones:**
- Usa un modelo más rápido: `"model": "gpt-3.5-turbo"` en config
- Reduce el tamaño del chunk
- Considera instalar optimizaciones GPU

## 💡 Consejos y Trucos

### 1. Traducción por Lotes

```bash
# Linux/Mac
for pdf in pdfs/*.pdf; do
    python src/translate_pdf.py "$pdf"
done

# Windows (PowerShell)
Get-ChildItem pdfs\*.pdf | ForEach-Object {
    python src\translate_pdf.py $_.FullName
}
```

### 2. Monitorear Costos de API

```bash
# Ver uso en: https://platform.openai.com/usage
# Tip: Usa GPT-3.5-turbo para ahorrar (20x más barato que GPT-4)
```

### 3. Mejorar Calidad

En `config/config.json`:
```json
{
  "model": "gpt-4",  // Mejor calidad pero más caro
  "max_tokens": 4000  // Más contexto
}
```

### 4. Acelerar Procesamiento

```bash
# Instalar optimizaciones GPU (si tienes NVIDIA GPU)
pip install -r requirements-gpu.txt

# Verificar mejoras
python scripts/check_optimizations.py
```

## 📚 Próximos Pasos

1. **Lee la documentación completa:** [README.md](../README.md)
2. **Aprende sobre Docker:** [DOCKER.md](DOCKER.md)
3. **Entrena tu modelo:** [TRAINING.md](TRAINING.md) (próximamente)
4. **Contribuye al proyecto:** [CONTRIBUTING.md](CONTRIBUTING.md) (próximamente)

## 🆘 Obtener Ayuda

- **Issues en GitHub:** https://github.com/Weryyy/PDF-Translator/issues
- **Discusiones:** https://github.com/Weryyy/PDF-Translator/discussions
- **README principal:** [README.md](../README.md)

## 🎉 Listo para Empezar

Ya estás listo para traducir PDFs. ¡Disfruta!

```bash
# Tu primer traducción
python src/translate_pdf.py mi-primer-documento.pdf
```

---

**¿Preguntas?** Abre un [issue](https://github.com/Weryyy/PDF-Translator/issues) o consulta la documentación completa.
