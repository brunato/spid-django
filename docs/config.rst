******************************************
Dettaglio delle configurazioni applicabili
******************************************

Per regolare il funzionamento della app *spid-django* vi sono una serie di configurazioni
che possono essere aggiunte ai *settings* del progetto.

Alcune impostazioni, quelle caratterizzate da un nome con prefisso *SPID_*, sono proprie
di *spid-django*.
Altre impostazioni sono invece relative a SAML (la libreria *pysaml2* e la app *djangosaml2*).


Configurazioni obbligatorie
===========================

Alcune configurazioni SPID e SAML2 sono obbligatorie, perché non prevedono dei valori di default.

SPID_CONTACTS
    Lista dei contatti da inserire nei metadati del servizio. Il numero di contatti
    dipende dal numero di soggetti che fanno capo al servizio abilitato con SPID.
    L'esempio seguente si riferisce ad un singolo *soggetto privato*::

        SPID_CONTACTS = [
            {
                'contact_type': 'other',
                'telephone_number': '+39 8475634785',
                'email_address': 'tech-info@example.org',
                'VATNumber': 'IT12345678901',
                'FiscalCode': 'XYZABCAAMGGJ000W',
                'Private': '',
            },
        ]


SAML_CONFIG
    Configurazione SAML2 della app *djangosaml2*. Non è necessario fornire la
    configurazione completa, ma è sufficiente specificare la sezione riguardante
    l'organizzazione a cui si riferisce il servizio, come nel seguente esempio::

        SAML_CONFIG = {
            'organization': {
                'name': [('Example', 'it'), ('Example', 'en')],
                'display_name': [('Example', 'it'), ('Example', 'en')],
                'url': [('http://www.example.it', 'it'), ('http://www.example.it', 'en')],
            },
        }

    Per default la configurazione SAML2 di SPID è costruita dinamicamente, per cui
    le altre impostazioni SAML2 per SPID sono determinate in modo fisso o dalle altre
    voci di configurazione *SPID_**.


Configurazioni opzionali
========================

Le restanti configurazioni sono tutte carattezzate da valori di default. I valori di default
a volte non sono adatti alla struttura del progetto, per cui è comunque necessario ridefinire
anche alcune impostazioni opzionali:

SPID_BASE_URL
    La parte *scheme* e *host* della URL del servizio. Per default è ``None``
    e la base URL è ricavata dinamicamente dalle request.

SPID_URLS_PREFIX
    Il prefisso nel path delle viste relative al servizio SPID, ``'spid'`` per default.

SPID_ACS_URL_PATH
    Path della URL dell'Attribute Consumer Service, per default è ``f'{SPID_URLS_PREFIX}/acs/'``.

SPID_SLO_POST_URL_PATH
    default is ``f'{SPID_URLS_PREFIX}/ls/post/'``.

SPID_SLO_URL_PATH
    default is ``f'{SPID_URLS_PREFIX}/ls/'``.

SPID_METADATA_URL_PATH
    Path della URL che restituisce i metadati XML, per default è ``f'{SPID_URLS_PREFIX}/metadata/'``.

SPID_CERTS_DIR
    Indica la directory dove sono depositati i certificati SSL per SPID, per default è la
    il filepath assoluto di directory ottenuto concatenando la ``BASE_DIR`` del progetto
    con ``'certificates/'``.

SPID_PUBLIC_CERT
    Il file contenente il certificato SSL pubblico per il servizio SPID, per default la
    concatenazione di ``SPID_CERTS_DIR`` con ``'public.cert'``.

SPID_PRIVATE_KEY
    Il file contenente la chiave privata per il certificato SSL del servizio SPID, per
    default la concatenazione di ``SPID_CERTS_DIR`` con ``'private.key'``.

SPID_DIG_ALG
    Algoritmo usato per i digest, ``saml2.xmldsig.DIGEST_SHA256`` per default.

SPID_SIG_ALG
    Algoritmo usato per le firme digitali, ``saml2.xmldsig.SIG_RSA_SHA256`` per default.

SPID_NAMEID_FORMAT
    Formato usato pei i nomi SPID, ``saml2.saml.NAMEID_FORMAT_TRANSIENT`` per default.

SPID_AUTH_CONTEXT
    Contesto di autenticazione SPID, ``'https://www.spid.gov.it/SpidL1'`` per default.

SPID_ACR_FAUTHN_MAP
    Una mappa che indica quando forzare il contesto di autenticazione.
    Per default è ``'false'`` per il contesto *SpidL1* e ``'true'`` per gli altri, in linea
    con quanto è definito nelle
    `regole tecniche SPID <https://docs.italia.it/italia/spid/spid-regole-tecniche/it/stabile/index.html>`_

SPID_IDENTITY_PROVIDERS_URL
    URL della risorsa che contiene i dati degli IdP, ``'https://registry.spid.gov.it/assets/data/idp.json'``
    per default.

SPID_IDENTITY_PROVIDERS_METADATA_DIR
    Path assoluto della directory dove salvare i metadati degli IdP, per default è la
    congiunzione del path ``BASE_DIR`` e ``'metadata/'``.

SPID_PREFIXES
    Associazioni dei namespace di SPID con prefissi, per default il prefisso **spid**
    è associato al namespace ``'https://spid.gov.it/saml-extensions'`` e il prefisso
    **fpa** è associato al namespace ``'https://spid.gov.it/invoicing-extensions'``.

SPID_REQUIRED_ATTRIBUTES
    Lista degli attributi SPID da richiedere come necessari (``isRequired='true'``).
    Il valore di default è ``['spidCode', 'name', 'familyName', 'fiscalNumber', 'email',]``.

SPID_OPTIONAL_ATTRIBUTES
    Lista degli attributi SPID da richiedere come opzionali (``isRequired='false'``).
    Se non specificato la lista comprende i seguenti attributi::

        [
            'gender',
            'companyName',
            'registeredOffice',
            'ivaCode',
            'idCard',
            'digitalAddress',
            'placeOfBirth',
            'countyOfBirth',
            'dateOfBirth',
            'address',
            'mobilePhone',
            'expirationDate',
        ]


Configurazioni SAML2 opzionali
++++++++++++++++++++++++++++++

Alcune impostazioni per SAML2 (*djangosaml2*) usate da *spid-django* assumono dei valori
di default quando non sono esplicitamente definite:

SAML_CONFIG_LOADER
    Default: ``'djangosaml2_spid.conf.config_settings_loader'``

SAML_USE_NAME_ID_AS_USERNAME
    Default: ``False``

SAML_DJANGO_USER_MAIN_ATTRIBUTE
    Default: ``'username'``

SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP
    Default: ``'__iexact'``

SAML_CREATE_UNKNOWN_USER
    Default: ``True``

SAML_LOGOUT_REQUEST_PREFERRED_BINDING
    Default: ``saml2.BINDING_HTTP_POST``

SAML_ATTRIBUTE_MAPPING
    Default::

        {
            'spidCode': ('username', ),
            'fiscalNumber': ('tin', ),
            'email': ('email', ),
            'name': ('first_name', ),
            'familyName': ('last_name', ),
            'placeOfBirth': ('place_of_birth',),
            'dateOfBirth': ('birth_date',),
        }
