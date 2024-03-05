import os
from pathlib import Path

import allure
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from core.exception import GotoTimeOut
from tools.data_class import Position


class BasePage:
    """
    页面原子操作封装
    """

    def __init__(self, page: Page):
        self.__page = page
        self.__image_dir = None
        self.__case_path = None

    def set_image_dir(self, image_dir):
        self.__image_dir,self.__case_path = image_dir
        if not Path(self.__image_dir):
            os.makedirs(self.__image_dir)

    def get_image_dir(self):
        return self.__image_dir

    def get_running_case_path(self):
        return self.__case_path

    @property
    def page(self):
        return self.__page

    @property
    def get_url(self):
        return self.__page.url

    def locator(self, selector, **kwargs):
        return self.__page.locator(selector=selector, **kwargs)

    def locators(self, selector, which=0, **kwargs):
        """定位可能事多个结果时，使用该方法指定第几个匹配的元素"""
        return self.__page.locator(selector=f"{selector} >> nth={which}", **kwargs)

    @allure.step('goto - {url}')
    def goto(self, url):
        try:
            self.__page.goto(url)
        except PlaywrightTimeoutError:
            raise GotoTimeOut("页面打开 Timeout")
        return self

    @allure.step('Click locator - {locator}')
    def click(self, locator: str):
        """点击"""
        try:
            self.__page.click(locator)
        except PlaywrightTimeoutError:
            raise TimeoutError("click time out")
        return self

    @allure.step('Check checkbox locator - {locator}')
    def check(self, locator: str):
        """选择"""
        self.__page.check(locator)
        return self

    @allure.step('Uncheck checkbox locator - {locator}')
    def uncheck(self, locator: str):
        """取消选择"""
        self.__page.uncheck(locator)
        return self

    @allure.step('Hover locator - {locator}')
    def hover(self, locator: str):
        self.__page.hover(locator)
        return self

    @allure.step('Type text - {text} into locator - {locator}')
    def type(self, locator: str, text: str):
        self.click(locator)
        self.__page.fill(locator, text)

    @allure.step('Select option - {option} in locator - {locator}')
    def select_option(self, locator: str, option: str):
        self.__page.select_option(locator, option)

    @allure.step('fill text - {value} into locator - {locator}')
    def fill(self, locator, value):
        """
        先点击再再输入，fill适用于 input textarea 和 contenteditable元素
        value为空时，清楚输入框
        :param locator: 定位器
        :param value: 输入值
        :return: None
        """
        self.__page.click(locator)
        self.__page.locator(selector=locator).fill(value)

    @allure.step('Is element - {locator} hidden')
    def is_element_hidden(self, locator: str):
        """
        等待元素不可见
        """
        try:
            self.__page.wait_for_selector(locator)
            self.__page.wait_for_selector(locator, state='hidden')
        except PlaywrightTimeoutError as e:
            allure.attach(self.page.screenshot(path='loading_fail.png', full_page=True), "等待超时截图",
                          allure.attachment_type.PNG)
            raise TimeoutError("等待loading消失超时")

    @allure.step("点击 - {text} 文字")
    def click_by_text(self, text):
        self.__page.click(f"'{text}'")
        return self

    @allure.step("获取标签属性")
    def get_attribute(self, locator: str, name: str):
        return self.__page.get_attribute(locator, name)

    @allure.step("鼠标拖拽")
    def drag_and_drop(self, start: Position, finish: Position):
        """
        拖动脑图
        :param start: 起始位置
        :param finish: 结束位置
        :return:
        """
        self.__page.mouse.move(start.x, start.y)
        self.__page.mouse.down()
        self.__page.mouse.move(finish.x, finish.y, steps=2)
        self.__page.mouse.up()

    @allure.step("获取文本")
    def get_text(self, locator):
        """
        获取元素文本
        :param locator: 定位器
        :return: 指定元素的text/value
        """
        return self.__page.inner_text(locator) if self.__page.inner_text(locator) else self.__page.input_value(locator)
