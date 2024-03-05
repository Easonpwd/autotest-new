import os.path

import allure

from po.page.main_page import MainPage
from po.page.operation import ResearchPage


class LoginPage(ResearchPage):
    """
    登录页面
    """

    @allure.step("通过用户名{email}，密码{password}登录")
    def login(self, email, password, path=None):
        """
        登录方法
        :param path: 缓存信息存放路径
        :param email: 用户名
        :param password: 密码
        :return: 主页面对象
        """
        self.page.fill(selector='id=email', value=email)
        self.page.fill(selector='id=password', value=password)
        with self.page.expect_navigation():
            self.page.locator("button:has-text(\"登录\")").click()

        if path:
            self.page.context.storage_state(path=os.path.join(path, f'{email}.json'))

        return MainPage(self.page)
