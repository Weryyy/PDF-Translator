# Deployment Guide - PDF Translator

Este documento resume las opciones de instalación y deployment para PDF Translator.

## 🎯 Opciones de Deployment

### 1. Instalación Local con Scripts Automáticos ⚡ (Recomendado para inicio)

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
./install.sh
```

**Pros:**
- ✅ Instalación completamente automática
- ✅ Crea entorno virtual aislado
- ✅ Instala todas las dependencias
- ✅ Detecta y configura GPU si está disponible

**Contras:**
- ❌ Requiere Python instalado en el sistema

---

### 2. Docker (CPU) 🐳 (Recomendado para portabilidad)

```bash
docker-compose up -d pdf-translator
```

**Pros:**
- ✅ No requiere Python en el sistema host
- ✅ Funciona igual en Windows, Linux y Mac
- ✅ Entorno completamente aislado
- ✅ Fácil de limpiar y reinstalar

**Contras:**
- ❌ Requiere Docker instalado
- ❌ Overhead mínimo de contenedor (~5%)

---

### 3. Docker GPU 🚀 (Recomendado para producción con GPU)

```bash
docker-compose --profile gpu up -d pdf-translator-gpu
```

**Pros:**
- ✅ Aprovecha aceleración GPU
- ✅ Entrenamiento de modelos hasta 50x más rápido
- ✅ Inferencia acelerada
- ✅ Portable entre sistemas con GPU NVIDIA

**Contras:**
- ❌ Requiere GPU NVIDIA + nvidia-docker
- ❌ Configuración más compleja

---

### 4. Instalación Manual 🔧 (Para usuarios avanzados)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Pros:**
- ✅ Control total del proceso
- ✅ Personalizable

**Contras:**
- ❌ Más pasos manuales
- ❌ Propenso a errores

---

## 📊 Comparación de Opciones

| Característica | Scripts Auto | Docker CPU | Docker GPU | Manual |
|----------------|--------------|------------|------------|--------|
| Facilidad | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Portabilidad | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Rendimiento | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Aislamiento | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Requisitos | Python | Docker | Docker+GPU | Python |

---

## 🎯 ¿Cuál Elegir?

### Para Usuarios Nuevos
👉 **Usa Scripts Automáticos** (`install.bat` o `install.sh`)
- Más rápido para empezar
- Menor curva de aprendizaje

### Para Desarrollo/Testing
👉 **Usa Docker CPU** (`docker-compose up -d`)
- Entorno limpio y reproducible
- Fácil de resetear

### Para Producción
👉 **Usa Docker GPU** (si tienes GPU) o **Scripts Automáticos con GPU**
- Máximo rendimiento
- Escalable

### Para CI/CD
👉 **Usa Docker**
- Reproducibilidad garantizada
- Integración fácil con pipelines

---

## 🚀 Quick Start por Método

### Scripts Automáticos

```bash
# 1. Clonar repo
git clone https://github.com/Weryyy/PDF-Translator.git
cd PDF-Translator

# 2. Ejecutar instalador
./install.sh  # o install.bat en Windows

# 3. Configurar
nano config/config.json  # Añadir API key

# 4. ¡Listo!
python src/translate_pdf.py documento.pdf
```

### Docker

```bash
# 1. Clonar repo
git clone https://github.com/Weryyy/PDF-Translator.git
cd PDF-Translator

# 2. Configurar
cp config/config.example.json config/config.json
nano config/config.json  # Añadir API key

# 3. Iniciar
docker-compose up -d

# 4. Usar
docker-compose exec pdf-translator python src/translate_pdf.py pdfs/documento.pdf
```

---

## 📚 Documentación Adicional

- **[Guía de Inicio Rápido](docs/QUICKSTART.md)** - Tutorial de 5 minutos
- **[Guía Docker Detallada](docs/DOCKER.md)** - Todo sobre Docker
- **[README Principal](README.md)** - Documentación completa

---

## 💡 Consejos

1. **Primera vez:** Usa scripts automáticos
2. **Múltiples entornos:** Usa Docker
3. **GPU disponible:** Instala optimizaciones GPU
4. **Producción:** Docker GPU o scripts con GPU
5. **Desarrollo:** Lo que prefieras, ambos funcionan bien

---

## 🆘 Soporte

¿Problemas? Consulta:
- [Guía de Solución de Problemas](docs/QUICKSTART.md#-problemas-comunes)
- [Issues en GitHub](https://github.com/Weryyy/PDF-Translator/issues)
