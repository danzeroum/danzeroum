<?php
/**
 * Handler do formulário de contato da Danzeroum.
 * Envia por SMTP autenticado usando PHPMailer (entrega confiável, SPF/DKIM).
 *
 * As credenciais SMTP vêm de VARIÁVEIS DE AMBIENTE (injetadas pelo Docker via o
 * arquivo .env do projeto): SMTP_HOST, SMTP_PORT, SMTP_ENCRYPTION, SMTP_USER,
 * SMTP_PASS, SMTP_FROM, SMTP_FROM_NAME, MAIL_TO. A senha nunca vai para o git
 * nem para a imagem. Veja .env.example.
 *
 * Se SMTP_HOST não estiver definido, cai num fallback com a função mail().
 *
 * Sucesso  -> 303 /obrigado.html
 * Falha    -> 303 /index.html?erro=1#contato
 */

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require __DIR__ . '/lib/PHPMailer/Exception.php';
require __DIR__ . '/lib/PHPMailer/PHPMailer.php';
require __DIR__ . '/lib/PHPMailer/SMTP.php';

// ---- Configuração (via ambiente) ----
function env($k, $default = '') {
    $v = getenv($k);
    return ($v === false || $v === '') ? $default : $v;
}
$DESTINO = env('MAIL_TO', 'contato@danzeroum.com');   // quem recebe os contatos
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

// ---- Config SMTP via variáveis de ambiente (.env do Docker) ----
$smtpHost = env('SMTP_HOST');

$enviado = false;

if ($smtpHost !== '') {
    // ---- Envio via SMTP autenticado (PHPMailer) ----
    $mail = new PHPMailer(true);
    try {
        $mail->isSMTP();
        $mail->Host       = $smtpHost;
        $mail->Port       = (int)env('SMTP_PORT', '587');
        $mail->SMTPAuth   = true;
        $mail->Username   = env('SMTP_USER');
        $mail->Password   = env('SMTP_PASS');
        $mail->CharSet    = PHPMailer::CHARSET_UTF8;

        $enc = strtolower(env('SMTP_ENCRYPTION', 'tls'));
        if ($enc === 'ssl' || $enc === 'smtps') {
            $mail->SMTPSecure = PHPMailer::ENCRYPTION_SMTPS;      // porta 465
        } elseif ($enc === 'tls' || $enc === 'starttls') {
            $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;   // porta 587
        }

        $from     = env('SMTP_FROM', env('SMTP_USER', $DESTINO));
        $fromName = env('SMTP_FROM_NAME', 'Site Danzeroum');
        $mail->setFrom($from, $fromName);
        $mail->addAddress($DESTINO);
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
    $headers[] = 'From: Site Danzeroum <' . $DESTINO . '>';
    $headers[] = 'Reply-To: ' . $nome . ' <' . $email . '>';
    $headers[] = 'Content-Type: text/plain; charset=UTF-8';
    $enviado = @mail(
        $DESTINO,
        '=?UTF-8?B?' . base64_encode($assunto) . '?=',
        $corpo,
        implode("\r\n", $headers)
    );
}

// ---- Redireciona ----
header('Location: ' . ($enviado ? SUCESSO : FALHA), true, 303);
exit;
