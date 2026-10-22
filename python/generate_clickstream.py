import requests
from bs4 import BeautifulSoup
import random
import oracledb
import time
from datetime import datetime, timedelta
import uuid
from urllib.parse import urljoin
from tqdm import tqdm


def get_random_link(url, click_probability=1.0, visited=[], session_data=[], session_id=None):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except Exception as e:
        print(f"Error: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    # Collect active links, excluding "#" links and footer links
    if soup.select("a[href]"):
        for a in soup.select("a[href]"):
            if a.get("href") != "#":
                if a.find_parent("footer"): continue  # Skip links inside the footer
                link = urljoin(url, str(a.get("href")))
                # Append product_id to cart page URLs
                if "/cart/" in str(a.get("href")):
                    link += "product_id=" + str(a.get("data-product-id"))
            links.append(link)
        # Exclude the current page from the list
        links = [link for link in links if link != url]
    else:
        return

    # Add the current URL to the list of visited pages
    visited.append(url)

    # Randomly select the next URL
    next_url = random.choice(links)

    time.sleep(0.01)

    # Determine whether a click occurs based on the specified probability
    if random.random() < click_probability:
        # Generate the click timestamp
        if session_data:
            timestamp = datetime.strptime(session_data[-1]["timestamp"], "%Y-%m-%d %H:%M:%S")
        else:
            # Generate the initial timestamp
            timestamp = datetime.strptime("2025-01-01 12:00:00", "%Y-%m-%d %H:%M:%S") \
                        + timedelta(days=random.randint(0, 200)) \
                        + timedelta(hours=random.randint(0, 23)) \
                        + timedelta(minutes=random.randint(0, 59)) \
                        + timedelta(seconds=random.randint(0, 59))

        # Add random time delays
        if random.random() < 0.1:
            timestamp += timedelta(hours=random.randint(0, 23))
        if random.random() < 0.5:
            timestamp += timedelta(minutes=random.randint(0, 10))
        if random.random() < 0.7:
            timestamp += timedelta(seconds=random.randint(0, 59))

        # Check whether the timestamp falls within nighttime hours (00:00–06:00)
        if 0 <= timestamp.hour <= 6:
            if random.random() < 0.95:
                return

        # Format URLs as short paths for easier readability
        url_to_print = url.replace("http://127.0.0.1:8000/", "/") if url.startswith("http://127.0.0.1:8000/") else url
        next_url_to_print = next_url.replace("http://127.0.0.1:8000/", "/") if next_url.startswith("http://127.0.0.1:8000/") else next_url

        # Add the click record to session_data
        session_data.append({
            "timestamp": datetime.strftime(timestamp, '%Y-%m-%d %H:%M:%S'),
            "source_url": url_to_print,
            "target_url": next_url_to_print,
            "session_id": session_id
        })

        # Recursively navigate to the next URL
        get_random_link(next_url if '/cart/' not in next_url else url, random.uniform(0.85, 0.95), visited, session_data, session_id)

    return session_data


def send_click(settings, data, max_retries=5, delay=10):
    attempt = 0
    while attempt < max_retries:
        try:
            with oracledb.connect(**settings) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO CLICKS (CLICK_TIMESTAMP, SOURCE_URL, TARGET_URL, SESSION_ID)
                        VALUES (
                            TO_TIMESTAMP(:timestamp, 'YYYY-MM-DD HH24:MI:SS'),
                            :source_url,
                            :target_url,
                            :session_id
                        )
                        """,
                        data
                    )
                    connection.commit()
            return
        except oracledb.Error as error:
            attempt += 1
            print(f"Error connecting to Oracle (attempt {attempt}/{max_retries}):", error)
            if attempt < max_retries:
                time.sleep(delay)
            else:
                print("Maximum number of attempts reached. Data was not sent.")


if __name__ == "__main__":
    settings = {
        "user": "MY_SCHEMA",
        "password": "xxxxx",
        "dsn": "xxxxx_high",
        "config_dir": "xxxxx\\wallet_folder",
        "wallet_location": "xxxxx\\wallet_folder",
        "wallet_password": "xxxxx",
    }

    SITE_URL = "http://127.0.0.1:8000/"
    try:
        response = requests.get(SITE_URL)
        if not response.ok:
            raise requests.exceptions.RequestException
        else:
            for i in tqdm(range(200)):
                click_probability = random.uniform(0.85, 0.95)
                session_id = str(uuid.uuid4().hex)
                session_data = get_random_link(SITE_URL, click_probability=click_probability, visited=[], session_data=[], session_id=session_id)
                if session_data:
                    for click_data in session_data:
                        send_click(settings, click_data)
    except requests.exceptions.RequestException:
        print("Site is not available")
    input('Press Enter...')