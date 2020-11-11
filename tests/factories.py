import factory
from resolver.models import User, Substance


class UserFactory(factory.Factory):

    username = factory.Sequence(lambda n: "user%d" % n)
    email = factory.Sequence(lambda n: "user%d@mail.com" % n)
    password = "mypwd"

    class Meta:
        model = User


class SubstanceFactory(factory.Factory):

    id = factory.Sequence(lambda n: f"DTXCID{n:09}")
    identifiers = (
        { "preferred_name":"Moperone","display_name":"Moperone","casrn":"1050-79-9",
        "inchikey": "AGAHNABIDCTLHW-UHFFFAOYSA-N",
        "casalts":[{"casalt":"0001050799","weight":0.5},{"casalt":"1050799","weight":0.5}],
        "synonyms": [{"identifier": "Meperon","weight": 0.75},{"identifier": "Methylperidol","weight": 0.5}]}
    )

    class Meta:
        model = Substance
