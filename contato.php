<?php
/**
 * Handler do formulário de contato da Danzeroum.
 * Recebe o POST do formulário em index.html, valida, e envia por e-mail.
 * Sem dependências — usa a função mail() do PHP (VPS Hostinger).
 *
 * Em caso de sucesso, redireciona para /obrigado.html (303).
 * Em caso de erro/spam, volta para a seção de contato com ?erro=1.
 *
 * Para entrega mais confiável (SPF/DKIM), considere trocar mail() por SMTP
 * autenticado via PHPMailer apontando para o servidor de e-mail do domínio.
 */

// ---- Configuração ----
const DESTINO   = 'contato@danzeroum.com';      // quem recebe os contatos
const REMETENTE = 'no-reply@danzeroum.com';     // From: (use um endereço do seu domínio p/ não cair em spam)
const SUCESSO   = '/obrigado.html';
const FALHA     = '/index.html?erro=1#contato';

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

// ---- Monta e envia o e-mail ----
$assunto = '[Site Danzeroum] Novo contato' . ($empresa !== '' ? ' — ' . $empresa : '');

$corpo  = "Novo contato pelo site danzeroum.com\n";
$corpo .= str_repeat('-', 40) . "\n";
$corpo .= "Nome:     {$nome}\n";
$corpo .= "Empresa:  " . ($empresa !== '' ? $empresa : '—') . "\n";
$corpo .= "E-mail:   {$email}\n";
$corpo .= "Interesse:" . ($tipo !== '' ? ' ' . $tipo : ' —') . "\n";
$corpo .= str_repeat('-', 40) . "\n";
$corpo .= "Mensagem:\n{$mensagem}\n";

$headers   = [];
$headers[] = 'From: Danzeroum <' . REMETENTE . '>';
$headers[] = 'Reply-To: ' . $nome . ' <' . $email . '>';
$headers[] = 'Content-Type: text/plain; charset=UTF-8';
$headers[] = 'X-Mailer: PHP/' . phpversion();

$enviado = @mail(DESTINO, '=?UTF-8?B?' . base64_encode($assunto) . '?=', $corpo, implode("\r\n", $headers));

// ---- Redireciona ----
header('Location: ' . ($enviado ? SUCESSO : FALHA), true, 303);
exit;
