# Sistema de Verificação - Pesquisa MJ

Sistema web desenvolvido em Dash para verificação de erros em formulários de pesquisa judicial.

## 📋 Descrição

Esta aplicação permite que coordenadoras de pesquisa verifiquem a qualidade dos dados coletados em formulários sobre processos judiciais. O sistema:

- Conecta-se à API do LimeSurvey para recuperar dados
- Executa validações automáticas nos dados coletados
- Gera relatórios detalhados de erros encontrados
- Apresenta estatísticas de preenchimento dos formulários

## 🚀 Funcionalidades

- **Busca por Processo**: Digite o número do processo para ver todos os dados relacionados
- **Validação Automática**: Executa múltiplas validações nos dados:
  - Validação de processo (número, ano, tribunal)
  - Validação de vítima (nome, idade, gênero)
  - Validação de réu (nome, idade, gênero)  
  - Validação de provas (existência, tipos)
  - Validação de consistência geral
- **Relatórios Detalhados**: Apresenta erros categorizados com severidade
- **Estatísticas**: Mostra percentual de preenchimento dos campos
- **Interface Intuitiva**: Design responsivo e fácil de usar

## 🛠️ Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Acesso à API do LimeSurvey

### Passos de instalação

1. **Clone ou baixe o projeto**
```bash
cd /Users/Marcella/check_pesquisa_mj
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:
```
LIME_API_URL=https://sua-instancia-limesurvey.com/admin/remotecontrol
LIME_USERNAME=seu_usuario
LIME_PASSWORD=sua_senha
SURVEY_ID=123456
```

5. **Execute a aplicação**
```bash
python src/app.py
```

6. **Acesse a aplicação**
Abra seu navegador em: http://localhost:8050

## 📁 Estrutura do Projeto

```
check_pesquisa_mj/
├── src/
│   ├── app.py                 # Aplicação principal
│   ├── config/
│   │   └── settings.py        # Configurações da aplicação
│   ├── data/
│   │   ├── lime_api.py        # Conexão com LimeSurvey
│   │   └── data_processor.py  # Processamento de dados
│   ├── validation/
│   │   ├── conjunto_validator.py    # Validador principal
│   │   ├── processo_validator.py    # Validador de processo
│   │   ├── vitima_validator.py      # Validador de vítima
│   │   ├── reu_validator.py         # Validador de réu
│   │   └── provas_validator.py      # Validador de provas
│   ├── components/
│   │   ├── search_form.py      # Componente de busca
│   │   ├── process_summary.py  # Resumo do processo
│   │   └── error_report.py     # Relatório de erros
│   ├── layouts/
│   │   └── main_layout.py      # Layout principal
│   └── callbacks/
│       └── main_callbacks.py   # Callbacks da aplicação
├── assets/
│   └── style.css              # Estilos CSS
├── requirements.txt           # Dependências Python
├── .env.example              # Exemplo de configuração
└── README.md                 # Este arquivo
```

## 🔧 Configuração

### Mapeamento de Colunas

O arquivo `src/config/settings.py` contém o mapeamento entre os códigos do LimeSurvey e os nomes internos das colunas. Ajuste conforme seu formulário:

```python
COLUMN_MAPPING = {
    'G01Q01': 'processo_numero',
    'G01Q02': 'processo_ano',
    'G01Q03': 'tribunal',
    # ... adicione outros mapeamentos
}
```

### Validações Customizadas

Cada validador pode ser customizado editando os arquivos na pasta `src/validation/`:

- `processo_validator.py`: Validações específicas de processo
- `vitima_validator.py`: Validações específicas de vítima
- `reu_validator.py`: Validações específicas de réu
- `provas_validator.py`: Validações específicas de provas

## 🚀 Uso

1. **Acesse a aplicação** no navegador
2. **Digite o número do processo** no campo de busca
3. **Clique em "Buscar Processo"**
4. **Visualize os resultados**:
   - Resumo do processo com estatísticas
   - Relatório detalhado de erros encontrados
   - Ações disponíveis (download de relatório, atualização)

## 🐛 Solução de Problemas

### Erro de Conexão com LimeSurvey
- Verifique se a URL da API está correta
- Confirme se o usuário e senha estão corretos
- Teste a conectividade com a API externamente

### Nenhum Dado Encontrado
- Verifique se o número do processo está correto
- Confirme se existem respostas no LimeSurvey para este processo
- Verifique o mapeamento de colunas na configuração

### Erros de Validação
- Revise as regras de validação nos arquivos de validador
- Verifique se os dados estão no formato esperado
- Confirme se os campos obrigatórios estão configurados corretamente

## 📝 Desenvolvimento

### Adicionando Novas Validações

1. Edite o validador apropriado em `src/validation/`
2. Adicione o novo teste no método `validate()`
3. Teste a validação com dados reais

### Modificando a Interface

1. Edite os componentes em `src/components/`
2. Atualize o layout em `src/layouts/main_layout.py`
3. Modifique os estilos em `assets/style.css`

### Adicionando Novos Campos

1. Atualize o mapeamento em `src/config/settings.py`
2. Adicione validações apropriadas
3. Modifique os componentes de exibição

## 📄 Licença

Este projeto é de uso interno para pesquisa acadêmica.

## 👥 Suporte

Para dúvidas ou problemas, entre em contato com a equipe de desenvolvimento.
