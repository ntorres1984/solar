# SHERPA / iLetComfort — piloto para Home Assistant

**Estado: preparação experimental de leitura. O ligar/desligar independente da
climatização ainda não está implementado nem validado na bomba.**

O controlador mostrado na app tem código de modelo `171H120F`. Este código já
tem um perfil ATW no projeto [ha-iletcomfort](https://github.com/tgenov/ha-iletcomfort),
mas é partilhado por variantes com formatos diferentes. As capturas do ecrã
não contêm as mensagens do protocolo e não confirmam a variante da SHERPA.

## O que está preparado

- Preparador que descarrega uma revisão fixa do projeto original, verifica os
  ficheiros alterados por SHA-256 e gera a pasta `custom_components/iletcomfort`.
- Descoberta da bomba, seleção EU/US, consultas e diagnóstico do projeto original.
  A compatibilidade destas leituras com esta SHERPA ainda precisa de teste real.
- Bloqueio dos comandos ATW genéricos, incluindo temperatura, boost e silencioso,
  até existirem comandos comprovados para cada separador.
- Cartão de climatização sem funcionalidades de controlo anunciadas.
- A temperatura do depósito AQS não é apresentada como temperatura da climatização.
- O estado de climatização fica desconhecido quando a resposta não corresponde
  ao formato cuja leitura de potência já foi validada pelo projeto original.

Não foram enviadas mensagens à bomba nem utilizados os dados de login.
Não estão incluídos credenciais, números de série individuais ou imagens da conta.

## Preparar e instalar o piloto

Num computador com Python 3 e Git:

```bash
python3 prepare.py --output sherpa-preparada
```

O destino deve ser uma pasta nova. O comando só prepara ficheiros: não instala
nem configura o Home Assistant. O código original é descarregado diretamente
do autor; este diretório contém apenas as adaptações e os testes adicionais.

Se ainda não existir uma integração `iletcomfort`, copiar a pasta gerada
`sherpa-preparada/custom_components/iletcomfort` para
`/config/custom_components/iletcomfort` do Home Assistant. Reiniciar e adicionar
**SHERPA iLetComfort — piloto de leitura** em Definições → Dispositivos e serviços.
Se já existir a integração original, guardar uma cópia antes de a substituir:
ambas usam o mesmo domínio e não podem estar instaladas lado a lado. Atualizações
pelo HACS da integração original substituem estas adaptações.

Para Portugal começar pela região **EU**. Se houver erro de autenticação/região,
guardar o código do erro; não assumir que é palavra-passe incorreta. A conta pode
ter sido criada noutro servidor.

O serviço permite uma sessão por conta. Para consultas regulares usar uma segunda
conta iLetComfort com a bomba partilhada para essa conta. O modo de coexistência
com a app também é só de leitura e pode terminar a sessão do telefone no arranque.

## O que falta para concluir o controlo

1. Instalar o piloto e descarregar **Diagnósticos** da integração, com a app
   aberta no mesmo momento, para comparar os valores reais.
2. Confirmar o formato da resposta e as temperaturas da climatização e AQS.
3. Recolher as mensagens reais do iLetComfort iOS para ligar/desligar **apenas
   Climatização**, com o estado AQS registado antes e depois. A recolha das
   mensagens será orientada após verificar os diagnósticos; não é necessário
   instalar ferramentas de captura nesta fase.
4. Implementar comandos específicos e testar ON/OFF, reinício e perda de ligação,
   verificando que o estado, setpoint e programação AQS permanecem iguais.

As regras de produção solar devem ser ligadas apenas depois desta validação.
Este piloto não contém automações solares nem uma declaração de compatibilidade
comprovada. O preparador bloqueia escritas para todos os dispositivos com perfil
ATW; destina-se a uma instalação dedicada a esta SHERPA.

## Verificação do código

`test_sherpa_pilot.py` usa dados sintéticos e testa que nenhuma chamada de controlo
ATW chega ao transporte, que o cartão não anuncia controlo e que não confunde a
temperatura AQS com a climatização. Não é um teste físico da bomba.

Para executar, criar um checkout da revisão indicada em `prepare.py`, instalar
`requirements_test.txt`, `requests`, `cryptography` e `paho-mqtt`, executar `adapt`
sobre a pasta do componente e copiar o teste adicional para `tests/`. Os testes
upstream que exigem escrita ATW genérica ou temperatura AQS no cartão climático
mudam deliberadamente de expectativa neste piloto.

Verificação em 04/10/2026: **288 testes passaram**; dois testes antigos foram
excluídos porque exigem precisamente os comportamentos substituídos pelos testes
do piloto (escrita ATW genérica e temperatura AQS no cartão de climatização).
O preparador também foi executado de ponta a ponta numa pasta temporária.
Ambiente de teste: Python 3.12 / Home Assistant 2025.1.4. Não foi testada a
instalação no Home Assistant do utilizador nem a comunicação com a bomba.

```bash
python -m pytest tests/ -q \
  --deselect tests/test_api.py::test_set_device_atw_uses_build_c3_set_frame \
  --deselect tests/test_climate.py::test_current_temperature_atw_reads_th_temp
```
