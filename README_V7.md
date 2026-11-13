# Crypto Hunter AI 7.0 — Etapa 1

Protótipo independente para testes, sem substituir a versão 6.0.

## Funcionalidades implementadas
- Interface em 8 idiomas (português, inglês, espanhol, francês, alemão, italiano, chinês simplificado e japonês).
- Consulta de saldo e quantidade de transações confirmadas de endereços públicos Bitcoin via mempool.space.
- Catálogo manual de desafios públicos com fonte HTTPS, declaração de verificação das regras, pesquisa e exportação CSV.
- Triagem local de recuperação: **não envia dados**, não guarda segredos, não transfere moedas.

## Instalação local
```bash
pip install -r requirements_v7.txt
streamlit run app_v7.py
```

## Como testar no GitHub/Streamlit sem perder a versão 6
1. Faça backup dos arquivos atuais.
2. Adicione `app_v7.py` e `requirements_v7.txt` ao repositório **sem apagar `app.py`**.
3. Crie um novo app no Streamlit Community Cloud apontando para `app_v7.py` (ou use um branch de teste). O Streamlit Cloud costuma instalar dependências de `requirements.txt`, não de `requirements_v7.txt`: acrescente `requests>=2.31,<3` ao `requirements.txt` atual se ainda não estiver presente.
4. Teste os oito idiomas, um endereço público e a exportação CSV. Não publique formulários com dados pessoais até haver autenticação, privacidade e armazenamento adequados.

## Limitações conhecidas
- Catálogo apenas na sessão do navegador; reiniciar sessão perde itens não exportados.
- Sem descoberta automática de desafios, sem IA externa, sem PostgreSQL, sem autenticação ou pagamentos.
- A API pública pode estar indisponível ou limitar requisições.
- Não determina se endereços estão abandonados e não acessa carteiras de terceiros.
- A tradução cobre a interface principal; rótulos técnicos e avisos secundários ainda precisam de revisão nativa.
