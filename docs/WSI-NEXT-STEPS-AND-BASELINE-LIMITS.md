# Próxima etapa: análise do WSI e limites da base Faux123 (2026-11-25)

## Evidência de compatibilidade da base

A release pública Faux123 v1.1.8 declara como base Mesa 26.3.0-devel commit 5a07217f e panvk-kbase-android v0.1.0-rc4 commit 5b87b74, acrescida de patches privados do autor. A própria documentação limita os testes do autor a Mali-G57, G77, G610 e G710. O POCO X7 Pro com G720 MC7 não está entre os dispositivos de validação do autor. Isso não invalida o relato community de funcionamento no G720, mas impede tratar a combinação como validada pelo mantenedor Faux123.

Fonte: https://github.com/faux123/panvk-faux123-driver-rg556/releases

## Distinção importante no problema de tela preta

O relato público do mesmo modelo de aparelho em panvk-kbase-android issue 16 descreve `VK_ERROR_INCOMPATIBLE_DISPLAY_KHR` na criação da swapchain. O mantenedor respondeu que v26.3.1 escolhe o caminho de apresentação por swapchain e pode ajudar nesse erro. No caso do usuário atual, o log mostra que a swapchain foi criada (2712x1220, 6 imagens) e há atividade de renderização `[v12pass]`; portanto, não é o mesmo estágio exato. A issue é uma referência arquitetural, não prova da causa da falha atual.

Fonte: https://github.com/zenithblue-oss/panvk-kbase-android/issues/16

## Caminho de apresentação relevante

O changelog da linha panvk-kbase mais recente documenta mudanças específicas de Android present: aguardar a image fence, thread opcional de apresentação e registro do timing no log FPS. A linha RC4 incorporada à Faux123 v1.1.8 é anterior a essas mudanças. Como os patches Faux123 são privados e a RC10 não tem fonte pública verificada, não é seguro transplantar alterações isoladas sem obter a árvore exata e revisar a compatibilidade.

Fonte: https://github.com/zenithblue-oss/panvk-kbase-android/releases

## Plano de comparação sem alterar o driver instalado

1. Manter o artefato Faux123 v1.1.8 original como baseline.
2. Mapear a ordem do Android WSI: acquire da imagem, submit GPU, export/import de fence, espera pela image fence e present.
3. Distinguir a falha de swapchain (retorno VK_ERROR), falha de sincronização (fence nunca sinalizada/timeout), e falha de conteúdo (present retorna mas pixels são pretos).
4. Só propor patch mínimo se a diferença for demonstrável contra a base RC4; não copiar automaticamente a série P-C da v26.3.1.
5. Manter o fallback MediaTek de formato plain e não forçar AFBC/modifier.
6. Tratar cópias CPU de shader global memory como hipótese de desempenho separada da tela preta.

## Estado

Apenas análise de fontes e documentação. Sem build, sem alteração de .so, sem instalação e sem teste no dispositivo. Para distinguir os três casos acima, é necessário um log completo do mesmo episódio incluindo retorno de acquire/submit/present e eventual fence timeout.
