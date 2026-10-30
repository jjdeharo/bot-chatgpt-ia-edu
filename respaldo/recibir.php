<?php
// SPDX-License-Identifier: AGPL-3.0-or-later
// Recibe cada madrugada la copia de lo que el Bot de IA Educativa solo tiene en el NAS:
// quién es dueño de cada recurso del repositorio de VCE (catalogo.json) y la cuenta del
// gasto (estado-bot.json). Si el NAS se pierde, de aquí se recupera (README, «Si el NAS falla»).
//
// Mismo método que el panel del vigía (vigilancia-nas): un testigo compartido en la
// cabecera X-Token, sin claves SSH en el NAS. Guarda una copia por día y borra las de
// más de 30 días. El .htaccess impide descargar nada desde la web.

declare(strict_types=1);

$directorio = __DIR__;
$config = $directorio . '/token.txt';
$dias = 30;

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    exit(json_encode(['error' => 'Solo POST.']));
}
if (!is_readable($config)) {
    http_response_code(500);
    exit(json_encode(['error' => 'Falta el testigo en el servidor.']));
}
$esperado = trim((string) file_get_contents($config));
$recibido = trim((string) ($_SERVER['HTTP_X_TOKEN'] ?? ''));
if ($esperado === '' || !hash_equals($esperado, $recibido)) {
    http_response_code(403);
    exit(json_encode(['error' => 'Testigo incorrecto.']));
}

$cuerpo = file_get_contents('php://input');
if ($cuerpo === false || strlen($cuerpo) > 5000000) {
    http_response_code(413);
    exit(json_encode(['error' => 'Cuerpo vacío o demasiado grande.']));
}
$datos = json_decode($cuerpo, true);
if (!is_array($datos) || !isset($datos['marca'], $datos['catalogo'])) {
    http_response_code(400);
    exit(json_encode(['error' => 'Eso no es una copia del bot.']));
}

$destino = $directorio . '/copia-' . gmdate('Y-m-d') . '.json';
$temporal = $destino . '.' . getmypid();
if (file_put_contents($temporal, $cuerpo) === false || !rename($temporal, $destino)) {
    @unlink($temporal);
    http_response_code(500);
    exit(json_encode(['error' => 'No se pudo guardar.']));
}
foreach (glob($directorio . '/copia-*.json') as $viejo) {
    if (filemtime($viejo) < time() - $dias * 86400) {
        @unlink($viejo);
    }
}
echo json_encode(['ok' => true, 'guardado' => basename($destino)]);
