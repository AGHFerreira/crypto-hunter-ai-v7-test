import csv
import io
import json
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
import streamlit as st

st.set_page_config(page_title='Crypto Hunter AI 7.1', page_icon='₿', layout='wide')
LANGS = {'Português (Brasil)':'pt','English':'en','Español':'es','Français':'fr','Deutsch':'de','Italiano':'it','中文':'zh','日本語':'ja'}
# Translation keys are kept separate from the business logic for easy expansion.
T = {
'pt': {'subtitle':'Inteligência blockchain e pesquisa de desafios públicos','menu':'Menu','explorer':'Explorador Bitcoin','puzzles':'Pesquisa de enigmas','recovery':'Central de recuperação','about':'Sobre e segurança','address':'Endereço público Bitcoin','fetch':'Consultar dados públicos','balance':'Saldo confirmado','txs':'Transações confirmadas','invalid':'Endereço inválido ou não suportado.','error':'Não foi possível consultar a API pública. Tente novamente.','source':'Fonte: API pública mempool.space. Dados confirmados na blockchain.','no_secrets':'Nunca informe frases-semente, chaves privadas ou senhas nesta plataforma.','puzzle_intro':'Cadastre apenas desafios públicos cujas regras autorizem a participação. O cadastro não verifica automaticamente a legitimidade.','title':'Título','url':'Fonte oficial (URL)','clues':'Descrição e pistas públicas','authorized':'Verifiquei as regras e a autorização de participação','add':'Adicionar desafio','required':'Preencha título, URL HTTPS válida e confirme as regras.','saved':'Desafio adicionado à sessão.','empty':'Nenhum desafio registrado nesta sessão.','catalog':'Desafios registrados','export':'Exportar CSV','clear':'Limpar lista','session':'Os registros ficam apenas nesta sessão. Exporte o CSV para conservá-los.','remove':'Excluir','recovery_intro':'Triagem informativa para proprietários legítimos. Não é um serviço de recuperação automática.','scenario':'Qual é a situação?','backup':'Situação do backup','owner':'Confirmo que sou proprietário ou representante autorizado','checklist':'Gerar orientações','choose':'Selecione uma opção','lost':'Perdi acesso à carteira','exchange':'Perdi acesso à corretora','file':'Tenho arquivo de carteira antigo','seed':'Tenho minha frase de recuperação guardada com segurança','unknown':'Não sei','yes':'Disponível','no':'Não disponível','plan':'Orientações iniciais','ownership':'Confirme sua titularidade e mantenha qualquer informação secreta fora deste aplicativo.','backup_tip':'Procure backups locais e documentação oficial da carteira, sem enviar arquivos sensíveis a terceiros.','exchange_tip':'Use exclusivamente os canais oficiais da corretora e os procedimentos de verificação de identidade.','file_tip':'Preserve cópias do arquivo original e procure instruções oficiais para restauração em ambiente local e seguro.','seed_tip':'Use a frase somente no aplicativo oficial e confiável, em dispositivo seguro; nunca a cole aqui.','general_tip':'Registre o software utilizado, datas aproximadas e endereços públicos, sem compartilhar segredos.','not_authorized':'Confirme a titularidade ou autorização para continuar.','estimate':'Simulador de comissão (hipotético)','btc':'BTC recuperados (simulação)','rate':'Comissão (%)','commission':'Comissão simulada','not_payment':'Estimativa ilustrativa. Não há cobrança nem transferência de fundos.','about_text':'Esta versão consulta dados públicos, organiza desafios autorizados e fornece triagem educativa. Não identifica proprietários de endereços nem recupera chaves. Não há autenticação ou armazenamento persistente: não insira dados pessoais ou sensíveis.','how':'Como funciona','how_text':'Selecione um módulo no menu. Use apenas endereços públicos, desafios autorizados e informações não sensíveis.'},
'en': {'subtitle':'Blockchain intelligence and public puzzle research','menu':'Menu','explorer':'Bitcoin explorer','puzzles':'Puzzle research','recovery':'Recovery center','about':'About & safety','address':'Public Bitcoin address','fetch':'Fetch public data','balance':'Confirmed balance','txs':'Confirmed transactions','invalid':'Invalid or unsupported address.','error':'Unable to query the public API. Try again.','source':'Source: mempool.space public API. Confirmed on-chain data.','no_secrets':'Never enter seed phrases, private keys or passwords in this app.','puzzle_intro':'Only register public challenges whose rules authorize participation. Entries are not automatically verified.','title':'Title','url':'Official source (URL)','clues':'Description and public clues','authorized':'I have checked the rules and permission to participate','add':'Add challenge','required':'Provide a title, valid HTTPS URL and confirm the rules.','saved':'Challenge added to this session.','empty':'No challenges registered in this session.','catalog':'Registered challenges','export':'Export CSV','clear':'Clear list','session':'Records are kept only for this session. Export CSV to preserve them.','remove':'Remove','recovery_intro':'Informational triage for legitimate owners. This is not an automatic recovery service.','scenario':'What happened?','backup':'Backup status','owner':'I confirm I am the owner or an authorized representative','checklist':'Generate guidance','choose':'Select an option','lost':'Lost access to wallet','exchange':'Lost access to exchange','file':'Have an old wallet file','seed':'Have my recovery phrase stored safely','unknown':'Unknown','yes':'Available','no':'Unavailable','plan':'Initial guidance','ownership':'Verify ownership and keep all secret information outside this app.','backup_tip':'Look for local backups and official wallet documentation; do not send sensitive files to others.','exchange_tip':'Use only official exchange support and identity verification channels.','file_tip':'Preserve copies of the original file and consult official restoration guidance in a secure local environment.','seed_tip':'Use your phrase only in a trusted official wallet on a secure device; never paste it here.','general_tip':'Record wallet software, approximate dates and public addresses without sharing secrets.','not_authorized':'Confirm ownership or authorization to proceed.','estimate':'Commission simulator (hypothetical)','btc':'Recovered BTC (simulation)','rate':'Commission (%)','commission':'Simulated commission','not_payment':'Illustrative estimate only. No payments or transfers occur.','about_text':'This version queries public data, organizes authorized puzzles and provides educational triage. It does not identify address owners or recover keys. There is no authentication or persistent storage: do not enter personal or sensitive data.','how':'How it works','how_text':'Choose a module from the menu. Use only public addresses, authorized challenges and non-sensitive information.'}
}
# Complete eight-language interface using concise localized translations.
EXTRA = {
'es':['Inteligencia blockchain e investigación de desafíos públicos','Menú','Explorador Bitcoin','Investigación de acertijos','Centro de recuperación','Acerca de y seguridad','Dirección pública Bitcoin','Consultar datos públicos','Saldo confirmado','Transacciones confirmadas','Dirección inválida o no compatible.','No se pudo consultar la API pública.','Fuente: API pública mempool.space.','Nunca introduzca frases semilla, claves privadas ni contraseñas.','Registre solo desafíos públicos con participación autorizada.','Título','Fuente oficial (URL)','Descripción y pistas públicas','He verificado las reglas y autorización','Añadir desafío','Complete título, URL HTTPS válida y confirme las reglas.','Desafío añadido a la sesión.','No hay desafíos registrados.','Desafíos registrados','Exportar CSV','Borrar lista','Los datos duran solo esta sesión. Exporte CSV.','Eliminar','Orientación para propietarios legítimos; no es recuperación automática.','¿Qué sucedió?','Estado de la copia de seguridad','Confirmo que soy propietario o representante autorizado','Generar orientación','Seleccione una opción','Perdí acceso a mi cartera','Perdí acceso al exchange','Tengo un archivo antiguo','Tengo mi frase de recuperación guardada','No sé','Disponible','No disponible','Orientación inicial'],
'fr':['Analyse blockchain et recherche de défis publics','Menu','Explorateur Bitcoin','Recherche d’énigmes','Centre de récupération','À propos et sécurité','Adresse Bitcoin publique','Consulter les données publiques','Solde confirmé','Transactions confirmées','Adresse invalide ou non prise en charge.','Impossible de consulter l’API publique.','Source : API publique mempool.space.','Ne saisissez jamais de phrase de récupération, clé privée ou mot de passe.','Enregistrez uniquement des défis publics autorisés.','Titre','Source officielle (URL)','Description et indices publics','J’ai vérifié les règles et l’autorisation','Ajouter le défi','Renseignez un titre, une URL HTTPS valide et confirmez les règles.','Défi ajouté à la session.','Aucun défi enregistré.','Défis enregistrés','Exporter CSV','Effacer la liste','Les données restent dans cette session. Exportez le CSV.','Supprimer','Conseils pour les propriétaires légitimes, sans récupération automatique.','Quelle est la situation ?','État de la sauvegarde','Je confirme être propriétaire ou représentant autorisé','Générer des conseils','Choisir une option','Accès au portefeuille perdu','Accès à la plateforme perdu','Ancien fichier de portefeuille','Phrase de récupération conservée','Inconnu','Disponible','Indisponible','Premiers conseils'],
'de':['Blockchain-Analyse und öffentliche Rätsel','Menü','Bitcoin-Explorer','Rätselforschung','Wiederherstellungszentrum','Info & Sicherheit','Öffentliche Bitcoin-Adresse','Öffentliche Daten abrufen','Bestätigtes Guthaben','Bestätigte Transaktionen','Ungültige oder nicht unterstützte Adresse.','Öffentliche API nicht erreichbar.','Quelle: öffentliche mempool.space-API.','Niemals Seed-Phrasen, private Schlüssel oder Passwörter eingeben.','Nur öffentliche, ausdrücklich erlaubte Herausforderungen erfassen.','Titel','Offizielle Quelle (URL)','Beschreibung und öffentliche Hinweise','Regeln und Teilnahmeberechtigung geprüft','Herausforderung hinzufügen','Titel, gültige HTTPS-URL und Bestätigung erforderlich.','Zur Sitzung hinzugefügt.','Keine Herausforderungen vorhanden.','Erfasste Herausforderungen','CSV exportieren','Liste leeren','Daten gelten nur für diese Sitzung. CSV exportieren.','Entfernen','Informationen für rechtmäßige Eigentümer, keine automatische Wiederherstellung.','Was ist passiert?','Backup-Status','Ich bin Eigentümer oder bevollmächtigt','Hinweise erstellen','Option wählen','Wallet-Zugriff verloren','Börsenzugriff verloren','Alte Wallet-Datei vorhanden','Wiederherstellungsphrase sicher aufbewahrt','Unbekannt','Verfügbar','Nicht verfügbar','Erste Hinweise'],
'it':['Analisi blockchain e ricerca di sfide pubbliche','Menu','Esplora Bitcoin','Ricerca enigmi','Centro recupero','Informazioni e sicurezza','Indirizzo Bitcoin pubblico','Consulta dati pubblici','Saldo confermato','Transazioni confermate','Indirizzo non valido o non supportato.','Impossibile consultare l’API pubblica.','Fonte: API pubblica mempool.space.','Non inserire mai frasi seed, chiavi private o password.','Registra solo sfide pubbliche con partecipazione autorizzata.','Titolo','Fonte ufficiale (URL)','Descrizione e indizi pubblici','Ho verificato regole e autorizzazione','Aggiungi sfida','Inserisci titolo, URL HTTPS valido e conferma le regole.','Sfida aggiunta alla sessione.','Nessuna sfida registrata.','Sfide registrate','Esporta CSV','Svuota elenco','I dati durano solo per questa sessione. Esporta CSV.','Rimuovi','Indicazioni per proprietari legittimi, non recupero automatico.','Cosa è successo?','Stato del backup','Confermo di essere proprietario o delegato','Genera indicazioni','Seleziona un’opzione','Accesso al wallet perso','Accesso all’exchange perso','Ho un vecchio file wallet','Ho la frase di recupero al sicuro','Non so','Disponibile','Non disponibile','Indicazioni iniziali'],
'zh':['区块链分析与公开谜题研究','菜单','比特币浏览器','谜题研究','恢复中心','关于与安全','公开比特币地址','查询公开数据','已确认余额','已确认交易','地址无效或不受支持。','无法查询公共 API。','来源：mempool.space 公共 API。','切勿输入助记词、私钥或密码。','仅登记允许参与的公开挑战。','标题','官方来源（URL）','描述与公开线索','我已核实规则及参与授权','添加挑战','请填写标题、有效 HTTPS 网址并确认规则。','挑战已添加到本次会话。','尚无挑战。','已登记挑战','导出 CSV','清空列表','数据仅保留在本次会话中，请导出 CSV。','删除','仅为合法所有者提供指导，不提供自动恢复。','遇到什么情况？','备份状态','我确认自己是所有者或授权代表','生成建议','选择选项','无法访问钱包','无法访问交易所','拥有旧钱包文件','安全保存了助记词','未知','可用','不可用','初步建议'],
'ja':['ブロックチェーン分析と公開パズルの調査','メニュー','ビットコイン検索','パズル調査','復旧センター','概要と安全','公開ビットコインアドレス','公開データを取得','承認済み残高','承認済み取引','無効または未対応のアドレスです。','公開 API に接続できません。','出典：mempool.space 公開 API。','シードフレーズ、秘密鍵、パスワードを入力しないでください。','参加が許可された公開チャレンジのみ登録してください。','タイトル','公式情報源（URL）','説明と公開ヒント','ルールと参加許可を確認しました','チャレンジを追加','タイトル、有効な HTTPS URL、ルール確認が必要です。','セッションに追加しました。','登録されたチャレンジはありません。','登録済みチャレンジ','CSV を出力','一覧を消去','データはこのセッションのみ保存されます。CSV を出力してください。','削除','正当な所有者向けの案内です。自動復旧ではありません。','状況を選択','バックアップ状況','所有者または正当な代理人です','案内を作成','選択してください','ウォレットにアクセスできない','取引所にアクセスできない','古いウォレットファイルがある','復旧フレーズを安全に保管している','不明','あり','なし','初期案内']
}
keys=list(T['en'].keys())[:37] # fixed shared keys through 'plan'
for code,values in EXTRA.items():
    T[code]=dict(T['en'])
    T[code].update(dict(zip(keys,values)))

if 'puzzles' not in st.session_state: st.session_state.puzzles=[]
with st.sidebar:
    language=st.selectbox('🌐 Language / Idioma', list(LANGS), index=0)
    lang=LANGS[language]
    tr=T[lang]
    st.info(tr['how_text'])
    page=st.radio(tr['menu'],[tr['explorer'],tr['puzzles'],tr['recovery'],tr['about']])

st.title('₿ Crypto Hunter AI 7.1')
st.caption(tr['subtitle'])

@st.cache_data(ttl=90, show_spinner=False)
def fetch_address(address):
    response=requests.get('https://mempool.space/api/address/'+address, timeout=15)
    response.raise_for_status()
    return response.json()

def plausible_address(s):
    return bool(re.fullmatch(r'(bc1[ac-hj-np-z02-9]{11,87}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})',s))

if page==tr['explorer']:
    st.header(tr['explorer'])
    address=st.text_input(tr['address'],placeholder='bc1... / 1... / 3...')
    if st.button(tr['fetch']):
        if not plausible_address(address.strip()): st.error(tr['invalid'])
        else:
            try:
                data=fetch_address(address.strip())
                chain=data['chain_stats']
                sats=chain['funded_txo_sum']-chain['spent_txo_sum']
                a,b=st.columns(2)
                a.metric(tr['balance'],f'{sats/100_000_000:,.8f} BTC')
                b.metric(tr['txs'],f"{chain['tx_count']:,}")
                st.caption(tr['source'])
            except (requests.RequestException,KeyError,ValueError): st.error(tr['error'])
elif page==tr['puzzles']:
    st.header(tr['puzzles'])
    st.info(tr['puzzle_intro'])
    with st.form('puzzle_form',clear_on_submit=True):
        title=st.text_input(tr['title'],max_chars=120)
        url=st.text_input(tr['url'],placeholder='https://...')
        clues=st.text_area(tr['clues'],max_chars=3000)
        authorized=st.checkbox(tr['authorized'])
        submit=st.form_submit_button(tr['add'])
    if submit:
        parsed=urlparse(url.strip())
        if not title.strip() or parsed.scheme!='https' or not parsed.netloc or not authorized:
            st.error(tr['required'])
        else:
            st.session_state.puzzles.append({'title':title.strip(),'url':url.strip(),'clues':clues.strip(),'created_utc':datetime.now(timezone.utc).isoformat()})
            st.success(tr['saved'])
    st.subheader(tr['catalog'])
    if not st.session_state.puzzles: st.info(tr['empty'])
    else:
        for i,p in enumerate(st.session_state.puzzles):
            with st.expander(p['title']):
                st.write(p['url'])
                st.write(p['clues'])
                if st.button(tr['remove'],key=f'remove_{i}'):
                    st.session_state.puzzles.pop(i)
                    st.rerun()
        buffer=io.StringIO()
        writer=csv.DictWriter(buffer,fieldnames=['title','url','clues','created_utc'])
        writer.writeheader(); writer.writerows(st.session_state.puzzles)
        st.download_button(tr['export'],buffer.getvalue().encode('utf-8-sig'),'crypto_hunter_puzzles.csv','text/csv')
        if st.button(tr['clear']): st.session_state.puzzles=[]; st.rerun()
    st.caption(tr['session'])
elif page==tr['recovery']:
    st.header(tr['recovery'])
    st.warning(tr['no_secrets'])
    st.write(tr['recovery_intro'])
    options=['lost','exchange','file','seed']
    scenario=st.selectbox(tr['scenario'],options,format_func=lambda k:tr[k])
    backup=st.selectbox(tr['backup'],['unknown','yes','no'],format_func=lambda k:tr[k])
    owner=st.checkbox(tr['owner'])
    if st.button(tr['checklist']):
        if not owner: st.error(tr['not_authorized'])
        else:
            st.subheader(tr['plan'])
            st.write('• '+tr['ownership'])
            st.write('• '+tr[{'exchange':'exchange_tip','file':'file_tip','seed':'seed_tip','lost':'backup_tip'}[scenario]])
            st.write('• '+tr['general_tip'])
            if backup=='yes': st.write('• '+tr['backup_tip'])
    st.divider()
    st.subheader(tr['estimate'])
    amount=st.number_input(tr['btc'],min_value=0.0,max_value=21_000_000.0,value=0.0,step=0.01,format='%.8f')
    rate=st.slider(tr['rate'],0,30,15)
    st.metric(tr['commission'],f'{amount*rate/100:,.8f} BTC')
    st.caption(tr['not_payment'])
else:
    st.header(tr['about'])
    st.warning(tr['no_secrets'])
    st.write(tr['about_text'])
