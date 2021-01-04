from urllib.parse import urlparse

from standards.models import Term



# DEFAULT TERM SETTERS
###############################################################################

def get_default_license():
    """
    Return default value for license foreign key fields (All Rights Reserved).
    Used for StandardsDocument, StandardsCrosswalk, ContentCollection,
    ContentNode, and ContentCorrelation classes.
    """
    return Term.objects.get(
        vocabulary__jurisdiction__name="Global",
        vocabulary__name="LicenseKinds",
        path="All_Rights_Reserved"
    )


def get_default_standard_node_relation_kind():
    """
    Return the default ``kind`` for ``StandardNodeRelation`` objects.
    """
    return Term.objects.get(
        vocabulary__jurisdiction__name="Global",
        vocabulary__name="StandardNodeRelationKinds",
        path="majorAlignment"
    )


def get_default_content_standard_relation_kind():
    """
    Return the default ``kind`` for ``ContentStandardRelation`` objects.
    """
    return Term.objects.get(
        vocabulary__jurisdiction__name="Global",
        vocabulary__name="ContentStandardRelationKinds",
        path="majorCorrelation"
    )
