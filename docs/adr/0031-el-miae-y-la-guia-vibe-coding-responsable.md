# 31. El MIAE y la guía Vibe coding responsable

Fecha: 2026-11-05 · Estado: aceptado

## Contexto

El bot solo respondía con lo dicho en los grupos, la Biblioteca digital, el repositorio y el diario, y
sus instrucciones le prohíben contestar con su propio conocimiento. Del MIAE y de la guía Vibe coding
responsable, que se usan a diario en los grupos, solo encontraba lo que alguien hubiera comentado:
16 mensajes sobre el MIAE y unos 10 sobre la guía (05-11-2026). Ninguno de los 119 PDF de la Biblioteca
trata de ellos. De la guía, solo sabía el capítulo de licencias, que lleva escrito en «Sobre ti» para
la revisión de los recursos. Juanjo pidió que el bot pudiera «responder cualquier pregunta sobre este
tema» y aprobó la propuesta ese mismo día.

## Decisión

- Las dos obras se toman de sus repositorios públicos de GitHub, donde se generan
  (`Vibe-Coding-Educativo/vibe-responsable` y `jjdeharo/miae`), y no de la web ni de una copia. Una vez
  al día, `scripts/marcos.py` descarga el `tar.gz` de cada uno desde `codeload.github.com`, que no
  gasta cuota de la API, y extrae solo los `.md` y `.json` de `contenido/`, `content/` y `data/`.
- Se escribe un Markdown por página publicada, con su dirección en `enlaces-<idioma>.json`:
  - de la guía, todas sus páginas (presentación, guía, herramientas, crear con IA, VCER, referencias,
    créditos), los diez capítulos y los dos archivos para la IA, que enlazan a la página que los
    enseña (`para-la-ia.html` y `vcer.html`), no al `.md` suelto;
  - del MIAE, el marco completo de la versión vigente (`data/versions.json`), la guía rápida y la
    ficha para declarar el uso de IA y comunicar los usos permitidos, pasadas de JSON a Markdown.
- Se indexan con `documentacion.py`, el mismo programa que la documentación de Karla bot (ADR 0008):
  un índice por idioma, para que una búsqueda no devuelva el mismo apartado cinco veces. Solo se
  recalcula lo que ha cambiado.
- Dos herramientas, `buscar_marcos` (consulta, idioma de la conversación y, si hace falta, una sola
  obra) y `leer_marco` (un apartado entero). Cada resultado trae el enlace de su página.
- En las instrucciones, una excepción a «solo buscas en los grupos»: sobre el MIAE y la guía responde
  con sus textos, sin añadir nada que no digan y con el enlace de cada explicación. Para clasificar un
  uso en un nivel, aplica las reglas del marco y, si no sabe qué hizo la persona y qué hizo la IA, lo
  pregunta.
- En la ayuda para enseñar (ADR 0011) también están, como fuente revisada: el revisor recibe el texto
  de cada apartado citado, y el programa escribe debajo «MIAE» o «Guía Vibe coding responsable» con el
  enlace. Preguntar qué dice una de las dos obras no es pedir ayuda para enseñar, y lo resuelve Haiku.
- La ayuda del bot (`ayuda_buscar`) lo dice en los cinco idiomas.

## Alternativas descartadas

- Subir los PDF de las dos obras a la Biblioteca: duplicaría lo que ya está publicado, el bot solo
  leería las primeras páginas y se quedaría con una versión fija.
- Leer la web publicada: sería una copia de lo que se genera en el repositorio, con todo el HTML.
- Dejarlas fuera de la ayuda para enseñar: se probó y el modelo las llamaba igualmente, porque las
  instrucciones las nombran, y la revisión no sabía comprobar sus enlaces, que salían con `[[…]]`.

## Consecuencias

- Sin gasto fijo nuevo: la búsqueda es local, y una pregunta sobre el MIAE o la guía cuesta como otra
  cualquiera (entre 0,001 y 0,003 USD con Haiku en las pruebas).
- Un cambio en la guía o en el MIAE llega al bot como mucho al día siguiente.
- La primera indexación en el NAS tarda unos minutos (en el portátil, seis); después, solo lo nuevo.

## Riesgos y limitaciones

- Si GitHub no responde, el bot sigue con la última copia. Si pasan tres días sin poder descargar,
  avisa a Juanjo una vez al día.
- Si cambia la estructura de un repositorio (carpetas o nombres de los JSON del MIAE), el Markdown de
  esa parte deja de generarse. Las pruebas cubren la estructura del 05-11-2026.
- Las traducciones de las dos obras se hicieron con IA, sin revisión profesional: el bot responde con
  lo que dicen.

## Validación

- `pruebas/test_marcos.py`, sin red ni modelo: enlaces de cada página, paso de los JSON del MIAE a
  Markdown, búsqueda por idioma y por obra, lectura de un apartado, índice que falta, descarga que
  solo extrae texto y no sale de su carpeta, y enlaces del MIAE y la guía como fuentes citables.
- 05-11-2026, en el portátil con los índices reales: los 110 enlaces (22 páginas por cinco idiomas)
  responden 200. Ocho preguntas reales con Haiku y Sonnet: nivel de corregir la ortografía,
  licencia en catalán, accesibilidad con su punto de la VCER, cómo comunicar al alumnado los usos
  permitidos, crear una app con el alumnado, un ensayo con ChatGPT en inglés y «ha usado Gemini, ¿qué
  nivel es?», en el que pide los datos que faltan en vez de inventar un nivel.
