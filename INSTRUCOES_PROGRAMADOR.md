# Rede de Mentores — Inatel Startups (Guia de Implementação)

Este projeto contém o módulo responsivo da seção **Nossos Mentores** do Inatel Startups (15 mentores da Vitrine Oficial com fotos de alta resolução, cargos, links do LinkedIn e botão para o Airtable), publicado e pronto para ser inserido via **Embed (`<iframe>`)** ou **código-fonte direto**.

---

## 🔗 Links Oficiais do Projeto

- **URL do Frame (GitHub Pages):** [https://inatelstartups.github.io/mentores-startups/](https://inatelstartups.github.io/mentores-startups/)
- **Repositório GitHub:** [https://github.com/inatelstartups/mentores-startups](https://github.com/inatelstartups/mentores-startups)
- **Base Oficial no Airtable:** [https://airtable.com/appNpzNg1CLsXf3Hn/shrhHcTKwTnzAdM4o/tblz2ADXqNnD830uA](https://airtable.com/appNpzNg1CLsXf3Hn/shrhHcTKwTnzAdM4o/tblz2ADXqNnD830uA)

---

## ⚡ Opção 1 (Recomendada): Inserir apenas o Código do Frame (`<iframe>`)

Para que futuras atualizações de mentores, fotos ou cargos feitas no GitHub apareçam **automaticamente no site** sem precisar mexer no código da página novamente, basta colar o trecho abaixo no local onde a seção de Mentores deve ser exibida (também disponível no arquivo `CODIGO_EMBED_IFRAME.html`):

```html
<!-- REDE DE MENTORES — INATEL STARTUPS (AUTO-ATUALIZÁVEL VIA GITHUB) -->
<div id="inatel-mentores-embed-wrapper" style="width: 100%; overflow: hidden;">
    <iframe
        id="inatel-mentores-iframe"
        src="https://inatelstartups.github.io/mentores-startups/"
        title="Nossos Mentores - Inatel Startups"
        style="width: 100%; min-height: 580px; border: none; display: block; background: transparent;"
        scrolling="no"
        loading="lazy"
        allowtransparency="true"
    ></iframe>
</div>

<script>
    // Ajusta automaticamente a altura do frame ao redimensionar a tela (sem barra de rolagem interna)
    window.addEventListener('message', function (event) {
        if (event.data && event.data.type === 'inatel-mentors-resize' && event.data.height) {
            var iframe = document.getElementById('inatel-mentores-iframe');
            if (iframe) {
                iframe.style.height = event.data.height + 'px';
            }
        }
    });
</script>
```

> **Como funciona o redimensionamento automático:** O `mentores.js` dentro do frame possui um `ResizeObserver` que envia via `postMessage` a altura exata da seção sempre que a página carrega ou muda de tamanho (desktop/mobile), garantindo que não haja barras de rolagem internas.

---

## 🧩 Opção 2: Integração Direta no Código-Fonte (HTML + CSS + JS)

Caso prefira incorporar diretamente no código da página em vez de usar `<iframe>`:

1. **Assets (Fotos):** Copie a pasta `elementos/mentores/` mantendo o caminho relativo `elementos/mentores/...`.
2. **HTML:** Copie a `<section id="mentores" class="section">...</section>` do arquivo `index.html`.
3. **CSS:** Inclua os estilos da folha `style.css`.
4. **JS:** Inclua o script `mentores.js` antes do fechamento do `</body>`.
5. **Atualizações via Git:** Para puxar novas atualizações do repositório:
   ```bash
   git pull origin main
   ```
