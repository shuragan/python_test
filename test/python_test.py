import pytest
from faker import Faker
from requests import get as _get, post as _post, delete as _delete
from allure import description as desc


BASE_URL = "https://petstore.swagger.io/v2"

fake = Faker()

@pytest.fixture
def create_pet(status="available"):
    payload = {
        "id": fake.random_int(min=1, max=9999),
        "category": {
            "id": fake.random_int(min=1, max=100),
            "name": fake.word()
        },
        "name": fake.first_name(),
        "photoUrls": [fake.url()],
        "tags": [
            {
                "id": fake.random_int(min=1, max=100),
                "name": fake.word()
            }
        ],
        "status": status
    }

    r = _post(f"{BASE_URL}/pet", json=payload)
    response_data = r.json()  # Получаем тело ответа
    response_data['status_code'] = r.status_code  # Добавляем статус-код в словарь
    return response_data, payload

@desc('Генерация данных для обновления сущности pet')
def generate_updated_pet_payload(pet_id):
    return {
        'id': pet_id,
        'category.id': fake.random_int(min=1, max=100),
        'category.name': fake.word(),
        'name': fake.first_name(),
        'photoUrls': fake.url(),
        'tags.id': fake.random_int(min=1, max=100),
        'tags.name': fake.word(),
        'status': 'available'
    }

@desc('Создание и проверка сущность pet')
def test_create_pet(create_pet):
    response_data, payload = create_pet
    assert 200 == response_data['status_code']
    assert response_data['id'] == payload['id']
    assert response_data['name'] == payload['name']
    assert response_data['status'] == payload['status']

@desc('Создание и получение сущности pet')
def test_get_created_pet(create_pet):
    response_data, payload = create_pet
    get_response_data = _get(f"{BASE_URL}/pet/{response_data['id']}").json()
    assert get_response_data['id'] == payload['id']
    assert get_response_data['name'] == payload['name']
    assert get_response_data['status'] == payload['status']

@desc('Обновить сущность pet')
def test_update_pet(create_pet):
    response_data, payload = create_pet
    updated_payload = generate_updated_pet_payload(response_data['id'])

    r = _post(f"{BASE_URL}/pet/{response_data['id']}", data=updated_payload)
    assert 200 == r.status_code

    r = _get(f"{BASE_URL}/pet/{r.json().get('message')}")
    assert 200 == r.status_code

@desc('Удалить сущность pet')
def test_delete_pet():
    # Получить доступных питомцев
    r = _get(f'{BASE_URL}/pet/findByStatus?status=available')
    assert 200 == r.status_code

    pets = r.json()
    random_pet_id = fake.random_element(pets)['id']

    # Удалить выбранного питомца
    r = _delete(f'{BASE_URL}/pet/{random_pet_id}')
    assert 200 == r.status_code

    # Проверить, что питомца больше нет
    r = _get(f'{BASE_URL}/pet/{random_pet_id}')
    assert 404 == r.status_code
