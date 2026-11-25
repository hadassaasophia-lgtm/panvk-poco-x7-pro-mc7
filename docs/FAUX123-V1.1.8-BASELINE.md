# Faux123 v1.1.8 — referência para POCO X7 Pro / Mali-G720 MC7

Status: auditoria/adaptação experimental. Não é uma reconstrução binária do pacote Faux123 e não está validado no aparelho.

## Decisão

Usar o Faux123 PanVK v1.1.8 como referência principal de comportamento e integração. Preservar as versões anteriores do projeto em suas branches; esta linha de trabalho parte de `audit/panvk-kbase-v26.3.1` e não as sobrescreve.

## Hardware-alvo

- POCO X7 Pro, codinome rodin
- MediaTek Dimensity 8400-Ultra / MT6899
- ARM Mali-G720 MC7, GPU ID 0xC8700010
- Mali v12 / CSF
- Android 16 / API 36, arm64-v8a

## Proveniência do Faux123 v1.1.8

Release oficial: https://github.com/faux123/panvk-faux123-driver-pixel7/releases/tag/v1.1.8

Arquivo publicado: `panvk_faux123_v1.1.8.adpkg.zip`

SHA-256 do ZIP publicado (asset GitHub): `1898e89be6256e67762876fe249e9017717f8643cc5fb6194cf11195fe6da6c8`

SHA-256 da biblioteca informado nas notas da release: `499e3eae32a27340777cb890aac92468c2519d57223bfad93a2e2a8f71029728`

Build declarado pelo autor:
- Mesa `5a07217f`
- `zenithblue-oss/panvk-kbase-android` série `v0.1.0-rc4`, commit `5b87b74`
- 149 patches do Faux123

A release v1.1.8 declara duas mudanças principais:
1. Buffers de texel inteiros lidos como float retornam os bits armazenados, corrigindo baixa taxa de quadros e iluminação incorreta em alguns jogos.
2. Quando carregado pelo loader Vulkan do Android, o driver deixa de expor present-wait, present-ID, present-timing e swapchain-maintenance, evitando o caminho de crash correspondente.

A release foi testada pelo autor em G57, G77, G610 e G710. Isso não deve ser confundido com validação oficial do autor em G720. Há registros comunitários no FauxVkDB para G720 MC7/POCO X7 Pro, mas isso não substitui o teste do BOTW neste aparelho.

## Regra de implementação

- Preservar a base e as correções comprovadas do Faux123 sempre que o código-fonte correspondente estiver disponível.
- Não substituir os 149 patches por alterações especulativas.
- Não declarar equivalência binária nem reconstrução idêntica sem acesso aos patches completos e comparação de hashes.
- A documentação pública da release informa os 149 patches, mas o conjunto completo não está publicado nos repositórios públicos consultados. Portanto, uma compilação independente só poderá ser chamada de adaptação baseada no Faux123, nunca de rebuild idêntico.
- Adaptar para G720 MC7 apenas com evidência técnica: detecção GPU/CSF, KBASE, formatos de framebuffer/MT6899, sincronização e memória.
- Não aplicar patches G720 MC8 automaticamente ao MC7.
- Não alterar bibliotecas de sistema/vendor; distribuição apenas como pacote de driver de usuário.
- Não declarar correção de tela preta ou estabilidade sem teste real no POCO X7 Pro com logs.

## Próximas verificações obrigatórias

1. Obter e inspecionar o ZIP oficial original, incluindo estrutura interna e metadados do pacote.
2. Comparar estrutura e metadados com o formato realmente aceito pelo gerenciador de drivers usado pelo usuário. Não presumir que todo importador AdrenoTools aceite pacotes Mali.
3. Verificar disponibilidade/licença dos fontes e patches; identificar exatamente o que é reproduzível.
4. Preparar uma branch de build separada e reproduzível, preservando os artefatos originais.
5. Validar ELF/ABI, dependências, ICD e símbolos.
6. Testar no aparelho: inicialização Vulkan, BOTW, tela preta, renderização, memória, sincronização e FPS.

## Critério de conclusão

Build verde significa apenas que compilação e empacotamento passaram. Conclusão exige teste real no POCO X7 Pro e evidência de que o BOTW inicia e renderiza sem tela preta, travamentos ou regressões graves.
