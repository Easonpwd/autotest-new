import allure
import pytest


@pytest.fixture(autouse=True)
def add_rest_qc_marker(request):
    request.node.add_marker(allure.suite('xxx'))
    request.node.add_marker(pytest.mark.xxx)


@pytest.fixture()
def goto_rest_qc_page(goto_rest_subjects_page):
    page = goto_rest_subjects_page

    with allure.step('Step 4:xxx'):
        page.click_by_text("xxx")

    yield page
