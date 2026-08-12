# Benedito MVP

Protótipo informacional do assistente virtual da Prefeitura de Macaé.

## O que esta versão faz
- Lê a aba `Base_Oficial` da planilha do projeto.
- Interpreta perguntas simples por intenção/palavras-chave.
- Recupera a unidade mais provável.
- Responde endereço, horário, telefone, WhatsApp e e-mail.
- Respeita campos incompletos e evita completar dados por inferência.
- Usa a Ouvidoria Geral como fallback quando a confiança é baixa.

## Rodar localmente
1. Instale Python 3.11+.
2. `pip install -r requirements.txt`
3. `streamlit run app.py`

## Implantar no Streamlit Community Cloud
Suba estes arquivos para um repositório GitHub e escolha `app.py` como entrypoint.

## Decisão arquitetural do piloto
Esta versão deliberadamente não usa um LLM/API. O objetivo é validar a base oficial,
as intenções e as regras de segurança sem custo variável e sem alucinação generativa.
Na fase seguinte, um LLM pode ser adicionado apenas como camada de interpretação,
mantendo a base oficial como fonte da verdade.
