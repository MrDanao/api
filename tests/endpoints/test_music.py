from hashlib import sha256

import pytest

from core.config import config
from data.object_store import engine as object_store
from tests.conftest import client


headers = {}
music = {}


def test_login(client):
    data = {
        'username': config.api_user,
        'password': config.api_pass
    }
    response = client.post('/login', json=data)
    assert response.status_code == 200
    assert response.json()['access_token']
    headers['Authorization'] = f"Bearer {response.json()['access_token']}"


def test_get_musics(client):
    response = client.get('/music')
    assert response.status_code == 200
    assert response.json() == []


def test_post_music(client):
    data = {
        'artist': 'a',
        'title': 'a',
        'album': 'a',
        'label': 'a',
        'year': 1
    }
    response = client.post('/music', headers=headers, json=data)
    assert response.status_code == 201
    music.update(response.json())


def test_music_by_id(client):
    response = client.get(f"/music/{music['_id']}", headers=headers)
    assert response.status_code == 200
    assert response.json() == music


def test_patch_music_by_id(client):
    data = {
        'artist': 'b',
        'title': 'b',
        'album': 'b',
        'label': 'b',
        'year': 2
    }
    response = client.patch(f"/music/{music['_id']}", headers=headers, json=data)
    assert response.status_code == 200
    assert response.json() == {
        '_id': music['_id'],
        'artist': 'b',
        'title': 'b',
        'album': 'b',
        'label': 'b',
        'year': 2,
        '_sha256': {
            'audio': '0',
            'image': '0'
        }
    }


@pytest.mark.parametrize('value,expected', [
    (
        {'type': 'audio', 'file': 'tests/testdata/test.mp3', 'ct': 'audio/mpeg'},
        '401e6a16361bb4e80339da138ddb3e6e5c02fe1dacd521879ccb0d773513b790'
    ),
    (
        {'type': 'image', 'file': 'tests/testdata/test.png', 'ct': 'image/png'},
        '16887bc863042798c6add99f0420f384e1ebeb6552a234165f959bb78f26eec3'
    )
])
def test_upload_music_file(client, value, expected):
    files = {value['type']: (value['file'], open(value['file'],'rb'), value['ct'])}
    response = client.put(f"/music/{music['_id']}/{value['type']}", headers=headers, files=files)
    download = object_store.get_object('music', f"{music['_id']}/{value['type']}")
    h = sha256()
    h.update(download.read())
    downloaded_sha256sum = h.hexdigest()
    download.close()
    download.release_conn()
    assert response.status_code == 201
    assert response.json()['_sha256'][value['type']] == expected
    assert downloaded_sha256sum == expected


def test_delete_image_by_id(client):
    response = client.delete(f"/music/{music['_id']}", headers=headers)
    assert response.status_code == 204
