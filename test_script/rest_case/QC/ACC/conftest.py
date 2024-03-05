import allure
import pytest

from po.page.QC_page import QCPage


@pytest.fixture(autouse=True)
def add_rest_qc_acc_marker(request):
    request.node.add_marker(allure.sub_suite('xxx'))
    request.node.add_marker(pytest.mark.xxx)


@pytest.fixture()
def goto_rest_qc_acc_page(goto_rest_qc_page):
    page = goto_rest_qc_page

    with allure.step('Step 5：xxx'):
        page.click_by_text("xxx")

    yield QCPage(page.page)
