# Análise final do caminho Android present: decisão de não portar cegamente (2026-11-25)

## Descoberta de implementação

Foram lidos integralmente os patches públicos da referência panvk-kbase v26.3.1:

- `patches/wsi/016-android-surface-swapchain.patch`
- `patches/wsi/017-android-swapchain-owned-ahb.patch`
- `patches/jm-v7-wip/0117-panvk-wsi-Android-present-waits-for-the-image-s-fenc.patch`
- `patches/jm-v7-wip/0118-panvk-wsi-Android-swapchain-presents-on-its-own-thre.patch`
- `patches/staging-115/pc/NOTES.md`

## Achados

1. WSI 016 implementa um caminho próprio Android: AHB-backed swapchain, acquire/present e cópia CPU para ANativeWindow via `AHardwareBuffer_lock` + `memcpy` + `ANativeWindow_unlockAndPost`. O patch explicitamente chama `DeviceWaitIdle` em cada present antes da cópia. Isso serializa CPU/GPU e é incompatível com a meta de FPS sustentado se for usado sem as correções seguintes. O próprio patch declara teste em Poco X6 Pro/Mali-G615, não no POCO X7 Pro/G720 MC7.
2. WSI 017 marca AHBs próprios do swapchain como driver-owned para permitir um fallback linear probe que escreve cookies no buffer. Esse mecanismo é específico da combinação android/014 + wsi/016; não é uma correção genérica para buffers importados do Gralloc do sistema.
3. Patch 0117 substitui `DeviceWaitIdle` por espera na fence da imagem apresentada. O rationale é que WSI common já submeteu a present fence, que cobre as semaphores do present e trabalho anterior na queue. A alteração só se aplica ao swapchain Android próprio do PanVK e depende das premissas de fence/queue da versão correspondente.
4. Patch 0118 move a cópia CPU e o dequeue/post da janela para uma thread própria; acquire só devolve uma imagem quando a thread terminou de ler. Isso permite sobreposição CPU/GPU e evita bloquear a thread da aplicação. Porém, a transferência de pixels continua sendo uma cópia CPU (aprox. 8 MB por frame 1080p segundo as notas), portanto não é zero-copy nem prova de alto FPS em resolução 2712x1220.
5. Os patches 0117/0118 são uma otimização de um caminho de present já existente, não uma prova de que a causa da tela preta do usuário é a fence. O relatório do usuário mostra swapchain criada e atividade de render targets, mas não traz retorno de present nem confirmação do post ao compositor.
6. O comentário do mantenedor sobre WSI por swapchain se refere a correções de caminho/compatibilidade, mas não autoriza transplantar uma implementação WSI inteira. O patch 016 usa stubs em certas compilações e assume um formato/uso AHB específico; o 017 usa CPU probe em AHB pertencente ao driver. Copiar isso sem validar os contratos do HAL MediaTek pode causar corrupção, tela preta ou falha de apresentação.

## Decisão para o projeto Faux123 v1.1.8

**Não portar WSI 016/017 nem 0117/0118 diretamente agora.** Motivos:
- Faux123 v1.1.8 é baseado em panvk-kbase RC4 com patches privados.
- A árvore exata completa do Faux123 e o código-fonte da RC10 não estão disponíveis no histórico desta sessão.
- O código dos patches depende de estruturas internas de WSI/Mesa e contratos de fence que mudaram entre a base RC4 e a v26.3.1.
- O sintoma ainda não está classificado entre: (A) submit não conclui, (B) present/fence falha, (C) present retorna sucesso mas o buffer não é postado/exibido, (D) pixels renderizados já são pretos.

## Plano mínimo de engenharia que permanece válido

- Confirmar no log o resultado de `vkQueuePresentKHR` e `vkAcquireNextImageKHR`; procurar `VK_ERROR_*`, timeout e erros nativos.
- Instrumentar o caminho atual de present sem alterar semântica: índice da imagem, fence associada, início/fim de wait, chamada de post e resultado de unlock/post.
- Se o wait global estiver presente no código atual e a fence da imagem estiver disponível, revisar uma substituição por fence da imagem, mas só após confirmar a garantia de ordering da fila e de semaphores na base RC4.
- Se o present thread for avaliado, garantir propriedade/vida útil de AHB, filas bounded, acquire/release, destruction drain e wait-for-present. Testar stress de resize/recreate e shutdown.
- Não desativar o fallback linear MediaTek nem forçar modifiers.
- Para FPS, medir tempo da fence, cópia CPU e dequeue/post separadamente; não usar DeviceWaitIdle por frame; não assumir que mover memcpy para thread remove custo de banda.

## Limite operacional desta etapa

O repositório de trabalho do usuário contém um ZIP de uma árvore Mesa diferente e scripts/patches de auditoria, não contém a árvore completa exata Faux123 v1.1.8 nem RC10 com os 149 patches privados. O artifact v1.1.8 original é um pacote binário, não fonte suficiente para reconstruir/alterar com segurança o WSI. Assim, não existe base técnica para produzir um novo .so Faux123 modificado e atribuir-lhe uma correção verificada nesta etapa.

Nenhum binário foi alterado, nenhum driver foi instalado, nenhum patch experimental foi ativado e nenhum teste físico foi simulado como sucesso.
