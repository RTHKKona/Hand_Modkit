
# Hand_Modkit

Hand_Modkit, tambien conocido como Handburger Modkit, es una herramienta versátil para modding en Monster Hunter Generations Ultimate (MHGU). Con un conjunto de utilidades
especializadas, esta herramienta ayuda a los modders a editar, analizar y manejar varios archivos del juego facilmente. Ya sea que estes incoporando encabezados de audio, calculando propiedades de audio u organizando las carpetas de mods, Hand_Modkit simplifica las complejas tareas involucradas en el MHGU modding.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/L3L711AIP8)

## Características

- **Herramienta de edición STQ**: Editar y ver archivos STQ/STQR, incluyendo analisis de patrones hex y edición hexadecimal específica.
- **Insertor de encabezado Opus**: Modificar encabezados Opus e inserta ya editados en archivos Opus audio sin encabezado.
- **Calculadora de audio**: Calcular las propiedades del audio como el bitrate, tamaño de archivo y duración.
- **Creador de carpetas**:  Crear carpetas y directorios para tus propios proyectos.
- **Codificador/Descodificador Hex**: Codificar o descodificar datos hexadecimales, útil para conversiones y análisis de archivos.
- **Conversor a NSOpus**: Convertir archivos de audio a formato Opus o viceversa, con soporte para el formato .Opus de Nintendo Switch para MHGU.
- **Extractor de metadatos Opus**: Extraer metadatos de los archivos Opus para un manejo y edicion mas facíl.


## Primeros pasos

### Requisitos previos

- **Python 3.x**: Asegurese de que esta instalado Python en su dispositivo. Lo puede descargar [aquí](https://www.python.org/downloads/).
- **PyQt5**: Instalar PyQt5, la libreria utilizada por la GUI. Lo puede instalar via pip:
  \`\`\`bash
  pip install PyQt5
  \`\`\`

### Instalación

1. Clona el repositorio:
   \`\`\`bash
   git clone https://github.com/RTHKKona/Hand_Modkit.git
   \`\`\`
2. Navega hacia el directorio del proyecto:
   \`\`\`bash
   cd Hand_Modkit
   \`\`\`
3. Abre el archivo Hb_Modkit.py o cualquier script de Python independiente en /scripts/

## Futuras funcionalidades

Estoy trabajando para mejorar Hand_Modkit y expandir sus capacidades. Aquí hay un vistazo de lo que va a haber en actualizaciones futuras:

- Gestor de conflictos STQR: Arregla conflictos multi-mod de los archivos stqr.
- Convertidor de Audio a MCA: Una heramienta para convertir varios formatos de audio directamente a MCA, simplificando el proceso de modding del audio.
- Insertor/Editor de Encabezado MCA:Una herramienta avanzada para insetar y editar encabezados en archivos MCA, permitiendo un control mas detallado sobre las modificaciones de audio.
- Compatibilidad con Kuriimu2: Integración con Kuriimu2, incluyendo soporte para archivos .dll, abriendo archivos .arc y editando archivos .tex. Esto ayudará a la versatilidad de Hand_Modkit y parmitirá la edición perfecta de los recursos del juego.
- Compilar en un Exe completo: El objetivo es compilar Hand_Modkit en un ejecutable independiente, haciendolo mas fácil para distribuír y usar sin la necesidad de tener un entorno Python.
- Mejor GUI para un uso más sencillo: Estamos trabajando en perfeccionar la interfaz gráfica del usuario para hacerlo mas intuitivo y amigable, asegurando que hasta los nuevos usuarios pueden navegar y usar la herramienta efectivamente.

Esten pendientes de estas actualizaciones!

# Contribuciones

Contribuciones son bienvenidas! Si tenes alguna idea sobre mejoras, sientete libre de crear un fork del repositorio, realiza tus cambios y publica una pull request.

## Contribuidores
<a href="https://github.com/RTHKKona/Hand_Modkit/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=RTHKKona/Hand_Modkit" />
</a>

### Reportes de bugs y solicitud de funciones

Por favor usa [issue tracker](https://github.com/RTHKKona/Hand_Modkit/issues) para reportar bugs o solicitar nuevas funciones.

## Ayudas

Si le pareció útil la herramienta y le gustaría ayudar en el desarollo, considera apoyarme con una pequeña contribución ;D!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/L3L711AIP8)

## Licencia

Este proyecto esta protegido por una licencia del MIT - revisar el archivo [LICENSE](LICENSE) para más detalles.
