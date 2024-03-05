import base64
from pathlib import Path

import allure
import pytest


def pytest_collection_modifyitems(config, items):
    nodeId = Path(__file__).parent.relative_to(config.rootpath).as_posix()
    for item in items:
        if nodeId in item.nodeid:
            item.add_marker(pytest.mark.Rest)


@pytest.fixture(autouse=True)
def add_rest_marker(request):
    """
    自动添加Rest标签
    :param request:
    :return:
    """
    request.node.add_marker(allure.parent_suite('Rest'))


@pytest.fixture()
def goto_rest_subjects_page(research_login):
    """
    进入结构页面
    """
    with allure.step('Step 1: xxx'):
        page = research_login

    with allure.step('Step 2: xxx'):
        page.选择项目('xxx').选择用户('xxx')

    with allure.step('Step 3：xxx'):
        try:
            page.选择处理结果('REST_AutoTest.zip').收起侧边栏()
        except Exception:
            img_base64 = base64.b64encode(page.screenshot(path="screenshot.png", full_page=True)).decode()
            allure.attach.file(img_base64, name='登录失败', attachment_type=allure.attachment_type.PNG)

    yield page
