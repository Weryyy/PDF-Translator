# PDF Translator

Un traductor de PDFs personal que utiliza modelos de lenguaje (OpenAI GPT) para traducir documentos PDF a diferentes idiomas.

## Características

- ✅ Extrae texto de archivos PDF
- ✅ Traduce usando modelos de lenguaje avanzados (GPT-3.5/GPT-4)
- ✅ Genera un nuevo PDF con el texto traducido
- ✅ Soporta múltiples idiomas
- ✅ Procesa documentos largos dividiéndolos en chunks
- ✅ Interfaz de línea de comandos fácil de usar

## Requisitos

- Python 3.7 o superior
- Una clave API de OpenAI

## Instalación

1. Clona este repositorio:
```bash
git clone https://github.com/Weryyy/PDF-Translator.git
cd PDF-Translator
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura tu clave API de OpenAI:

Opción A - Usando archivo de configuración:
```bash
cp config.example.json config.json
# Edita config.json y añade tu clave API
```

Opción B - Usando variable de entorno:
```bash
export OPENAI_API_KEY="tu-clave-api-aqui"
```

## Uso

### Uso básico

Traducir un PDF (usa la configuración por defecto - español):
```bash
python translate_pdf.py "documento.pdf"
```

### Opciones avanzadas

Especificar archivo de salida:
```bash
python translate_pdf.py "documento.pdf" -o "documento_traducido.pdf"
```

Especificar idioma de destino:
```bash
python translate_pdf.py "documento.pdf" -l en  # Traducir a inglés
python translate_pdf.py "documento.pdf" -l es  # Traducir a español
python translate_pdf.py "documento.pdf" -l fr  # Traducir a francés
```

Usar un archivo de configuración personalizado:
```bash
python translate_pdf.py "documento.pdf" -c mi_config.json
```

### Ejemplo completo

```bash
python translate_pdf.py "Mushoku Tensei Redundant Reincarnation Vol. 3.pdf" -o "output.pdf" -l es
```

## Configuración

El archivo `config.json` permite personalizar el comportamiento del traductor:

```json
{
  "openai_api_key": "tu-clave-api",
  "model": "gpt-3.5-turbo",
  "source_language": "auto",
  "target_language": "es",
  "max_tokens": 2000
}
```

- `openai_api_key`: Tu clave API de OpenAI
- `model`: Modelo a usar (gpt-3.5-turbo, gpt-4, etc.)
- `source_language`: Idioma de origen (auto para detección automática)
- `target_language`: Idioma de destino por defecto
- `max_tokens`: Número máximo de tokens por solicitud

## Estructura del Proyecto

```
PDF-Translator/
├── translate_pdf.py           # Script principal de traducción
├── requirements.txt           # Dependencias de Python
├── config.example.json        # Ejemplo de configuración
├── config.json               # Tu configuración (no versionada)
├── .gitignore               # Archivos ignorados por git
└── README.md                # Este archivo
```

## Limitaciones

- La calidad de la traducción depende del modelo de lenguaje utilizado
- Los PDFs con imágenes o texto en imágenes no serán traducidos (solo texto extraíble)
- Los PDFs muy grandes pueden requerir múltiples llamadas a la API
- El formato del PDF de salida es simplificado (no mantiene el diseño original)

## Costos

Este proyecto usa la API de OpenAI, que tiene costos asociados:
- GPT-3.5-turbo: ~$0.002 por 1K tokens
- GPT-4: ~$0.03 por 1K tokens

Consulta los [precios actuales de OpenAI](https://openai.com/pricing) para más información.

## Solución de Problemas

### Error: "OpenAI API key not found"
- Asegúrate de haber configurado la clave API en `config.json` o como variable de entorno

### Error: "No text extracted from PDF"
- El PDF puede estar protegido o contener solo imágenes
- Intenta con un PDF diferente que contenga texto seleccionable

### Error de instalación de dependencias
- Asegúrate de tener Python 3.7 o superior
- Intenta actualizar pip: `pip install --upgrade pip`

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request para sugerencias o mejoras.

## Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.
