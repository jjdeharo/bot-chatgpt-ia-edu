# 50. Revisión manual de lo que la Biblioteca digital no acepta

Fecha: 2026-11-21 · Estado: aceptado

## Contexto

El tema de la Biblioteca digital está cerrado a los miembros (ADR 0047): un documento que el bot no acepta ya no se puede publicar de otra forma. El mismo día, el bot rechazó por error el «Manual urgente sobre IA en el aula» dos veces, como repetido y como no compartible (ADR 0048). Juanjo pidió que quien manda un documento pueda pedir que lo revise él: «así nadie se queda con las ganas de publicar si realmente se puede». El repositorio de Vibe Coding Educativo ya tenía una revisión parecida (ADR 0004).

## Decisión

- **Cuándo se ofrece.** Cuando el bot decide algo que puede ser un error suyo, la respuesta lleva el botón «Pedir una revisión». Ocurre en cinco casos: el documento no trata de IA en educación, la búsqueda por similitud lo da por repetido, no tiene texto legible (un escaneado), pesa más de 20 MB al subirlo o más de 50 MB al descargarlo de una web. Si la licencia no deja adjuntar el archivo, la vista previa añade «Creo que se puede compartir: pedir una revisión».
- **Cuándo no se ofrece.** No se ofrece cuando la persona puede resolverlo sola (la web no deja descargar el documento o el enlace es de una red social; el bot ya le dice qué mandar). Tampoco ante un repetido por dirección o por huella del PDF, que es seguro.
- **Lo que llega a Juanjo, por privado:**
  - quién lo manda (nombre enlazado a su cuenta y alias) y el motivo del bot, con el enlace del supuesto repetido si lo hay;
  - el documento (el que se subió o el descargado);
  - la ficha, hecha aunque el bot lo rechazara, para que no tenga que prepararla él;
  - los botones «Publicar con el archivo», «Publicar solo la ficha» y «No publicar». Sin texto legible no hay ficha, y los botones son «Lo gestiono yo» y «No publicar».
- **Lo que recibe la persona.** Si se publica, sale con su nombre y la persona recibe el enlace, con el botón de quitarlo durante 48 horas, como cualquier publicación. Si no, recibe la decisión. Cada caso queda en `datos/revisiones-biblioteca.json`, que sobrevive a un reinicio, y un segundo toque no publica otra vez.
- **Tope.** Como mucho, tres peticiones por persona y día.
- **Corregir el filtro.** Lo que se publica tras un rechazo se apunta en `datos/correcciones-biblioteca.jsonl`. Un aviso del agente lo recoge para corregir el filtro con su prueba, de modo que el mismo error no se repita.
- **Textos.** Las respuestas que decían «súbelo tú directamente a la Biblioteca» ya no lo dicen, porque el tema está cerrado: ahora ofrecen la revisión.

## Evidencia y validación

- `pruebas/test_revision_biblioteca.py` comprueba:
  - el botón en cada caso;
  - el aviso a Juanjo con la cuenta, el supuesto repetido, el PDF y los botones;
  - el tope de tres peticiones al día;
  - publicar con el archivo, solo la ficha o no publicar, y lo que se apunta;
  - que un segundo toque no publica otra vez;
  - la gestión a mano sin texto legible;
  - el archivo de más de 20 MB;
  - la petición de revisar la licencia;
  - los textos en los cinco idiomas y que ninguno remita al tema cerrado.

## Riesgos

- Una petición sobre un documento que no trata de IA hace la ficha igualmente: unos 0,05-0,10 USD, dentro del tope mensual del bot. El tope de tres por persona y día lo acota.
- Si Juanjo no contesta, la persona espera sin plazo. Lo pendiente está en `datos/revisiones-biblioteca.json`.
