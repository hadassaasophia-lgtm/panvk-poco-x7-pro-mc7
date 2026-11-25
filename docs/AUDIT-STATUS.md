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


## Varredura pública Faux123

- Auditoria dos quatro repositórios PanVK do perfil Faux123, releases, issues, comentários, relatórios FauxVkDB e relatos públicos concluída em 2026-11-25.
- Relatório detalhado: [docs/FAUX123-PANVK-ECOSYSTEM-SCAN.md](FAUX123-PANVK-ECOSYSTEM-SCAN.md).
- Achado principal: há validação FauxVkDB v1.1.8 no POCO X7 Pro/Mali-G720 MC7 (72 checks aprovados), mas também há relatos de tela preta em jogos específicos no mesmo aparelho. A série própria de patches Faux123 está em repositório companheiro privado; não é possível baixar os 149 patches a partir dos repositórios públicos.
- Nenhuma biblioteca ou patch foi transplantado nesta etapa. O relatório orienta a próxima auditoria de Android WSI/AHB/gralloc, FP16 e ownership de present extensions.



## Evidência de runtime recebida: BOTW Recomp / Faux123 v1.1.8 (2026-11-25)

Log fornecido pelo usuário para o POCO X7 Pro / MT6899 / Android 16:

- O aplicativo carregou explicitamente `panvk_faux123_v1_1_8_g720_mc7_D/libvulkan_panfrost.so` por AdrenoTools; portanto, este registro é do Faux123 v1.1.8, não do binário compilado nesta branch.
- O dispositivo Vulkan foi criado como Mali-G720 MC7, vendor `0x13b5`, device `0xc8700010`, API reportada 1.4.363.
- A swapchain foi criada em 2712x1220; o aplicativo registrou superfície/janela com a mesma dimensão e depois recriou a swapchain ao retornar do segundo plano.
- O relatório de display mostra buffers de swapchain em `VK_FORMAT_R8G8B8A8_UNORM`, stride 2720, pitch 10880 bytes, modifier zero e fallback `linear-forced 1`. O stride maior que a largura visível é compatível com alinhamento de buffer; não deve ser tratado como erro isoladamente.
- Os registros `[v12pass]` chegam a n=600, com render targets RGBA8 e importações KBASE repetidas. Isso demonstra atividade de renderização/submissão, mas o contador por si só não prova que cada quadro foi apresentado corretamente nem mede FPS.
- Não aparece neste trecho `VK_ERROR_DEVICE_LOST`, erro explícito de `vkQueuePresentKHR` ou falha de criação da swapchain. O último evento é retorno do app do segundo plano e recriação da swapchain.
- O caminho de apresentação linear forçado é uma pista forte para preservar/investigar a compatibilidade MediaTek gralloc/display. Comparar o comportamento do fallback linear com o layout de render targets tiled/modifier `0x800000000000351`; não forçar linear em todos os recursos internos, pois isso pode degradar desempenho.
- O log informa `no heap import: shader global memory through CPU copies`. Esse caminho de memória merece auditoria de performance separada; não é prova de causa de tela preta.
- A criação de `/data/.cache` falhou por permissão e o cache de shaders foi desativado. Isso pode afetar compilação/tempo de carregamento, mas não explica sozinho a apresentação preta.
- O PSS do processo no início da sessão atual era 389 MB; o registro da sessão anterior indica encerramento voluntário (`exit self`, status 0) com PSS 5440 MB e RSS 3271 MB. Não há indicação de crash fatal nesse encerramento anterior, mas o alto uso de memória merece acompanhamento em sessões longas.
- O usuário confirmou que, com o pacote Faux123 anterior, a imagem aparecia normalmente. Isso é evidência prática de que ao menos essa combinação de driver/app conseguiu apresentar imagem no aparelho. Não generalizar para o nosso build, pois são bibliotecas diferentes.

### Decisões derivadas do log

1. Preservar como referência o comportamento do Faux123 v1.1.8 no mesmo aparelho.
2. Auditar primeiro o caminho de AHardwareBuffer/gralloc e a seleção do layout linear para buffers efetivamente apresentados à ANativeWindow.
3. Manter recursos internos tiled quando suportados; converter/selecionar linear somente no limite de apresentação se a implementação e as restrições do display exigirem.
4. Investigar a ausência de heap import e o cache de shaders como tópicos de desempenho/estabilidade separados.
5. Solicitar, para uma análise conclusiva de qualquer falha futura, o trecho do log que inclua o momento exato em que a imagem deixa de aparecer, mensagens de present/fence e encerramento do processo.

**Limite:** esta evidência é de runtime do Faux123 v1.1.8. Não confirma que o pacote PanVK compilado nesta branch contém essas correções nem que a tela preta está corrigida em todos os jogos. Nenhuma alteração de código do driver foi feita com base apenas neste log.


## Evidência adicional de runtime: BOTW Recomp — telemetria de frames (2026-11-25)

Trecho de log enviado pelo usuário, aproximadamente 68–228 s de execução:

- A aplicação continuou produzindo atividade Vulkan durante a sessão: contadores de draws, passes, flushes, uploads e framebuffer copies avançam até o fechamento da janela. Isso não comprova, isoladamente, que a imagem estava visualmente correta em todos os momentos.
- O FPS por intervalo é extremamente irregular: há amostras em torno de 19,6–24,3 FPS, mas também diversas quedas para 0,3–1,1 FPS; picos de frame chegam a 3.587 ms.
- vk acquire blocked registra bloqueios de 37–317 ms em vários momentos. É um indício direto de espera na aquisição de imagens da swapchain, mas ainda é necessário correlacionar com fences, vkQueuePresentKHR, SurfaceFlinger e o estado da janela para atribuir a causa.
- vsync timer late aparece com atrasos de 57, 97 e 164 ms, consistente com perda de cadência de apresentação ou atraso de execução.
- A telemetria registra fbcopy repetidamente (por exemplo, 240 cópias e 7.400 leituras numa amostra) e uploads muito altos (por exemplo, 576,2 MB na mesma amostra). Esses números são relevantes para investigar custo de cópia/largura de banda, mas não devem ser interpretados como bytes por frame sem confirmar a semântica do contador e a duração de cada janela de amostragem.
- O indicador de kernel no core 0 mostra períodos com 38–67% de ocupação e esperas acumuladas de aproximadamente 5,1–14,5 s por janela de 30 s, com esperas individuais até 1.255 ms. Isso reforça a hipótese de contenção/espera no caminho de execução, mas o significado exato de takes/waited/held depende da instrumentação do app/kernel.
- O jogo alterna repetidamente o present interval entre 2 e 3. Isso pode produzir cadência irregular, mas o log não prova que a alternância seja a causa primária; pode ser uma reação do frame pacing ao tempo de trabalho variável.
- O trecho termina com window closed e estatísticas de saída do compilador de shaders. Não há, no trecho fornecido, erro explícito VK_ERROR_DEVICE_LOST, VK_ERROR_OUT_OF_DATE_KHR, VK_ERROR_SURFACE_LOST_KHR ou resultado de vkQueuePresentKHR.

### Direção da investigação

1. Priorizar instrumentação de vkAcquireNextImageKHR/vkQueuePresentKHR, fences/semaphores e latência de apresentação, correlacionando com SurfaceFlinger/ANativeWindow.
2. Auditar os caminhos de framebuffer copy e upload para identificar cópias CPU desnecessárias ou conversões de formato/stride; não remover cópias necessárias sem validar layout e sincronização.
3. Investigar contenção no core 0 e alternância de present interval como possíveis fatores de frame pacing, sem atribuir automaticamente o problema ao driver.
4. Separar otimização de desempenho da correção de tela preta/WSI. O log demonstra degradação severa de desempenho, mas não identifica sozinho a origem nem autoriza uma alteração específica no driver.

**Limite:** o trecho não identifica inequivocamente o nome/versão do ICD carregado. Não atribuir estes números ao build desta branch ou ao Faux123 v1.1.8 sem a linha de inicialização que identifica a biblioteca. O workflow #28 compilou com sucesso o código atualmente empacotado, mas não incluiu uma correção de runtime baseada neste log.



## Evidência de inicialização/runtime identificada: build desta branch no BOTW (2026-11-25)

O novo trecho enviado pelo usuário identifica explicitamente o ICD utilizado nesta sessão:

- Caminho carregado pelo AdrenoTools: `panvk_poco_x7_pro_mc7.adpkg/libvulkan_panfrost.so`.
- Dispositivo: PanVK-G720 MC7, vendor `0x13b5`, device `0xc8700010`, Mesa `27.0.0-devel`, API reportada 1.4.363; Android 16 / POCO X7 Pro `2412DPC0AG`.
- O dispositivo Vulkan foi criado e a swapchain inicializada em 2712x1220, com seis imagens confirmadas pelo runtime. Não há falha explícita de criação de superfície/swapchain neste trecho.
- O pipeline cache foi ignorado por estar ilegível, malformado ou incompatível, e a execução começou com cache vazio. Isso pode provocar recompilações e stutter durante a primeira execução; ainda não prova ser a única causa.
- O runtime mantém no máximo 1.500 pipelines e 1.000 programas, com descarte LRU. Deve-se verificar se há churn/evicção e recompilação sob carga antes de alterar esses limites.
- A tradução de command lists ocorre em uma render thread com um frame de antecedência. O log posterior confirma que essa thread pode esperar por shader/pipeline build.
- A importação de heap não está disponível (`host import no`); shader global memory é mantida por cópias via CPU. É uma hipótese relevante de custo de CPU/memória, mas não é evidência direta de falha WSI nem autoriza trocar o caminho de memória sem verificar requisitos de coerência e sincronização.
- O display inicialmente solicita 120 FPS de conteúdo e depois solicita 0 FPS; o jogo define present interval 2 e posteriormente alterna para 3. Isso pode influenciar pacing, mas não comprova a causa raiz.
- O trecho registra RAM saving desligado e limite de heap do jogo de 3120 MB. O uso de memória e a política de cache merecem medição durante sessões longas.

### Correlação com a telemetria de frames enviada junto

- A compilação de shaders/pipelines é uma causa concreta de parte das pausas: no frame 798 são registrados vários draws ignorados enquanto shaders ainda estão sendo construídos.
- No watchdog, o render thread está esperando shader/pipeline build enquanto traduz uma command list; há 22 requisições pendentes na fila assíncrona e uma apresentação em andamento.
- A amostra do frame 904 registra 0,3 FPS, frame máximo de 8.582 ms e `compile 57 (waited 7977ms)`. A mensagem seguinte informa que os frames retomaram após 8,0 s. Essa correlação é forte evidência de uma pausa de compilação de pipeline/shader no caminho crítico desta sessão.
- A mesma janela registra GPU submitted sequence 3276 e last known done 3261, com último submit 3,4 s antes do watchdog. Isso indica trabalho GPU pendente, mas não demonstra sozinho deadlock do driver nem identifica qual fence/semaphore está bloqueando.
- Mais tarde, o FPS permanece muito baixo em alguns intervalos, com novas esperas de compilação e framebuffer copies. Logo, otimizar apenas o cache pode reduzir stutter inicial, mas não explica necessariamente toda a degradação.
- O log não contém erro explícito de `VK_ERROR_DEVICE_LOST`, `VK_ERROR_OUT_OF_DATE_KHR` ou `VK_ERROR_SURFACE_LOST_KHR` neste trecho.

### Prioridade técnica revisada

1. Investigar por que o pipeline cache persistente foi rejeitado: formato/versão/vendor/device/driver UUID, caminho de armazenamento e validade dos dados. Não reutilizar cache incompatível.
2. Instrumentar e revisar o ciclo de vida de pipeline/shader: compilação assíncrona, deduplicação de pedidos, espera no render thread, cache hit/miss e evicção LRU. Evitar simplesmente aumentar limites sem medir RAM e churn.
3. Medir o caminho de shader global memory sem heap import e as cópias CPU, identificando quais recursos realmente usam esse caminho e se há uma alternativa segura via DMA-BUF/AHB no aparelho.
4. Correlacionar submissões e conclusões GPU com fences/semaphores e present, pois a fila ainda tinha trabalho pendente durante o watchdog.
5. Manter a investigação de WSI/gralloc separada: este trecho prova que a swapchain foi criada e que o jogo chegou a renderizar; não prova que todos os frames foram apresentados corretamente.

**Conclusão:** esta sessão é do binário empacotado nesta branch, não do Faux123. A causa imediata mais bem sustentada para o congelamento de oito segundos é espera de compilação de shader/pipeline no render thread, com trabalho GPU ainda pendente. A causa raiz do cache incompatível e a contribuição de CPU-copy/WSI ainda precisam ser confirmadas. Nenhuma correção de código foi aplicada nesta atualização documental.


## Inspeção direta dos caminhos de runtime no código-fonte (2026-11-25)

A auditoria foi ampliada para incluir os arquivos completos de implementação relevantes, e não apenas ocorrências de texto. O workflow de inspeção concluiu com sucesso; artefato: `PanVK-Source-Internals-Audit`, run `45595270689`.

### Pipeline/shader/cache

- `panvk_compile_nir()` executa o pipeline NIR e chama `pan_shader_compile()`; a compilação efetiva do shader ocorre nesse caminho.
- `panvk_compile_shaders()` usa `compiler_lock()/compiler_unlock()`, mas o mutex global só é tomado quando shader dumping ou `PANVK_DEBUG(NIR)` está habilitado. Portanto, o código não mostra um mutex global obrigatório serializando toda compilação em produção.
- O cache Vulkan interno do dispositivo é criado em `panvk_vX_device.c` com `weak_ref = true`. O uso do disk cache depende de `ENABLE_SHADER_CACHE`, da existência de `physical->disk_cache` e da opção `skip_disk_cache`.
- `vk_pipeline_cache_load()` rejeita dados iniciais quando o cabeçalho completo não corresponde ao cabeçalho esperado, incluindo tamanho/versão, vendor ID, device ID e pipelineCacheUUID. Isso é um mecanismo de compatibilidade; não prova que a rejeição vista no log veio desse código, pois a mensagem pode ter sido emitida pelo wrapper/aplicativo.
- O cache de kernels pré-compilados `panvk_precomp_cache` é uma tabela fixa para programas internos, protegida por mutex e preenchida sob demanda. Não é o mesmo cache LRU de pipelines de 1.500 entradas mencionado na telemetria do aplicativo.

### Android WSI, AHardwareBuffer e sincronização KBASE

- `panvk_wsi_init()` inicializa o WSI comum com fd `-1`, ativa suporte a modifiers e callback de apresentação DRM por dispositivo. O arquivo PanVK WSI não contém implementação própria de criação de Android surface; isso mantém a integração Android/gralloc como ponto prioritário de investigação.
- `panvk_android_import_ahb_memory()` obtém o dma-buf do AHardwareBuffer, verifica compatibilidade de requisitos de memória e importa o fd via `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT`.
- Para dispositivos reconhecidos como KBASE, `panvk_GetSwapchainGrallocUsageANDROID/2ANDROID` pede buffers sem AFBC e uso de compositor. A condição depende de `pan_kmod_dev_is_kbase()`; não presumir que foi ativada no aparelho sem log específico.
- `panvk_AcquireImageANDROID()` faz `poll()` do native fence no CPU por até 5.000 ms quando o dispositivo é KBASE; em timeout/erro, registra aviso e segue desenhando. Essa espera pode contribuir para bloqueios de aquisição em determinadas condições, mas os waits de 30–149 ms do log não provam timeout nem explicam a pausa de compilação de aproximadamente 8 s.
- O provider KBASE importa sync files como objetos pendentes e permite que a espera seja atendida posteriormente; o comentário do código explica que uma espera imediata em AcquireImage seguraria a aquisição até o compositor liberar o buffer. O caminho precisa ser avaliado junto com a sincronização da submissão GPU, sem remover a espera de segurança.
- `kbase_kmod_bo_wait()` declara que BO wait ainda não está implementado. Não é seguro concluir que isso causa o problema sem rastrear todos os callers e a estratégia de sincronização KBASE usada nas submissões.

### Conclusão técnica atualizada

1. A compilação de shader/pipeline permanece a explicação mais forte para a pausa de ~8 s, com base no watchdog e na telemetria do jogo.
2. A integração Android de apresentação e fences é uma segunda frente concreta: há espera CPU de native fence em KBASE e a inicialização PanVK WSI é genérica.
3. Não foi encontrada evidência suficiente para alterar limites LRU, desativar sincronização, trocar o formato de memória ou aplicar cópias CPU de framebuffer.
4. Ainda não foi aplicada correção de runtime. As alterações desta etapa foram somente no workflow de auditoria e neste relatório.
5. Próxima etapa segura: rastrear os callers de `panvk_AcquireImageANDROID`, a implementação Android WSI comum efetivamente compilada e a origem exata da mensagem de cache rejeitado; em paralelo, rastrear a chamada de compilação que bloqueia o render thread no caminho do emulador.



## Rastreamento adicional de cache e fences KBASE (2026-11-25)

A leitura dos arquivos completos confirma alguns detalhes que não apareciam no primeiro relatório:

- O caminho de compilação de shader chama `pan_shader_compile()` diretamente após o pós-processamento NIR. A função `panvk_compile_shaders()` envolve a chamada em `compiler_lock/unlock`, mas esse mutex só bloqueia quando shader dumping ou debug NIR está habilitado. Portanto, não há evidência aqui de um mutex global de compilação ativo em produção.
- O driver registra callbacks `serialize` e `deserialize` para seus shaders. A serialização armazena metadados de shader, binário compilado, dados auxiliares e strings de NIR/assembly quando presentes. A desserialização valida diversos limites e erros de leitura antes do upload do binário.
- A propriedade `pipelineCacheUUID` e `shaderBinaryUUID` vem de `device->cache_uuid`. O recurso de cache interno de pipeline binary é anunciado somente quando `device->vk.disk_cache != NULL`. O device também cria um cache Vulkan em memória com `weak_ref = true`; isso, isoladamente, não garante persistência entre execuções.
- A mensagem de runtime sobre cache rejeitado não pode ser atribuída ao cache Mesa apenas com o trecho de log atual. Precisamos identificar quem a emite e obter o UUID/cabeçalho do cache utilizado pelo app.

### Sincronização KBASE observada no código

- O provider KBASE mantém syncobjs em uma tabela de processo, com estados `UNSIGNALED`, `SIGNALED` e `SUBMITTED`; uma submissão CSF associa sequência/grupo e pode exportar um sync file da GPU.
- `ks_import_sync_file()` duplica o fence e o mantém pendente em vez de bloquear a chamada de importação. O comentário explica que esperar nesse ponto segurava `vkAcquireNextImageKHR` até o compositor liberar o buffer.
- `pan_kmod_kbase_submit_async()` cria um soft fence trigger dependente dos jobs GPU para exportar um sync file; a fila usa thread de eventos para receber conclusão. Isso mostra que existe um mecanismo de fence assíncrono no provider.
- Ao mesmo tempo, `panvk_AcquireImageANDROID()` faz um `poll()` explícito de até 5.000 ms para native fence quando `panvk_android_is_kbase()` é verdadeiro. O comentário dessa função diz que o syncobj DRM comum não preservaria a espera no KBASE.
- A coexistência desses dois caminhos exige confirmar a sequência real de chamadas na implementação Android comum e no loader. O poll explícito pode explicar parte dos bloqueios de aquisição medidos (30–149 ms), mas não há evidência para removê-lo com segurança ainda.
- O caminho de importação AHardwareBuffer duplica o dma-buf e usa `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT`; o código consulta os requisitos de memória e corrige o tipo de memória para um tipo compatível. Isso não comprova que o caminho host import está habilitado para heap global de shaders.

**Ação segura:** não alterar o poll de fence nem o provider sync até mapear as chamadas entre `vkAcquireNextImageKHR`, `vkAcquireImageANDROID`, importação de semaphore fd e submissão KBASE. Uma mudança prematura pode converter um atraso visível em corrupção de buffer ou tela preta.
