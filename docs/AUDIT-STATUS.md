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
