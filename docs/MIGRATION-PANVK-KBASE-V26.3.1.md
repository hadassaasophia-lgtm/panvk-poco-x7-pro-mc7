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

## Pipeline de compilação experimental

Foi criado `.github/workflows/build-panvk-kbase-v26.yml` na branch de migração. O workflow:

1. Clona o tag upstream imutável `panvk-kbase-v26.3.1` e verifica o commit `3c82008657f3edd44cc5fbed4c2f80f8a29c90fc`.
2. Lê e verifica o commit Mesa `5a07217f034b3e50d8c7c7794f97a2df1742613b` de `sources.lock`.
3. Aplica as famílias de patches selecionadas pelo script upstream para `g720-v12-csf`.
4. Compila Android ARM64 com NDK r29 e API mínima 35.
5. Faz verificações estáticas e prepara um pacote ADPKG marcado explicitamente como `experimental_unverified`, com proveniência e hashes.

Execução iniciada pelo push:
- Run: https://github.com/hadassaasophia-lgtm/panvk-poco-x7-pro-mc7/actions/runs/45602166811
- Run ID: `45602166811`
- Commit inicial do workflow: `e8d30089bcad480495ecaefdae294689713a6eff`

Uma correção de empacotamento (uso do NOTICE.md do upstream e newline válido nos JSON) foi aplicada depois que essa primeira execução começou. Portanto, se a primeira execução alcançar a etapa de empacotamento, ela pode refletir a versão inicial do workflow; a revisão atual na branch contém a correção e deverá ser usada em uma execução posterior se necessário.

**Importante:** este pipeline não inventa patches CSF v12 ausentes. O resultado, se compilar, será apenas um candidato experimental para teste controlado; não prova suporte ao MC7 nem resolve a tela preta por si só.


## Correção G720 CSF incorporada ao pipeline (2026-11-25)

A auditoria do repositório de referência fixado em `wonderkast02/panvk-g720-kbase-csf@d9cbb91e5df720f0a62c4b5010d96c327aec315f` encontrou uma correção específica de contagem de registradores CSF para G720:

- `cs_reg_count` passa a ser derivado de `(stream_features & 0xff) + 1`, em vez de assumir 96.
- `nr_kernel_registers` passa a usar `MAX2(csif_info->unpreserved_cs_reg_count, 4)`.

A correção foi adicionada localmente em `patches/csf/0001-g720-csf-register-count.patch` e o workflow agora:
1. aplica a série comum da release v26.3.1;
2. verifica o patch G720 com `git apply --check`;
3. aplica o patch G720;
4. copia o patch para a árvore upstream antes de calcular `patchSeriesId`, para que a proveniência inclua esse delta.

Referência pública do patch original:
https://github.com/wonderkast02/panvk-g720-kbase-csf/blob/d9cbb91e5df720f0a62c4b5010d96c327aec315f/patches/0001-panvk-kbase-g720-register-count.patch

**Limite da evidência:** o README da referência relata validações em Mali-G720 MC8, não especificamente no MC7 do POCO X7 Pro. O patch é pertinente à arquitetura G720, mas ainda precisa passar pela aplicação limpa no Mesa 26.3.0-devel e pelo teste real neste aparelho.

CI disparado pelo push: https://github.com/hadassaasophia-lgtm/panvk-poco-x7-pro-mc7/actions/runs/45602486853
Estado no último acompanhamento: execução em andamento; nenhum binário validado ou artefato disponível ainda.


## Primeiro bloqueio de compilação e correção do CI

A primeira execução que chegou à configuração Meson falhou antes de compilar o driver: faltava a dependência de desenvolvimento **libdrm** no ambiente host (`Dependency "libdrm" not found`). A aplicação da série upstream e do patch G720 havia passado nessa execução.

Correção aplicada ao workflow:
- adiciona `libdrm-dev` às dependências do runner Ubuntu;
- adiciona um grupo de concorrência por branch com cancelamento de builds antigos, evitando gastar runners em compilações redundantes geradas por cada commit de ajuste.

A correção do ambiente não altera o código do driver. A próxima execução precisa confirmar que a configuração Meson passa e revelar eventuais dependências seguintes.
