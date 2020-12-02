import factory
from faker import Faker
from faker.providers import BaseProvider

from resolver.models import User, Substance

fake = Faker()
Faker.seed(0)


class UserFactory(factory.Factory):

    username = factory.Sequence(lambda n: "user%d" % n)
    email = factory.Sequence(lambda n: "user%d@mail.com" % n)
    password = "mypwd"

    class Meta:
        model = User


class SubstanceProvider(BaseProvider):
    """
    Fake color names are as good as any other dummy string for substances
    """

    def substancename(self):
        return fake.color_name()

    def synonymidentifier(self):
        return fake.color_name()

    def synonymtype(self):
        return fake.random_elements(
            elements=("Generic Name", "Alternate CAS-RN", "Collapsed CAS-RN", "EINECS"),
            length=1,
        )[0]

    def synonymweight(self):
        return fake.randomize_nb_elements(number=40) / 100

    def substanceidentifierjson(self):
        identifiers = {}
        identifiers["preferred_name"] = fake.color_name()
        identifiers["display_name"] = identifiers["preferred_name"]
        identifiers["casrn"] = fake.numerify(text="####-##-#")
        identifiers["inchikey"] = fake.lexify(text="????????????-??????????-?")
        identifiers["compound_id"] = fake.numerify(text="DTXCID#########")
        identifiers["synonyms"] = [
            {
                "identifier": fake.numerify(text="00######"),
                "weight": fake.randomize_nb_elements(number=50) / 100,
                "synonymtype": "Alternate CAS-RN",
            },
            {
                "identifier": fake.numerify(text="00######"),
                "weight": fake.randomize_nb_elements(number=50) / 100,
                "synonymtype": "Alternate CAS-RN",
            },
            {
                "identifier": fake.color_name(),
                "weight": fake.randomize_nb_elements(number=50) / 100,
                "synonymtype": "Generic Name",
            },
        ]
        return identifiers


fake.add_provider(SubstanceProvider)


class SubstanceFactory(factory.Factory):
    id = factory.Sequence(lambda n: f"DTXSID{n:09}")

    identifiers = factory.LazyAttribute(lambda n: fake.substanceidentifierjson())

    class Meta:
        model = Substance
