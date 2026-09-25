# Solar

Painel estático (`index.html`) para acompanhar o inversor Deye. A interface lê
`/data`, `/today-chart` e `/history` no Cloudflare Worker configurado em `CFG.proxy`.

## Segurança e operação

- A password da página é local a cada navegador. Impede acesso casual nesse
  navegador, mas não autentica as chamadas ao Worker nem protege dados na rede.
- O Worker responde atualmente a pedidos públicos de telemetria. Antes de usar
  dados privados ou comandos, criar autenticação no servidor, limitar origens e
  acesso, e guardar segredos exclusivamente no servidor.
- A chave Deye esteve publicada no histórico deste repositório. Revogar/rodar a
  chave na conta de desenvolvedor e atualizar o segredo do Worker. Apagar a
  chave apenas do HTML não a invalida.
- O código do Worker não está neste repositório. Implantar alterações de backend
  apenas no projeto que gere esse Worker.
