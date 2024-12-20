GET:
    Exibe os detalhes do leilão.
    - Parâmetros:
        - leilao_id (str): O ID do leilão a ser inspecionado.
    - Retorna:
        - Renderiza a página com os detalhes do leilão.
POST:
    Processa um novo lance.
    - Parâmetros:
        - leilao_id (str): O ID do leilão a ser inspecionado.
        - price (float): O valor do lance submetido pelo usuário.
    - Retorna:
        - Redireciona para a página do leilão com uma mensagem de sucesso ou erro.
    - Ações:
        - Verifica se o leilão existe.
        - Verifica se o lance é válido e superior ao lance atual.
        - Atualiza o lance atual do leilão.
        - Adiciona um novo lance ao banco de dados.
        - Emite uma atualização em tempo real via socketio.
