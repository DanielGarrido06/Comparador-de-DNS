# Ferramenta de Medição de Métricas de Carregamento de Páginas Web com DNS Customizado

Este projeto automatiza a medição de métricas de carregamento de páginas web utilizando diferentes servidores DNS, com interceptação de tráfego via mitmproxy e análise detalhada dos fluxos de rede.

A principal intenção é comparar o valoume de dados transferido entre carregamentos regulares de páginas, e carregamentos feitos com o uso de DNS Sinkholes para bloquear requisições indesejadas, como publicidade.

Atualmente, esse projeto *não restaura as configurações de DNS às originais depois de executado.* Portanto, é necessário restaurá-las manualmente, ou usar o servidor de DNS desejado como o último da lista de servidores a se testar.

## Funcionalidades
- Troca automática do servidor DNS da interface de rede ativa.
- Limpa o cache de DNS do sistema entre medições
- Execução de medições de carregamento de páginas web com Selenium e Firefox, sempre em 1920x1080, para que as medições sejam comparáveis em sites com conteúdo dinâmico baseado em resolução.
- Interceptação e gravação do tráfego HTTP/HTTPS usando mitmproxy.
- Análise dos fluxos capturados para extrair métricas como número de requisições, URLs únicas e volume de dados transferidos.
- Geração de relatórios automáticos em arquivos `.txt` para cada DNS testado.
- Geração de gráficos comparatórios para cada página web visitada

## Estrutura dos Arquivos
- `run_suite.py`: Script principal que coordena a execução dos testes para cada DNS e página.
- `measure_page.py`: Realiza o carregamento da página web e coleta as métricas.
- `analyze_mitm_flows.py`: Analisa os fluxos capturados pelo mitmproxy e gera o relatório.
- `dns_utils.py`: Utilitários para manipulação de DNS e interface de rede no Windows.
- `graphing.py`: Lê os relatórios em texto e gera representações gráficas
- `input.txt`: Listas de Servidores de DNS e URLs a serem testadas.

## Pré-requisitos
- Python 3.8+
- [mitmproxy](https://mitmproxy.org/)
- [Selenium](https://selenium.dev/) e [geckodriver](https://github.com/mozilla/geckodriver) (para Firefox)
- [Matplotlib](https://matplotlib.org/) (para geração dos gráficos)

- Permissões de administrador no Windows (necessário para alterar o DNS)

## Como Usar
1. Instale as dependências necessárias:
   ```bash
   pip install selenium mitmproxy matplotlib
   ```
2. Certifique-se de que o `geckodriver` está no PATH do sistema.
3. Edite o arquivo `input.txt` com os endereços dos servidores DNS (Separados por vírgula, na linha DNS:) e das URLs que deseja testar (um por linha, incluindo o protocolo, ex: https://www.exemplo.com).
4. Execute o script principal como administrador:
   ```bash
   python run_suite.py
   ```
5. Os resultados serão salvos em arquivos `.txt` nomeados conforme o DNS utilizado, e em gráficos na pasta `charts`.

## Observações
- O script deve ser executado como administrador para conseguir alterar o DNS da interface de rede.
- O mitmproxy precisa estar instalado e acessível no PATH.