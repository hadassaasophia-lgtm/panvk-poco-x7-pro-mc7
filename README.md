# PanVK — POCO X7 Pro / Mali-G720 MC7

Projeto experimental de avaliação do PanVK para o POCO X7 Pro.

## Alvo de hardware

- Dispositivo: POCO X7 Pro (codinome `rodin`)
- SoC: MediaTek Dimensity 8400-Ultra (MT6899)
- GPU: ARM Mali-G720 MC7
- GPU ID informado pelo aparelho: `0xC8700010`
- Arquitetura: Mali v12 / CSF
- Android: 16 (API 36)
- ABI: `arm64-v8a`

## Estado real do projeto

**Experimental — ainda não validado para uso no aparelho.**

O workflow de CI compila o pacote e verifica arquitetura ELF, metadados, licença e símbolos ICD. Uma execução verde confirma somente essas verificações de build/empacotamento; não prova que o driver inicializa corretamente no Android do POCO, que a GPU é reconhecida pelo KBASE/CSF ou que jogos funcionam.

Veja [docs/AUDIT-STATUS.md](docs/AUDIT-STATUS.md) para o escopo da auditoria, evidências e bloqueios.

## Compilação

O workflow manual está em [Build PanVK POCO X7 Pro MC7](.github/workflows/build-android.yml). Ele usa o código-fonte compactado `mali-panvk-main.zip`, Android NDK r29 e LLVM 21.

## Critério para declarar concluído

1. Confirmar a origem, versão e integridade do código-fonte e patches.
2. Compilar ARM64 a partir do código-fonte auditado.
3. Verificar dependências e carregamento ICD no ambiente Android alvo.
4. Validar identificação real do G720 MC7 via KBASE/CSF.
5. Executar testes Vulkan e aplicações-alvo no aparelho.
6. Publicar pacote reproduzível, hashes e resultados dos testes.

Não instalar esta biblioteca sobre o driver de sistema nem substituir bibliotecas de vendor.