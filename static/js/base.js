document.addEventListener("DOMContentLoaded", function () {
    // 🌞 Alternância de tema escuro/claro
    const botaoTema = document.getElementById("toggle-dark");
    const logo = document.querySelector(".logo");
    const temaSalvo = localStorage.getItem("tema");
    const body = document.body;

    if (temaSalvo === "escuro") {
        body.classList.add("tema-escuro");
        if (botaoTema) botaoTema.textContent = "🌙";
        if (logo) logo.src = "/static/imagens_sistema/logo-noite.png";
    } else {
        if (logo) logo.src = "/static/imagens_sistema/logo-dia.png";
    }

    if (botaoTema) {
        botaoTema.addEventListener("click", function () {
            body.classList.toggle("tema-escuro");
            const escuroAtivo = body.classList.contains("tema-escuro");
            botaoTema.textContent = escuroAtivo ? "🌙" : "🌞";
            localStorage.setItem("tema", escuroAtivo ? "escuro" : "claro");
            if (logo) {
                logo.src = escuroAtivo
                    ? "/static/imagens_sistema/logo-noite.png"
                    : "/static/imagens_sistema/logo-dia.png";
            }
        });
    }

    // 🔠 Alternância de tamanho de fonte
    const botaoFonte = document.getElementById("botao-fonte");
    const fonteSalva = localStorage.getItem("fonte");
    if (fonteSalva === "grande") {
        body.classList.add("fonte-grande");
        if (botaoFonte) botaoFonte.textContent = "A";
    } else {
        localStorage.setItem("fonte", "normal");
        if (botaoFonte) botaoFonte.textContent = "a";
    }

    if (botaoFonte) {
        botaoFonte.addEventListener("click", () => {
            body.classList.toggle("fonte-grande");
            const ativa = body.classList.contains("fonte-grande");
            localStorage.setItem("fonte", ativa ? "grande" : "normal");
            botaoFonte.textContent = ativa ? "A" : "a";
        });
    }

    // 💾 Fazer Backup
    const botaoBackup = document.getElementById("fazer-backup");
    if (botaoBackup) {
        botaoBackup.addEventListener("click", function (e) {
            e.preventDefault();
            if (confirm("Deseja realmente criar um backup agora?")) {
                fetch("/fazer-backup")
                    .then(res => res.json())
                    .then(dados => {
                        alert(dados.mensagem || "Backup concluído.");
                    })
                    .catch(() => {
                        alert("Erro ao fazer backup.");
                    });
            }
        });
    }

    // 📂 Executar backup (abrir instruções)
    const botaoInstrucoes = document.getElementById("executar-backup");
    if (botaoInstrucoes) {
        botaoInstrucoes.addEventListener("click", function (e) {
            e.preventDefault();
            if (confirm("⚠️ Isso abrirá a pasta de backups com as instruções para restaurar manualmente. Deseja continuar?")) {
                fetch("/instrucoes-backup")
                    .then(res => res.json())
                    .then(resp => {
                        alert(resp.mensagem || resp.erro || "Instruções abertas.");
                    })
                    .catch(() => alert("Erro ao abrir instruções."));
            }
        });
    }

    // ✅ Oculta automaticamente mensagens flash de sucesso/erro
    document.addEventListener("DOMContentLoaded", () => {
        const alerta = document.querySelector(".alerta-sucesso, .alerta-erro");
        if (alerta) {
            window.scrollTo({ top: 0, behavior: "smooth" });
            setTimeout(() => {
                alerta.style.display = "none";
            }, 8000);
        }
    });

});
