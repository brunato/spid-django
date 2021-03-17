import os
import copy
from typing import Optional

import saml2
from saml2.config import SPConfig
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.sigver import get_xmlsec_binary
from saml2.xmldsig import DIGEST_SHA256, SIG_RSA_SHA256

from django.conf import settings
from django.http import HttpRequest
from django.core.exceptions import ImproperlyConfigured

#
# Required settings

if not hasattr(settings, 'SPID_CONTACTS'):
    raise ImproperlyConfigured('Manca la configurazione SPID_CONTACTS!')

if not hasattr(settings, 'SAML_CONFIG'):
    raise ImproperlyConfigured('Manca la configurazione base per SAML2!')
elif not isinstance(settings.SAML_CONFIG, dict):
    raise ImproperlyConfigured('Formato improprio per la configurazione SAML2!')
elif 'organization' not in settings.SAML_CONFIG:
    raise ImproperlyConfigured("Mancano le informazioni sull'organizzazione "
                               "nella configurazione SAML2!")

#
# SPID settings with default values

settings.SPID_URLS_PREFIX = getattr(settings, 'SPID_URLS_PREFIX', 'spid/')

settings.LOGIN_URL = getattr(settings, 'LOGIN_URL', '/spid/login')
settings.LOGOUT_URL = getattr(settings, 'LOGOUT_URL', '/spid/logout')
settings.LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '/spid/echo_attributes')

settings.SPID_DEFAULT_BINDING = getattr(
    settings, 'SPID_DEFAULT_BINDING', saml2.BINDING_HTTP_POST
)

settings.SPID_DIG_ALG = getattr(settings, 'SPID_DIG_ALG', DIGEST_SHA256)
settings.SPID_SIG_ALG = getattr(settings, 'SPID_SIG_ALG', SIG_RSA_SHA256)

settings.SPID_NAMEID_FORMAT = getattr(
    settings, 'SPID_NAMEID_FORMAT', NAMEID_FORMAT_TRANSIENT
)
settings.SPID_AUTH_CONTEXT = getattr(
    settings, 'SPID_AUTH_CONTEXT', 'https://www.spid.gov.it/SpidL1'
)

SPID_CERTS_DIR = os.path.join(os.environ.get('PWD'), 'certificates/')
SPID_PUBLIC_CERT = os.path.join(SPID_CERTS_DIR, 'public.cert')
SPID_PRIVATE_KEY = os.path.join(SPID_CERTS_DIR, 'private.key')

# source: https://registry.spid.gov.it/identity-providers
settings.SPID_IDENTITY_PROVIDERS_URL = getattr(
    settings, 'SPID_IDENTITY_PROVIDERS_URL',
    'https://registry.spid.gov.it/assets/data/idp.json'
)

settings.SPID_IDENTITY_PROVIDERS_METADATA_DIR = os.path.join(
    settings.BASE_DIR, 'spid_config/metadata/'
)

# Validation tools settings
settings.SPID_SAML_CHECK_REMOTE_METADATA_ACTIVE = getattr(
    settings,
    'SPID_SAML_CHECK_REMOTE_METADATA_ACTIVE',
    os.environ.get('SPID_SAML_CHECK_REMOTE_METADATA_ACTIVE', 'False') == 'True'
)

settings.SPID_SAML_CHECK_METADATA_URL = getattr(
    settings,
    'SPID_SAML_CHECK_METADATA_URL',
    os.environ.get('SPID_SAML_CHECK_METADATA_URL', 'http://localhost:8080/metadata.xml')
)

settings.SPID_TESTENV2_REMOTE_METADATA_ACTIVE = getattr(
    settings,
    'SPID_TESTENV2_REMOTE_METADATA_ACTIVE',
    os.environ.get('SPID_TESTENV2_REMOTE_METADATA_ACTIVE', 'False') == 'True'
)

settings.SPID_TESTENV2_METADATA_URL = getattr(
    settings,
    'SPID_TESTENV2_METADATA_URL',
    os.environ.get('SPID_TESTENV2_METADATA_URL', 'http://localhost:8088/metadata')
)

# Avviso 29v3
settings.SPID_PREFIXES = getattr(settings, 'SPID_PREFIXES', dict(
    spid='https://spid.gov.it/saml-extensions',
    fpa='https://spid.gov.it/invoicing-extensions'
))


#
# Defaults for other SAML settings

settings.SAML_CONFIG_LOADER = getattr(
    settings, 'SAML_CONFIG_LOADER', 'djangosaml2_spid.conf.config_settings_loader'
)

# OR NAME_ID or MAIN_ATTRIBUTE (not together!)
settings.SAML_USE_NAME_ID_AS_USERNAME = getattr(
    settings, 'SAML_USE_NAME_ID_AS_USERNAME', False
)
settings.SAML_DJANGO_USER_MAIN_ATTRIBUTE = getattr(
    settings, 'SAML_DJANGO_USER_MAIN_ATTRIBUTE', 'username'
)
settings.SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP = getattr(
    settings, 'SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP', '__iexact'
)
settings.SAML_CREATE_UNKNOWN_USER = getattr(
    settings, 'SAML_CREATE_UNKNOWN_USER', True
)

# logout
settings.SAML_LOGOUT_REQUEST_PREFERRED_BINDING = getattr(
    settings, 'SAML_LOGOUT_REQUEST_PREFERRED_BINDING', saml2.BINDING_HTTP_POST
)

settings.SAML_ATTRIBUTE_MAPPING = getattr(settings, 'SAML_ATTRIBUTE_MAPPING', {
    'spidCode': ('username', ),
    'fiscalNumber': ('tin', ),
    'email': ('email', ),
    'name': ('first_name', ),
    'familyName': ('last_name', ),
    'placeOfBirth': ('place_of_birth',),
    'dateOfBirth': ('birth_date',),
})


def config_settings_loader(request: Optional[HttpRequest] = None) -> SPConfig:
    conf = SPConfig()
    if request is None or not request.path.lstrip('/').startswith(settings.SPID_URLS_PREFIX):
        # Not a SPID request: load SAML_CONFIG unchanged
        conf.load(copy.deepcopy(settings.SAML_CONFIG))
        return conf

    # Build a SAML_CONFIG for SPID
    spid_base_url = request.build_absolute_uri('spid')

    saml_config = {
        'entityid': f'{spid_base_url}metadata',
        'attribute_map_dir': f'{settings.BASE_DIR}/spid_config/attribute-maps/',

        'service': {
            'sp': {
                'name': f'{spid_base_url}metadata',
                'name_qualifier': request.get_host(),
                'name_id_format': [settings.SPID_NAMEID_FORMAT],

                'endpoints': {
                    'assertion_consumer_service': [
                        (f'{spid_base_url}acs', settings.SPID_DEFAULT_BINDING),
                    ],
                    'single_logout_service': [
                        (f'{spid_base_url}ls/post', settings.SPID_DEFAULT_BINDING),
                    ],
                },

                # Mandates that the IdP MUST authenticate the presenter directly
                # rather than rely on a previous security context.
                'force_authn': False,  # SPID
                'name_id_format_allow_create': False,

                # attributes that this project need to identify a user
                'required_attributes': [
                    'spidCode',
                    'name',
                    'familyName',
                    'fiscalNumber',
                    'email'
                ],

                'requested_attribute_name_format': saml2.saml.NAME_FORMAT_BASIC,
                'name_format': saml2.saml.NAME_FORMAT_BASIC,

                # attributes that may be useful to have but not required
                'optional_attributes': [
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
                    'expirationDate'
                ],

                'signing_algorithm': settings.SPID_SIG_ALG,
                'digest_algorithm': settings.SPID_DIG_ALG,

                'authn_requests_signed': True,
                'logout_requests_signed': True,

                # Indicates that Authentication Responses to this SP must
                # be signed. If set to True, the SP will not consume
                # any SAML Responses that are not signed.
                'want_assertions_signed': True,

                # When set to true, the SP will consume unsolicited SAML
                # Responses, i.e. SAML Responses for which it has not sent
                # a respective SAML Authentication Request.
                'allow_unsolicited': False,

                # Permits to have attributes not configured in attribute-mappings
                # otherwise...without OID will be rejected
                'allow_unknown_attributes': True,
            },
        },

        'metadata': {
            'local': [settings.SPID_IDENTITY_PROVIDERS_METADATA_DIR],
            'remote': []
        },

        # Signing
        'key_file': settings.SPID_PRIVATE_KEY,
        'cert_file': settings.SPID_PUBLIC_CERT,

        # Encryption
        'encryption_keypairs': [{
            'key_file': settings.SPID_PRIVATE_KEY,
            'cert_file': settings.SPID_PUBLIC_CERT,
        }],

        'organization': copy.deepcopy(settings.SAML_CONFIG['organization'])
    }

    if settings.SAML_CONFIG.get('debug'):
        saml_config['debug'] = True

    if 'xmlsec_binary' in settings.SAML_CONFIG:
        saml_config['xmlsec_binary'] = copy.deepcopy(settings.SAML_CONFIG['xmlsec_binary'])
    else:
        saml_config['xmlsec_binary'] = get_xmlsec_binary(['/opt/local/bin', '/usr/bin/xmlsec1'])

    if settings.SPID_SAML_CHECK_REMOTE_METADATA_ACTIVE:
        saml_config['metadata']['remote'].append(
            {'url': settings.SPID_SAML_CHECK_METADATA_URL}
        )

    if settings.SPID_TESTENV2_REMOTE_METADATA_ACTIVE:
        saml_config['metadata']['remote'].append(
            {'url': settings.SPID_TESTENV2_METADATA_URL}
        )

    conf.load(saml_config)
    return conf
