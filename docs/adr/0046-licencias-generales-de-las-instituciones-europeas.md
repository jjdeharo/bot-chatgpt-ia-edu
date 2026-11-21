# 46. Licencias generales de las instituciones europeas

Fecha: 2026-11-21 · Estado: aceptado

## Contexto

La Biblioteca digital solo adjuntaba el PDF de las conclusiones del Consejo de la UE sobre competencias en IA (documento 14902/26) si el propio documento indicaba una licencia abierta. El PDF no indica ninguna. Sin embargo, el Consejo permite reutilizar todos sus documentos públicos mediante una norma general. La Comisión Europea y el Parlamento Europeo hacen lo mismo con su aviso legal. El bot publicaba la ficha sin el archivo, como si el documento tuviera todos los derechos reservados.

## Decisión

- Cuando el PDF se descarga por https desde el dominio oficial de una de estas instituciones o desde uno de sus subdominios, se aplica su licencia general. Cuenta el dominio que sirve el PDF después de las redirecciones.
  - `consilium.europa.eu`: la Decisión (UE) 2017/1842 permite reutilizar el documento citando la fuente y sin deformar su contenido.
  - `commission.europa.eu` y `ec.europa.eu`: CC BY 4.0, según el aviso legal de la Comisión y la Decisión 2011/833/UE.
  - `europarl.europa.eu`: su aviso legal permite reutilizar el documento citando la fuente y sin alterarlo.
- Esa licencia, con el enlace a su norma, sustituye al apartado Licencia de la ficha y el PDF se adjunta. El botón «Publicar» sigue pidiendo la confirmación de la persona.
- Si la ficha recoge una reserva expresa del documento, como «todos los derechos reservados», derechos de terceros o una prohibición, esa reserva se mantiene y solo se publica la ficha. Las tres normas excluyen las obras con derechos de terceros. El «©» por sí solo no cuenta como reserva, porque estas instituciones lo ponen en todo lo que publican.
- Un PDF subido como archivo, sin su dirección, sigue la comprobación habitual.

## Evidencia y validación

- [Decisión (UE) 2017/1842 del Consejo](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32017D1842). Los artículos 4 y 6 permiten la reutilización gratuita y comercial, con tres condiciones: citar la procedencia, no deformar el contenido y eximir al Consejo de responsabilidad. El artículo 2 excluye los documentos sujetos a derechos de terceros.
- [Aviso legal de la Comisión](https://commission.europa.eu/legal-notice_es). Salvo indicación contraria, los contenidos propiedad de la UE en sus webs se publican con CC BY 4.0. Las obras de terceros pueden necesitar permiso.
- [Aviso legal del Parlamento Europeo](https://www.europarl.europa.eu/legal-notice/es/). Autoriza la reutilización si se respeta la integridad del documento y se menciona su fuente.
- Caso original: el PDF del documento 14902/26 en castellano. `documento_web.buscar` le aplica la Decisión 2017/1842.
- `pruebas/test_documento_web.py` comprueba los dominios y sus subdominios. También comprueba que se rechacen los dominios parecidos, las direcciones sin https y los PDF redirigidos a otro sitio, que se adjunte el PDF sin licencia propia y que una reserva expresa prevalezca.

## Riesgos

- La reserva se detecta por las palabras con que la ficha recoge lo que dice el documento. Si una obra de terceros se publica en estas webs sin que el PDF lo diga, recibe la licencia general. En ese caso la norma de la institución tampoco la cubriría. La persona que publica ve la licencia en la vista previa antes de pulsar «Publicar».
- Otras administraciones con regímenes parecidos, como la Administración General del Estado, no se incluyen. Cada ministerio tiene su propio aviso legal y habría que comprobarlos uno a uno.
