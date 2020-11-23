import pytest
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
        "casalts": [
            {"casalt": "0001050799", "weight": 0.5},
            {"casalt": "1050799", "weight": 0.5},
        ],
        "synonyms": [
            {"identifier": "Meperon", "weight": 0.75},
            {"identifier": "Methylperidol", "weight": 0.5},
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
        "casalts": [
            {"casalt": "0001050799", "weight": 0.5},
            {"casalt": "1050799", "weight": 0.5},
        ],
        "synonyms": [
            {"identifier": "Meperon", "weight": 0.75},
            {"identifier": "Methylperidol", "weight": 0.5},
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
        "casalts": [
            {"casalt": "0001050799", "weight": 0.5},
            {"casalt": "1050799", "weight": 0.5},
        ],
        "synonyms": [
            {"identifier": "Meperon", "weight": 0.75},
            {"identifier": "Methylperidol", "weight": 0.5},
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
        "inchikey": "UUTBLVFYDQGDNV-UHFFFAOYSA-N",
        "compound_id": "DTXCID302000003",
        "casalts": [
            {"casalt": "3757-31-1", "weight": 0.5},
        ],
        "synonyms": [
            {
                "identifier": "Butyric acid, 2-(5-nitro-alpha-iminofurfuryl)hydrazide",
                "weight": 0.75,
            },
            {
                "identifier": "N'-Butanoyl-5-nitrofuran-2-carbohydrazonamide",
                "weight": 0.5,
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
    preferred_name = "Miracle Whip"
    search_url = url_for("resolved_substance_list", identifier=preferred_name)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}
    assert results["data"][0]["attributes"]["matches"]["preferred_name"] == 1
    assert results["data"][0]["attributes"]["matches"]["display_name"] == 1

    # test CASRN match
    casrn = "1050-79-9"
    search_url = url_for("resolved_substance_list", identifier=casrn)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}
    assert results["data"][0]["attributes"]["matches"]["casrn"] == 1

    # test display name match
    display_name = "Kraft Miracle Whip Original Dressing"
    search_url = url_for("resolved_substance_list", identifier=display_name)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}
    assert results["data"][0]["attributes"]["matches"]["display_name"] == 1

    # test synonym match
    synonym = "Meperon"
    search_url = url_for("resolved_substance_list", identifier=synonym)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}
    assert results["data"][0]["attributes"]["matches"]["synonyms"] == {"Meperon": 0.75}

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

    # test name containment
    partial_name = "Miracle"
    search_url = url_for("resolved_substance_list", identifier=partial_name)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}

    # test case insensitivity
    partial_name = "miracle"
    search_url = url_for("resolved_substance_list", identifier=partial_name)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 1}

    # test multiple matches
    partial_name = "Original Dressing"
    search_url = url_for("resolved_substance_list", identifier=partial_name)
    rep = client.get(search_url)
    assert rep.status_code == 200
    results = rep.get_json()
    assert results["meta"] == {"count": 2}


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
