# WSI per-swapchain: comparação de referência (2026-11-25)

## Nova evidência pública

A issue `zenithblue-oss/panvk-kbase-android#16` reproduz o mesmo aparelho (Xiaomi 2412DPC0AG / rodin, Mali-G720 MC7, Android 16) com áudio e submissões GPU funcionando, mas sem imagem. Naquele caso, `vkCreateSwapchainKHR` retornava `VK_ERROR_INCOMPATIBLE_DISPLAY_KHR`. O log apontava ausência de gralloc hwmodule visível ao processo e fallback de Gralloc. Isso é um precedente muito próximo, mas o log do nosso usuário já mostrou criação da swapchain; portanto, o estágio exato pode ser diferente.

O mantenedor respondeu na issue que a release PanVK-kbase v26.3.1 passou a incluir pacote AdrenoTools e que o WSI escolhe o caminho de apresentação por swapchain, com o objetivo de ajudar no `INCOMPATIBLE_DISPLAY`. A resposta recomenda validar primeiro com PanPlay 1.3.1 e PanProbe 1.3.2. Fonte: https://github.com/zenithblue-oss/panvk-kbase-android/issues/16#issuecomment-6540891178

O changelog da tag `panvk-kbase-v26.3.1` também documenta:
- caminhos de apresentação por swapchain no conjunto staging 1.15 (P-C, patches jm-v7-wip 0113–0119);
- descoberta vendor-neutral do gralloc mapper, backend HIDL mapper4 e CPU linear probe para AHBs de swapchain pertencentes ao driver (`android/014`, `wsi/017`);
- a validação no Poco X6 Pro/G615 MC6 é separada e não deve ser confundida com validação do POCO X7 Pro/G720 MC7.

Fonte: https://github.com/zenithblue-oss/panvk-kbase-android/blob/panvk-kbase-v26.3.1/CHANGELOG.md

## Comparação com Faux123

O README público Faux123 declara que as quatro distribuições v1.0+ são o mesmo binário para G57/G77/G610/G710 e que o desenvolvedor não testou outros dispositivos. O build v1.1.8 declara Mesa 26.3.0-devel commit 5a07217f + panvk-kbase-android v0.1.0-rc4 commit 5b87b74 + 149 patches privados Faux123. Portanto, não podemos presumir que a correção de WSI per-swapchain adicionada posteriormente à linha panvk-kbase v26.3.1 esteja incluída na v1.1.8 ou na RC10.

Fonte: https://github.com/faux123/panvk-faux123-driver-rg556

## Decisão para a nossa linha de trabalho

- Não migrar a base para Mesa v26.3.1: o objetivo continua sendo preservar Faux123 v1.1.8 como base de comportamento e não misturar bases.
- Não transplantar patches 014/017 ou a série P-C automaticamente. Eles precisam ser comparados com a árvore exata Mesa 26.3.0-devel + rc4 e com os 149 patches Faux123, que não estão todos públicos.
- A informação mais útil é o desenho funcional: o WSI seleciona o caminho de apresentação por swapchain, em vez de assumir um único caminho global; e o mapper pode ser descoberto de forma vendor-neutral. Isso orienta uma futura correção mínima somente se o código-base exato permitir.
- O fallback linear observado no relatório do usuário não deve ser removido: a referência Faux123 documenta uso de frames comprimidos em certos painéis, mas a v1.1.5 também inclui correção MediaTek de formato. Precisamos manter a seleção específica por buffer/format/modifier e não forçar todos os recursos.
- A etapa imediata continua sendo obter log completo do momento em que a tela some, com resultados de acquire, submit, release fence e present. O relatório atual não permite identificar se a falha é WSI, fence ou renderização.

## Status

Auditoria de referência avançada; nenhuma alteração de runtime/build foi feita. A tag v26.3.1 foi consultada apenas como referência de arquitetura WSI, não como versão escolhida para o driver do usuário.
