# 44. Destino de los enlaces sueltos

Fecha: 2026-11-18 · Estado: aceptado

## Contexto

Al recibir un enlace suelto, el bot preparaba una ficha para el repositorio de Vibe Coding Educativo si la persona era miembro. Las excepciones eran los PDF, arXiv para miembros de ChatGPT-IA-edu y los enlaces de Telegram. Así, una guía o un artículo que se publicara en una página web podía acabar en el repositorio de recursos.

## Decisión

El bot determina el destino por el formato del enlace o por los metadatos de la página. Los PDF y las fichas académicas que identifican el PDF de su artículo van a la Biblioteca digital. Una página que se declara aplicación puede ir al repositorio. Las señales en conflicto, una página ilegible o su falta de metadatos dejan el destino por confirmar. La presencia de un enlace cualquiera a un PDF no basta, porque puede ser el manual de una aplicación.

En los casos que quedan por confirmar, el bot responde al enlace con botones para los destinos a los que la persona pertenece, más «Consultarlo» y «Cancelar». El botón usa una clave por enlace, caduca al transcurrir la espera y solo se puede usar una vez. Un enlace posterior o un comando sustituye la pregunta anterior. Los enlaces a mensajes de Telegram mantienen su recorrido habitual de consulta. Los comandos `/biblioteca` y `/repositorio` y las solicitudes explícitas conservan prioridad.

## Consecuencias y validación

- La lectura inicial usa el descargador que ya comprueba los destinos públicos y sus redirecciones. Lee como máximo 3 MB, con un máximo de cuatro lecturas iniciales simultáneas. La clasificación inicial prescinde de una llamada al modelo. Cuando se elige el destino, se ejecuta la preparación normal y se sigue pidiendo confirmación para publicar.
- Se prueban el PDF servido sin extensión, los metadatos del artículo y de la aplicación, las señales en conflicto, las páginas inaccesibles, los comandos explícitos y la pertenencia a los grupos. También se prueban los botones pulsados dos veces, un enlace nuevo que sustituye a otro y la consulta sobre el enlace en su recorrido normal.
