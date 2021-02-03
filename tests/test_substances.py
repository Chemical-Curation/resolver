import pytest
import copy
from flask import url_for

from resolver.api.schemas import SubstanceSchema
from resolver.models import Substance


def test_get_substance(client, db, substance):
    # test 404
    substance_url = url_for("substance_detail", id="ZTXCID302000003")
    rep = client.get(substance_url)
    assert rep.status_code == 200
    assert rep.get_json() is None

    db.session.add(substance)
    db.session.commit()

    # test get_substance
    substance_url = url_for("substance_detail", id=substance.id)
    rep = client.get(substance_url)
    assert rep.status_code == 200

    idents = rep.get_json()["data"]["attributes"]["identifiers"]
    assert idents == substance.identifiers


def test_patch_substance(client, db, substance):
    # test 404
    substance_url = url_for("substance_detail", id="ZTXCID302000003")
    data = {
        "data": {
            "id": "ZTXCID302000003",
            "type": "substance",
            "attributes": {"identifiers": {}},
        }
    }
    rep = client.patch(
        substance_url, json=data, headers={"content-type": "application/vnd.api+json"}
    )
    assert rep.status_code == 404

    db.session.add(substance)
    db.session.commit()
    new_idents = {
        "preferred_name": "Moperone Updated",
        "casrn": "1050-79-9",
        "inchikey": "AGAHNABIDCTLHW-UHFFFAOYSA-N",
        "synonyms": [
            {
                "identifier": "0001050799",
                "weight": 0.5,
                "synonymtype": "Alternate CAS-RN",
            },
            {
                "identifier": "1050799",
                "weight": 0.5,
                "synonymtype": "Alternate CAS-RN",
            },
            {
                "identifier": "Meperon",
                "weight": 0.75,
                "synonymtype": "Generic Name",
            },
            {
                "identifier": "Methylperidol",
                "weight": 0.5,
                "synonymtype": "Generic Name",
            },
        ],
    }
    data["data"]["id"] = substance.id
    data["data"]["attributes"]["identifiers"] = new_idents

    substance_url = url_for("substance_detail", id=substance.id)
    # test update substance
    rep = client.patch(
        substance_url, json=data, headers={"content-type": "application/vnd.api+json"}
    )
    assert rep.status_code == 200
    print(rep.get_json())
    substance_idents = rep.get_json()["data"]["attributes"]["identifiers"]
    assert substance_idents == new_idents


def test_delete_substance(client, db, substance):
    # test 404
    substance_url = url_for("substance_detail", id="ZTXCID302000003")
    print(substance_url)
    rep = client.delete(substance_url)
    assert rep.status_code == 404

    db.session.add(substance)
    db.session.commit()

    # test delete_substance

    substance_url = url_for("substance_detail", id=substance.id)
    rep = client.delete(substance_url)
    assert rep.status_code == 200
    assert db.session.query(Substance).filter_by(id=substance.id).first() is None


def test_create_substance(client, db):
    # test bad data
    substances_url = url_for("substance_list")
    data = {"data": {"id": "", "type": "substance", "attributes": {}}}
    rep = client.post(
        substances_url, json=data, headers={"content-type": "application/vnd.api+json"}
    )
    assert rep.status_code == 500

    data["data"]["id"] = "DTXCID302000999"
    idents = {
        "preferred_name": "Miracle Whip",
        "display_name": "Miracle Whip",
        "casrn": "1050-79-9",
        "inchikey": "AGAHNABIDCTLHW-UHFFFAOYSA-N",
        "synonyms": [
            {"identifier": "Meperon", "weight": 0.75, "synonymtype": "Generic Name"},
            {
                "identifier": "Methylperidol",
                "weight": 0.5,
                "synonymtype": "Generic Name",
            },
            {
                "identifier": "0001050799",
                "weight": 0.5,
                "synonymtype": "Alternate CAS-RN",
            },
            {
                "identifier": "1050799",
                "weight": 0.5,
                "synonymtype": "Alternate CAS-RN",
            },
        ],
    }
    data["data"]["attributes"]["identifiers"] = idents

    rep = client.post(
        substances_url, json=data, headers={"content-type": "application/vnd.api+json"}
    )
    assert rep.status_code == 201

    data = rep.get_json()
    rep_ident_values = data["data"]["attributes"]["identifiers"].values()
    substance = db.session.query(Substance).filter_by(id=data["data"]["id"]).first()

    assert substance.identifiers == idents
    # test those index_properties
    assert substance.casrn in rep_ident_values
    assert substance.preferred_name in rep_ident_values


def test_get_all_substances(client, db, substance_factory):
    substances_url = url_for("substance_list")
    substances = substance_factory.create_batch(30)

    db.session.add_all(substances)
    db.session.commit()

    rep = client.get(substances_url)
    assert rep.status_code == 200

    results = rep.get_json()
    for substance in substances:
        assert any(c["id"] == substance.id for c in results["data"])


def test_resolve_substance(client, db, substance):

    # TODO: replace this with factories and ORM creation once we figure out how to
    # maintain valid JSON in the identifiers field
    substances_url = url_for("substance_list")
    data = {"data": {"id": "", "type": "substance", "attributes": {}}}

    data["data"]["id"] = "DTXSID302000999"
    idents = {
        "preferred_name": "Miracle Whip",
        "display_name": "Kraft Miracle Whip Original Dressing",
        "casrn": "1050-79-9",
        "inchikey": "AGAHNABIDCTLHW-UHFFFAOYSA-N",
        "compound_id": "DTXCID302000093",
        "synonyms": [
            {"identifier": "Meperon", "weight": 0.75, "synonymtype": "Generic Name"},
            {
                "identifier": "Methylperidol",
                "weight": 0.5,
                "synonymtype": "Generic Name",
            },
            {
                "identifier": "0001050799",
                "weight": 0.5,
                "synonymtype": "Alternate CAS-RN",
            },
            {
                "identifier": "1050799",
                "weight": 0.5,
                "synonymtype": "Alternate CAS-RN",
            },
        ],
    }
    data["data"]["attributes"]["identifiers"] = idents

    rep = client.post(
        substances_url, json=data, headers={"content-type": "application/vnd.api+json"}
    )

    # second substance
    data = {"data": {"id": "", "type": "substance", "attributes": {}}}

    data["data"]["id"] = "DTXSID60191004"
    idents = {
        "preferred_name": "Butyric acid, 2-(5-nitro-alpha-iminofurfuryl)hydrazide",
        "display_name": "Butyric acid Original Dressing",
        "casrn": "3757-31-1",
        "inchikey": "AECPIECQUWDXGM-UXBLZVDNSA-N",  # this inchikey is verified vs SMILES and inchi searches.
        "compound_id": "DTXCID302000003",
        "synonyms": [
            {
                "identifier": "Butyric acid, 2-(5-nitro-alpha-iminofurfuryl)hydrazide",
                "weight": 0.75,
                "synonymtype": "Generic Name",
            },
            {
                "identifier": "3757311",
                "weight": 0.5,
                "synonymtype": "Alternate CAS-RN",
            },
            {
                "identifier": "N'-Butanoyl-5-nitrofuran-2-carbohydrazonamide",
                "weight": 0.5,
                "synonymtype": "Generic Name",
            },
        ],
    }
    data["data"]["attributes"]["identifiers"] = idents

    rep = client.post(
        substances_url, json=data, headers={"content-type": "application/vnd.api+json"}
    )

    # test non-resolving identifier
    search_url = url_for("resolved_substance_list", identifier="Foobar")
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["data"] == []

    # test preferred name match
    # (encode spaces in string first?)
    search_url = url_for(
        "resolved_substance_list",
        identifier="Miracle Whip",
    )
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}

    # test CASRN match
    casrn = "1050-79-9"
    search_url = url_for("resolved_substance_list", identifier=casrn)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}

    # test display name match
    display_name = "Kraft Miracle Whip Original Dressing"
    search_url = url_for("resolved_substance_list", identifier=display_name)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}

    # test synonym matches
    synonym = "3757311"
    search_url = url_for("resolved_substance_list", identifier=synonym)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}

    synonym = "Meperon"
    search_url = url_for("resolved_substance_list", identifier=synonym)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}

    # test CID match
    cid = "DTXCID302000003"
    search_url = url_for("resolved_substance_list", identifier=cid)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}

    # test SID match
    sid = "DTXSID60191004"
    search_url = url_for("resolved_substance_list", identifier=sid)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}

    # test Inchikey match
    inchikey = "AECPIECQUWDXGM-UXBLZVDNSA-N"
    search_url = url_for("resolved_substance_list", identifier=inchikey)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}
    assert results["data"][0]["attributes"]["score"] == 1

    # test SMILES match
    smiles = "CCCC(=O)N/N=C(/C1=CC=C(O1)[N+](=O)[O-])"
    search_url = url_for("resolved_substance_list", identifier=smiles)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}
    assert results["data"][0]["attributes"]["score"] == 1

    # test Inchi match
    inchikey = "InChI=1S/C9H11N3O4/c1-2-3-8(13)11-10-6-7-4-5-9(16-7)12(14)15/h4-6H,2-3H2,1H3,(H,11,13)/b10-6+"
    search_url = url_for("resolved_substance_list", identifier=inchikey)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}
    assert results["data"][0]["attributes"]["score"] == 1

    # test mis-formatted CASRN matches (1050799 and 0001050799 match as synonyms)
    bad_casrns = ["001050799", "000001050-7-99"]
    for bad_casrn in bad_casrns:
        search_url = url_for("resolved_substance_list", identifier=bad_casrn)
        rep = client.get(search_url)
        assert rep.status_code == 200
        results = rep.get_json()
        assert results["meta"] == {"count": 1}
        assert results["data"][0]["attributes"]["score"] == 0.25
        assert results["data"][0]["attributes"]["matches"]["casrn"] == 0.25

    # test name containment (Partial Matching Removed in ticket #21)
    partial_name = "Miracle"
    search_url = url_for("resolved_substance_list", identifier=partial_name)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 0}

    # test case insensitivity
    partial_name = "miracle whip"
    search_url = url_for("resolved_substance_list", identifier=partial_name)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}
    assert results["data"][0]["attributes"]["score"] == 1  # exact match despite case

    # test multiple matches (Partial Matching Removed in ticket #21)
    partial_name = "Original Dressing"
    search_url = url_for("resolved_substance_list", identifier=partial_name)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 0}


# Tests both create and update functionality using param create_test.
@pytest.mark.parametrize("create_test", [pytest.param(False), pytest.param(True)])
def test_substance_index(client, db, substance_factory, create_test):
    url = url_for("substance_index")

    if create_test:
        # instance to be created
        instance = substance_factory.build()
    else:
        # instance to be updated
        instance = substance_factory.create()
        db.session.add(instance)
        db.session.commit()
    substance_dict = SubstanceSchema().dump(instance)
    resp = client.post(
        url, json=substance_dict, headers={"content-type": "application/vnd.api+json"}
    )

    assert resp.status_code == 201
    results = resp.get_json()
    assert results["data"]["attributes"]["identifiers"] == instance.identifiers


def test_substance_index_delete(client, db, substance_factory):
    url = url_for("substance_index")

    # Create a Substance.  Add to test database
    sub = substance_factory.create()
    db.session.add(sub)
    db.session.commit()
    assert Substance.query.count() != 0

    # Delete entire index
    resp = client.delete(url, headers={"content-type": "application/vnd.api+json"})
    results = resp.get_json()

    # Verify response and database state
    assert resp.status_code == 200
    assert "Substance Index successfully cleared" in results["meta"]["message"]
    assert Substance.query.count() == 0


def test_resolve_many_substances(client, db, substance_factory):
    # add a lot of substances
    substances = substance_factory.create_batch(1000)
    db.session.add_all(substances)
    db.session.commit()

    # query the database and
    # pick some attributes to search for:

    substances = Substance.query.all()

    substance_first = substances[0]
    substance_later = substances[50]

    id_first = substance_first.id

    # the index properties can be used here to fetch the preferred_name
    # without using the identifiers["preferred_name"] key
    name_first = substance_first.preferred_name
    name_later = substance_later.preferred_name

    synonym_1_identifier_later = substance_later.identifiers["synonyms"][0][
        "identifier"
    ]

    # make sure the factory generated distinct values
    assert (
        substance_later.identifiers["preferred_name"]
        != substance_first.identifiers["preferred_name"]
    )

    # Searching by ID should return one result
    search_url = url_for("resolved_substance_list", identifier=id_first)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}

    # Searching by preferred_name should return one result
    search_url = url_for("resolved_substance_list", identifier=name_first)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}

    # Searching by synonym should return one result when the Alternate CAS-RN
    # synonyms are all unique
    search_url = url_for(
        "resolved_substance_list", identifier=synonym_1_identifier_later
    )
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}

    # The Generic Name synonyms (index [2]) are not necessarily as unique,
    # so create a condition where the search term is known to be a synonym and
    # a preferred_name, and confirm that multiple records are returned
    substance_first.identifiers = copy.deepcopy(substance_first.identifiers)
    substance_first.identifiers["synonyms"][2]["identifier"] = name_later
    db.session.add(substance_first)
    db.session.commit()
    assert substance_first.identifiers["synonyms"][2]["identifier"] == name_later

    search_url = url_for("resolved_substance_list", identifier=name_later)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"]["count"] > 1

    # A later substance's preferred_name has been assigned
    # as a synonym to the first substance, so the first result
    # should be the higher-scoring substance, which would normally
    # not appear sorted at the beginning
    assert results["data"][0]["attributes"]["score"] == 1
    assert results["data"][1]["attributes"]["score"] < 1
    # the "matches" dict should report what synonym type produced the match
    assert "Generic Name" in results["data"][1]["attributes"]["matches"].keys()
    # However many results there are, scores should descend monotonically
    score_previous = 1.0
    for d in results["data"]:
        score_current = d["attributes"]["score"]
        assert score_current <= score_previous
        score_previous = score_current


def test_resolve_searches_all_rows(client, db, substance_factory):
    preferred_name = "Substance"

    # Make 100 substances with near preferred name matches
    for i in range(100):
        substance = substance_factory()
        substance.identifiers["preferred_name"] = f"{preferred_name} {i}"
        db.session.add(substance)
        db.session.commit()

    # Add substance with preferred name exact match.
    exact_substance = substance_factory()
    exact_substance.identifiers["preferred_name"] = preferred_name
    db.session.add(exact_substance)
    db.session.commit()

    search_url = url_for("resolved_substance_list", identifier=preferred_name)
    rep = client.get(search_url)

    assert rep.status_code == 200
    results = rep.get_json()
    # 100 close matches + 1 exact match (Ticket #21 containment no longer matches. Count from 101 to 1)
    assert results["meta"] == {"count": 1}

    first_result = results["data"][0]
    assert first_result["attributes"]["score"] == 1  # First result is a perfect score
    assert first_result["id"] == exact_substance.id  # First result is the correct sid


def test_resolve_no_pagination(client, db, substance_factory):
    n = 100
    identifier = "Substance"

    # Make n substances
    for i in range(n):
        substance = substance_factory()
        substance.identifiers["preferred_name"] = f"{identifier}"
        db.session.add(substance)
        db.session.commit()

    # search all substances
    search_url = url_for("resolved_substance_list", identifier=identifier)
    resp = client.get(search_url)
    results = resp.get_json()

    assert not results.get("links")
    assert len(results["data"]) == n
