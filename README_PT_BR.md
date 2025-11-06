# Plugin de Dados de Ações AKShare para Dify

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-green.svg)](https://dify.ai/)
[![AKShare](https://img.shields.io/badge/AKShare-Latest-blue.svg)](https://github.com/akfamily/akshare)

## 📞 Informações de Contato

- **Autor**: shaoxing-xie
- **Email**: sxxiefg@163.com
- **Repositório**: [https://github.com/shaoxing-xie/akshare-stockdata-plugin](https://github.com/shaoxing-xie/akshare-stockdata-plugin)
- **Relatórios de Problemas**: [GitHub Issues](https://github.com/shaoxing-xie/akshare-stockdata-plugin/issues)

## 📋 Visão Geral

**Plugin de Dados de Ações AKShare** é uma ferramenta abrangente de dados de ações desenvolvida especificamente para a plataforma Dify, construída na renomada biblioteca Python [AKShare](https://github.com/akfamily/akshare). Este plugin oferece aos usuários uma solução de acesso a dados do mercado de ações em um só lugar, cobrindo múltiplas dimensões de informações profissionais sobre ações, incluindo cotações em tempo real, dados históricos, análise financeira, fluxo de capital, análise técnica e Shanghai-Shenzhen-Hong Kong Stock Connect.

> **Destaques de Funcionalidades**: Fornece 78 ferramentas profissionais e 190+ interfaces de dados, cobrindo mercados de ações globais. Veja a [Documentação Completa de Funcionalidades](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md) para todos os detalhes de interfaces, guias de parâmetros e referências técnicas.

> **Aviso Importante**: Este plugin é uma ferramenta de integração da plataforma Dify baseada na biblioteca AKShare. AKShare é uma biblioteca de interface de dados financeiros de código aberto projetada para fins de pesquisa acadêmica. Expressamos nossa sincera gratidão à equipe do projeto AKShare por seu excelente trabalho.

> **⚠️ Aviso de Atualização de Interface**: Devido a problemas de estabilidade de transmissão de rede, as seguintes 8 interfaces de análise de acionistas foram removidas:
> - `stock_gdfx_free_holding_analyse_em` - Análise de Participação de Acionistas (Top 10 Acionistas Circulantes)
> - `stock_gdfx_holding_analyse_em` - Análise de Participação de Acionistas (Top 10 Acionistas)
> - `stock_gdfx_free_holding_detail_em` - Detalhes de Participação de Acionistas (Top 10 Acionistas Circulantes)
> - `stock_gdfx_holding_detail_em` - Detalhes de Participação de Acionistas (Top 10 Acionistas)
> - `stock_gdfx_free_holding_statistics_em` - Estatísticas de Participação de Acionistas (Top 10 Acionistas)
> - `stock_gdfx_holding_statistics_em` - Estatísticas de Participação de Acionistas (Top 10 Acionistas)
> - `stock_gdfx_free_holding_change_em` - Estatísticas de Mudança de Participação de Acionistas (Top 10 Acionistas Circulantes)
> - `stock_gdfx_holding_change_em` - Estatísticas de Mudança de Participação de Acionistas (Top 10 Acionistas)
> 
> Outras interfaces relacionadas a acionistas (Top 10 Acionistas, etc.) permanecem disponíveis.

## 🚀 Características Principais

### 💎 **Sem Necessidade de Chave API**
- ✅ **Uso Zero Configuração**: Não é necessário solicitar chaves API ou tokens
- ✅ **Plug and Play**: Pronto para uso imediatamente após a instalação, sem configuração complexa
- ✅ **Economia de Custos**: Completamente gratuito para usar, sem limites de uso

### 🌐 **Fontes de Dados Autoritativas**
- 📊 **Eastmoney**: Cotações em tempo real, dados financeiros, análise de mercado
- 📈 **Sina Finance**: Cotações históricas, notícias de ações
- 🏢 **Tonghuashun**: Indicadores técnicos, análise de fluxo de capital
- 💰 **Tencent Finance**: Dados de ações de Hong Kong e EUA
- 📱 **NetEase Finance**: Visão geral do mercado, informações de ações individuais
- 🔗 **APIs Públicas**: Interfaces de dados oficiais das bolsas de valores

### 🛠️ **Matriz de Funcionalidades Poderosas**
- 🎯 **78 Ferramentas Profissionais**: Cobrindo todos os aspectos da análise de dados de ações
  - **Categorizadas por Domínio Funcional**: Visão geral do mercado, informações de ações individuais, dados de cotações, dados financeiros, fluxo de capital, análise técnica e 12 grandes domínios funcionais
  - **Design Granular**: Cada ferramenta foca em funcionalidade específica para invocação precisa
- 🌍 **190+ Interfaces de Dados**: Cobertura ampla dos principais mercados de ações globais
- 📊 **Suporte Multi-Mercado**: A-shares, B-shares, Hong Kong, EUA, STAR Market, BSE
- 🔄 **Tempo Real + Histórico**: Tanto cotações em tempo real quanto análise de dados históricos
- 📋 **Saída Dupla**: Tabelas Markdown + formato JSON, fácil de ler e processar
- 📈 **Análise Técnica**: Ferramentas profissionais de cálculo e análise de indicadores técnicos

### 🔧 **Vantagens Técnicas**
- 🛡️ **Tratamento Inteligente de Erros**: Mecanismo de retry automático, recuperação elegante de erros
- 🌐 **Suporte Completo Unicode**: Processamento perfeito de caracteres chineses e símbolos especiais
- ⚡ **Otimização de Performance**: Isolamento de subprocesso, gerenciamento eficiente de memória
- 🔄 **Validação de Parâmetros**: Validação automática de parâmetros e conversão de formato

## 👥 Público-Alvo

### 🎓 **Pesquisadores Acadêmicos**
- Pesquisadores de finanças realizando análise de mercado e pesquisa acadêmica
- Acadêmicos de economia estudando padrões de volatilidade do mercado de ações
- Pesquisadores de ciência de dados realizando análise quantitativa

### 🤖 **Desenvolvedores de Aplicações de IA**
- Construindo assistentes de investimento inteligentes e chatbots financeiros
- Desenvolvendo sistemas de recomendação de ações baseados em IA
- Criando ferramentas de análise de dados financeiros automatizadas

### 💼 **Profissionais Financeiros**
- Analistas financeiros precisando de acesso rápido a dados de mercado
- Gestores de portfólio monitorando posições de ações
- Consultores de investimento fornecendo insights baseados em dados

## 📥 Download Rápido

[![Download Plugin](https://img.shields.io/badge/Download-Plugin%20Package-blue)](https://github.com/shaoxing-xie/akshare-stockdata-plugin/releases/tag/v0.7.0)

**Download Direto do Pacote de Plugin Mais Recente** | [Ver Todas as Versões](https://github.com/shaoxing-xie/akshare-stockdata-plugin/releases)

## 🛠️ Detalhes das Ferramentas

O plugin fornece **78 ferramentas profissionais**, categorizadas por domínio funcional da seguinte forma:

### 📊 **I. Ferramentas de Visão Geral do Mercado** (20 ferramentas)
Obter visão geral do mercado e dados estatísticos, incluindo visão geral do mercado de bolsas, dados de penhora de ações, dados de goodwill, estatísticas de contas de ações, subscrição de IPO, notificações de eventos de negociação, participações institucionais, avaliação de classificação, anúncios de empresas, lista de dragão e tigre, negociação em bloco, negociação de margem, dados de setores, dados de popularidade de ações, dados de limite de alta/baixa, etc.

| Nome da Ferramenta | Função Principal | Casos de Uso |
|-------------------|------------------|--------------|
| **Obter Visão Geral do Mercado de Bolsas** | Dados de visão geral do mercado SSE e SZSE | Análise de mercado, pesquisa macroeconômica |
| **Obter Dados de Penhora de Ações** | Visão geral do mercado de penhora de ações, proporção de penhora de empresas listadas | Monitoramento de risco, análise de penhora |
| **Obter Dados de Goodwill** | Visão geral do mercado de goodwill, detalhes de goodwill de ações individuais | Análise de goodwill, monitoramento de depreciação |
| **Obter Estatísticas de Contas de Ações** | Dados estatísticos mensais de contas de ações | Análise de participação no mercado |
| **Obter Dados de Número de Acionistas do Mercado A-shares** | Dados estatísticos de número de acionistas | Análise de estrutura de acionistas |
| **Obter Dados de Comentários de Ações** | Dados de comentários de ações | Análise de sentimento do mercado |
| **Obter Dados de Subscrição de IPO** | Dados de subscrição e loteria de IPO | Análise de IPO, estratégia de novas ações |
| **Obter Notificações de Eventos de Negociação** | Alertas de suspensão/retomada, dividendos | Alertas de negociação, monitoramento de eventos |
| **Obter Dados de Participações Institucionais do Mercado** | Visão geral de participações institucionais, pool de recomendações | Análise de tendências institucionais |
| **Obter Registros de Classificação e Avaliação de Ações** | Registros de classificação de ações, análise de avaliação | Classificação de investimento, pesquisa de avaliação |
| **Obter Dados de Anúncios de Empresas** | Notícias de empresas, anúncios importantes | Rastreamento de eventos de empresas |
| **Obter Dados de Divulgação de Empresas** | Dados de divulgação de empresas | Análise de divulgação |
| **Obter Dados de Lista de Ações** | Códigos e nomes de ações A-shares de Shanghai-Shenzhen-Beijing | Consulta de lista de ações |
| **Obter Lista de Dragão e Tigre** | Dados de negociação da lista de dragão e tigre | Análise de fluxo de capital |
| **Obter Negociação em Bloco** | Dados de negociação em bloco | Análise de grandes transações |
| **Obter Negociação de Margem do Mercado A-shares** | Dados de negociação de margem | Análise de capital alavancado |
| **Obter Dados de Setores Flush** | Dados de setores de conceitos e indústrias Flush | Análise de setores, investimento temático |
| **Obter Dados de Setores East Money** | Dados de setores de conceitos e indústrias East Money | Análise de setores, pesquisa de indústria |
| **Obter Dados de Popularidade de Ações do Mercado A-shares** | Rankings de popularidade de ações | Análise de popularidade do mercado |
| **Obter Dados de Limite de Alta/Baixa do Mercado A-shares** | Dados de limite de alta/baixa | Análise de limite de alta, monitoramento de risco |

### 🏢 **II. Ferramentas de Informações de Ações Individuais** (6 ferramentas)
Obter informações básicas de ações individuais, notícias e relatórios de pesquisa, informações de dividendos, mudanças de participação de acionistas, números de acionistas, dados de emissão e listagem de ações, etc.

| Nome da Ferramenta | Função Principal | Casos de Uso |
|-------------------|------------------|--------------|
| **Obter Informações Básicas de Ações** | Informações de ações, introdução do negócio principal, composição do negócio principal, perfil da empresa | Análise fundamental, pesquisa de empresas |
| **Obter Notícias e Relatórios de Pesquisa de Ações** | Informações de notícias, relatórios de pesquisa de ações individuais | Rastreamento de informações, análise de relatórios |
| **Obter Informações de Dividendos de Ações** | Detalhes de distribuição de dividendos, dividendos históricos | Análise de dividendos, investimento em dividendos |
| **Obter Mudanças de Participação de Acionistas** | Top 10 acionistas, top 10 acionistas circulantes, mudanças de participação | Análise de estrutura de acionistas |
| **Obter Detalhes de Número de Acionistas A-shares** | Dados detalhados de número de acionistas | Análise de dispersão de acionistas |
| **Obter Dados de Emissão e Lançamento de Ações** | Emissão de novas ações, emissão adicional de ações, liberação de ações restritas | Análise de emissão e listagem |

### 📈 **III. Ferramentas de Dados de Cotações** (8 ferramentas)
Obter cotações em tempo real, cotações históricas, cotações intradiárias, dados de comparação para vários mercados, etc.

| Nome da Ferramenta | Função Principal | Casos de Uso |
|-------------------|------------------|--------------|
| **Obter Cotação em Tempo Real de Ações** | Cotação em tempo real de ações individuais | Monitoramento em tempo real, decisões de negociação |
| **Obter Cotações Históricas de Ações** | Dados diários e de minuto de A-shares | Análise técnica, pesquisa de backtesting |
| **Obter Cotações Intradiárias de Ações** | Dados de minuto intradiários, dados de minuto | Análise intradiária, análise de livro de ordens |
| **Obter Comparação de Pares de Ações** | Crescimento, avaliação, análise DuPont, comparação de tamanho da empresa | Comparação de indústria, análise de avaliação |
| **Obter Cotações de Ações do Mercado A-shares** | Cotações em tempo real de A-shares de Shanghai-Shenzhen-Beijing | Monitoramento de cotações de mercado |
| **Obter Cotações de Setores A-shares** | Cotações em tempo real de novas ações, ChiNext, STAR Market | Análise de cotações de setores |
| **Obter Dados de Comparação de Ações** | Comparação de ações AH, comparação de ações AB | Comparação entre mercados |
| **Obter Cotações de Ações Especiais** | Sub-novas ações, duas redes e ações delistadas | Análise de ações especiais |

### 💰 **IV. Ferramentas de Dados Financeiros** (6 ferramentas)
Obter demonstrações financeiras e dados de desempenho, incluindo relatórios de desempenho, balanços patrimoniais, demonstrações de resultados, demonstrações de fluxo de caixa, indicadores financeiros, etc.

| Nome da Ferramenta | Função Principal | Casos de Uso |
|-------------------|------------------|--------------|
| **Obter Dados de Relatórios de Desempenho A-shares** | Demonstrações de desempenho, relatórios de desempenho, previsões de desempenho | Análise de desempenho, rastreamento de desempenho |
| **Obter Balanço Patrimonial A-shares** | Dados de balanço patrimonial | Análise financeira, análise de solvência |
| **Obter Demonstração de Resultados A-shares** | Dados de demonstração de resultados | Análise de rentabilidade |
| **Obter Demonstração de Fluxo de Caixa A-shares** | Dados de demonstração de fluxo de caixa | Análise de fluxo de caixa |
| **Obter Indicadores Financeiros A-shares** | Dados de indicadores financeiros | Análise de indicadores financeiros |
| **Obter Indicadores de Análise Financeira A-shares** | Dados de indicadores de análise financeira | Análise financeira abrangente |

### 🌊 **V. Ferramentas de Fluxo de Capital** (6 ferramentas)
Analisar fluxo de capital e sentimento do mercado, incluindo fluxo de capital de ações individuais, fluxo de capital de setores, fluxo de capital da força principal, distribuição de chips, etc.

| Nome da Ferramenta | Função Principal | Casos de Uso |
|-------------------|------------------|--------------|
| **Obter Fluxo de Fundos de Ações** | Dados de fluxo de fundos de ações individuais | Análise de fluxo de capital |
| **Obter Distribuição de Chips de Ações** | Dados de distribuição de chips | Análise de chips |
| **Obter Ranking de Fluxo de Fundos de Ações do Mercado** | Dados de ranking de fluxo de fundos | Análise de fluxo de fundos |
| **Obter Histórico de Fluxo de Fundos do Mercado** | Dados históricos de fluxo de fundos | Análise de tendências de fluxo de fundos |
| **Obter Ranking de Fluxo de Fundos de Setores** | Rankings de fluxo de fundos de setores | Análise de capital de setores |
| **Obter Rastreamento de Grandes Negócios** | Dados de rastreamento de grandes negócios | Rastreamento de tendências da força principal |

### 📈 **VI. Ferramentas de Análise Técnica** (7 ferramentas)
Indicadores técnicos e dados de inovação alta/baixa, incluindo altas/baixas de inovação, subida/queda contínua, análise de volume, análise de ruptura, análise de preço-volume, classificações ESG, etc.

| Nome da Ferramenta | Função Principal | Casos de Uso |
|-------------------|------------------|--------------|
| **Obter Inovação Alta/Baixa Técnica** | Ações de inovação alta, ações de inovação baixa | Seleção técnica de ações, análise de tendências |
| **Obter Subida/Queda Contínua Técnica** | Ações de subida contínua, ações de queda contínua | Análise de tendências, análise de reversão |
| **Obter Análise de Volume Técnica** | Ações de aumento contínuo de volume, ações de diminuição contínua de volume | Análise de preço-volume |
| **Obter Análise de Ruptura Técnica** | Ações de ruptura ascendente, ações de ruptura descendente | Análise de ruptura, julgamento de tendências |
| **Obter Análise de Preço-Volume Técnica** | Ações de subida de preço-volume, ações de queda de preço-volume | Análise de relação preço-volume |
| **Obter Divulgação de Seguro Técnica** | Dados de placard raising de capital de seguro | Tendências de capital de seguro |
| **Obter Dados de Classificação ESG** | Dados de classificação ESG | Investimento ESG, investimento em responsabilidade social |

### 📉 **VII. Ferramentas de Indicadores Técnicos** (5 ferramentas) ⭐ **Ferramentas de Indicadores Estendidas**
Ferramentas de análise abrangente baseadas em dados históricos de ações individuais calculando vários indicadores técnicos.

| Nome da Ferramenta | Função Principal | Casos de Uso |
|-------------------|------------------|--------------|
| **Obter Indicadores de Tendência e Momentum Diários de Ações** | Cálculo de indicadores técnicos diários | Análise técnica, pesquisa quantitativa |
| **Obter Indicadores de Tendência e Momentum de Minuto de Ações** | Cálculo de indicadores técnicos de nível de minuto | Análise de alta frequência, negociação intradiária |
| **Obter Indicadores de Avaliação Dinâmica de Ações** | Indicadores de avaliação dinâmica | Análise de avaliação, decisões de investimento |
| **Obter Indicadores de Avaliação Histórica de Ações** | Indicadores de avaliação histórica | Análise de tendências de avaliação |
| **Obter Resumo de Informações Básicas de Ações** | Resumo de informações básicas de ações individuais | Consulta abrangente de informações |

### 🔗 **VIII. Ferramentas HSGT** (4 ferramentas)
Dados de participações e fluxo de capital norte, incluindo dados de taxa de câmbio, fluxo de capital, dados de ranking, participações de ações individuais, etc.

| Nome da Ferramenta | Função Principal | Casos de Uso |
|-------------------|------------------|--------------|
| **Obter Dados de Taxa de Câmbio HSGT** | Dados de taxa de câmbio do Hong Kong Stock Connect | Análise de taxa de câmbio, análise de capital transfronteiriço |
| **Obter Dados de Fluxo de Fundos HSGT** | Dados de fluxo de fundos | Análise de tendências de capital estrangeiro |
| **Obter Dados de Ranking HSGT** | Rankings de setores, rankings de ações | Análise de participações de capital estrangeiro |
| **Obter Participações Individuais HSGT** | Dados de participações de ações específicas | Análise de participações de capital estrangeiro de ações individuais |

### 📊 **IX. Ferramentas de Dados de Índices** (3 ferramentas) ⭐ **Ferramentas de Análise de Índices**
Interfaces de dados relacionadas a índices A-shares, incluindo cotações em tempo real de índices, dados históricos, indicadores técnicos, etc.

| Nome da Ferramenta | Função Principal | Casos de Uso |
|-------------------|------------------|--------------|
| **Obter Cotações em Tempo Real de Índices A-shares** | Dados de cotações em tempo real de índices | Monitoramento de índices, tendências de mercado |
| **Obter Cotações Históricas de Índices A-shares** | Dados de cotações históricas de índices | Análise de índices, pesquisa técnica |
| **Obter Indicadores de Tendência e Momentum Diários de Índices** | Cálculo de indicadores técnicos de índices | Análise técnica de índices |

### 🇭🇰 **X. Ferramentas de Dados de Ações de Hong Kong** (8 ferramentas) ⭐ **Ferramentas Independentes**
Interfaces de dados relacionadas a ações de Hong Kong, incluindo cotações em tempo real de ações de Hong Kong, dados históricos, análise financeira, informações de empresas, informações de dividendos, etc.

| Nome da Ferramenta | Função Principal | Casos de Uso |
|-------------------|------------------|--------------|
| **Obter Informações Individuais de HK** | Informações básicas individuais de ações de Hong Kong | Análise fundamental de ações de Hong Kong |
| **Obter Cotações Históricas de HK** | Dados de cotações históricas de ações de Hong Kong | Análise técnica de ações de Hong Kong |
| **Obter Cotações de Minuto Diárias de HK** | Dados de cotações de minuto de ações de Hong Kong | Análise intradiária de ações de Hong Kong |
| **Obter Pagamento de Dividendos de HK** | Dados de pagamento de dividendos de ações de Hong Kong | Análise de dividendos de ações de Hong Kong |
| **Obter Indicadores Financeiros de HK** | Dados de indicadores financeiros de ações de Hong Kong | Análise financeira de ações de Hong Kong |
| **Obter Demonstrações Financeiras de HK** | Dados de demonstrações financeiras de ações de Hong Kong | Análise de demonstrações financeiras de ações de Hong Kong |
| **Obter Comparação de Indústria de HK** | Dados de comparação de indústria de ações de Hong Kong | Comparação de indústria de ações de Hong Kong |
| **Obter Cotações em Tempo Real de HK** | Dados de cotações em tempo real de ações de Hong Kong | Monitoramento em tempo real de ações de Hong Kong |

### 🇺🇸 **XI. Ferramentas de Dados de Ações dos EUA** (5 ferramentas) ⭐ **Ferramentas Independentes**
Interfaces de dados relacionadas a ações dos EUA, incluindo cotações em tempo real de ações dos EUA, dados históricos, análise financeira, etc.

| Nome da Ferramenta | Função Principal | Casos de Uso |
|-------------------|------------------|--------------|
| **Obter Cotações em Tempo Real dos EUA** | Dados de cotações em tempo real de ações dos EUA | Monitoramento em tempo real de ações dos EUA |
| **Obter Cotações Históricas dos EUA** | Dados de cotações históricas de ações dos EUA | Análise técnica de ações dos EUA |
| **Obter Cotações de Minuto Diárias dos EUA** | Dados de cotações de minuto de ações dos EUA | Análise intradiária de ações dos EUA |
| **Obter Indicadores Financeiros dos EUA** | Dados de indicadores financeiros de ações dos EUA | Análise financeira de ações dos EUA |
| **Obter Demonstrações Financeiras dos EUA** | Dados de demonstrações financeiras de ações dos EUA | Análise de demonstrações financeiras de ações dos EUA |

---

**Estatísticas de Ferramentas**:
- **Total**: 78 ferramentas profissionais
- **Interfaces de Dados**: 190+ interfaces de dados
- **Cobertura Funcional**: Visão geral do mercado, informações de ações individuais, dados de cotações, dados financeiros, fluxo de capital, análise técnica, indicadores técnicos, HSGT, dados de índices, dados de ações de Hong Kong, dados de ações dos EUA e 12 grandes domínios funcionais

## 📦 Como Instalar

### Método 1: Download Direto e Instalação (Recomendado)

[![Download Plugin](https://img.shields.io/badge/Download-Plugin%20Package-blue)](https://github.com/shaoxing-xie/akshare-stockdata-plugin/releases/tag/v0.7.0)

1. **Download Rápido**: Clique no botão acima para baixar diretamente o pacote de plugin mais recente
2. **Instalar no Dify**:
   - Abra seu workspace do Dify
   - Navegue para **Ferramentas** → **Plugins** → **Instalar Plugin**
   - Selecione **"Instalar do Arquivo"**
   - Carregue o arquivo `.difypkg` baixado
   - Clique no botão **Instalar**

### Método 2: Download do Diretório Releases
1. Visite o [diretório releases](https://github.com/shaoxing-xie/akshare-stockdata-plugin/tree/main/releases)
2. Baixe o arquivo **"AKShare-Stockdata-plugin-v0.7.0.difypkg"**
3. Siga as etapas do Método 1 para instalar no Dify

### Método 3: Via GitHub Releases
1. Visite [GitHub Releases](https://github.com/shaoxing-xie/akshare-stockdata-plugin/releases)
2. Baixe o pacote de plugin da versão mais recente
3. Siga as etapas do Método 1 para instalar no Dify

### Método 4: Instalação Manual
1. Clone este repositório localmente
   ```bash
   git clone https://github.com/shaoxing-xie/akshare-stockdata-plugin.git
   ```
2. Instale as dependências Python
   ```bash
   cd akshare-stockdata-plugin
   pip install -r requirements.txt
   ```
3. Empacote o plugin usando Dify CLI
   ```bash
   dify plugin package
   ```
4. Carregue o arquivo .difypkg gerado no Dify

Após a instalação, consulte a [Documentação Detalhada de Funcionalidades](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md) para entender rapidamente todas as interfaces.

## 🎯 Como Usar

### Início Rápido em Três Etapas
1. **Selecionar Ferramenta**: Escolha entre 78 ferramentas profissionais (categorizadas por domínio funcional)
2. **Selecionar Interface**: Escolha entre 190+ interfaces de dados para fontes de dados específicas
3. **Configurar Parâmetros**: Configure códigos de ações, intervalos de datas e outros parâmetros

### Exemplos de Uso

#### Obter Cotações Históricas de Ações
```json
{
  "interface": "East Money - Dados de Mercado Histórico A-shares",
  "symbol": "600519",
  "period": "daily",
  "start_date": "20240101",
  "end_date": "20241231",
  "adjust": "qfq"
}
```

#### Obter Dados de Cotação em Tempo Real
```json
{
  "interface": "East Money - Mercado em Tempo Real de Ações A-shares de Xangai",
  "symbol": "600519"
}
```

#### Consultar Dados Financeiros de Ações Individuais
```json
{
  "interface": "East Money - Relatório Expresso de Desempenho - Balanço Patrimonial",
  "date": "20240331"
}
```

Mais exemplos veja a [Documentação Detalhada de Funcionalidades](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md).

## 🔒 Privacidade e Segurança

Este plugin adere estritamente aos princípios de proteção de privacidade de dados:
- ✅ **Sem Armazenamento de Dados do Usuário**: Todos os dados são processados apenas na memória, sem armazenamento persistente
- ✅ **Sem Coleta de Informações Pessoais**: Não obtém ou transmite informações pessoais sensíveis do usuário  
- ✅ **Processamento Transparente de Dados**: Todas as fontes de dados e procedimentos de processamento são completamente transparentes
- ✅ **Auditável de Código Aberto**: Código-fonte completamente aberto para revisão e verificação

Para informações detalhadas, consulte a [Política de Privacidade](PRIVACY.md)

Combine com a [Documentação Detalhada de Funcionalidades](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md) para entender os detalhes do processamento de dados.

## ⚖️ Declaração de Conformidade

Este plugin está totalmente em conformidade com os requisitos legais e regulamentares relevantes:
- 📋 **Conformidade de Código Aberto**: Projeto de código aberto baseado na licença MIT
- 🌐 **Conformidade de Dados**: Usa apenas fontes de dados publicamente acessíveis
- 🔍 **Operações Transparentes**: Métodos de aquisição de dados e procedimentos de processamento são completamente transparentes
- ⚖️ **Conformidade Legal**: Adere estritamente aos regulamentos relevantes de uso de dados financeiros

Para informações detalhadas, consulte o [Aviso Legal](LEGAL.md)

## 🙏 Agradecimentos

### Equipe do Projeto AKShare
Este plugin é construído na excelente biblioteca [AKShare](https://github.com/akfamily/akshare). Expressamos nossa sincera gratidão a:
- **Equipe de Desenvolvimento AKShare**: Por criar e manter esta biblioteca abrangente de interfaces de dados financeiros
- **Contribuidores da Comunidade de Código Aberto**: Por contribuições valiosas para o desenvolvimento do projeto

### Plataforma Dify
Agradecemos à equipe [Dify](https://dify.ai/) por fornecer uma excelente plataforma de desenvolvimento de aplicações de IA que torna as aplicações de IA para dados financeiros mais convenientes.

## 📄 Licença

Este projeto está licenciado sob a **Licença MIT** - veja o arquivo [LICENSE](LICENSE) para detalhes.

**Nota**: Este plugin é uma ferramenta wrapper para a biblioteca AKShare. Para funcionalidade de acesso a dados subjacente, consulte os termos da licença MIT do AKShare.

## 🤝 Contribuindo

Acolhemos contribuições da comunidade! Siga estes passos para participar:

1. Fork este repositório
2. Crie uma branch de funcionalidade (`git checkout -b feature/AmazingFeature`)
3. Faça commit de suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Crie um Pull Request

## 📞 Suporte Técnico

Se você encontrar problemas ou tiver sugestões:
1. Verifique a página [Issues](https://github.com/shaoxing-xie/akshare-stockdata-plugin/issues)
2. Crie um novo issue com informações detalhadas
3. Consulte a documentação oficial do AKShare

## 🔄 Atualização de Versão

### Atualizando de 0.6.0 para 0.7.0
- ✅ **Otimização de Divisão de Ferramentas**: Dividido de 12 ferramentas grandes em 78 ferramentas granulares para invocação mais precisa
- ✅ **Classificação por Domínio Funcional**: Exibido por domínio funcional para busca e uso mais fáceis
- ✅ **Totalmente Compatível com Versões Anteriores**: Todos os workflows baseados na versão 0.6.0 podem ser usados diretamente sem modificação
- ✅ **Aprimoramento de Funcionalidades**: Mais interfaces de dados e funcionalidades

👉 **[Guia Detalhado de Atualização](UPGRADE_GUIDE.md)** - Instruções completas de atualização de versão

## 📚 Documentação Detalhada de Funcionalidades

O plugin fornece 78 ferramentas profissionais com 190+ interfaces de dados. Para manter o README conciso, a documentação detalhada de interfaces foi separada em um documento técnico dedicado:

### 📖 **Documentação Técnica Completa**
👉 **[Documentação Detalhada de Funcionalidades do Plugin de Dados de Ações AKShare.md](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md)** - Sua Referência de Interfaces!

Este documento contém:
- ✅ **190+ descrições completas de interfaces** - Função, parâmetros e informações de referência AKShare para cada interface
- ✅ **78 classificações detalhadas de ferramentas** - Lista completa de ferramentas categorizadas por domínio funcional  
- ✅ **Guia de uso de parâmetros** - Instruções detalhadas de entrada de parâmetros e requisitos de formato
- ✅ **Informações de referência técnica** - Referências completas de interfaces AKShare e URLs de destino

### 🎯 **Navegação Rápida (Categorizada por Domínio Funcional)**
- [I. Ferramentas de Visão Geral do Mercado (20 ferramentas)](AKShare%20股票数据插件详细功能文档.md#一市场总貌类工具)
- [II. Ferramentas de Informações de Ações Individuais (6 ferramentas)](AKShare%20股票数据插件详细功能文档.md#二个股信息类工具)
- [III. Ferramentas de Dados de Cotações (8 ferramentas)](AKShare%20股票数据插件详细功能文档.md#三行情数据类工具)
- [IV. Ferramentas de Dados Financeiros (6 ferramentas)](AKShare%20股票数据插件详细功能文档.md#四财务数据类工具)
- [V. Ferramentas de Fluxo de Capital (6 ferramentas)](AKShare%20股票数据插件详细功能文档.md#五资金流向类工具)
- [VI. Ferramentas de Análise Técnica (7 ferramentas)](AKShare%20股票数据插件详细功能文档.md#六技术分析类工具)
- [VII. Ferramentas de Indicadores Técnicos (5 ferramentas)](AKShare%20股票数据插件详细功能文档.md#七技术指标类工具) ⭐ **Ferramentas de Indicadores Estendidas**
- [VIII. Ferramentas HSGT (4 ferramentas)](AKShare%20股票数据插件详细功能文档.md#八沪深港通类工具)
- [IX. Ferramentas de Dados de Índices (3 ferramentas)](AKShare%20股票数据插件详细功能文档.md#九指数数据类工具) ⭐ **Ferramentas de Análise de Índices**
- [X. Ferramentas de Dados de Ações de Hong Kong (8 ferramentas)](AKShare%20股票数据插件详细功能文档.md#十港股数据类工具) ⭐ **Ferramentas Independentes**
- [XI. Ferramentas de Dados de Ações dos EUA (5 ferramentas)](AKShare%20股票数据插件详细功能文档.md#十一美股数据类工具) ⭐ **Ferramentas Independentes**

## 🎯 Demonstração e Exemplos

### 📋 **Demonstração de Workflow Dify**

Fornecemos dois arquivos de demonstração de workflow Dify completos que mostram como usar vários recursos do Plugin de Dados de Ações AKShare:

#### 🔧 **Arquivo de Demonstração 1: Demonstração de Funcionalidade do Plugin**
**Arquivo**: `应用示例/AKShare 股票数据插件 CHATFLOW-DEMO.yml`

**Descrição**: Demonstra o uso de todas as ferramentas do plugin e suas interfaces, mostrando a funcionalidade completa de 78 ferramentas profissionais

**Conteúdo da Demonstração**:
- **Resumo do Mercado de Ações** - Aquisição de dados de visão geral do mercado
- **Resumo de Informações de Ações Individuais** - Consultas de informações detalhadas de ações individuais
- **Cotações de Ações em Tempo Real** - Aquisição de dados de preços em tempo real
- **Cotações Históricas de Ações** - Análise de dados de preços históricos
- **Participações Shanghai-Shenzhen-Hong Kong Stock Connect** - Participações de capital norte
- **Análise de Fluxo de Capital** - Análise de dados de fluxo de capital
- **Análise de Dados Financeiros de Ações** - Aquisição de dados de demonstrações financeiras
- **Análise Técnica de Ações** - Cálculos de indicadores técnicos

**Recursos da Demonstração**:
- **Ramificação Condicional Inteligente** - Seleciona automaticamente interfaces de dados apropriadas com base na entrada do usuário
- **Conversão de Formato de Dados** - Converte automaticamente tabelas Markdown para arquivos Excel
- **Exibição Multi-dimensional** - Cobre cenários de uso para todas as 78 ferramentas profissionais
- **Workflow Completo** - Processo completo da aquisição de dados à exibição de resultados

#### 🤖 **Arquivo de Demonstração 2: Aplicação de Análise Profunda de Ações Individuais**
**Arquivo**: `应用示例/个股行情分析-ChatFlow.yml`

**Descrição**: Aplicação ChatFlow de análise profunda de ações individuais baseada no Plugin de Dados de Ações AKShare, fornecendo análise multi-dimensional de ações

**Recursos Principais**:
- **Reconhecimento Inteligente de Ações** - Identifica automaticamente códigos de ações e tipos de mercado (A-shares de Xangai, A-shares de Shenzhen, Bolsa de Valores de Pequim)
- **Análise de Cotações Históricas** - Análise técnica baseada em dados históricos de um ano
- **Análise de Indicadores Financeiros** - Análise fundamental baseada em dados financeiros
- **Análise de Fluxo de Fundos** - Análise de fluxo de fundos baseada em dados de fluxo de capital
- **Relatórios de Pesquisa de Ações Individuais** - Acesso aos relatórios de pesquisa mais recentes de ações individuais
- **Recomendações de Investimento Abrangentes** - Recomendações de investimento baseadas em dados multi-dimensionais

**Recursos Técnicos**:
- **Cálculo Dinâmico de Datas** - Calcula automaticamente o intervalo de tempo mais recente dos dados históricos
- **Validação do Mercado A-shares** - Identifica e valida inteligentemente códigos de ações A-shares
- **Integração de Múltiplas Fontes de Dados** - Integra cotações históricas, dados financeiros, fluxo de fundos, relatórios de pesquisa e outros dados multi-dimensionais
- **Relatórios de Análise Profissional** - Gera relatórios de análise abrangentes incluindo aspectos técnicos, fundamentais e de fluxo de fundos

#### 🔧 **Como Usar a Demonstração**
1. Importe o arquivo de demonstração correspondente na plataforma Dify
2. Certifique-se de que o Plugin de Dados de Ações AKShare está instalado
3. Execute o workflow para experimentar vários recursos de dados de ações
4. Modifique e personalize o workflow conforme necessário

Para suporte e perguntas:
- Abra uma issue no GitHub
- Consulte a documentação oficial
- Entre em contato com a equipe de desenvolvimento

## 🔧 Solução de Problemas

### ❌ **Problemas Comuns e Soluções**

#### 1. **Plugin Não Exibido nas Ferramentas do Dify Após Instalação**
**Sintomas**: Após a instalação do plugin, o plugin não está visível na lista de ferramentas do Dify

**Possíveis Causas e Soluções**:

**Caso 1: Pré-compilação Ainda Não Completa**
- ⏰ **Verificar Status da Pré-compilação**: Verificar os logs de execução do plugin no backend do Dify para confirmar se a pré-compilação ainda está em andamento
- 📊 **Monitorar Progresso**: O processo de pré-compilação geralmente leva 5-15 minutos, aguarde pacientemente
- 🔍 **Verificar Logs**: Verificar os logs de execução do plugin no backend administrativo do Dify para confirmar o progresso da compilação

**Caso 2: Pré-compilação Completa Mas Ferramentas Não Exibidas**
- 🔄 **Reinstalar**: Após a pré-compilação estar completa, se o plugin ainda não estiver exibido nas ferramentas do Dify, instale o pacote do plugin novamente, e o plugin será exibido normalmente
- ✅ **Comportamento Normal**: Este é um problema conhecido do sistema de plugins do Dify, reinstalar resolverá o problema

**Notas Técnicas**:
- Configuração de timeout de pré-compilação: 30 minutos (suficiente para completar a compilação)
- Arquivo `.difyignore` otimizado para excluir arquivos de teste e acelerar a compilação
- Este é um problema comum do sistema de plugins do Dify que pode afetar todos os plugins

#### 2. **Chamada de Ferramenta Retorna Dados Vazios**
**Sintomas**: A chamada da ferramenta é bem-sucedida mas retorna `{"data": []}`

**Possíveis Causas**:
- Problemas de conexão de rede
- Fonte de dados temporariamente indisponível
- Erros de configuração de parâmetros

**Soluções**:
- Verificar conexão de rede
- Aumentar contagem de tentativas e duração do timeout
- Verificar formato dos parâmetros (formato de data: YYYYMMDD)

#### 3. **Problemas de Compatibilidade Dify 0.3.0+**
**Sintomas**: O plugin não pode funcionar adequadamente em versões mais recentes do Dify

**Soluções**:
- Garantir o uso do pacote de plugin mais recente
- Verificar configuração do arquivo `.env`:
  ```env
  FORCE_VERIFYING_SIGNATURE=false
  PLUGIN_PYTHON_ENV_INIT_TIMEOUT=600
  ```

---

**Última Atualização**: 2025-11-06  
**Versão**: 0.7.0  
**Autor**: Equipe do Plugin de Dados de Ações AKShare  
**Licença**: MIT License
