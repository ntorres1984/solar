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

## Futuras integrações de climatização

O iLetComfort e o SmartLife devem ser ligados por um serviço autenticado, sem
credenciais no navegador. Primeiro apresentar estados e permitir ações manuais
com confirmação; depois introduzir agendamento com prioridades independentes
para AQS e ventiloconvetores. Validar temperatura, modo, energia disponível,
limites do equipamento, comandos repetidos e intervenção manual antes de ativar
regras automáticas. O painel solar fornece leituras, nunca é a autoridade para
comandar a bomba de calor.
