# Varredura pública Faux123 / PanVK — POCO X7 Pro Mali-G720 MC7

Data da auditoria: 2026-11-25

## Escopo consultado

- Perfil público de `faux123`.
- Os quatro repositórios PanVK: `panvk-faux123-driver-rp4pro`, `panvk-faux123-driver-rg556`, `panvk-faux123-driver-ace` e `panvk-faux123-driver-pixel7`.
- Releases públicas, README, issues, comentários e relatos de usuários.
- FauxVkDB: relatório de validação #3263, benchmark #3350 e matriz do Mali-G720 MC7.
- Reddit r/faux123 e issue pública do Eden #4734.
- Não foram acessados canais privados do Discord, repositório companheiro privado, nem conteúdo privado de usuário.

## Achado principal: existe validação pública do mesmo aparelho

O FauxVkDB tem um relatório válido, atestado e com bootloader bloqueado para:
- POCO X7 Pro / Xiaomi 2412DPC0AG
- MediaTek MT6899, Mali-G720 MC7
- Android 16, arm64-v8a, 11 GB
- PanVK Faux123 v1.1.8, Mesa 26.3.0-devel (git-b50c318cbc)
- SHA-256 da biblioteca: `499e3eae32a27340777cb890aac92468c2519d57223bfad93a2e2a8f71029728`

O relatório #3263 marcou 72 checks como pass, sem falhas/crashes/inconclusivos. Inclui desenho/readback, resubmissão do mesmo command buffer, memória, sincronização, compute, blend e recursos Vulkan. Isso é evidência forte de que o binário v1.1.8 executou corretamente vários testes nesse aparelho; não equivale a certificação Vulkan nem prova que todos os jogos funcionem.

O relatório lista `VK_ANDROID_external_memory_android_hardware_buffer` e `VK_KHR_swapchain`; também lista `VK_EXT_map_memory_placed`. A verificação `wsi.present_wait` aparece como unsupported. O banco distingue 36 itens não suportados e 46 não testados; portanto, “72/72” não significa que todos os recursos do Vulkan foram implementados ou testados.

O benchmark #3350 do mesmo aparelho/driver teve score 1531 (posição indicativa #52/190), com cenas medidas em 1080p/4K. É um benchmark sintético do driver, não FPS de BOTW nem comparação controlada com nosso build.

## Releases e correções relevantes

As quatro páginas PanVK publicam o mesmo pacote binário desde v1.0.0. A versão pública mais recente encontrada nesta varredura é v1.1.8 (16 nov 2026). As notas informam que o pacote é idêntico entre os quatro repositórios.

- **v1.1.5 — tela cinza / traços coloridos em MediaTek:** o release descreve que o display/gralloc do telefone não conseguia ler o formato comprimido do framebuffer. O driver passa a solicitar um formato simples em MediaTek com Mali-G615/G720 e posteriores, Android 13+. O autor diz que testadores confirmaram a correção em MT6899 Android 16 e Mali-G720. Também corrige placed maps em G57/G77 e ajusta o caminho de BC1–BC3.
- **v1.1.7 — tela 3D preta em G720/G920/G925 em emuladores Switch baseados em Eden:** overflow ao converter float para FP16 podia arredondar acima do limite para infinito; blend produzia NaN e contaminava o frame. A correção trunca em direção a zero, preservando o caminho rápido FP16. Também corrige travamento com 2x AA e BC4/5/6H.
- **v1.1.8 — iluminação/FPS e frame generation:** corrige leitura de texel buffer inteiro como float, devolvendo os bits armazenados; e evita crash de present-wait quando Android loader é dono da swapchain, ocultando as extensões de present wait/ID/timing/maintenance nesse caminho. Quando o app carrega a biblioteca diretamente, essas extensões continuam disponíveis.

Build declarado pelo projeto para v1.1.8: Mesa 26.3.0-devel commit-base `5a07217f`, série `panvk-kbase-android` v0.1.0-rc4 (`5b87b74`), 149 patches próprios. A base do nosso projeto atual é Mesa 27.0.0-devel, portanto os patches não podem ser aplicados sem portabilidade e revisão de API/estruturas.

## Relatos de bugs que importam ao POCO X7 Pro / G720

1. **Fire Emblem Three Houses — POCO X7 Pro, G720:** issue #3 do repositório RG556 relata falhas gráficas pesadas inicialmente. O autor do relato disse em 18 nov que a atualização mais recente passou a executar o jogo, mas com FPS abaixo de 20 e carregamento lento; o mantenedor disse em 20 nov que deveria estar corrigido nas versões mais recentes. Evidência de progresso real no mesmo aparelho, mas desempenho ainda fraco.
2. **Pokémon Legends Z-A — POCO X7 Pro, G720:** issue #5 do repositório Ace relata que o jogo abre e depois fica com tela preta mesmo nas versões mais recentes. O mantenedor pediu o arquivo `panvk_display_*.txt` e log do emulador; o relato ainda não contém diagnóstico final. Portanto v1.1.8 não elimina toda tela preta no G720.
3. **Life is Strange 2 — POCO X7 Pro, G720:** issue Eden #4734 relata áudio funcionando com tela 3D preta. O log aponta recursos Vulkan ausentes/limites incompatíveis e “Geometry streams is not implemented”; o usuário testou Faux123 v1.1.7 e v1.1.8, com imagem muito fraca por instantes e depois tela preta/fechamento. É um caso de compatibilidade jogo/emulador/recursos, não prova de falha universal do WSI.
4. **Mali-G1-Ultra / MediaTek MT6993:** issues #5, #7, #8 e #10 no repositório RP4 Pro registram faixas pretas/flicker, corrupção visual com HW overlays, crash em draws instanciados, custo alto por draw e OOM por expansão de BC6H. São pistas sobre riscos em outras gerações MediaTek, não podem ser atribuídas diretamente ao G720.
5. **Mali-G615 MC6 / MT6897:** issue #4 no repositório Ace descreve swapchain criada e crash logo após primeiro frame em v1.1.3–v1.1.8; o relato depois identificou chamada do app a `vkCmdClearColorImage` com `VkImage` nulo/inválido. O caso foi fechado como not planned pelo autor do relato e não deve ser tratado como bug confirmado do driver.
6. **Outros relatos:** Pixel 7/G710 com tela preta apenas no objeto 3D e HUD visível; G57 com personagens sem cor/preto em Dragon Ball; G925 com glitches em Sniper Elite 4; G57 com quedas de FPS em Call of Duty. Esses relatórios reforçam que compatibilidade é específica por jogo, app, GPU e versão.

## Disponibilidade do código-fonte e patches

Os repositórios públicos dos quatro drivers contêm essencialmente README, LICENSE e workflows; não contêm a árvore Mesa nem a série completa dos patches próprios. O README informa que o build container, os patches, os testes e o guia de reprodução ficam num repositório companheiro privado. Logo, não há como baixar/publicamente auditar os 149 patches completos a partir do perfil público.

Os elementos reproduzíveis publicamente são: base Mesa/commit, série KBASE v0.1.0-rc4, contagem de patches por release, notas de release, hashes dos binários, relatórios FauxVkDB e issues. O pacote binário não deve ser confundido com o código-fonte dos patches.

## Implicações para nosso projeto

1. A correção MediaTek/gralloc/layout do v1.1.5 e o fix FP16 do v1.1.7 são referências prioritárias para comparar com nosso código.
2. O v1.1.8 é uma referência real do mesmo POCO X7 Pro: o relatório #3263 confirma execução de checks e o #3350 dá uma linha de base sintética.
3. O nosso diagnóstico anterior encontrou ausência de entrada/registro Android WSI na árvore atual. O FauxVkDB confirma que o v1.1.8 tem AHB e swapchain, e os relatos no POCO mostram jogos que chegam a apresentar frames. Isso mantém Android WSI, AHB/gralloc, sincronização/fences e formato de buffer como prioridade de investigação.
4. Não transplantar cegamente os patches nem substituir nossa biblioteca por binário de outra base. A série própria é privada e a diferença Mesa 26.3 vs 27.0 exige port manual e testes.
5. Não declarar a tela preta resolvida até testar no aparelho, com um teste de apresentação contínua e depois jogos. Manter renderização/apresentação pela GPU; evitar `DeviceWaitIdle` por frame e cópia CPU de framebuffer.
6. O pacote v1.1.8 pode servir como baseline comparativa de comportamento no mesmo aparelho, desde que o app aceite o formato e carregamento PanVK/Mali. Não é garantia para BOTW Recomp nem substitui nosso teste.

## Links consultados

- Perfil: https://github.com/faux123
- RP4 Pro PanVK: https://github.com/faux123/panvk-faux123-driver-rp4pro
- RG556 PanVK: https://github.com/faux123/panvk-faux123-driver-rg556
- Ace PanVK: https://github.com/faux123/panvk-faux123-driver-ace
- Pixel 7 PanVK: https://github.com/faux123/panvk-faux123-driver-pixel7
- Release v1.1.8: https://github.com/faux123/panvk-faux123-driver-ace/releases/tag/v1.1.8
- Release v1.1.7: https://github.com/faux123/panvk-faux123-driver-ace/releases/tag/v1.1.7
- Release v1.1.5: https://github.com/faux123/panvk-faux123-driver-ace/releases/tag/v1.1.5
- FauxVkDB #3263 (validação exata): https://fauxvkdb.canonspike.com/report/3263
- FauxVkDB #3350 (benchmark exato): https://fauxvkdb.canonspike.com/report/3350
- FauxVkDB matriz G720 MC7: https://fauxvkdb.canonspike.com/gpu/13b5-c8700010/499e3eae32a27340?speed_on=xiaomi-2412dpc0ag
- POCO X7 Pro / Fire Emblem Three Houses: https://github.com/faux123/panvk-faux123-driver-rg556/issues/3
- POCO X7 Pro / Pokémon Legends Z-A: https://github.com/faux123/panvk-faux123-driver-ace/issues/5
- G615 crash after present: https://github.com/faux123/panvk-faux123-driver-ace/issues/4
- G720 Life is Strange 2 black screen: https://git.eden-emu.dev/eden-emu/eden/issues/4734
- Reddit v1.1.7: https://www.reddit.com/r/faux123/comments/1xx6hd4/panvk_v117_black_3d_screen_fixed_on_g720g920g925/
- Reddit v1.1.8: https://www.reddit.com/r/faux123/comments/1xy42ex/panvk_v118_fixes_very_low_frame_rates_and_wrong/
