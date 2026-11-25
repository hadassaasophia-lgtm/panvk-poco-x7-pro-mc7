# Correção de base: Faux123 v1.1.8 / Mesa 26.3.0 (2026-11-25)

A direção anterior que usava `mali-panvk-main.zip` / Mesa 27.0.0-devel foi descartada para esta linha de trabalho. O usuário determinou explicitamente que a base deve ser a mesma da release Faux123 v1.1.8.

## Pins públicos verificados na release Faux123 v1.1.8

- Mesa: `5a07217f034b3e50d8c7c7794f97a2df1742613b` (26.3.0-devel)
- panvk-kbase-android: `v0.1.0-rc4`, commit `5b87b74d3e2580d5816e7f2c629f6f016a462f28`
- A release informa ainda 149 patches privados Faux123.
- O pacote oficial é `panvk_faux123_v1.1.8.adpkg.zip`; seu hash SHA-256 oficial é `1898e89be6256e67762876fe249e9017717f8643cc5fb6194cf11195fe6da6c8`.
- Hash da biblioteca oficial: `499e3eae32a27340777cb890aac92468c2519d57223bfad93a2e2a8f71029728`.

Fontes:
- https://github.com/faux123/panvk-faux123-driver-rg556/releases/tag/v1.1.8
- https://github.com/zenithblue-oss/panvk-kbase-android/commit/5b87b74d3e2580d5816e7f2c629f6f016a462f28

## Alteração no pipeline

Criado `.github/workflows/build-faux123-mesa2630-base.yml` para buscar os pins exatos acima, buscar Mesa pelo commit fixo, aplicar a série pública KBASE RC4 para perfil G720 v12 CSF e compilar ARM64 Android.

O pipeline nomeia o resultado como **public Faux123 base experimental** e registra explicitamente que não inclui os 149 patches privados. Portanto, ele não será descrito como reconstrução idêntica nem como pacote oficial Faux123. Isso impede falsa equivalência enquanto preserva a base Mesa 26.3.0 pedida.

O workflow de auditoria que lia `mali-panvk-main.zip` (Mesa 27) foi removido desta branch como gatilho automático, para não continuar misturando bases.

## Limitação incontornável

A release pública não contém os 149 patches privados em arquivos fonte. O pacote .adpkg oficial contém a biblioteca compilada, não a árvore-fonte desses patches. Sem receber uma fonte licenciada/fornecida pelo autor, não é possível reconstruir o Faux123 completo nem aplicar com segurança suas alterações privadas ao código-fonte. O pipeline pode compilar a base pública exata, mas não pode inventar nem alegar incluir os patches privados.

## Estado

- Base Mesa 27 retirada do fluxo automático desta branch.
- Mesa 26.3.0-devel commit e KBASE RC4 commit fixados.
- Pipeline de build criado; execução e artefato ainda precisam ser concluídos.
- Nenhum pacote foi instalado ou validado no POCO X7 Pro.
