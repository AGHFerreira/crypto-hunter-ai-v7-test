import csv
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
import streamlit as st

st.set_page_config(page_title='Crypto Hunter AI 7.0', page_icon='₿', layout='wide')

LANGS = {'Português (Brasil)': 'pt', 'English': 'en', 'Español': 'es', 'Français': 'fr', 'Deutsch': 'de', 'Italiano': 'it', '中文': 'zh', '日本語': 'ja'}
T = {
'pt': ['Investigação blockchain e pesquisa de desafios públicos','Explorador Bitcoin','Pesquisa de enigmas','Centro de recuperação','Sobre e segurança','Endereço público Bitcoin','Consultar dados públicos','Saldo confirmado','Transações confirmadas','Última atividade confirmada (amostra)','Não identificada','Adicionar desafio público','Título','Fonte oficial (URL)','Descrição / pistas públicas','Regras e autorização verificadas','Adicionar à lista local','Desafios cadastrados','Exportar catálogo CSV','Solicitação de recuperação','Como funciona','Não informe frases-semente, chaves privadas ou senhas.','O proprietário deve autorizar expressamente qualquer recuperação.','Este protótipo não recebe credenciais nem transfere fundos.','Pesquisar por título ou pista','Endereço inválido ou não suportado.','Erro ao consultar API pública.','A inatividade não comprova abandono.','Informe somente dados públicos e não sensíveis.','Não há desafios cadastrados.','As informações são mantidas nesta sessão; exporte o CSV para preservá-las.','Formulário de triagem (não envia dados)','Tipo de problema','Backup disponível?','Gerar checklist','Confira a titularidade, reúna backups locais e use somente ferramentas oficiais. Nunca compartilhe segredos neste aplicativo.'],
'en': ['Blockchain intelligence and public puzzle research','Bitcoin explorer','Puzzle research','Recovery center','About & safety','Public Bitcoin address','Fetch public data','Confirmed balance','Confirmed transactions','Last confirmed activity (sample)','Unknown','Add public challenge','Title','Official source (URL)','Description / public clues','Rules and authorization verified','Add to session list','Registered challenges','Export catalog CSV','Recovery request','How it works','Never enter seed phrases, private keys or passwords.','The owner must expressly authorize any recovery.','This prototype does not collect credentials or transfer funds.','Search title or clue','Invalid or unsupported address.','Error querying public API.','Inactivity does not prove abandonment.','Enter only public, non-sensitive information.','No challenges registered.','Data is kept for this session; export CSV to retain it.','Intake form (does not submit data)','Issue type','Backup available?','Generate checklist','Verify ownership, gather local backups and use official tools only. Never share secrets in this app.'],
'es': ['Investigación blockchain y acertijos públicos','Explorador Bitcoin','Investigación de acertijos','Centro de recuperación','Información y seguridad','Dirección pública Bitcoin','Consultar datos públicos','Saldo confirmado','Transacciones confirmadas','Última actividad confirmada (muestra)','Desconocida','Añadir desafío público','Título','Fuente oficial (URL)','Descripción / pistas públicas','Reglas y autorización verificadas','Añadir a la sesión','Desafíos registrados','Exportar catálogo CSV','Solicitud de recuperación','Cómo funciona','Nunca introduzca frases semilla, claves privadas ni contraseñas.','El propietario debe autorizar expresamente la recuperación.','Este prototipo no recopila credenciales ni transfiere fondos.','Buscar título o pista','Dirección inválida o no admitida.','Error al consultar la API pública.','La inactividad no demuestra abandono.','Introduzca solo información pública no sensible.','No hay desafíos registrados.','Los datos se conservan en esta sesión; exporte CSV.','Formulario de evaluación (no envía datos)','Tipo de problema','¿Hay copia de seguridad?','Generar lista de verificación','Verifique la titularidad, reúna copias locales y use solo herramientas oficiales. Nunca comparta secretos.'],
'fr': ['Analyse blockchain et énigmes publiques','Explorateur Bitcoin','Recherche d’énigmes','Centre de récupération','Informations et sécurité','Adresse Bitcoin publique','Consulter les données publiques','Solde confirmé','Transactions confirmées','Dernière activité confirmée (échantillon)','Inconnue','Ajouter un défi public','Titre','Source officielle (URL)','Description / indices publics','Règles et autorisation vérifiées','Ajouter à la session','Défis enregistrés','Exporter le catalogue CSV','Demande de récupération','Fonctionnement','Ne saisissez jamais de phrase secrète, clé privée ou mot de passe.','Le propriétaire doit autoriser toute récupération.','Ce prototype ne collecte pas de secrets et ne transfère pas de fonds.','Rechercher titre ou indice','Adresse invalide ou non prise en charge.','Erreur de consultation de l’API.','L’inactivité ne prouve pas l’abandon.','Saisissez uniquement des données publiques.','Aucun défi enregistré.','Les données restent dans cette session ; exportez le CSV.','Formulaire préliminaire (aucun envoi)','Type de problème','Sauvegarde disponible ?','Créer une liste de contrôle','Vérifiez la propriété, rassemblez les sauvegardes locales et utilisez les outils officiels. Ne partagez aucun secret.'],
'de': ['Blockchain-Analyse und öffentliche Rätsel','Bitcoin-Explorer','Rätselforschung','Wiederherstellungszentrum','Info und Sicherheit','Öffentliche Bitcoin-Adresse','Öffentliche Daten abrufen','Bestätigtes Guthaben','Bestätigte Transaktionen','Letzte bestätigte Aktivität (Stichprobe)','Unbekannt','Öffentliche Herausforderung hinzufügen','Titel','Offizielle Quelle (URL)','Beschreibung / öffentliche Hinweise','Regeln und Erlaubnis geprüft','Zur Sitzung hinzufügen','Gespeicherte Herausforderungen','Katalog als CSV exportieren','Wiederherstellungsanfrage','Funktionsweise','Niemals Seed-Phrasen, private Schlüssel oder Passwörter eingeben.','Jede Wiederherstellung erfordert die Zustimmung des Eigentümers.','Dieser Prototyp sammelt keine Zugangsdaten und überträgt keine Gelder.','Titel oder Hinweis suchen','Ungültige oder nicht unterstützte Adresse.','Fehler bei der öffentlichen API.','Inaktivität beweist keine Aufgabe.','Nur öffentliche, nicht sensible Daten eingeben.','Keine Herausforderungen vorhanden.','Daten bleiben nur in dieser Sitzung; CSV exportieren.','Vorprüfung (keine Übermittlung)','Problemtyp','Backup vorhanden?','Checkliste erstellen','Eigentum prüfen, lokale Backups sammeln und nur offizielle Werkzeuge verwenden. Niemals Geheimnisse teilen.'],
'it': ['Analisi blockchain ed enigmi pubblici','Esplora Bitcoin','Ricerca enigmi','Centro recupero','Informazioni e sicurezza','Indirizzo Bitcoin pubblico','Consulta dati pubblici','Saldo confermato','Transazioni confermate','Ultima attività confermata (campione)','Sconosciuta','Aggiungi sfida pubblica','Titolo','Fonte ufficiale (URL)','Descrizione / indizi pubblici','Regole e autorizzazione verificate','Aggiungi alla sessione','Sfide registrate','Esporta catalogo CSV','Richiesta recupero','Come funziona','Non inserire mai seed phrase, chiavi private o password.','Il proprietario deve autorizzare ogni recupero.','Questo prototipo non raccoglie credenziali né trasferisce fondi.','Cerca titolo o indizio','Indirizzo non valido o non supportato.','Errore API pubblica.','L’inattività non dimostra abbandono.','Inserire solo dati pubblici non sensibili.','Nessuna sfida registrata.','I dati restano nella sessione; esporta CSV.','Modulo preliminare (nessun invio)','Tipo di problema','Backup disponibile?','Genera lista di controllo','Verifica la proprietà, raccogli backup locali e usa solo strumenti ufficiali. Non condividere segreti.'],
'zh': ['区块链分析与公开谜题研究','比特币查询','谜题研究','恢复中心','说明与安全','公开比特币地址','查询公开数据','已确认余额','已确认交易','最近确认活动（样本）','未知','添加公开挑战','标题','官方来源（网址）','描述 / 公开线索','已核实规则与授权','添加到本次会话','已登记的挑战','导出 CSV','恢复申请','使用说明','切勿输入助记词、私钥或密码。','任何恢复操作均须获得所有者明确授权。','本原型不收集凭据，也不转移资金。','搜索标题或线索','地址无效或不受支持。','公开 API 查询失败。','长期未活动不代表资产被遗弃。','仅输入公开且非敏感的信息。','暂无挑战。','数据仅在本次会话保存；请导出 CSV。','初步评估（不提交数据）','问题类型','是否有备份？','生成检查清单','核实所有权，收集本地备份，仅使用官方工具。切勿分享秘密信息。'],
'ja': ['ブロックチェーン分析と公開パズル研究','Bitcoin エクスプローラー','パズル研究','復旧センター','概要と安全','公開 Bitcoin アドレス','公開データを取得','承認済み残高','承認済み取引','最終承認活動（サンプル）','不明','公開チャレンジを追加','タイトル','公式情報源（URL）','説明・公開ヒント','ルールと許可を確認済み','セッションに追加','登録済みチャレンジ','CSV を出力','復旧の相談','仕組み','シードフレーズ、秘密鍵、パスワードを入力しないでください。','復旧には所有者の明示的な許可が必要です。','この試作版は認証情報を収集せず、送金もしません。','タイトルやヒントで検索','アドレスが無効または未対応です。','公開 API への問い合わせに失敗しました。','長期間動きがなくても放棄された証拠にはなりません。','公開されている非機密情報のみ入力してください。','チャレンジはまだありません。','データはこのセッションのみ保存されます。CSV を出力してください。','事前確認フォーム（送信なし）','問題の種類','バックアップはありますか？','チェックリストを作成','所有権を確認し、ローカルバックアップを集め、公式ツールのみ使用してください。秘密情報は共有しないでください。']}

lang_name = st.sidebar.selectbox('🌐 Language / Idioma', list(LANGS), index=0)
lang = LANGS[lang_name]
def tr(n): return T[lang][n]
st.title('₿ Crypto Hunter AI 7.0')
st.caption(tr(0))
st.sidebar.warning(tr(20))
page = st.sidebar.radio('Menu', [tr(i) for i in [1,2,3,4]])

if page == tr(1):
    st.subheader(tr(1))
    address = st.text_input(tr(5), placeholder='bc1... / 1... / 3...').strip()
    if st.button(tr(6)):
        if not re.fullmatch(r'(bc1[ac-hj-np-z02-9]{11,87}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})', address, re.IGNORECASE):
            st.error(tr(26))
        else:
            try:
                r = requests.get(f'https://mempool.space/api/address/{address}', timeout=15)
                r.raise_for_status()
                data = r.json()
                stats = data['chain_stats']
                sats = stats['funded_txo_sum'] - stats['spent_txo_sum']
                c1,c2 = st.columns(2)
                c1.metric(tr(7), f'{sats / 1e8:,.8f} BTC')
                c2.metric(tr(8), f"{stats['tx_count']:,}")
                st.info(tr(28))
                st.caption('Source: mempool.space public API. Confirmed on-chain data only.')
            except (requests.RequestException, ValueError, KeyError) as exc:
                st.error(tr(27))
                st.caption(str(exc))

elif page == tr(2):
    st.subheader(tr(2))
    st.info(tr(29))
    if 'puzzles' not in st.session_state:
        st.session_state.puzzles = []
    with st.form('puzzle_form', clear_on_submit=True):
        title = st.text_input(tr(12), max_chars=150)
        url = st.text_input(tr(13), placeholder='https://...')
        clues = st.text_area(tr(14), max_chars=2000)
        verified = st.checkbox(tr(15))
        add = st.form_submit_button(tr(16))
    if add:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if not title.strip() or parsed.scheme != 'https' or not parsed.netloc or not verified:
            st.warning(tr(15) + ' · HTTPS URL + title required')
        else:
            st.session_state.puzzles.append({'title':title.strip(), 'source_url':url, 'public_clues':clues.strip(), 'rules_verified_by_user':True, 'added_utc':datetime.now(timezone.utc).isoformat()})
            st.success('✓')
    query = st.text_input(tr(25))
    rows = [p for p in st.session_state.puzzles if query.casefold() in (p['title']+' '+p['public_clues']).casefold()]
    st.subheader(tr(17))
    if rows:
        st.dataframe(rows, use_container_width=True)
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        st.download_button(tr(18), data=output.getvalue().encode('utf-8-sig'), file_name='puzzle_research.csv', mime='text/csv')
    else:
        st.caption(tr(30))
    st.caption(tr(31))

elif page == tr(3):
    st.subheader(tr(19))
    st.warning(tr(20))
    st.info(tr(21))
    st.caption(tr(22))
    issue = st.selectbox(tr(33), ['Lost wallet backup', 'Forgotten wallet password', 'Exchange account access', 'Other'])
    backup = st.selectbox(tr(34), ['Unknown', 'Yes', 'No'])
    if st.button(tr(35)):
        st.success(tr(36))
        st.write(f'{tr(33)}: {issue} | {tr(34)}: {backup}')
else:
    st.subheader(tr(24))
    st.write(tr(22))
    st.write(tr(28))
    st.write('Version 7.0 - stage 1: multilingual UI, public-address explorer, session puzzle catalog and non-submitting recovery intake. No automatic puzzle discovery, private-key search, AI inference, persistent database, authentication or payment processing.')
    st.write('Privacy: no private credentials; API requests for public addresses go to mempool.space. The catalog and intake remain in Streamlit session state.')
