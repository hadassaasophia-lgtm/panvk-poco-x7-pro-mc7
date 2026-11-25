# Migração experimental — PanVK KBASE v26.3.1

Data: 2026-11-25

## Decisão

A linha experimental deste projeto passa a avaliar a release `panvk-kbase-v26.3.1` do projeto `zenithblue-oss/panvk-kbase-android`, mantendo a linha Mesa 27 isolada no branch `audit/fix-panvk-g720-mc7`.

- Branch de migração: `audit/panvk-kbase-v26.3.1`
- Release de referência: `panvk-kbase-v26.3.1`
- Repositório upstream: https://github.com/zenithblue-oss/panvk-kbase-android
- Commit exato do tag da release: `3c82008657f3edd44cc5fbed4c2f80f8a29c90fc`
- Commit-base Mesa 26.3.0-devel citado na auditoria upstream: `5a07217f034b3e50d8c7c7794f97a2df1742613b`

## Por que testar essa base

A release reúne uma série de integração KBASE/CSF e Android WSI, além de mudanças de gerenciamento de memória relevantes para investigar tela preta, falha de apresentação e encerramento sob pressão de memória. Isso a torna uma base experimental mais rastreável para o nosso alvo do que continuar adicionando correções isoladas sobre a snapshot Mesa 27 atual.

Isso **não** demonstra que a release funciona no POCO X7 Pro, nem que será mais rápida. O perfil G720 v12 CSF do projeto upstream foi descrito como planejado, não como validado especificamente neste aparelho.

## Regras de migração

1. Não alterar nem sobrescrever `audit/fix-panvk-g720-mc7`; ele permanece como referência Mesa 27.
2. Fixar e registrar a origem do código Mesa e a série de patches por commit/hash antes de compilar.
3. Revisar as mudanças Android WSI/gralloc e KBASE/CSF da release contra o ambiente Android 16/MediaTek MT6899.
4. Reaplicar somente correções locais comprovadamente compatíveis, uma a uma; não transplantar patches Mesa 27 sem revisão.
5. Preservar o comportamento correto de sincronização: nunca descartar native fence nem fingir que espera KBASE foi concluída.
6. Manter o pacote AdrenoTools rootless e não substituir bibliotecas de sistema/vendor.
7. Validar build, ELF, metadados e ZIP; depois testar no aparelho. Build verde não equivale a teste de runtime.
8. Comparar logs de criação/apresentação da swapchain, formatos de framebuffer, AHardwareBuffer/gralloc, sincronização e memória. Só então medir FPS.

## Estado desta branch

- [x] Criada branch isolada a partir da auditoria anterior.
- [x] Registrada a release e o commit exato do tag upstream.
- [ ] Auditar integralmente workflow, fonte, patches e manifesto da release.
- [ ] Identificar e registrar os hashes do código-fonte e da série de patches usados.
- [ ] Adaptar o workflow deste projeto para compilar exatamente essa base.
- [ ] Executar CI e inspecionar o pacote gerado.
- [ ] Testar no POCO X7 Pro / Mali-G720 MC7 / Android 16.

## Critério para avançar

Não publicar a migração como pacote recomendado enquanto não houver build reproduzível e teste de inicialização/apresentação no aparelho. Se a integração não puder ser reproduzida a partir dos arquivos públicos, registrar o bloqueio em vez de substituir silenciosamente a fonte atual.
