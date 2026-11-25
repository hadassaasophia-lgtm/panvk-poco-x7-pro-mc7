# Auditoria técnica — estado e evidências

Data da atualização: 2026-11-25

## Identificação do alvo

Dados fornecidos pelo proprietário do aparelho e registrados no perfil do projeto:

- POCO X7 Pro / `rodin` / modelo `2412DPC0AG`
- MediaTek Dimensity 8400-Ultra / MT6899
- Mali-G720 MC7
- GPU ID: `0xC8700010`
- Mali v12 CSF
- Android 16 / API 36 / ARM64

## O que foi verificado no repositório

- O branch de auditoria `audit/fix-panvk-g720-mc7` existe.
- O workflow `.github/workflows/build-android.yml` extrai `mali-panvk-main.zip`, instala LLVM 21 e NDK r29, executa `build.sh`, verifica ELF64/AArch64, metadados, NOTICE e símbolos ICD e publica ZIP como artifact.
- O workflow contém buscas textuais por G720, GPU ID, KBASE e CSF. Essas buscas são diagnósticas e não demonstram suporte funcional.
- O perfil do dispositivo declara o alvo G720 MC7 / GPU ID `0xc8700010`.
- O arquivo de código-fonte `mali-panvk-main.zip` está versionado no repositório, mas o workflow não registra um commit upstream do Mesa, uma série de patches identificada por hash, nem um manifesto de proveniência do conteúdo extraído. O SHA do blob Git do arquivo é `65b2781bfff596e7f901f31a05d165d3a303ff67`; isso identifica o objeto Git, não comprova a origem upstream nem equivale a SHA-256 do arquivo.
- O README anterior marcava integração de fonte, patches, compilação, testes e ZIP final como pendentes.

## Comparação com referência Android KBASE/CSF

Foi inspecionado o projeto público `zenithblue-oss/panvk-kbase-android` como referência técnica, sem copiar nem aplicar patches:

- O projeto fixa Mesa no commit `5a07217f034b3e50d8c7c7794f97a2df1742613b` (26.3.0-devel) e identifica separadamente a série de patches por hash.
- O projeto descreve uma pilha de patches KBASE/CSF, perfis por arquitetura e testes de runtime; isso é substancialmente mais rastreável do que apenas compilar um ZIP de fonte sem proveniência registrada.
- O arquivo `profiles/g720-v12-csf.json` desse projeto marca o perfil G720 v12 CSF como planejado, não como validado para o POCO X7 Pro MC7. Portanto, não é uma base pronta para substituição direta.
- A documentação desse projeto cita `wonderkast02/panvk-g720-kbase-csf` como referência principal de CSF/G720. Isso é uma referência para auditoria, não prova que nosso código contém as mesmas correções.
- A versão Faux `panvk_faux123_v1.1.8` tem relatório de testes no POCO X7 Pro / Mali-G720 MC7, mas os testes de recursos Vulkan não comprovam compatibilidade com BOTW Recomp nem eliminam a tela preta.

## Correção de metadados de compatibilidade

- O campo `supported_devices` foi removido de `meta.json`, pois não há validação em aparelho real que justifique declarar o POCO X7 Pro como dispositivo suportado.
- O alvo agora é registrado em `target_devices`, com estado explícito `experimental_unverified`.
- `scripts/validate_project.py` foi atualizado para exigir esses campos e impedir que uma futura alteração volte a declarar suporte sem mudar conscientemente o critério.
- Essa mudança corrige a precisão dos metadados; não modifica a biblioteca Vulkan nem resolve a tela preta.

## Melhorias automatizadas adicionadas nesta branch

- Foi adicionado `scripts/validate_project.py` para validar os campos do perfil e do `meta.json`, testar o CRC do ZIP, rejeitar caminhos inseguros/duplicados e confirmar os pontos de entrada `build.sh` e `meson.build` antes da extração.
- O workflow chama essa validação antes de extrair o código-fonte.
- O workflow também foi configurado para tentar executar em atualizações desta branch, além do acionamento manual.
- A execução dessa nova versão ainda não foi confirmada; a alteração por si só não comprova compilação nem compatibilidade.

## Limites importantes

1. A compilação do workflow não é um teste de execução no POCO X7 Pro.
2. As verificações de símbolos ICD não garantem que todas as funções Vulkan necessárias estejam implementadas corretamente.
3. Uma correspondência textual de G720 ou `0xc8700010` não prova que o kernel KBASE/CSF reporta os recursos reais do MC7 corretamente.
4. Não há, nesta auditoria, leitura confirmada de `RAW_CORE_FEATURES` e `RAW_SHADER_PRESENT` do aparelho.
5. Não há resultado de teste de PanVK executando jogos BOTW Recomp ou GTA V Recomp no aparelho.
6. O ZIP de artifact previamente inspecionado continha a biblioteca `libvulkan_panfrost.so`, `meta.json` e `NOTICE.txt`, mas não incluía o código-fonte.
7. O SHA-256 da biblioteca do Build 14 difere do SHA-256 reportado pelo Faux 1.1.8 no banco de testes; portanto, são binários distintos e não se deve afirmar que o nosso build incorpora o Faux.

## Próximas verificações técnicas necessárias

- Extrair e revisar o conteúdo completo de `mali-panvk-main.zip` (incluindo histórico/origem, submódulos e patches locais).
- Registrar SHA-256 do arquivo de fonte e identificar exatamente o commit Mesa e todos os patches usados.
- Auditar a tabela de modelos Panfrost e a decodificação do GPU ID v12.
- Auditar a leitura de propriedades KBASE/CSF, especialmente shader core mask e recursos brutos.
- Comparar a implementação com resultados específicos do POCO X7 Pro, sem copiar patches de outra revisão sem validar compatibilidade.
- Adicionar testes automatizados que falhem quando o alvo não é identificado ou quando a configuração esperada não é aplicada.
- Fazer validação em dispositivo real antes de recomendar instalação.

## Segurança

Não substituir bibliotecas Vulkan/GLES de vendor, não alterar partições do sistema e não instalar o pacote como driver principal enquanto os testes de inicialização, estabilidade e recuperação não forem concluídos.

## Conclusão atual

**Status: auditoria documental/CI em andamento; compatibilidade real não comprovada.**

Nenhuma correção de código-fonte do PanVK é declarada nesta atualização. Esta nota evita que um build bem-sucedido seja confundido com validação funcional.

## Nova pista: tela preta no caminho de vídeo do BOTW

- A documentação técnica upstream do BOTW Recomp registra um caso Mali-G720 em que o log termina exatamente após `first frame decoded`, descrito como crash na primeira moldura de vídeo na Mali; também registra congelamento em tela preta após a primeira moldura em Xclipse 530. Isso é uma pista de compatibilidade do caminho de vídeo/FFmpeg, não prova de defeito no PanVK.
- A mesma triagem separa esse sintoma de falhas de GPU/device-lost e de problemas de memória após minutos de jogo. Portanto, não se deve alterar shader, swapchain ou alocação Vulkan sem identificar o último marco do log no nosso caso.
- O log já fornecido para este aparelho confirma criação do dispositivo Vulkan e da swapchain, mas o trecho termina antes de mostrar o evento exato que antecede a tela preta. Não há evidência suficiente para aplicar uma correção segura no código PanVK.
- Referência técnica: `mamcjr/BOTWRecompAndroid/docs/BOTW-PORT.md`, triagem de 2026-10-30, família de falhas de vídeo (#93 Mali-G720; #86/#107 Xclipse 530; #113 arquivo de vídeo ausente). A correção precisa ser dirigida ao componente que falha, e não presumida como correção de driver.


## Nova evidência: falha geral de apresentação (WSI) no mesmo aparelho

- Foi localizada a issue pública `zenithblue-oss/panvk-kbase-android#16`, relatando tela preta em importação AdrenoTools no Xiaomi `2412DPC0AG` / `rodin`, Mali-G720 MC7, Android 16 — o mesmo modelo/GPU/versão Android deste projeto.
- Nesse relato, o PanVK enumera a GPU e executa submissões, mas `vkCreateSwapchainKHR` falha com `VK_ERROR_INCOMPATIBLE_DISPLAY_KHR`; o log também informa ausência de gralloc hwmodule e uso de fallback. O autor aponta a integração Android WSI / ANativeWindow / gralloc como suspeita.
- Como o proprietário informa agora que todos os jogos ficam pretos, a hipótese prioritária passa a ser uma falha comum de apresentação (WSI/swapchain/ANativeWindow/gralloc) no driver empacotado, em vez de um defeito exclusivo do BOTW.
- A issue é evidência comparativa forte, mas não prova que este binário apresenta o mesmo erro: o log fornecido anteriormente registra criação de swapchain, e ainda não contém o resultado de apresentação nem erro WSI. Não se deve aplicar um ajuste arbitrário de `compositeAlpha`, gralloc ou swapchain sem confirmar o caminho efetivamente usado pelo nosso build.
- Referência: https://github.com/zenithblue-oss/panvk-kbase-android/issues/16
- Nenhuma alteração na biblioteca foi feita nesta etapa. A correção precisa atuar na implementação Android WSI compatível com o loader de importação; compilar novamente sem essa correção não resolveria a causa.


## Comparação adicional: PanVK Faux123 RP4 Pro

- Foi inspecionado o README público de `faux123/panvk-faux123-driver-rp4pro`. O projeto documenta correções diretamente relevantes ao sintoma de tela preta: integração Android swapchain em que o driver não lia o layout de buffers MediaTek e a apresentação de frames falhava; e uma falha de renderização preta quando uma cena submetia os mesmos comandos mais de uma vez.
- O README também registra correções de profundidade/culling, temporização de clock da GPU, sincronização/cache e scratch memory. Esses itens são pistas de auditoria; não demonstram que todos sejam aplicáveis ao Mali-G720 MC7 deste aparelho.
- A partir de v1.0.0, o autor declara um pacote binário comum aos seus quatro dispositivos testados (Mali-G57, G77, G610 e G710), mas o G720 MC7 não está nessa lista. O autor afirma explicitamente que os demais dispositivos não foram testados e não oferece garantia para eles.
- A receita documentada usa Mesa 26.3.0-devel no commit `5a07217f`, série `zenithblue-oss/panvk-kbase-android` v0.1.0-rc4 (`5b87b74`), 49 patches próprios no histórico inicial e NDK 27.3/API 29. Isso fornece uma referência concreta para comparar a origem e a integração KBASE/Android, mas não autoriza substituir nosso binário pelo pacote RP4 Pro nem transplantar patches sem validar a geração de GPU e a base Mesa.
- O README informa que os testes foram feitos principalmente no Retroid Pocket 4 Pro com Mali-G77 MC9 e Android 13; não foi validado no POCO X7 Pro. Os testes de tela descritos são cenas Vulkan-Samples, não prova de compatibilidade com todos os jogos.
- Conclusão de auditoria: priorizar a comparação do tratamento de layout MediaTek/gralloc e do caminho de apresentação Android WSI, além do caso de comandos repetidos que podem produzir renderização preta. Nenhuma correção de código foi aplicada com base apenas no README.
- Referência: https://github.com/faux123/panvk-faux123-driver-rp4pro


## Prioridade de estabilidade/FPS: releases Faux123 v1.1.7 e v1.1.8

- A release v1.1.7 (15 nov 2026) descreve explicitamente correção de tela 3D preta em Mali-G720/G920/G925: shaders que convertem valores para 16 bits sem especificar arredondamento podiam transformar valores logo acima do limite em infinito; a correção muda o arredondamento para truncar em direção a zero, evitando NaN que contaminava o efeito de brilho. O jogo de reprodução citado é Fire Emblem Engage em emuladores baseados em Eden.
- A mesma release declara testes nos quatro dispositivos próprios (G57/G77/G610/G710) e também RG557/G615; os testes de renderização/feature não equivalem a validação do POCO X7 Pro. O release note declara o cenário G720 como corrigido, mas não afirma que o aparelho do usuário foi testado.
- A release v1.1.8 (16 nov 2026) corrige crash com frame generation causado por `vkWaitForPresentKHR` atrás do loader Android: quando o driver é carregado pelo loader Vulkan do Android, o loader gerencia a swapchain e o driver deixa de expor present-wait, present-ID, present-timing e swapchain-maintenance nesse caminho. O autor reporta 72 checks e métricas praticamente iguais à v1.1.7 nos quatro aparelhos próprios.
- Esses dois pontos são agora referências prioritárias para a auditoria: (1) conversão/arredondamento float->16-bit nos shaders PanVK para G720, sem desativar o caminho rápido de 16 bits; (2) detecção correta de loader Android e ownership da swapchain/present extensions. O segundo ponto pode evitar incompatibilidade com certos loaders e frame generation, mas não prova por si só ser a causa da tela preta em todos os jogos deste aparelho.
- O release v1.1.8 publica SHA-256 do pacote de biblioteca `499e3eae32a27340777cb890aac92468c2519d57223bfad93a2e2a8f71029728`; esse hash é diferente do nosso Build 14 (`aa89e3adc7acc38c40865be4f36b5cb51f29e83c617032de012a44270396541a`). Não se deve substituir ou renomear o binário Faux como se fosse build validado para o POCO.
- Estratégia para preservar FPS: não aplicar um modo global de compatibilidade lenta nem desligar recursos de 16 bits por padrão. Portar apenas correções específicas após inspeção de código e compatibilidade com a base Mesa; manter os caminhos rápidos e exigir build/validação. Primeiro objetivo é eliminar tela preta; depois comparar desempenho com a mesma cena e configuração.
- Referências: https://github.com/faux123/panvk-faux123-driver-rp4pro/releases/tag/v1.1.7 e https://github.com/faux123/panvk-faux123-driver-rp4pro/releases/tag/v1.1.8



## Auditoria Android WSI: resultado do workflow #23 e revisão dos patches

- O workflow #23 concluiu com sucesso a compilação ARM64 e a validação estrutural do ZIP. Isso confirma compilação, não funcionamento em runtime no POCO X7 Pro.
- O diagnóstico do código-fonte encontrou `vk_android.h`, mas não encontrou implementação/registro de `VK_KHR_android_surface`, `panvk_CreateAndroidSurfaceKHR`, `VK_ICD_WSI_PLATFORM_ANDROID` nem chamadas Android de apresentação em `panvk_wsi.c`. O WSI atual inicializa o backend genérico e não registra uma interface Android.
- O teste `git apply --check` confirmou que os patches de referência 015 e 016 se aplicam à árvore empacotada; o patch 006 falha em três arquivos (`panvk_vX_device.c`, `csf/panvk_cmd_buffer.h`, `panvk_vX_physical_device.c`) e não pode ser aplicado diretamente.
- Revisão manual do patch 016 encontrou um caminho de apresentação que chama `DeviceWaitIdle` a cada frame, bloqueia/ lê o AHardwareBuffer pela CPU e copia os pixels para o buffer da ANativeWindow. Isso não atende ao requisito de manter o caminho acelerado e pode causar perda importante de FPS. O próprio cabeçalho do patch declara como referência/teste um G615 beta.2, não o Mali-G720 MC7.
- O patch 016 também anuncia MAILBOX/IMMEDIATE sem comprovação de suporte real no backend e usa um ciclo de aquisição simplificado. Não deve ser tratado como implementação pronta para produção sem revisão de sincronização, formatos, stride, fence, ownership e lifecycle.
- O patch 017 encontrado no mesmo repositório apenas marca AHBs da swapchain como pertencentes ao driver para um fallback de layout sem mapper; depende dos patches Android 014 e WSI 016 e foi testado em Mali-G57. Não resolve a apresentação por GPU nem elimina a cópia CPU.
- Decisão: não aplicar 015/016/017 automaticamente. O patch 015 altera stubs de hardware/linkagem e é uma dependência de build, não uma correção isolada da apresentação. A implementação Android WSI precisa ser adaptada à base Mesa incluída e usar import/export AHB, sincronização/fences e apresentação sem cópia CPU/DeviceWaitIdle por frame; em paralelo, auditar a compatibilidade MediaTek gralloc/layout indicada pelo relato do mesmo aparelho.
- Próxima validação necessária: testes de loader/surface/swapchain/present em Android real, incluindo ciclo de vida e pelo menos centenas de apresentações, seguidos de teste em jogos. Nenhuma correção de tela preta está declarada concluída até esses testes.
- Referências: https://github.com/zenithblue-oss/panvk-kbase-android/blob/cf70e02b918e1864cbcd746a7fefa57b96c673ce/patches/wsi/016-android-surface-swapchain.patch e https://github.com/zenithblue-oss/panvk-kbase-android/blob/cf70e02b918e1864cbcd746a7fefa57b96c673ce/patches/wsi/017-android-swapchain-owned-ahb.patch
