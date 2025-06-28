# Projeto Dignidade

Sistema local e offline de gestão para instituições sociais. Desenvolvido para substituir planilhas e papéis, centralizando informações sobre pessoas atendidas, visitas domiciliares, doações, voluntários, presenças e atividades.

## 🚀 Versão Executável

Se você baixou a versão `.zip`:

1. **Extraia o arquivo**
2. Abra a pasta e execute o **`ProjetoDignidade.exe`**
3. O sistema será aberto automaticamente no navegador padrão

> ⚠️ Não remova ou renomeie pastas como `static/`, `templates/` ou `banco/`. Elas são essenciais para o funcionamento.  

---

## 🧰 Funcionalidades

- Cadastro completo de pessoas (com foto, familiares, histórico etc.)
- Registro de visitas domiciliares com preenchimento automático de endereço
- Doações de entrada e saída com rastreamento por beneficiário
- Controle de voluntários e suas disponibilidades
- Lista de presença diária com autocomplete de beneficiários
- Atividades com participantes e botão para carregar lista de presença
- Exportação para Excel com colunas dinâmicas
- Modo escuro, aumento de fonte e acessibilidade

---

## 💻 Para Desenvolvedores

Se você quiser rodar ou modificar o projeto com Python:

### ⚙️ Requisitos

- Python 3.10+
- `venv` ou ambiente virtual
- Pip

### 🛠️ Como executar

```bash
pip install -r requirements.txt
python app.py
```

Depois acesse em:
```
http://localhost:5000
```

---

## 🗂 Estrutura

```
projeto_dignidade/
├── app.py                # Arquivo principal
├── banco/                # Banco de dados e scripts
├── rotas/                # Módulos organizados por funcionalidade
├── static/               # Imagens, CSS e JS
├── templates/            # HTMLs por funcionalidade
├── executavel/           # Versão .exe e arquivos necessários
└── README.md
```

---

## 👤 Autor

**Marcelo Barbosa da Silva**  
[GitHub](https://github.com/Marcelo0070)

---

## 📦 Licença

Este projeto é de uso livre para fins sociais e educativos.  
Distribuição comercial não autorizada.
