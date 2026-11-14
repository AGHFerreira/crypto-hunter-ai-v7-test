import csv
import io
import re
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
import streamlit as st

st.set_page_config(page_title='Crypto Hunter AI 7.2', page_icon='₿', layout='wide')
LANGS = {'Português (Brasil)':'pt','English':'en','Español':'es','Français':'fr','Deutsch':'de','Italiano':'it','中文':'zh','日本語':'ja'}
TEXT = {
'pt': ['Explorador Bitcoin','Pesquisa de enigmas','Central de recuperação','Meus casos','Sobre e segurança','Consultar dados públicos','Endereço público Bitcoin','Saldo confirmado','Transações confirmadas','Desafios públicos autorizados','Título','Fonte oficial HTTPS','Pistas públicas','Confirme que verificou as regras e a autorização','Adicionar desafio','Desafios registrados','Exportar CSV','Excluir','Solicitação de recuperação','Tipo de problema','Backup disponível?','Confirmo ser o proprietário ou representante autorizado','Gerar orientações','Simulador de comissão','BTC recuperados (simulação)','Comissão (%)','Comissão estimada','Login','E-mail','Senha','Entrar','Criar conta','Sair','Salvar caso','Descrição não sensível','Casos registrados','Nenhum registro','Conta de teste: dados temporários. Para persistência privada, configure Supabase e políticas RLS.','Não informe frases-semente, chaves privadas, senhas de carteira ou arquivos confidenciais.','Informe apenas dados públicos e não sensíveis.','Sem conexão segura ao banco: cadastro desativado.','Operação concluída.','Falha na operação. Confira a configuração e tente novamente.','Autenticação necessária para salvar casos.','Recuperação de carteira','Acesso à corretora','Arquivo antigo','Frase de recuperação guardada','Desconhecido','Sim','Não','Análise inicial','Verifique titularidade e backups locais; use ferramentas oficiais e mantenha segredos fora desta plataforma.','A autorização declarada não substitui a verificação documental.','Pesquisa e recuperação autorizada; não é um serviço automático de resgate.'],
'en': ['Bitcoin explorer','Puzzle research','Recovery center','My cases','About & safety','Fetch public data','Public Bitcoin address','Confirmed balance','Confirmed transactions','Authorized public challenges','Title','Official HTTPS source','Public clues','Confirm you checked the rules and authorization','Add challenge','Registered challenges','Export CSV','Delete','Recovery request','Problem type','Backup available?','I confirm I am the owner or authorized representative','Generate guidance','Commission simulator','Recovered BTC (simulation)','Commission (%)','Estimated commission','Sign in','Email','Password','Sign in','Create account','Sign out','Save case','Non-sensitive description','Registered cases','No records','Demo mode: data is temporary. Configure Supabase and RLS for private persistence.','Never provide seed phrases, private keys, wallet passwords or confidential files.','Only enter public, non-sensitive information.','No secure database connection: case submission disabled.','Operation completed.','Operation failed. Check settings and retry.','Sign in to save cases.','Wallet recovery','Exchange access','Old wallet file','Recovery phrase safely stored','Unknown','Yes','No','Initial assessment','Verify ownership and local backups; use official tools and keep secrets outside this platform.','Self-declared authorization is not documentary verification.','Authorized research and recovery; not automatic coin recovery.'],
'es': ['Explorador Bitcoin','Investigación de enigmas','Centro de recuperación','Mis casos','Seguridad','Consultar datos públicos','Dirección pública Bitcoin','Saldo confirmado','Transacciones confirmadas','Desafíos públicos autorizados','Título','Fuente oficial HTTPS','Pistas públicas','Confirmo que verifiqué reglas y autorización','Añadir desafío','Desafíos registrados','Exportar CSV','Eliminar','Solicitud de recuperación','Tipo de problema','¿Hay copia de seguridad?','Confirmo que soy propietario o representante autorizado','Generar orientación','Simulador de comisión','BTC recuperados (simulación)','Comisión (%)','Comisión estimada','Iniciar sesión','Correo','Contraseña','Entrar','Crear cuenta','Salir','Guardar caso','Descripción no sensible','Casos registrados','Sin registros','Modo de prueba: datos temporales. Configure Supabase y RLS.','Nunca introduzca frases semilla, claves privadas ni contraseñas.','Solo datos públicos y no sensibles.','Sin base de datos segura: registro desactivado.','Operación completada.','Operación fallida.','Inicie sesión para guardar casos.','Recuperación de cartera','Acceso a plataforma','Archivo antiguo','Frase guardada','Desconocido','Sí','No','Orientación inicial','Verifique propiedad y copias locales; use herramientas oficiales.','La declaración no sustituye la verificación documental.','Investigación autorizada; sin recuperación automática.'],
'fr': ['Explorateur Bitcoin','Recherche d’énigmes','Centre de récupération','Mes dossiers','Sécurité','Consulter les données publiques','Adresse Bitcoin publique','Solde confirmé','Transactions confirmées','Défis publics autorisés','Titre','Source HTTPS officielle','Indices publics','Je confirme avoir vérifié les règles','Ajouter un défi','Défis enregistrés','Exporter CSV','Supprimer','Demande de récupération','Type de problème','Sauvegarde disponible ?','Je suis propriétaire ou représentant autorisé','Générer des conseils','Simulateur de commission','BTC récupérés (simulation)','Commission (%)','Commission estimée','Connexion','E-mail','Mot de passe','Se connecter','Créer un compte','Déconnexion','Enregistrer le dossier','Description non sensible','Dossiers enregistrés','Aucun enregistrement','Mode démo : données temporaires. Configurez Supabase et RLS.','Ne fournissez jamais de phrase secrète ni de clé privée.','Uniquement des données publiques non sensibles.','Base sécurisée absente : enregistrement désactivé.','Opération réussie.','Échec de l’opération.','Connectez-vous pour enregistrer.','Portefeuille','Plateforme','Ancien fichier','Phrase conservée','Inconnu','Oui','Non','Premiers conseils','Vérifiez la propriété et les sauvegardes locales.','La déclaration ne remplace pas les justificatifs.','Recherche autorisée, pas de récupération automatique.'],
'de': ['Bitcoin-Explorer','Rätselforschung','Wiederherstellung','Meine Fälle','Sicherheit','Öffentliche Daten abrufen','Öffentliche Bitcoin-Adresse','Bestätigtes Guthaben','Bestätigte Transaktionen','Autorisierte öffentliche Rätsel','Titel','Offizielle HTTPS-Quelle','Öffentliche Hinweise','Regeln und Erlaubnis geprüft','Rätsel hinzufügen','Erfasste Rätsel','CSV exportieren','Löschen','Wiederherstellungsanfrage','Problemtyp','Backup verfügbar?','Ich bin Eigentümer oder bevollmächtigt','Hinweise erstellen','Provisionsrechner','Wiederhergestellte BTC (Simulation)','Provision (%)','Geschätzte Provision','Anmeldung','E-Mail','Passwort','Anmelden','Konto erstellen','Abmelden','Fall speichern','Nicht sensible Beschreibung','Gespeicherte Fälle','Keine Einträge','Demo: Daten temporär. Supabase und RLS einrichten.','Niemals Seed-Phrasen oder private Schlüssel eingeben.','Nur öffentliche, nicht sensible Daten.','Keine sichere Datenbank: Speichern deaktiviert.','Erfolgreich.','Vorgang fehlgeschlagen.','Zum Speichern anmelden.','Wallet','Börse','Alte Datei','Phrase vorhanden','Unbekannt','Ja','Nein','Erste Hinweise','Eigentum und lokale Backups prüfen.','Selbstauskunft ersetzt keinen Nachweis.','Autorisierte Forschung; keine automatische Wiederherstellung.'],
'it': ['Esplora Bitcoin','Ricerca enigmi','Centro recupero','I miei casi','Sicurezza','Consulta dati pubblici','Indirizzo Bitcoin pubblico','Saldo confermato','Transazioni confermate','Sfide pubbliche autorizzate','Titolo','Fonte HTTPS ufficiale','Indizi pubblici','Confermo di aver verificato regole e autorizzazione','Aggiungi sfida','Sfide registrate','Esporta CSV','Elimina','Richiesta recupero','Tipo di problema','Backup disponibile?','Sono proprietario o delegato','Genera indicazioni','Simulatore commissioni','BTC recuperati (simulazione)','Commissione (%)','Commissione stimata','Accesso','Email','Password','Accedi','Crea account','Esci','Salva caso','Descrizione non sensibile','Casi registrati','Nessun dato','Demo: dati temporanei. Configura Supabase e RLS.','Non inserire frasi seed o chiavi private.','Solo dati pubblici non sensibili.','Database sicuro assente: salvataggio disabilitato.','Operazione riuscita.','Operazione non riuscita.','Accedi per salvare.','Wallet','Exchange','Vecchio file','Frase conservata','Sconosciuto','Sì','No','Indicazioni iniziali','Verifica proprietà e backup locali.','La dichiarazione non sostituisce la verifica.','Ricerca autorizzata, non recupero automatico.'],
'zh': ['比特币浏览器','谜题研究','恢复中心','我的案例','安全说明','查询公开数据','公开比特币地址','已确认余额','已确认交易','获准的公开挑战','标题','官方 HTTPS 来源','公开线索','我已核实规则和授权','添加挑战','已登记挑战','导出 CSV','删除','恢复申请','问题类型','有备份吗？','我是所有者或授权代表','生成建议','佣金模拟','恢复 BTC（模拟）','佣金 (%)','预计佣金','登录','邮箱','密码','登录','注册','退出','保存案例','非敏感描述','已登记案例','暂无记录','演示模式：数据临时保存。请配置 Supabase 和 RLS。','切勿输入助记词或私钥。','仅输入公开非敏感信息。','未连接安全数据库，无法保存。','操作成功。','操作失败。','请先登录。','钱包','交易所','旧文件','已保存助记词','未知','是','否','初步建议','核实所有权和本地备份。','声明不能代替证明文件。','仅限授权研究，不自动恢复。'],
'ja': ['ビットコイン検索','パズル調査','復旧センター','マイケース','安全情報','公開データを取得','公開ビットコインアドレス','承認済み残高','承認済み取引','参加許可のある公開チャレンジ','タイトル','公式 HTTPS 情報源','公開ヒント','ルールと許可を確認しました','追加','登録済みチャレンジ','CSV 出力','削除','復旧依頼','問題の種類','バックアップはありますか？','所有者または正当な代理人です','案内を作成','手数料シミュレーター','復旧 BTC（試算）','手数料 (%)','試算手数料','ログイン','メール','パスワード','ログイン','アカウント作成','ログアウト','ケース保存','機密でない説明','登録済みケース','記録なし','デモモード：データは一時的です。Supabase と RLS を設定してください。','シードや秘密鍵を入力しないでください。','公開情報のみ入力してください。','安全なデータベースがないため保存できません。','完了しました。','失敗しました。','保存にはログインが必要です。','ウォレット','取引所','古いファイル','復旧フレーズ保管済み','不明','はい','いいえ','初期案内','所有権とローカルバックアップを確認してください。','自己申告は証明書類の代わりになりません。','許可された調査のみ。自動復旧ではありません。']
}
KEYS = ['explorer','puzzles','recovery','cases','about','fetch','address','balance','txs','puzzle_intro','title','url','clues','authorized','add','catalog','export','remove','request','scenario','backup','owner','checklist','estimate','btc','rate','commission','login','email','password','signin','signup','signout','save','description','records','empty','demo','no_secrets','public_only','no_db','done','failed','need_login','wallet','exchange','file','seed','unknown','yes','no','plan','guidance','ownership_note','about_text']
T = {code: dict(zip(KEYS,values)) for code,values in TEXT.items()}

try:
    SB_URL = str(st.secrets.get('SUPABASE_URL','')).rstrip('/')
    SB_KEY = str(st.secrets.get('SUPABASE_ANON_KEY',''))
except Exception:
    SB_URL = SB_KEY = ''
CONFIGURED = SB_URL.startswith('https://') and bool(SB_KEY)

if 'puzzles' not in st.session_state: st.session_state.puzzles=[]
if 'token' not in st.session_state: st.session_state.token=''
if 'user_id' not in st.session_state: st.session_state.user_id=''
if 'user_email' not in st.session_state: st.session_state.user_email=''

def api(method, path, payload=None, token=None, params=None):
    headers={'apikey':SB_KEY,'Content-Type':'application/json'}
    if token: headers['Authorization']='Bearer '+token
    if method=='POST' and path.startswith('/rest/'): headers['Prefer']='return=representation'
    r=requests.request(method,SB_URL+path,json=payload,params=params,headers=headers,timeout=15)
    r.raise_for_status()
    return r.json() if r.content else None

def sign_in(email,password,signup=False):
    path='/auth/v1/signup' if signup else '/auth/v1/token?grant_type=password'
    return api('POST',path,{'email':email,'password':password})

def valid_public_url(url):
    p=urlparse(url.strip())
    return p.scheme=='https' and bool(p.hostname) and not p.username and not p.password and p.hostname not in ('localhost','127.0.0.1')

@st.cache_data(ttl=90,show_spinner=False)
def get_address(address):
    r=requests.get('https://mempool.space/api/address/'+address,timeout=15)
    r.raise_for_status()
    return r.json()

with st.sidebar:
    lang_name=st.selectbox('🌐 Language / Idioma',list(LANGS))
    tr=T[LANGS[lang_name]]
    st.info(tr['public_only'])
    page=st.radio('Menu',[tr['explorer'],tr['puzzles'],tr['recovery'],tr['cases'],tr['about']])
    st.divider()
    if CONFIGURED:
        if st.session_state.token:
            st.caption(st.session_state.user_email)
            if st.button(tr['signout']):
                for k in ('token','user_id','user_email'): st.session_state[k]=''
                st.rerun()
        else:
            st.subheader(tr['login'])
            with st.form('auth'):
                email=st.text_input(tr['email'],max_chars=254)
                password=st.text_input(tr['password'],type='password')
                action=st.radio(tr['login'],[tr['signin'],tr['signup']],horizontal=True)
                go=st.form_submit_button(action)
            if go:
                try:
                    response=sign_in(email.strip(),password,action==tr['signup'])
                    if response and response.get('access_token') and response.get('user'):
                        st.session_state.token=response['access_token']
                        st.session_state.user_id=response['user']['id']
                        st.session_state.user_email=response['user'].get('email','')
                        st.rerun()
                    else: st.info('Check your email to confirm your account / Confirme o e-mail para ativar sua conta.')
                except (requests.RequestException,ValueError): st.error(tr['failed'])
    else: st.warning(tr['demo'])

st.title('₿ Crypto Hunter AI 7.2')
st.caption(tr['about_text'])

if page==tr['explorer']:
    st.header(tr['explorer'])
    addr=st.text_input(tr['address'],placeholder='bc1... / 1... / 3...')
    if st.button(tr['fetch']):
        if not re.fullmatch(r'(bc1[ac-hj-np-z02-9]{11,87}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})',addr.strip()): st.error('Invalid address / Endereço inválido')
        else:
            try:
                data=get_address(addr.strip())['chain_stats']
                a,b=st.columns(2)
                a.metric(tr['balance'],f"{(data['funded_txo_sum']-data['spent_txo_sum'])/1e8:,.8f} BTC")
                b.metric(tr['txs'],f"{data['tx_count']:,}")
                st.caption('Source: mempool.space public API')
            except (requests.RequestException,ValueError,KeyError): st.error(tr['failed'])

elif page==tr['puzzles']:
    st.header(tr['puzzles'])
    st.info(tr['puzzle_intro'])
    with st.form('new_puzzle',clear_on_submit=True):
        title=st.text_input(tr['title'],max_chars=120)
        url=st.text_input(tr['url'],max_chars=500)
        clues=st.text_area(tr['clues'],max_chars=3000)
        authorized=st.checkbox(tr['authorized'])
        submit=st.form_submit_button(tr['add'])
    if submit:
        if title.strip() and valid_public_url(url) and authorized:
            item={'id':str(uuid.uuid4()),'title':title.strip(),'source_url':url.strip(),'clues':clues.strip(),'created_at':datetime.now(timezone.utc).isoformat()}
            if CONFIGURED and st.session_state.token:
                try:
                    api('POST','/rest/v1/puzzles',dict(item,owner_id=st.session_state.user_id),st.session_state.token)
                    st.success(tr['done'])
                except requests.RequestException: st.error(tr['failed'])
            else:
                st.session_state.puzzles.append(item)
                st.success(tr['done'])
        else: st.error(tr['authorized']+' / HTTPS URL / '+tr['title'])
    st.subheader(tr['catalog'])
    items=st.session_state.puzzles
    if CONFIGURED and st.session_state.token:
        try: items=api('GET','/rest/v1/puzzles',token=st.session_state.token,params={'select':'id,title,source_url,clues,created_at','order':'created_at.desc','limit':'100'}) or []
        except requests.RequestException: st.error(tr['failed']); items=[]
    if not items: st.info(tr['empty'])
    for p in items:
        with st.expander(p['title']):
            st.write(p['source_url']); st.write(p.get('clues',''))
            if st.button(tr['remove'],key='del_p_'+p['id']):
                if CONFIGURED and st.session_state.token:
                    try: api('DELETE','/rest/v1/puzzles',token=st.session_state.token,params={'id':'eq.'+p['id']})
                    except requests.RequestException: st.error(tr['failed']); st.stop()
                else: st.session_state.puzzles=[x for x in st.session_state.puzzles if x['id']!=p['id']]
                st.rerun()
    if items:
        buf=io.StringIO(); writer=csv.DictWriter(buf,fieldnames=['title','source_url','clues','created_at'],extrasaction='ignore'); writer.writeheader(); writer.writerows(items)
        st.download_button(tr['export'],buf.getvalue().encode('utf-8-sig'),'puzzles.csv','text/csv')
    if not CONFIGURED: st.caption(tr['demo'])

elif page==tr['recovery']:
    st.header(tr['recovery']); st.warning(tr['no_secrets'])
    scenario=st.selectbox(tr['scenario'],['wallet','exchange','file','seed'],format_func=lambda x:tr[x])
    backup=st.selectbox(tr['backup'],['unknown','yes','no'],format_func=lambda x:tr[x])
    owner=st.checkbox(tr['owner'])
    if st.button(tr['checklist']):
        if owner: st.success(tr['plan']); st.write(tr['guidance']); st.caption(tr['ownership_note'])
        else: st.error(tr['owner'])
    st.divider(); st.subheader(tr['estimate'])
    amount=st.number_input(tr['btc'],min_value=0.0,value=0.0,step=0.01,format='%.8f')
    rate=st.slider(tr['rate'],0,30,15)
    st.metric(tr['commission'],f'{amount*rate/100:,.8f} BTC')
    st.caption('Illustrative only / Apenas simulação. No funds are transferred.')
    st.divider(); st.subheader(tr['request'])
    description=st.text_area(tr['description'],max_chars=1000,placeholder=tr['public_only'])
    if st.button(tr['save']):
        if not owner: st.error(tr['owner'])
        elif not CONFIGURED: st.error(tr['no_db'])
        elif not st.session_state.token: st.error(tr['need_login'])
        elif not description.strip(): st.error(tr['description'])
        else:
            try:
                api('POST','/rest/v1/cases',{'owner_id':st.session_state.user_id,'scenario':scenario,'backup':backup,'description':description.strip(),'status':'new'},st.session_state.token)
                st.success(tr['done'])
            except requests.RequestException: st.error(tr['failed'])

elif page==tr['cases']:
    st.header(tr['cases'])
    if not CONFIGURED: st.warning(tr['no_db'])
    elif not st.session_state.token: st.warning(tr['need_login'])
    else:
        try:
            items=api('GET','/rest/v1/cases',token=st.session_state.token,params={'select':'id,scenario,backup,description,status,created_at','order':'created_at.desc','limit':'100'}) or []
            if not items: st.info(tr['empty'])
            for c in items:
                with st.expander(f"{c['created_at'][:10]} · {tr.get(c['scenario'],c['scenario'])} · {c['status']}"):
                    st.write(c['description']); st.caption(tr['ownership_note'])
        except requests.RequestException: st.error(tr['failed'])
else:
    st.header(tr['about']); st.warning(tr['no_secrets']); st.write(tr['about_text']); st.caption(tr['ownership_note'])
