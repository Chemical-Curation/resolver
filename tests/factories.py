import factory
from api.models import User, Substance


class UserFactory(factory.Factory):

    username = factory.Sequence(lambda n: "user%d" % n)
    email = factory.Sequence(lambda n: "user%d@mail.com" % n)
    password = "mypwd"

    class Meta:
        model = User


class SubstanceFactory(factory.Factory):

    id = factory.Sequence(lambda n: "DTXCID%d" % n)
    identifiers = '{ "preferred_name":"Moperone","casrn":"1050-79-9","inchikey": "AGAHNABIDCTLHW-UHFFFAOYSA-N", "casalts":[{"casalt":"0001050799","weight:0.5},{"casalt":"1050799","weight":0.5}],"synonyms": [{"synonym": "Meperon","weight": 0.75},{"synonym": "Methylperidol","weight": 0.5}]}'

    class Meta:
        model = Substance
