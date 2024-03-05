import os
import sys
from pathlib import Path
from typing import Any, Dict

import allure
import pytest
from filelock import FileLock
from loguru import logger
from playwright.sync_api import Page, sync_playwright

from conf.Research import Research, User
from core.RandomData import Random
from core.allure_report import report_add_png
from po.page.login_page import LoginPage


def pytest_addoption(parser):
    """
    pytest命令行参数
    """
    parser.addini("base_url", help="base url for the application under test.")

    parser.addini('headed', help='是否使用headless模式')

    parser.addini('PWDEBUG', help='是否开启pwdebug模式')


def pytest_configure(config):
    """
    pytest配置
    """
    # 获取命令行参数
    PWDEBUG = config.getini("PWDEBUG")
    if PWDEBUG.lower() == "true":
        os.environ["PWDEBUG"] = "1"
    else:
        os.environ.pop("PWDEBUG", None)


@pytest.fixture(scope="session")
def base_url(request):
    """Return a base URL"""
    config = request.config
    base_url = config.getoption("base_url") or config.getini("base_url")
    if base_url is not None:
        return base_url


@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig: Any) -> Dict:
    """
    返回浏览器参数
    """
    launch_options = {"headless": pytestconfig.getoption("--headed")}

    browser_channel_option = pytestconfig.getoption("--browser-channel") or 'chrome'
    if browser_channel_option:
        launch_options["channel"] = browser_channel_option
    slowmo_option = pytestconfig.getoption("--slowmo")
    if slowmo_option:
        launch_options["slow_mo"] = slowmo_option
    return launch_options


@pytest.fixture(scope="session")
def _tmp_path(tmp_path_factory, worker_id):
    """
    返回pytest临时目录
    """
    tmp_path = tmp_path_factory.getbasetemp() if worker_id == 'master' else tmp_path_factory.getbasetemp().parent
    logger.debug(f'当前临时目录：{tmp_path}, worker_id: {worker_id}')
    return tmp_path


@pytest.fixture(scope='session', autouse=True)
def _init_login_page(_tmp_path, worker_id, base_url):
    """
    分布式执行时，初始化登录信息并缓存到本地
    """
    tmp_path = _tmp_path
    if worker_id == "master":
        pass  # 未启用分布式执行，直接跳过
    else:
        logger.info(f'初始化登录操作 {worker_id}')
        for i in User:
            tmp_auth = tmp_path / f'{i}.json'
            with FileLock(str(tmp_auth) + '.lock'):
                if tmp_auth.exists() is False:
                    logger.info(f'{worker_id}  登录信息不存在，初始化登录信息')
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=True, channel='chrome')
                        page = browser.new_page()
                        LoginPage(page).goto(base_url + Research.URL).login(email=i, password='xxxx', path=tmp_path)
                        logger.info(f'{worker_id}  登录成功,关闭了浏览器：{i}')
                        browser.close()
                else:
                    logger.info(f'{worker_id}  登录信息已存在，不需要初始化用户：{i}')


@pytest.fixture()
def browser_context_args(browser_context_args, request, _tmp_path, base_url):
    """
    浏览器上下文参数
    """
    user = getattr(request.module, 'login_user', None)
    browser_context_args.setdefault('base_url', base_url)  # 设置base_url

    context_args = {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        }
    }

    tmp_auth = _tmp_path / f'{user}.json'
    if tmp_auth.exists():
        context_args.setdefault('storage_state', tmp_auth)
    return context_args


@pytest.fixture
def research_login(request, page, _tmp_path):
    """
    登录
    :return: 登录后的页面
    """
    page: Page = page
    tmp_path = _tmp_path
    user = getattr(request.module, 'login_user', None)  # 获取运行时用例的login_user变量
    login_page = LoginPage(page).goto(Research.URL)

    tmp_auth = tmp_path / f'{user}.json'
    if tmp_auth.exists() is False:
        login_page.login(email=user, password='xxx', path=tmp_path)
    try:
        page.locator('button[role="button"]:has-text("上传")').wait_for()
    except Exception:
        fail_png_file = os.path.join(tmp_path, f'{Random.random_number()}.png')
        page.screenshot(path=fail_png_file, full_page=True)
        allure.attach.file(fail_png_file, name='登录失败', attachment_type=allure.attachment_type.PNG)
        raise Exception("登录失败")

    yield MainPage(page)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    用例失败后自动截图
    """
    import os

    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page: Page = item.funcargs['page']
        tmp_dir = item.funcargs['_tmp_path']
        png_name = f"{os.path.join(tmp_dir, item.originalname)}.png"
        try:
            page.screenshot(path=png_name, full_page=True)
            report_add_png(path=png_name, name="失败截图")
        except Exception as e:
            logger.error('截图失败')


@pytest.fixture
def img_path(request, worker_id):
    case_dir = request.fspath.dirname  # 当前用例目录
    case_name = request.node.originalname  # 当前用例名称
    image_dir = os.path.join(case_dir, 'image', case_name)  # 用例截图的目录
    case_path = request.path  # 当前用例的文件路径
    yield image_dir, case_path
    # 用例执行完毕,删除临时脑图
    if Path(image_dir).exists():
        files = os.listdir(image_dir)
        for file in files:
            suffix = file.split('_')[-1]
            if suffix == 'temp.png':
                os.remove(os.path.join(image_dir, file))
