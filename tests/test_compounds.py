from flask import url_for
from api.models import Compound


def test_get_compound(client, db, compound, admin_headers):
    # test 404
    compound_url = url_for("api.compound_by_id", compound_id="ZTXCID302000003")
    rep = client.get(compound_url, headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(compound)
    db.session.commit()

    # test get_compound
    compound_url = url_for("api.compound_by_id", compound_id=compound.id)
    rep = client.get(compound_url, headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()["compound"]
    assert data["identifiers"] == compound.identifiers


def test_put_compound(client, db, compound, admin_headers):
    # test 404
    compound_url = url_for("api.compound_by_id", compound_id="ZTXCID302000003")
    rep = client.put(compound_url, headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(compound)
    db.session.commit()
    newids = '{ "preferred_name":"Moperone Updated","casrn":"1050-79-9","inchikey": "AGAHNABIDCTLHW-UHFFFAOYSA-N", "casalts":[{"casalt":"0001050799","weight:0.5},{"casalt":"1050799","weight":0.5}],"synonyms": [{"synonym": "Meperon","weight": 0.75},{"synonym": "Methylperidol","weight": 0.5}]}'
    data = {"identifiers": newids}

    compound_url = url_for("api.compound_by_id", compound_id=compound.id)
    # test update compound
    rep = client.put(compound_url, json=data, headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()["compound"]
    assert data["identifiers"] == newids


def test_delete_compound(client, db, compound, admin_headers):
    # test 404
    compound_url = url_for("api.compound_by_id", compound_id="ZTXCID302000003")
    rep = client.delete(compound_url, headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(compound)
    db.session.commit()

    # test delete_compound

    compound_url = url_for("api.compound_by_id", compound_id=compound.id)
    rep = client.delete(compound_url, headers=admin_headers)
    assert rep.status_code == 200
    assert db.session.query(Compound).filter_by(id=compound.id).first() is None


def test_create_compound(client, db, admin_headers):
    # test bad data
    compounds_url = url_for("api.compounds")
    data = {"id": ""}
    rep = client.post(compounds_url, json=data, headers=admin_headers)
    assert rep.status_code == 400

    data["id"] = "DTXCID302000999"
    idents = '{ "preferred_name":"Miracle Whip","casrn":"1050-79-9","inchikey": "AGAHNABIDCTLHW-UHFFFAOYSA-N", "casalts":[{"casalt":"0001050799","weight:0.5},{"casalt":"1050799","weight":0.5}],"synonyms": [{"synonym": "Meperon","weight": 0.75},{"synonym": "Methylperidol","weight": 0.5}]}'
    data["identifiers"] = idents

    rep = client.post(compounds_url, json=data, headers=admin_headers)
    assert rep.status_code == 201

    data = rep.get_json()
    compound = db.session.query(Compound).filter_by(id=data["compound"]["id"]).first()

    assert compound.identifiers == idents
    # test those index_properties
    assert compound.casrn in data
    assert compound.preferred_name in data


def test_get_all_compounds(client, db, compound_factory, admin_headers):
    compounds_url = url_for("api.compounds")
    compounds = compound_factory.create_batch(30)

    db.session.add_all(compounds)
    db.session.commit()

    rep = client.get(compounds_url, headers=admin_headers)
    assert rep.status_code == 200

    results = rep.get_json()
    for compound in compounds:
        assert any(c["id"] == compound.id for c in results["results"])
