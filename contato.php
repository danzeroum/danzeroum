<?php
/**
 * Handler do formulário de contato da Danzeroum.
 * Envia por SMTP autenticado usando PHPMailer (entrega confiável, SPF/DKIM).
 *
 * As credenciais SMTP ficam num arquivo FORA do web root, carregado abaixo:
 *   __DIR__ . '/../danzeroum-smtp-config.php'
 * Assim a senha nunca vai para o git e o `rsync --delete` do deploy (que só
 * mexe no web root) não apaga o arquivo. Veja smtp-config.example.php.
 *
 * Se o arquivo de config não existir, cai num fallback com a função mail().
 *
 * Sucesso  -> 303 /obrigado.html
 * Falha    -> 303 /index.html?erro=1#contato
 */

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require __DIR__ . '/lib/PHPMailer/Exception.php';
require __DIR__ . '/lib/PHPMailer/PHPMailer.php';
require __DIR__ . '/lib/PHPMailer/SMTP.php';

// ---- Configuração ----
const DESTINO = 'contato@danzeroum.com';   // quem recebe os contatos
const SUCESSO = '/obrigado.html';
const FALHA   = '/index.html?erro=1#contato';

// ---- Só aceita POST ----
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /', true, 303);
    exit;
}

// ---- Honeypot anti-spam: se preenchido, finge sucesso e descarta ----
if (!empty($_POST['_gotcha'])) {
    header('Location: ' . SUCESSO, true, 303);
    exit;
}

// ---- Coleta + sanitização ----
function limpa($v) {
    return trim(preg_replace('/[\r\n]+/', ' ', (string)($v ?? '')));
}

$nome     = limpa($_POST['nome'] ?? '');
$empresa  = limpa($_POST['empresa'] ?? '');
$email    = limpa($_POST['email'] ?? '');
$tipo     = limpa($_POST['tipo'] ?? '');
$mensagem = trim((string)($_POST['mensagem'] ?? ''));

// ---- Validação mínima ----
$valido = $nome !== ''
    && filter_var($email, FILTER_VALIDATE_EMAIL)
    && $mensagem !== '';

if (!$valido) {
    header('Location: ' . FALHA, true, 303);
    exit;
}

// ---- Monta o conteúdo ----
$assunto = '[Site Danzeroum] Novo contato' . ($empresa !== '' ? ' — ' . $empresa : '');

$corpo  = "Novo contato pelo site danzeroum.com\n";
$corpo .= str_repeat('-', 40) . "\n";
$corpo .= "Nome:      {$nome}\n";
$corpo .= "Empresa:   " . ($empresa !== '' ? $empresa : '—') . "\n";
$corpo .= "E-mail:    {$email}\n";
$corpo .= "Interesse: " . ($tipo !== '' ? $tipo : '—') . "\n";
$corpo .= str_repeat('-', 40) . "\n";
$corpo .= "Mensagem:\n{$mensagem}\n";

// ---- Carrega config SMTP (fora do web root) ----
$smtpConfigPath = __DIR__ . '/../danzeroum-smtp-config.php';
$smtp = is_readable($smtpConfigPath) ? require $smtpConfigPath : null;

$enviado = false;

if (is_array($smtp) && !empty($smtp['host'])) {
    // ---- Envio via SMTP autenticado (PHPMailer) ----
    $mail = new PHPMailer(true);
    try {
        $mail->isSMTP();
        $mail->Host       = $smtp['host'];
        $mail->Port       = (int)($smtp['port'] ?? 587);
        $mail->SMTPAuth   = true;
        $mail->Username   = $smtp['username'] ?? '';
        $mail->Password   = $smtp['password'] ?? '';
        $mail->CharSet    = PHPMailer::CHARSET_UTF8;

        $enc = strtolower($smtp['encryption'] ?? 'tls');
        if ($enc === 'ssl' || $enc === 'smtps') {
            $mail->SMTPSecure = PHPMailer::ENCRYPTION_SMTPS;      // porta 465
        } elseif ($enc === 'tls' || $enc === 'starttls') {
            $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;   // porta 587
        }

        $from     = $smtp['from']      ?? ($smtp['username'] ?? DESTINO);
        $fromName = $smtp['from_name'] ?? 'Site Danzeroum';
        $mail->setFrom($from, $fromName);
        $mail->addAddress(DESTINO);
        $mail->addReplyTo($email, $nome);

        $mail->Subject = $assunto;
        $mail->Body    = $corpo;

        $mail->send();
        $enviado = true;
    } catch (Exception $e) {
        error_log('Danzeroum contato (SMTP): ' . $mail->ErrorInfo);
        $enviado = false;
    }
} else {
    // ---- Fallback: função mail() (caso o SMTP ainda não esteja configurado) ----
    $headers   = [];
    $headers[] = 'From: Site Danzeroum <' . DESTINO . '>';
    $headers[] = 'Reply-To: ' . $nome . ' <' . $email . '>';
    $headers[] = 'Content-Type: text/plain; charset=UTF-8';
    $enviado = @mail(
        DESTINO,
        '=?UTF-8?B?' . base64_encode($assunto) . '?=',
        $corpo,
        implode("\r\n", $headers)
    );
}

// ---- Redireciona ----
header('Location: ' . ($enviado ? SUCESSO : FALHA), true, 303);
exit;
