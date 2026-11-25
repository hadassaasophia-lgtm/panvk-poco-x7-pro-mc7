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

## Auditoria inicial da release upstream

Arquivos consultados diretamente no tag fixo `panvk-kbase-v26.3.1`:

- `sources.lock`: fixa Mesa em `5a07217f034b3e50d8c7c7794f97a2df1742613b`, versão `26.3.0-devel), e identifica a série por `sha256:374b7b830111a848515d3e0ec41a60b902bc57938deb420ecea7de8a03f58ecd`.
- `patches/README.md`: define famílias separadas para Android, KBASE, CSF por arquitetura, loader ICD e WSI; exige falha rígida em qualquer patch que não aplique exatamente.
- `scripts/apply-patches.sh`: para CSF, seleciona `common android kbase-common app-loader wsi csf csf-v12` quando o perfil declara arquitetura 12.
- `profiles/g720-v12-csf.json`: declara Mali-G720, arquitetura 12 e frontend CSF, mas seu status literal é **planned P24**, não validado no POCO X7 Pro.
- `.github/workflows/build.yml`: o CI upstream mostrado no tag executa validação de fonte e aplicabilidade para o perfil G615; não é evidência de build/teste G720.

### Consequência para nossa migração

A release fornece uma série pública e rastreável, mas o perfil G720 ainda é planejado. Portanto, não devemos usar o artefato da release como se fosse um binário G720 pronto. O trabalho correto é aplicar e auditar especificamente as famílias CSF v12 e Android/WSI, verificar cada patch sem offsets/fuzz e revisar o perfil antes de compilar.

A árvore upstream contém ainda patches Android WSI e KBASE de sincronização/memória que parecem diretamente relevantes, mas sua presença no repositório não significa que todos estejam incluídos no perfil G720 nem que funcionem no MT6899. A seleção efetiva deve seguir o script de aplicação e o manifesto da release.

Links fixos:
- https://github.com/zenithblue-oss/panvk-kbase-android/blob/panvk-kbase-v26.3.1/sources.lock
- https://github.com/zenithblue-oss/panvk-kbase-android/blob/panvk-kbase-v26.3.1/profiles/g720-v12-csf.json
- https://github.com/zenithblue-oss/panvk-kbase-android/blob/panvk-kbase-v26.3.1/scripts/apply-patches.sh
- https://github.com/zenithblue-oss/panvk-kbase-android/blob/panvk-kbase-v26.3.1/patches/README.md
