import requests
import json
import gspread
from google.oauth2.service_account import Credentials

# Function to scrape reviews and store in Google Sheets
def scrape_reviews():
    # API URL
    url = "https://www.justdial.com/api/getratings"

    # Headers
    headers = {
        "Host": "www.justdial.com",
        "Securitytoken": "2a282a2c2a2d292929282d2f292d",
        "Requesttime": "2024-25-11%2010%3A57%3A15%20AM",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36",
        "Content-Type": "application/json",
    }

    # Google Sheets setup
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    sheet_id = "1lOu_XSwUxzT9noKWq9RYlw3wbL7YjhJgFSQ-bgd2xj8"
    workbook = client.open_by_key(sheet_id)
    sheet = workbook.sheet1  # Assuming data goes into the first sheet

    # Initialize headers in the Google Sheet
    sheet.clear()  # Clear existing data
    sheet.append_row(["Reviewer Name", "Rating", "Review Text", "Profile Picture", "Sentiment", "Review URL"])

    page_number = 1
    reviews_fetched = 0

    while True:
        print(f"Fetching page {page_number}...")
        payload = {
            "docid": "044PXX44.XX44.170412085717.E3Q6",
            "gdocids": "044PXX44.XX44.181113125745.W3G2,044PXX44.XX44.170412085717.E3Q6",
            "np": page_number,
        }

        try:
            # Send the POST request
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code != 200:
                print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                break

            data = response.json()
            reviews = data.get("data", {}).get("rating", [])

            # Stop if no more reviews are found
            if not reviews:
                print("No more reviews found.")
                break

            # Process each review
            for review in reviews:
                reviewer_name = review.get("name", "No name")
                rating = review.get("rating", 0)
                review_text = review.get("rev", "No review text")
                profile_picture = review.get("dp", "No profile picture")
                sentiment = review.get("sentiment", "No sentiment")
                review_url = review.get("share_url", "No review URL")

                # Append review to Google Sheet
                sheet.append_row([reviewer_name, rating, review_text, profile_picture, sentiment, review_url])
                reviews_fetched += 1

            print(f"Fetched {len(reviews)} reviews from page {page_number}.")
            page_number += 1  # Move to the next page

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    print(f"Total reviews fetched and stored: {reviews_fetched}")

if __name__ == "__main__":
    scrape_reviews()
