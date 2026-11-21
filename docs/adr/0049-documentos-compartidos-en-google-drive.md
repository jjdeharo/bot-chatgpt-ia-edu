# 49. Documentos compartidos en Google Drive

Fecha: 2026-11-21 · Estado: aceptado

## Contexto

Las autoras del «Manual urgente sobre IA en el aula» lo difunden con un enlace de Google Drive (`drive.google.com/file/d/ID/view`). Al recibirlo, la Biblioteca digital contestó que no encontraba ningún documento. Esa página solo carga el visor de Drive, hecho con JavaScript, y no trae ningún enlace al archivo que se pueda seguir. Es una forma frecuente de compartir documentos en los grupos.

## Decisión

- Un enlace de un archivo de Drive (`/file/d/ID`, `/open?id=ID` o `/uc?id=ID`) se descarga por su dirección de descarga directa, `https://drive.google.com/uc?export=download&id=ID`. La ficha conserva el enlace que mandó la persona, que es el que usará quien la lea.
- Las carpetas de Drive y las direcciones que no son de Drive siguen el camino habitual.

## Evidencia y validación

- Caso original: `buscar` sobre `https://drive.google.com/file/d/1kMOM3IDQrEkbb_qY0R3QtHdZJPXXnagS/view` descarga el PDF, de 20 páginas y 7,5 MB, y devuelve `pdf` con el enlace de la vista.
- `pruebas/test_documento_web.py` comprueba las cuatro formas del enlace y las que se rechazan (una carpeta, otro dominio y una dirección sin https). Comprueba también que la ficha lleva el enlace mandado.

## Riesgos

- Para archivos de más de unos 100 MB, Drive pide confirmar la descarga y devuelve una página en lugar del archivo. No afecta a la Biblioteca, que acepta como mucho 50 MB, el límite de Telegram para un bot.
- Un archivo de Drive que no esté compartido con cualquiera que tenga el enlace no se descarga. Entonces el bot responde como con cualquier web que no deja descargar.
