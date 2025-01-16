import requests
import openpyxl
from getpass import getpass

# Static server details (hidden from user)
SERVER_URL = "https://example.com/api"
LOGIN_ENDPOINT = f"{SERVER_URL}/login"
BATCHES_ENDPOINT = f"{SERVER_URL}/batches"
LOCATION_ENDPOINT = f"{SERVER_URL}/submit-location"

def authenticate_user():
    print("\n--- User Authentication ---")
    username = input("Enter your username: ")
    password = getpass("Enter your password: ")  # Hides password input

    response = requests.post(LOGIN_ENDPOINT, json={"username": username, "password": password})
    if response.status_code == 200:
        print("Authentication successful!")
        return response.json().get("token")  # Assumes server returns a token
    else:
        print(f"Authentication failed: {response.json().get('error', 'Unknown error')}")
        exit()

def fetch_batches(token):
    print("\n--- Fetching Batches ---")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(BATCHES_ENDPOINT, headers=headers)
    if response.status_code == 200:
        batches = response.json()
        print("Available Batches:")
        for idx, batch in enumerate(batches, start=1):
            print(f"{idx}. {batch['name']}")
        return batches
    else:
        print("Error fetching batches.")
        exit()

def select_batch(batches):
    choice = int(input("\nSelect a batch by entering its number: "))
    if 1 <= choice <= len(batches):
        return batches[choice - 1]
    else:
        print("Invalid choice.")
        exit()

def get_location_from_excel():
    print("\n--- Reading Locations from Excel ---")
    excel_path = input("Enter the path to the Excel file: ")
    try:
        workbook = openpyxl.load_workbook(excel_path)
        sheet = workbook.active
        locations = [row[0].value for row in sheet.iter_rows(min_row=2, max_col=1)]
        print(f"Found {len(locations)} locations in the file.")
        return locations
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        exit()

def submit_location(token, batch_id, locations):
    print("\n--- Submitting Locations ---")
    headers = {"Authorization": f"Bearer {token}"}
    data = {"batch_id": batch_id, "locations": locations}
    response = requests.post(LOCATION_ENDPOINT, json=data, headers=headers)
    if response.status_code == 200:
        print("Locations submitted successfully!")
    else:
        print(f"Error submitting locations: {response.text}")

def main():
    token = authenticate_user()
    batches = fetch_batches(token)
    selected_batch = select_batch(batches)
    print(f"Selected Batch: {selected_batch['name']}")
    locations = get_location_from_excel()
    submit_location(token, selected_batch["id"], locations)

if __name__ == "__main__":
    main()