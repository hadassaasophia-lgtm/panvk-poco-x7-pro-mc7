# Investigação da tela preta e apresentação — Faux123 / POCO X7 Pro

Data: 2026-11-25

## Sintoma confirmado

O BOTW Recomp continua com áudio e controles responsivos durante a tela preta. Isso exclui um travamento total do processo, mas não separa sozinho falha de renderização de falha de apresentação (present).

## Achados novos nas notas oficiais Faux123

1. **v1.1.5 — correção MediaTek de formato de framebuffer.** O autor documenta que o display MediaTek não conseguia ler o formato comprimido em que alguns jogos desenhavam a imagem. A correção solicita um formato simples para MediaTek, Android 13 e Android 14+. Testadores em MT6899/Android 16 e Mali-G720 confirmaram que a tela cinza com traços coloridos desapareceu. A nota informa que os problemas/limitações da v1.1.5 continuam aplicáveis nas releases seguintes, inclusive v1.1.8.
   - Fonte: https://github.com/faux123/panvk-faux123-driver-rg556/releases

2. **Interpretação do display report.** O registro do POCO mostra swapchain RGBA8 com modifier zero e `linear-forced 1`. À luz da correção v1.1.5, isso pode ser exatamente o fallback deliberado para apresentar um formato simples no display MediaTek; não é evidência suficiente de defeito. Não remover nem inverter esse fallback sem comparar a implementação e provar que o HAL/display aceita outro formato.

3. **v1.1.7 — correção de cena 3D preta em G720/G920/G925.** A nota oficial descreve NaN propagado por conversão/arredondamento FP16 em shaders, corrigido com arredondamento em direção a zero sem desativar a velocidade FP16. A v1.1.8 inclui as mudanças posteriores e declara que as limitações da v1.1.5 permanecem.
   - Fonte: https://github.com/faux123/panvk-faux123-driver-rg556/releases

4. **v1.1.8 — mudanças de present-wait sob Android loader.** A release deixa de expor present-wait, present-ID, present-timing e swapchain-maintenance quando carregada pelo loader Android, pois o loader gerencia a swapchain. Isto é relevante para ownership e sincronização de apresentação, mas não prova que seja a causa do sintoma deste aparelho.

5. **v1.1.9-rc10 não localizada como release/tag público** nos repositórios Faux123 RG556 e RP4 Pro consultados em 2026-11-25. O nome da versão é confirmado pelo log do usuário, mas não há artefato público/diff disponível nessas fontes para atribuir regressão específica à RC10.
   - RG556: https://github.com/faux123/panvk-faux123-driver-rg556/releases
   - RP4 Pro: https://github.com/faux123/panvk-faux123-driver-rp4pro/releases

## Consequências para a investigação

- Não tratar `linear-forced 1` como erro por si só. A correção MediaTek da v1.1.5 pode depender justamente de solicitar um formato não comprimido/plain para o buffer de apresentação.
- Como o usuário relata áudio e controles ativos sem imagem, instrumentar separadamente: surface/swapchain creation, acquire, queue submit, release fence e queue present. A criação da swapchain e a atividade `[v12pass]` não provam que o frame chegou ao compositor.
- Separar tela totalmente preta de cena 3D preta com UI/compositor ainda visível. A correção FP16 v1.1.7 é pertinente à segunda categoria, não prova a causa de uma superfície inteira preta.
- A mensagem `no heap import: shader global memory through CPU copies` permanece uma frente de desempenho; não é, sem mais evidência, explicação da perda total de imagem.
- Não aplicar o patch experimental de acquire-fence, não remover poll de native fence, não forçar modifiers em todos os render targets e não introduzir cópia CPU/DeviceWaitIdle por frame.

## Próxima evidência necessária

No próximo log do mesmo episódio, preservar as linhas desde o início do jogo até depois da tela preta, especialmente qualquer retorno/erro de `vkAcquireNextImageKHR`, `vkQueueSubmit`, `vkQueuePresentKHR`, native fence, `VK_ERROR_*`, `surface`, `swapchain` ou `ANativeWindow`. Comparar o mesmo cenário entre v1.1.8 e RC10, mantendo resolução, opções e cena iguais.

## Estado

Auditoria documental atualizada. Nenhuma biblioteca foi modificada, nenhum patch de runtime foi aplicado e nenhum teste foi executado no aparelho nesta etapa.
