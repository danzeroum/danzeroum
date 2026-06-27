<?php
/**
 * EXEMPLO de configuração SMTP para o formulário (contato.php).
 *
 * COMO USAR no VPS:
 *   1. Copie este arquivo para UM NÍVEL ACIMA do web root, com o nome exato:
 *        <web root>/../danzeroum-smtp-config.php
 *      Ex.: se o site está em /var/www/danzeroum.com/public_html,
 *           o config vai em /var/www/danzeroum.com/danzeroum-smtp-config.php
 *      (Fora do web root = não é acessível pela web e o rsync --delete não apaga.)
 *   2. Preencha host/porta/usuário/senha com os dados do e-mail do domínio.
 *   3. NÃO comite o arquivo real com a senha. Este exemplo tem só placeholders.
 *
 * Hostinger (e-mail do domínio) — valores típicos:
 *   host: smtp.hostinger.com
 *   port: 465  + encryption: 'ssl'      (ou port 587 + encryption: 'tls')
 */

return [
    'host'       => 'smtp.hostinger.com',
    'port'       => 465,
    'encryption' => 'ssl',                 // 'ssl' (porta 465) ou 'tls' (porta 587)
    'username'   => 'contato@danzeroum.com',
    'password'   => 'COLOQUE_A_SENHA_DO_EMAIL_AQUI',
    'from'       => 'contato@danzeroum.com',  // remetente (use um endereço do próprio domínio)
    'from_name'  => 'Site Danzeroum',
];
