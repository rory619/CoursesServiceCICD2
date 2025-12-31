def test_create_course(client):
    r = client.post(
        "/api/courses",
        json={"code": "CICD101", "name": "CICD", "credits": 5},
    )
    assert r.status_code == 201
    return r.json()


def test_list_courses(client):
    test_create_course(client)
    r = client.get("/api/courses")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_course(client):
    created = test_create_course(client)
    course_id = created["id"]
    r = client.get(f"/api/courses/{course_id}")
    assert r.status_code == 200
    assert r.json()["id"] == course_id


def test_get_course_404(client):
    r = client.get("/api/courses/999999")
    assert r.status_code == 404


def test_update_course(client):
    created = test_create_course(client)
    course_id = created["id"]

    r = client.put(
        f"/api/courses/{course_id}",
        json={"code": "CICD101", "name": "CICD Updated", "credits": 6},
    )

    print("UPDATE STATUS:", r.status_code)
    print("UPDATE JSON:", r.json())

    assert r.status_code == 200
    assert r.json()["name"] == "CICD Updated"


def test_delete_course(client):
    created = test_create_course(client)
    course_id = created["id"]
    r = client.delete(f"/api/courses/{course_id}")
    assert r.status_code in (200, 204)
