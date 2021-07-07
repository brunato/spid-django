************
Introduzione
************

*spid-django* è una app per il `web framework Django <https://www.djangoproject.com/>`_
che permette di implementare un *Service Provider* con autenticazione SPID, il Sistema Pubblico di Identità Digitale.

Per maggiori informazioni su SPID consultare il `sito ufficiale di SPID <http://www.spid.gov.it/>`_.
La documentazione tecnica di SPID è disponibile sul sito di
`Docs Italia <https://docs.italia.it/italia/spid/spid-regole-tecniche>`_.


Installazione
=============

Prerequisiti per l'installazione è la disponibilità di alcune librerie e dei tool di sviluppo
necessari a compilare alcuni moduli esterni:

- xmlsec
- python3-pip
- python3-dev (su Debian, python3-devel su Fedora)
- libssl-dev (su Debian, openssl-devel su Fedora)
- libsasl2-dev (su Debian, cyrus-sasl-devel su Fedora)

Una volta installate le dipendenze, configurare e attivare un
`ambiente virtuale Python <https://docs.python.org/3/tutorial/venv.html>`_ per
evitare di alterare i pacchetti di sistema, e installare poi *spid-django* con
il comando::

    pip install spid-django

Il comando installerà anche le altre dipendenze necessarie al funzionamento
dell'applicazione.


Utilizzo in un progetto Django
==============================

Per attivare la app in un progetto Django, effettuare i seguenti passi:

* Aggiungere in ``settings.INSTALLED_APPS`` le seguenti linee::

    'djangosaml2',
    'djangosaml2_spid',

* Aggiungere in `settings.MIDDLEWARE` la configurazione per la gestione delle sessioni SAML::

     'djangosaml2.middleware.SamlSessionMiddleware'

* Aggiungere in `settings.AUTHENTICATION_BACKENDS` le seguenti linee::

    'django.contrib.auth.backends.ModelBackend',
    'djangosaml2.backends.Saml2Backend',

* Aggiungere le configurazioni obbligatorie e opzionali desiderate (vedere sezione per le
  specifiche voci di configurazione)
* Generare i certificati X.509 certificates per SPID e salvarli nel path configurato (vedi
  configurazione SPID_CERTS_DIR). Per generare i certificati si può utilizzare l'apposito
  tool disponibile sul repo https://github.com/italia/spid-compliant-certificates.


Licenza
=======

La app *spid-django* è distribuita con la licenza
`Apache-2.0 <https://opensource.org/licenses/Apache-2.0>`_.


Supporto
========

Questo software è pubblicato sul servizio GitHub, fare riferimento alla
`home del progetto spid-django <https://github.com/italia/spid-django>`_
per il codice sorgente e per la segnalazione di problemi di funzionamento.
