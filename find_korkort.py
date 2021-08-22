import smtplib
from datetime import datetime
import ssl
import time

from pydantic import BaseSettings, SecretStr, Field
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class Config(BaseSettings):
    GMAIL_USERNAME: str
    GMAIL_PASSWORD: SecretStr
    SEND_EMAIL_TO: str = Field(..., min_length=3)


def there_any_free_times(driver, url) -> bool:
    driver.get(url)

    # "välj prov" -> select "körprov"
    valj_prov_select = driver.find_element_by_id("examination-type-select")
    valj_prov_select.send_keys("körpr")  # körprov

    # "Var vill du göra provet?" -> sollentuna
    time.sleep(0.5)
    var_gora_provet = driver.find_element_by_id("id-control-searchText-1-1")
    var_gora_provet.click()
    for _ in range(20):
        var_gora_provet.send_keys(Keys.BACKSPACE)
        var_gora_provet.send_keys(Keys.DELETE)

    time.sleep(0.2)
    var_gora_provet.send_keys("Sollentuna")
    # var_gora_provet.send_keys("Uppsala")

    var_gora_provet.send_keys(Keys.ENTER)
    time.sleep(0.2)

    # "Vill du hyra bil av trafikverket?" -> "ja, manuell"
    hyra_bil_select = driver.find_element_by_id("vehicle-select")
    hyra_bil_select.send_keys("ja, ma")  # "ja, manuell"

    # Once we've selected it, there's a spinner.
    # We don't know when it's done, so let's just wait eight seconds and hope
    # that it's done...
    time.sleep(8)

    date_strings = sorted([
        el.text
        for el in driver.find_elements_by_xpath("//strong")
    ])

    any_free_times: bool = any(
        date_string.startswith("2021-08") or date_string.startswith("2021-09")
        for date_string in date_strings
    )
    if date_strings:
        print(f"  Earliest time found: {date_strings[0]}")
    else:
        print("  no free times")

    return any_free_times


def send_email(config: Config, url: str) -> None:
    print(f"Sending email to {config.SEND_EMAIL_TO}...")
    port = 465  # SSL port
    context = ssl.create_default_context()
    sender_email = f"{config.GMAIL_USERNAME}@gmail.com"
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(
            sender_email,
            config.GMAIL_PASSWORD.get_secret_value(),
        )

        message = f"""\
Subject: Korkortstider finns tillgangliga!

korkortsprovfinder@gmail.com har hittat lediga korkortstider.
Lank till bokning: {url}"""

        server.sendmail(
            sender_email,
            config.SEND_EMAIL_TO,
            message,
        )
        print(f"Sent email to {config.SEND_EMAIL_TO}")


if __name__ == "__main__":
    config = Config(_env_file=".env")

    driver = webdriver.Chrome('./chromedriver')

    # When asking to get elements, if they don't exist, try for up to 5 seconds
    driver.implicitly_wait(5)

    url = "https://fp.trafikverket.se/Boka/#/search/xYIIyyxLgcLAlA/5/0/0/0"

    while True:
        try:
            print(datetime.now().astimezone().strftime("%y%m%d %H:%M"))
            if there_any_free_times(driver, url):
                print("Det FINNS lediga tider!!111 boka!")

                send_email(config, url)

            else:
                print("Inga lediga tider!")

            time.sleep(20)
        except Exception as e:
            print("Got an exception:", e)
