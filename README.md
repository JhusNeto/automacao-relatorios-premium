# 📊 Automação de Relatórios — Projeto Premium

Solução de **automação de relatórios** que lê arquivos Excel (inconsistentes ou padronizados), trata os dados, gera um **dashboard em PDF** profissional e pode rodar **100% sem interação humana**, inclusive com monitoramento de pasta e agendamento.

---

## 🎯 O que este projeto faz

- **Lê** planilhas Excel em múltiplos formatos (múltiplas abas, colunas com nomes variados)
- **Detecta** automaticamente abas, colunas e tipos (data, número, texto)
- **Normaliza** nomes de colunas e trata erros comuns (colunas ausentes, tipos incorretos)
- **Limpa** duplicados, padroniza datas e converte texto para número
- **Cria métricas** genéricas: total por categoria, ticket médio, evolução mês a mês, percentual por grupo
- **Gera um PDF** com design corporativo: KPIs em cards, gráficos (barras, linha, pizza), tabelas e sumário
- **Automação**: processa ao colocar arquivos na pasta `input/` ou em modo monitoramento contínuo

---

## 🚀 Uso rápido

### Pré-requisitos

- Python 3.10+
- Dependências: `pip install -r requirements.txt`

### Fluxo básico

1. Coloque um ou mais arquivos Excel (`.xlsx` ou `.xls`) na pasta **`input/`**
2. Execute:

   ```bash
   python main.py
   ```

3. Os PDFs serão gerados na pasta **`output/`** com nome no formato `relatorio_YYYYMMDD_HHMMSS.pdf`

### Exemplo com arquivo de exemplo

```bash
cp sample_input.xlsx input/
python main.py
```

O projeto inclui **`sample_input.xlsx`** (dados de exemplo) e **`sample_output.pdf`** (exemplo de saída) na raiz do repositório.

### Modo monitoramento

Para processar automaticamente cada novo arquivo colocado em `input/`:

```bash
python main.py --watch
```

Novos arquivos Excel em `input/` gerarão um novo PDF em `output/` com timestamp. Encerre com `Ctrl+C`.

### Processar um arquivo específico

```bash
python main.py caminho/para/planilha.xlsx
```

### Definir pasta de saída

```bash
python main.py --output-dir /caminho/para/saida
```

---

## 📁 Estrutura do projeto

```
automacao-relatorios-premium/
├── main.py                 # Ponto de entrada (uso único ou --watch)
├── requirements.txt
├── sample_input.xlsx       # Planilha de exemplo
├── sample_output.pdf       # PDF de exemplo gerado
├── input/                  # Pasta de entrada (coloque os Excel aqui)
├── output/                 # Pasta de saída (PDFs gerados)
├── assets/                 # Screenshots e GIF de demonstração
├── scripts/
│   └── gerar_sample_input.py
└── src/
    ├── ingestao.py         # Leitura e normalização de Excel
    ├── tratamento.py       # Limpeza e métricas
    ├── relatorio_pdf.py    # Geração do PDF (KPIs, gráficos, tabelas)
    └── automacao.py        # Monitoramento de pasta
```

---

## 🧠 Arquitetura em 4 módulos

| Módulo | Função |
|--------|--------|
| **Ingestão** | Lê Excel, detecta abas/colunas, normaliza nomes, infere tipos (data, número, texto), trata erros comuns |
| **Tratamento** | Remove duplicados, padroniza datas, converte texto→número, calcula total por categoria, ticket médio, evolução mensal, % por grupo |
| **Relatório PDF** | Gera dashboard em PDF: sumário, cards de KPI, gráficos (barras, linha, pizza), tabela detalhada. Paleta: azul escuro, cinza, branco |
| **Automação** | Monitora `input/`, gera relatório ao detectar novo arquivo, salva em `output/` com timestamp |

---

## 📋 Formato esperado do Excel

O sistema **adapta-se** a vários formatos. Funciona melhor quando há:

- Pelo menos **uma coluna numérica** (valor, total, receita, etc.)
- Opcional: coluna de **data**, coluna de **categoria/grupo** (texto)

Nomes de colunas são **normalizados** (ex.: "Valor Total", "valor_total", "Valor" → tratados como valor). Colunas como "Categoria", "Tipo", "Produto", "Região" são usadas para agrupamentos e gráficos.

---

## 🎨 Estilo visual do PDF

- Paleta: **azul escuro** (#1e3a5f), **cinza** (#6b7280), **branco** e fundo de cards em cinza claro
- Títulos grandes e nítidos, KPIs em cards, gráficos com bordas limpas
- Layout inspirado em relatórios corporativos, branding neutro

---

## 📄 Licença

Uso livre para portfólio e adaptação em projetos clientes.
