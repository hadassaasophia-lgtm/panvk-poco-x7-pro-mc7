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
- O README anterior marcava integração de fonte, patches, compilação, testes e ZIP final como pendentes.

## Limites importantes

1. A compilação do workflow não é um teste de execução no POCO X7 Pro.
2. As verificações de símbolos ICD não garantem que todas as funções Vulkan necessárias estejam implementadas corretamente.
3. Uma correspondência textual de G720 ou `0xc8700010` não prova que o kernel KBASE/CSF reporta os recursos reais do MC7 corretamente.
4. Não há, nesta auditoria, leitura confirmada de `RAW_CORE_FEATURES` e `RAW_SHADER_PRESENT` do aparelho.
5. Não há resultado de teste de PanVK executando jogos BOTW Recomp ou GTA V Recomp no aparelho.
6. O ZIP de artifact previamente inspecionado continha a biblioteca `libvulkan_panfrost.so`, `meta.json` e `NOTICE.txt`, mas não incluía o código-fonte.

## Próximas verificações técnicas necessárias

- Extrair e revisar o conteúdo completo de `mali-panvk-main.zip` (incluindo histórico/origem, submódulos e patches locais).
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