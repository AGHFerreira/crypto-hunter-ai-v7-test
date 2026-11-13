# Crypto Hunter AI 7.1 — teste público

Aplicativo Streamlit independente para testes de oito idiomas, explorador de endereços públicos Bitcoin, catálogo de desafios públicos autorizados e triagem educativa de recuperação.

## Implantação

No repositório público de testes, **substitua `app_v7.py`** por este arquivo e **substitua `requirements.txt`** pelo arquivo do pacote. Mantenha a implantação com `Main file path = app_v7.py`. O Streamlit deve atualizar o aplicativo automaticamente após o commit.

## Testes

1. Mude entre os oito idiomas pelo menu lateral.
2. Consulte um endereço público conhecido e confira saldo e transações.
3. No Puzzle Research, tente enviar sem autorização (deve bloquear). Cadastre apenas desafios com autorização verificável, exporte CSV e teste a remoção.
4. No Recovery Center, teste a exigência de confirmação de titularidade, a geração de orientações e o simulador de comissão.

## Limitações e segurança

- O registro de enigmas é **manual e temporário** (Streamlit Session State); não há pesquisa automática nem verificação automática das regras.
- O Recovery Center **não recupera fundos**, não registra clientes e não oferece autenticação ou banco de dados.
- Não envie frases-semente, chaves privadas, senhas, backups, documentos pessoais ou informações de clientes.
- A consulta de Bitcoin depende da API pública mempool.space e pode sofrer limites ou indisponibilidade.
- A tradução de orientações mais extensas em alguns idiomas ainda é parcial; revisão linguística humana é recomendada antes de uso comercial.
- Esta é uma implantação de demonstração, **não** uma plataforma comercial pronta.
