// Verifica se a pessoa cadastrada é menor de idade (campo: data_nascimento)
function verificarIdade() {
    const data = document.querySelector('[name="data_nascimento"]').value;
    if (data.length === 10) {
        const nascimento = new Date(data);
        const hoje = new Date();
        const idade = hoje.getFullYear() - nascimento.getFullYear();
        const isMenor = idade < 18 || (idade === 18 && hoje < new Date(nascimento.setFullYear(hoje.getFullYear())));

        if (isMenor) {
            alert("⚠️ Pessoa menor de idade.");
        }
    }
}

// Capitaliza nomes próprios com exceções como 'de', 'da', etc.
function capitalizar(texto) {
    const excecoes = ['da', 'de', 'do', 'das', 'dos'];
    return texto.split(" ").map(p =>
        excecoes.includes(p.toLowerCase()) 
            ? p.toLowerCase() 
            : p.charAt(0).toUpperCase() + p.slice(1).toLowerCase()
    ).join(" ");
}

// Aplica capitalização ao valor de um campo input
function aplicarCapitalizacao(el) {
    el.value = capitalizar(el.value);
}

// Adiciona dinamicamente um familiar ao formulário
function adicionarMembro(index = null, nome = "", parentesco = "", data = "") {
    const container = document.getElementById("membros");
    const idx = index !== null ? index : container.children.length;

    const div = document.createElement("div");
    div.className = "form-card membro-bloco";
    div.style.width = "100%";

    div.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h3 class="titulo-familiar">Familiar ${idx + 1}</h3>
            <button type="button" onclick="this.closest('.membro-bloco').remove()"
                title="Remover familiar"
                style="background-color: transparent; border: none; font-size: 22px; color: #e53935; cursor: pointer; font-weight: bold;">
                ×
            </button>
        </div>

        <label>Nome:</label>
        <input type="text" name="membros[${idx}][nome]" value="${nome}" onblur="aplicarCapitalizacao(this)" required>

        <label>Parentesco:</label>
        <select name="membros[${idx}][parentesco]" required>
            ${[
                "Cônjuge / Companheiro(a)", "Filho(a)", "Enteado(a)", "Neto(a)", "Pai / Mãe", "Sogro(a)",
                "Genro / Nora", "Irmão(ã)", "Outro parente (ex: tio, primo, cunhado)",
                "Não parente (ex: agregado, amigo, pensionista)"
            ].map(op => `<option${op === parentesco ? ' selected' : ''}>${op}</option>`).join("")}
        </select>


        <label>Data de nascimento:</label>
        <input type="date" name="membros[${idx}][data_nascimento]" value="${data}" required>
    `;

    container.appendChild(div);
}

// Aplica a data de hoje no horário local
function aplicarDataHoje() {
    const hoje = new Date();
    const yyyy = hoje.getFullYear();
    const mm = String(hoje.getMonth() + 1).padStart(2, '0');
    const dd = String(hoje.getDate()).padStart(2, '0');
    const dataLocal = `${yyyy}-${mm}-${dd}`;

    document.querySelectorAll("input.data-hoje[type='date']").forEach(campo => {
        if (!campo.value) campo.value = dataLocal;
    });
}

document.addEventListener("DOMContentLoaded", aplicarDataHoje);

// Carrega beneficiários (pessoas e famílias) e ativa o autocomplete
function configurarAutocompleteBeneficiario({
    inputId = "beneficiario",
    sugestoesId = "sugestoes_beneficiario",
    campoId = "beneficiario_id",
    campoTipo = "beneficiario_tipo",
    aoSelecionar = null
}) {
    let pessoas = [], familias = [];

    fetch("/util/buscar_beneficiarios")
        .then(r => r.json())
        .then(data => {
            pessoas = data.filter(x => x.tipo === "pessoa");
            familias = data.filter(x => x.tipo === "familia");
        });

    const input = document.getElementById(inputId);
    const campoSugestoes = document.getElementById(sugestoesId);
    const campoIdElem = document.getElementById(campoId);
    const campoTipoElem = document.getElementById(campoTipo);

    input.addEventListener("input", () => {
        const termo = input.value.toLowerCase();
        const candidatos = [...pessoas, ...familias];
        const filtrados = candidatos.filter(e => e.nome.toLowerCase().startsWith(termo));

        campoSugestoes.innerHTML = "";
        filtrados.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item.nome;
            li.onclick = () => {
                input.value = item.nome;
                campoIdElem.value = item.id;
                campoTipoElem.value = item.tipo;
                campoSugestoes.innerHTML = "";

                if (typeof aoSelecionar === "function") {
                    aoSelecionar();
                }
            };
            campoSugestoes.appendChild(li);
        });

        campoSugestoes.style.display = filtrados.length ? "block" : "none";
    });
}

// Tabela Presença
let presentes = [];

function adicionarPresenca({ nome, id, tipo }) {
    if (!nome || !id || !tipo) {
        alert("Selecione um beneficiário válido.");
        return;
    }

    presentes.push({ nome, id, tipo });
    atualizarTabelaPresenca();
}

function atualizarTabelaPresenca() {
    const tbody = document.querySelector("#lista_presenca tbody");
    tbody.innerHTML = "";

    presentes.forEach((p, i) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${p.nome}</td>
            <td>${p.tipo}</td>
            <td><button type="button" onclick="removerPresenca(${i})">❌</button></td>
        `;
        tbody.appendChild(row);
    });

    const campoJson = document.getElementById("presentes_json");
    if (campoJson) campoJson.value = JSON.stringify(presentes);
}

function removerPresenca(index) {
    presentes.splice(index, 1);
    atualizarTabelaPresenca();
}

// Carrega beneficiários da presença de uma data e adiciona à lista da atividade
function carregarParticipantesPorData(campoDataId = "data") {
    const data = document.getElementById(campoDataId).value;
    if (!data) {
        alert("Selecione uma data primeiro.");
        return;
    }

    fetch(`/atividades/carregar_presencas?data=${data}`)
        .then(r => r.json())
        .then(lista => {
            if (!Array.isArray(lista) || lista.length === 0) {
                alert("Nenhuma presença encontrada para a data selecionada.");
                return;
            }

            lista.forEach(p => {
                adicionarPresenca({ nome: p.nome, id: p.id, tipo: p.tipo });
            });
        })
        .catch(() => {
            alert("Erro ao buscar dados da presença.");
        });
}

// Limpar lista
function limparListaPresenca() {
    if (confirm("Deseja realmente limpar todos os participantes da lista?")) {
        presentes = [];
        atualizarTabelaPresenca();
    }
}

// 🔄 Preenche o endereço com base no beneficiário selecionado
function preencherEnderecoDoBeneficiario({ idCampo, tipoCampo }) {
    const id = document.getElementById(idCampo)?.value;
    const tipo = document.getElementById(tipoCampo)?.value;

    if (!id || !tipo) return;

    fetch(`/util/buscar_endereco?id=${id}&tipo=${tipo}`)
        .then(response => response.json())
        .then(dados => {
            if (!dados) return;
            document.getElementById("rua_numero").value = dados.rua_numero || "";
            document.getElementById("bairro").value = dados.bairro || "";
            document.getElementById("cidade").value = dados.cidade || "";
            document.getElementById("estado").value = dados.estado || "";
        })
        .catch(() => {
            console.warn("Falha ao buscar endereço do beneficiário.");
        });
}

// 1️⃣ Função que configura o autocomplete do voluntário
function configurarAutocompleteVoluntario(inputElem) {
    const ul = inputElem.parentNode.querySelector(".sugestoes-voluntario");
    const hiddenInput = inputElem.parentNode.querySelector("input[type='hidden']");

    if (!ul || !hiddenInput) return;

    fetch("/util/buscar_voluntarios")
        .then(r => r.json())
        .then(voluntarios => {
            inputElem.addEventListener("input", () => {
                const termo = inputElem.value.toLowerCase();
                const filtrados = voluntarios.filter(v => v.nome.toLowerCase().includes(termo));

                ul.innerHTML = "";
                filtrados.forEach(v => {
                    const li = document.createElement("li");
                    li.textContent = v.nome;
                    li.onclick = () => {
                        inputElem.value = v.nome;
                        hiddenInput.value = v.id;
                        ul.innerHTML = "";
                    };
                    ul.appendChild(li);
                });

                ul.style.display = filtrados.length ? "block" : "none";
            });
        })
        .catch(() => {
            console.warn("Erro ao carregar voluntários.");
        });
}

// 2️⃣ Função que adiciona o voluntário ao DOM
function adicionarVoluntario() {
    const container = document.getElementById("lista_voluntarios");
    const index = container.children.length;

    const div = document.createElement("div");
    div.className = "form-card membro-bloco";
    div.style.width = "100%";
    div.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 class="titulo-familiar">Voluntário ${index + 1}</h3>
            <button type="button" onclick="this.closest('.membro-bloco').remove()" 
                style="background: transparent; border: none; font-size: 22px; color: #e53935; cursor: pointer;">×</button>
        </div>
        <div style="position: relative;">
            <input type="text" name="voluntarios[${index}][nome]" 
                   class="campo-voluntario" 
                   placeholder="Digite o nome do voluntário..." 
                   autocomplete="off" required>
            <input type="hidden" name="voluntarios[${index}][id]">
            <ul class="sugestoes sugestoes-voluntario"></ul>
        </div>
    `;

    container.appendChild(div);
    configurarAutocompleteVoluntario(div.querySelector(".campo-voluntario"));
}

//  preenchendo os campos com dados existentes (ID e nome do voluntário).
function adicionarVoluntarioComDados(index, id, nome) {
    const container = document.getElementById("lista_voluntarios");

    const div = document.createElement("div");
    div.className = "form-card membro-bloco";
    div.style.width = "100%";
    div.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 class="titulo-familiar">Voluntário ${index + 1}</h3>
            <button type="button" onclick="this.closest('.membro-bloco').remove()" 
                style="background: transparent; border: none; font-size: 22px; color: #e53935; cursor: pointer;">×</button>
        </div>
        <div style="position: relative;">
            <input type="text" name="voluntarios[${index}][nome]" 
                   class="campo-voluntario" 
                   placeholder="Digite o nome do voluntário..." 
                   autocomplete="off" required value="${nome}">
            <input type="hidden" name="voluntarios[${index}][id]" value="${id}">
            <ul class="sugestoes sugestoes-voluntario"></ul>
        </div>
    `;

    container.appendChild(div);
    configurarAutocompleteVoluntario(div.querySelector(".campo-voluntario"));
}

// Funções reutilizáveis de listagens

const campoColunas = document.getElementById("colunas");

function toggleColuna(classe) {
    const checkbox = document.getElementById("check_" + classe);
    const colunas = document.querySelectorAll(".col_" + classe);
    colunas.forEach(td => td.classList.toggle("hidden", !checkbox.checked));

    const atual = new Set(campoColunas?.value.split(",").filter(Boolean));
    checkbox.checked ? atual.add(classe) : atual.delete(classe);
    campoColunas.value = Array.from(atual).join(",");
}

function selecionarTodos() {
    const boxes = document.querySelectorAll('input[name="selecionados"]');
    const todosMarcados = Array.from(boxes).every(c => c.checked);
    boxes.forEach(c => c.checked = !todosMarcados);
}

function exportarParaExcel() {
    const selecionados = Array.from(document.querySelectorAll('input[name="selecionados"]:checked')).map(cb => cb.value);
    if (selecionados.length === 0) {
        alert("Selecione pelo menos uma pessoa para exportar.");
        return;
    }
    document.getElementById("ids_exportar").value = JSON.stringify(selecionados);
    document.getElementById("colunas_exportar").value = JSON.stringify(campoColunas?.value.split(",").filter(Boolean));
    document.getElementById("form_exportar").submit();
}

function ordenarPor(campo) {
    const atual = document.getElementById("ordem").value;
    const direcao = document.getElementById("direcao").value;
    document.getElementById("ordem").value = campo;
    document.getElementById("direcao").value = (campo === atual && direcao === "asc") ? "desc" : "asc";
    document.getElementById("filtro_form").submit();
}

function toggleMembros(id) {
  const linhas = document.querySelectorAll(".membro_" + id);
  linhas.forEach(linha => linha.classList.toggle("hidden"));

  // Alternar ícone ➕ / ➖
  const botao = document.querySelector(`button[onclick="toggleMembros('${id}')"]`);
  if (botao) {
    botao.textContent = botao.textContent === "➕" ? "➖" : "➕";
  }
}

 // Colapsar perfil
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-colapsar]").forEach(botao => {
    botao.addEventListener("click", () => {
      const id = botao.getAttribute("data-colapsar");
      const alvo = document.getElementById(id);
      const icone = document.getElementById("icone_" + id.split("_")[1]);
      if (alvo) {
        alvo.classList.toggle("colapsavel");
        if (icone) {
          icone.textContent = alvo.classList.contains("colapsavel") ? "[+]" : "[-]";
        }
      }
    });
  });
});