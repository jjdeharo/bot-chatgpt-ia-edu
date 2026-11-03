# 26. Texto completo de los PDF nuevos de la Biblioteca digital

Fecha: 2026-11-03 · Estado: aceptado

## Contexto

El Diario de IA Educativa dedica un artículo a cada documento que entra en la Biblioteca
digital (ADR 0006 del diario). Su documentalista lee el documento en la fuente oficial, pero en
la primera prueba (03-11-2026) no pudo con dos guías de la Generalitat de Catalunya: no aparecían
en ninguna web oficial con ese título. El bot ya descargaba cada PDF para sacar el texto de las
cuatro primeras páginas (`pdfs.py`), y lo borraba después.

## Decisión

- De los PDF de la Biblioteca que entran desde el 1 de octubre de 2026 (`COMPLETO_DESDE`),
  `pdfs.py` guarda además el texto entero en `datos/<grupo>/pdf-completo/<id>.txt`, hasta
  400.000 caracteres. El PDF se sigue borrando.
- No se indexa: el buscador sigue con las cuatro primeras páginas, como hasta ahora.
- No se recupera lo anterior a octubre, para no volver a descargar toda la biblioteca.

## Consecuencias

- Una descarga más por cada PDF de octubre ya leído (dos) y ninguna más para los nuevos, que
  ya se descargaban.
- Unos cientos de kilobytes por documento en el NAS; se puede rehacer desde el grupo.
