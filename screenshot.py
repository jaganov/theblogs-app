import os
from playwright.sync_api import sync_playwright

# URLs для публичных страниц
PUBLIC_PAGES = [
    ("index", "/"),
    ("search", "/search/?page=2"),
    ("authors_list", "/authors_list/"),
    ("privacy_policy", "/privacy_policy/"),
    ("terms_of_service", "/terms_of_service/"),
    ("contact", "/contact/"),
    ("post_detail", "/everything-you-need-to-know-about-data-science-tools-7169742a/"),  # замените slug на существующий
    ("register", "/account/register/"),
    ("login", "/account/login/"),
]

# URLs для страниц, требующих авторизации
PRIVATE_PAGES = [
    ("profile", "/account/profile/"),
    ("edit_profile", "/account/edit_profile/"),
    ("edit_post", "/account/edit_post/test-post/"),  # замените slug на существующий
    ("delete_post", "/account/delete_post/test-post/"),  # замените slug на существующий
    ("create_post", "/create_post/"),
]

# URLs для админки
ADMIN_PAGES = [
    ("admin_login", "/admin/login/"),
    ("admin_users", "/admin/account/customuser/"),
    ("admin_blogs", "/admin/blog/post/"),
    ("admin_blog_detail", "/admin/blog/post/1/change/"),  # замените id на существующий
]

BASE_URL = "http://localhost:80"
SCREENSHOTS_DIR = "screenshots"

# Данные для входа пользователя и админа
USER_CREDENTIALS = {"username": "testuser", "password": "testpass"}
ADMIN_CREDENTIALS = {"username": "admin", "password": "adminpass"}

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def take_screenshot(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
    page.screenshot(path=path, full_page=True)
    print(f"Saved {path}")

def main():
    ensure_dir(SCREENSHOTS_DIR)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Публичные страницы
        for name, url in PUBLIC_PAGES:
            page.goto(BASE_URL + url)
            page.wait_for_load_state("networkidle")
            take_screenshot(page, name)

        # Авторизация пользователя
        page.goto(BASE_URL + "/account/login/")
        page.fill('input[name="username"]', USER_CREDENTIALS["username"])
        page.fill('input[name="password"]', USER_CREDENTIALS["password"])
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Приватные страницы
        for name, url in PRIVATE_PAGES:
            page.goto(BASE_URL + url)
            page.wait_for_load_state("networkidle")
            take_screenshot(page, name)

        # Админка (новая сессия)
        admin_page = browser.new_page()
        admin_page.goto(BASE_URL + "/admin/login/")
        admin_page.fill('input[name="username"]', ADMIN_CREDENTIALS["username"])
        admin_page.fill('input[name="password"]', ADMIN_CREDENTIALS["password"])
        admin_page.click('input[type="submit"]')
        admin_page.wait_for_load_state("networkidle")
        for name, url in ADMIN_PAGES:
            admin_page.goto(BASE_URL + url)
            admin_page.wait_for_load_state("networkidle")
            take_screenshot(admin_page, name)

        browser.close()

if __name__ == "__main__":
    main() 