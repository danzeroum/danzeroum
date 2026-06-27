/* Alternância de tema claro/escuro, persistida no navegador.
   O "no-flash" (aplicar o tema antes de pintar) fica inline no <head> de cada página. */
(function () {
  var root = document.documentElement;
  var btn = document.getElementById('theme');
  if (!btn) return;
  btn.addEventListener('click', function () {
    root.classList.toggle('dark');
    try {
      localStorage.setItem('theme', root.classList.contains('dark') ? 'dark' : 'light');
    } catch (e) {}
  });
})();
