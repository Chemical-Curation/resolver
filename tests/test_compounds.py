from flask import url_for
from api.models import Substance


def test_get_substance(client, db, substance, admin_headers):
    # test 404
    substance_url = url_for("api.substance_by_id", substance_id="ZTXCID302000003")
    rep = client.get(substance_url, headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(substance)
    db.session.commit()

    # test get_substance
    substance_url = url_for("api.substance_by_id", substance_id=substance.id)
    rep = client.get(substance_url, headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()["substance"]
    assert data["identifiers"] == substance.identifiers


def test_put_substance(client, db, substance, admin_headers):
    # test 404
    substance_url = url_for("api.substance_by_id", substance_id="ZTXCID302000003")
    rep = client.put(substance_url, headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(substance)
    db.session.commit()
    newids = '{ "preferred_name":"Moperone Updated","casrn":"1050-79-9","inchikey": "AGAHNABIDCTLHW-UHFFFAOYSA-N", "casalts":[{"casalt":"0001050799","weight:0.5},{"casalt":"1050799","weight":0.5}],"synonyms": [{"synonym": "Meperon","weight": 0.75},{"synonym": "Methylperidol","weight": 0.5}]}'
    data = {"identifiers": newids}

    substance_url = url_for("api.substance_by_id", substance_id=substance.id)
    # test update substance
    rep = client.put(substance_url, json=data, headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()["substance"]
    assert data["identifiers"] == newids


def test_delete_substance(client, db, substance, admin_headers):
    # test 404
    substance_url = url_for("api.substance_by_id", substance_id="ZTXCID302000003")
    rep = client.delete(substance_url, headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(substance)
    db.session.commit()

    # test delete_substance

    substance_url = url_for("api.substance_by_id", substance_id=substance.id)
    rep = client.delete(substance_url, headers=admin_headers)
    assert rep.status_code == 200
    assert db.session.query(Substance).filter_by(id=substance.id).first() is None


def test_create_substance(client, db, admin_headers):
    # test bad data
    substances_url = url_for("api.substances")
    data = {"id": ""}
    rep = client.post(substances_url, json=data, headers=admin_headers)
    assert rep.status_code == 400

    data["id"] = "DTXCID302000999"
    idents = '{ "preferred_name":"Miracle Whip","casrn":"1050-79-9","inchikey": "AGAHNABIDCTLHW-UHFFFAOYSA-N", "casalts":[{"casalt":"0001050799","weight:0.5},{"casalt":"1050799","weight":0.5}],"synonyms": [{"synonym": "Meperon","weight": 0.75},{"synonym": "Methylperidol","weight": 0.5}]}'
    data["identifiers"] = idents

    rep = client.post(substances_url, json=data, headers=admin_headers)
    assert rep.status_code == 201

    data = rep.get_json()
    substance = (
        db.session.query(Substance).filter_by(id=data["substance"]["id"]).first()
    )

    assert substance.identifiers == idents
    # test those index_properties
    assert substance.casrn in data
    assert substance.preferred_name in data


def test_get_all_substances(client, db, substance_factory, admin_headers):
    substances_url = url_for("api.substances")
    substances = substance_factory.create_batch(30)

    db.session.add_all(substances)
    db.session.commit()

    rep = client.get(substances_url, headers=admin_headers)
    assert rep.status_code == 200

    results = rep.get_json()
    for substance in substances:
        assert any(c["id"] == substance.id for c in results["results"])
