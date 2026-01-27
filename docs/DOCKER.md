# Docker Deployment Guide

Esta guía te ayudará a desplegar PDF Translator usando Docker en cualquier sistema.

## Requisitos Previos

- Docker instalado (versión 20.10 o superior)
- Docker Compose instalado (opcional pero recomendado)
- Para GPU: NVIDIA Docker Runtime (`nvidia-docker2`)

## Instalación de Docker

### Windows
1. Descarga Docker Desktop desde: https://www.docker.com/products/docker-desktop
2. Instala y reinicia tu computadora
3. Verifica la instalación: `docker --version`

### Linux (Ubuntu/Debian)
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt-get install docker-compose

# Agregar tu usuario al grupo docker (para no usar sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verificar instalación
docker --version
docker-compose --version
```

### macOS
1. Descarga Docker Desktop desde: https://www.docker.com/products/docker-desktop
2. Instala arrastrando a la carpeta Aplicaciones
3. Verifica la instalación: `docker --version`

## Configuración Inicial

### 1. Clonar el repositorio
```bash
git clone https://github.com/Weryyy/PDF-Translator.git
cd PDF-Translator
```

### 2. Crear archivo de configuración
```bash
cp config/config.example.json config/config.json
```

Edita `config/config.json` y añade tu clave API de OpenAI o configura para usar modelo local:
```json
{
  "openai_api_key": "tu-clave-api-aqui",
  "model": "gpt-3.5-turbo",
  "target_language": "es",
  "use_local_model": false
}
```

### 3. Crear directorios necesarios
```bash
mkdir -p pdfs output translations models synthetic_data
```

## Uso con Docker Compose (Recomendado)

### Opción 1: Contenedor CPU (Sin GPU)

```bash
# Iniciar el contenedor en segundo plano
docker-compose up -d pdf-translator

# Ver logs
docker-compose logs -f pdf-translator

# Acceder al contenedor
docker-compose exec pdf-translator bash

# Dentro del contenedor, traducir un PDF
python src/translate_pdf.py pdfs/documento.pdf

# Detener el contenedor
docker-compose down
```

### Opción 2: Contenedor GPU (Con NVIDIA GPU)

**Requisitos adicionales:**
- GPU NVIDIA con drivers actualizados
- NVIDIA Container Toolkit instalado

```bash
# Instalar NVIDIA Container Toolkit (Ubuntu/Debian)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Iniciar contenedor con soporte GPU
docker-compose --profile gpu up -d pdf-translator-gpu

# Acceder al contenedor GPU
docker-compose exec pdf-translator-gpu bash

# Verificar que la GPU está disponible
nvidia-smi

# Traducir usando GPU
python src/translate_pdf.py pdfs/documento.pdf
```

## Uso con Docker Directo (Sin Compose)

### Construir la imagen

```bash
# Imagen CPU
docker build -t pdf-translator --target base .

# Imagen GPU
docker build -t pdf-translator-gpu --target gpu .
```

### Ejecutar contenedor

```bash
# Contenedor CPU interactivo
docker run -it \
  -v $(pwd)/pdfs:/app/pdfs \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/translations:/app/translations \
  -v $(pwd)/config/config.json:/app/config/config.json:ro \
  -e OPENAI_API_KEY="tu-api-key" \
  pdf-translator bash

# Contenedor GPU interactivo
docker run -it --gpus all \
  -v $(pwd)/pdfs:/app/pdfs \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/translations:/app/translations \
  -v $(pwd)/config/config.json:/app/config/config.json:ro \
  -e OPENAI_API_KEY="tu-api-key" \
  pdf-translator-gpu bash
```

### Ejecutar traducción directamente

```bash
# Traducir un PDF sin entrar al contenedor
docker run --rm \
  -v $(pwd)/pdfs:/app/pdfs \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config/config.json:/app/config/config.json:ro \
  pdf-translator \
  python src/translate_pdf.py pdfs/documento.pdf
```

## Ejemplos Prácticos

### Ejemplo 1: Traducir un PDF
```bash
# 1. Copiar tu PDF al directorio pdfs/
cp mi-documento.pdf pdfs/

# 2. Iniciar contenedor
docker-compose up -d pdf-translator

# 3. Traducir
docker-compose exec pdf-translator python src/translate_pdf.py pdfs/mi-documento.pdf

# 4. El resultado estará en output/
ls -la output/
```

### Ejemplo 2: Entrenar modelo propio
```bash
# 1. Iniciar contenedor GPU (si tienes GPU)
docker-compose --profile gpu up -d pdf-translator-gpu

# 2. Acceder al contenedor
docker-compose exec pdf-translator-gpu bash

# 3. Generar datos sintéticos
python scripts/generate_synthetic_data.py -n 1000 -b 100

# 4. Entrenar modelo
python scripts/train_model_hpc.py -d synthetic_data

# 5. El modelo estará en models/ (persistente gracias al volumen)
```

### Ejemplo 3: Procesamiento por lotes
```bash
# Script para traducir múltiples PDFs
docker-compose up -d pdf-translator

for pdf in pdfs/*.pdf; do
  echo "Traduciendo: $pdf"
  docker-compose exec pdf-translator python src/translate_pdf.py "$pdf"
done

docker-compose down
```

## Gestión de Volúmenes

Los volúmenes en Docker permiten que los datos persistan:

```yaml
volumes:
  - ./models:/app/models          # Modelos entrenados
  - ./synthetic_data:/app/synthetic_data  # Datos de entrenamiento
  - ./output:/app/output          # PDFs traducidos
  - ./translations:/app/translations  # Traducciones
  - ./pdfs:/app/pdfs             # PDFs de entrada
```

Esto significa que:
- Los modelos que entrenes persisten entre reinicios
- Los PDFs traducidos quedan en tu sistema host
- Puedes agregar PDFs al directorio `pdfs/` y estarán disponibles en el contenedor

## Variables de Entorno

Puedes configurar el contenedor con variables de entorno:

```bash
# Crear archivo .env
cat > .env << EOF
OPENAI_API_KEY=tu-clave-api-aqui
PYTHONPATH=/app
EOF

# Docker Compose usará automáticamente el archivo .env
docker-compose up -d
```

## Solución de Problemas

### Error: "Cannot connect to Docker daemon"
```bash
# Linux: Asegúrate de que el servicio Docker esté corriendo
sudo systemctl start docker
sudo systemctl enable docker

# Verifica tu usuario está en el grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### Error: "Permission denied" al acceder a volúmenes
```bash
# Linux: Cambiar permisos de los directorios
chmod -R 755 pdfs/ output/ translations/ models/ synthetic_data/
```

### Error: "NVIDIA driver not found" (GPU)
```bash
# Verifica que los drivers NVIDIA estén instalados
nvidia-smi

# Reinstala nvidia-docker si es necesario
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### El contenedor se queda sin memoria
```bash
# Aumentar memoria asignada a Docker (Docker Desktop)
# Settings > Resources > Memory > Aumentar a 8GB o más

# O limitar el uso de memoria en docker-compose.yml:
services:
  pdf-translator:
    mem_limit: 4g
```

### Limpiar contenedores e imágenes antiguas
```bash
# Detener todos los contenedores
docker-compose down

# Eliminar contenedores detenidos
docker container prune

# Eliminar imágenes no usadas
docker image prune -a

# Limpiar todo (cuidado, elimina todos los contenedores e imágenes)
docker system prune -a
```

## Ventajas de Usar Docker

✅ **Portabilidad**: Funciona igual en Windows, Linux y Mac
✅ **Aislamiento**: No afecta tu sistema host
✅ **Reproducibilidad**: Mismo entorno en todos los sistemas
✅ **Fácil limpieza**: Elimina el contenedor y listo
✅ **Múltiples versiones**: Puedes tener diferentes versiones en paralelo
✅ **Sin conflictos**: No hay conflictos con otras instalaciones de Python

## Recursos Adicionales

- [Documentación oficial de Docker](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)

## Próximos Pasos

1. **Optimizar imagen**: Considera usar imágenes multi-stage para reducir tamaño
2. **CI/CD**: Integra con GitHub Actions para builds automáticos
3. **Docker Hub**: Publica tu imagen en Docker Hub para distribución fácil
4. **Kubernetes**: Para producción a gran escala, considera Kubernetes

## Preguntas Frecuentes

**¿Necesito Docker para usar PDF Translator?**
No, Docker es opcional. Puedes instalar directamente usando `install.bat` o `install.sh`.

**¿El contenedor es más lento que la instalación nativa?**
El overhead es mínimo (< 5%). Para la mayoría de usos, no notarás diferencia.

**¿Puedo usar GPU dentro del contenedor?**
Sí, usa el perfil GPU y asegúrate de tener nvidia-docker instalado.

**¿Los datos quedan en el contenedor?**
No, los volúmenes guardan los datos en tu sistema host, no dentro del contenedor.
