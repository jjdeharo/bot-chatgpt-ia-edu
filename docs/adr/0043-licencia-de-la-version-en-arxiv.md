# 43. Licencia de la versión del artículo en arXiv

Fecha: 2026-11-18 · Estado: aceptado

## Contexto

La Biblioteca digital ofreció publicar solo la ficha de un preprint cuyo PDF no indicaba la licencia, aunque la ficha del artículo en arXiv indicaba CC BY 4.0. El bot descargaba el PDF, pero la licencia de la ficha original no llegaba al paso de comprobación del archivo (ADR 0002 y 0035).

## Decisión

- Los enlaces oficiales de arXiv a un artículo o a su PDF se reconocen como documentos de la Biblioteca.
- Se lee el enlace de licencia del artículo en su ficha oficial y se descarga el PDF de la versión indicada por la propia ficha. Se comprueban el identificador de la versión, el dominio y la cabecera del PDF. Así la evidencia y el PDF se refieren a la misma versión, también cuando el enlace recibido apunta a la más reciente.
- Cuando esa ficha publica una licencia Creative Commons que permite compartir el PDF original, esa evidencia sustituye el apartado de licencia generado a partir del PDF. En la vista previa figuran la licencia y su enlace, la ficha oficial de la versión y el PDF. El botón «Publicar» sigue pidiendo la confirmación de la persona.
- Sin evidencia verificable de arXiv se conserva la comprobación habitual del PDF. El permiso no exclusivo de depósito por sí solo concede la distribución a arXiv. Los permisos de otra versión, otro sitio o un enlace ajeno a la licencia del artículo no sirven como evidencia.

## Evidencia y validación

- [Ayuda de arXiv sobre licencias](https://info.arxiv.org/help/license/index.html). La licencia se asigna a cada versión y puede ser diferente entre versiones.
- [Caso original](https://arxiv.org/abs/2611.20061v1). Probadas la ficha sin versión y la URL directa del PDF de la primera versión. Ambas descargan los mismos 2.965.207 bytes y obtienen CC BY 4.0 de la ficha oficial.
- `pruebas/test_documento_web.py` comprueba la extracción, los enlaces directos, el aislamiento de versiones y dominios, la licencia de depósito y la vista previa con el PDF aunque la ficha generada indicara ausencia de licencia.
