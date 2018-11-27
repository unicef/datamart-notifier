from django.conf import settings

# DEFAULT_MODELS = ['etools.applications.audit.models.*',
#                   'etools.applications.hact.models.AggregateHact',
#                   'etools.applications.partners.models.PartnerOrganization',
#                   'etools.applications.partners.models.Intervention',
#                   'etools.applications.users.models.User',
#                   # SpotCheck, Audit, SpecialAudit, MicroAssessment, Engagement, User
#                   ]
MODELS = getattr(settings, 'DNSS_MODELS', [])
WEBHOOK = getattr(settings, 'DNSS_WEBHOOK', 'https://datamart.unicef.io/hook/update')

TIMEOUT = getattr(settings, 'DNSS_TIMEOUT', 0.5)
USERNAME = getattr(settings, 'DNSS_USERNAME', '')
PASSWORD = getattr(settings, 'DNSS_PASSWORD', 'PASSWORD')
