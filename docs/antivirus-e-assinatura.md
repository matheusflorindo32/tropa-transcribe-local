# Microsoft Defender, SmartScreen e assinatura

Nunca desative o antivírus, o SmartScreen ou políticas institucionais para
instalar este projeto. Falso positivo deve ser registrado com hash, versão,
arquivo afetado e resultado, e submetido ao fornecedor para análise.

## Validação obrigatória

1. Gere o bundle e os hashes em máquina controlada.
2. Mantenha Defender atualizado e execute verificação completa no diretório
   `dist` e no instalador.
3. Registre data, versão das definições, hashes, resultado e captura.
4. Em VM Windows 11 limpa, baixe o instalador pelo canal de teste e registre o
   comportamento do SmartScreen.
5. Se houver alerta, não ensine a contorná-lo como procedimento normal; suspenda
   a publicação e investigue.

## Authenticode

Use certificado de assinatura de código emitido para a identidade responsável
ou serviço de assinatura compatível. O `SignTool` do Windows SDK deve usar
SHA-256 para digest e timestamp RFC 3161, seguido de verificação:

```powershell
signtool sign /fd SHA256 /tr "URL_RFC3161_DO_PROVEDOR" /td SHA256 /a arquivo.exe
signtool verify /pa /all /v arquivo.exe
```

Não armazene PFX, senha ou segredo de assinatura no repositório. Certificados
OV/EV e serviços gerenciados têm custos, validação de identidade e requisitos
variáveis; obtenha cotação atual do fornecedor. Assinatura melhora identidade e
integridade, mas uma versão nova ainda pode apresentar aviso de reputação do
SmartScreen. Em 2026-07-24, o host de desenvolvimento executou scans
personalizados com Defender ativo (definição `1.455.328.0`) no bundle e no
instalador e não registrou detecção recente. Isso não substitui a repetição na
VM limpa. O instalador atual permanece **NotSigned** e o SmartScreen ainda não
foi validado.

Fontes oficiais: documentação do
[SignTool](https://learn.microsoft.com/windows/win32/seccrypto/signtool) e de
[reputação do SmartScreen](https://learn.microsoft.com/windows/apps/package-and-deploy/smartscreen-reputation).
