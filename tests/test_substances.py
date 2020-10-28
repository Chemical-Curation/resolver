from flask import url_for
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
            {"synonym": "Meperon", "weight": 0.75},
            {"synonym": "Methylperidol", "weight": 0.5},
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
        "casalts": [
            {"casalt": "0001050799", "weight": 0.5},
            {"casalt": "1050799", "weight": 0.5},
        ],
        "synonyms": [
            {"synonym": "Meperon", "weight": 0.75},
            {"synonym": "Methylperidol", "weight": 0.5},
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

    data["data"]["id"] = "DTXCID302000999"
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
            {"synonym": "Meperon", "weight": 0.75},
            {"synonym": "Methylperidol", "weight": 0.5},
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