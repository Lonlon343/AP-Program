import pytest
import requests
from faker import Faker

fake = Faker()


BASE_URL = "http://127.0.0.1:8000/"

def test_read_root():
    """Test the root endpoint for greeting message"""

    #Make a GET request to the root endpoint
    response = requests.get(BASE_URL)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response JSON contains the expected greeting message
    data = response.json()
    assert "message" in data
    assert data["message"] == "Hello World!"

def test_404_error():
    """Test that accessing a non-existent endpoint returns a 404 error"""

    # Make a GET request to a non-existent endpoint
    response = requests.get(BASE_URL + "non-existent-endpoint") #non-existent endpoint to trigger 404 error

    # Assert that the response status code is 404 (Not Found)
    assert response.status_code == 404

def test_greetings():
    """Test the personalized greeting endpoint"""

for _ in range(10):
     # Run the test multiple times with different random names
    # Define a name to test with
    name = fake.first_name() # Generate a random first name using Faker

    # Make a GET request to the personalized greeting endpoint
    response = requests.get(f"{BASE_URL}greetings/{name}")

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response JSON contains the expected personalized greeting message
    data = response.json()
    assert "message" in data
    assert data["message"] == f"Hello {name}!"


def test_is_adult():
    """Test the is-adult endpoint with different ages"""

    for age in range(0,40): # Test with edge cases (0 and 40) to ensure correct behavior at boundaries
        
       
        adult = age >= 18
        response = requests.get(f"{BASE_URL}is-adult/{age}")
        assert response.status_code == 200
        data = response.json()
        

        for key in ["is_adult","can_vote","can_drive"]:
            assert data[key] == adult
        assert data["age"] == age


def test_is_adult_negative_age():
    """Test if adult is not negative"""

    for age in range(-20,0): # Test with edge cases (0 and 40) to ensure correct behavior at boundaries
        
       
        response = requests.get(f"{BASE_URL}is-adult/{age}")
        assert response.status_code == 400


