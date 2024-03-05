# -*- coding: utf-8 -*-
from functools import wraps
from types import FunctionType

import allure
from allure_commons import plugin_manager
from allure_commons._allure import StepContext
from allure_commons.utils import func_parameters, represent
from loguru import logger


def step(title):
    """
    测试报告步骤
    使用时,如果没有定义title,则title是被装饰的方法
    如果title有值,则为字符串
    :param title: 步骤名称
    :return: MyStepContext
    """
    if callable(title):  # 装饰器方式
        return MyStepContext(title.__name__, {})(title)
    else:  # with step 方式使用
        return MyStepContext(title, {})


class MyStepContext(StepContext):
    """
    重写allure的StepContext方法
    如果是with 语句进来的,直接走__enter__方法,输出title
    装饰器时,如果没有传title与方法名一致,
    """

    def __enter__(self):
        logger.info(self.title)
        plugin_manager.hook.start_step(uuid=self.uuid, title=self.title, params=self.params)

    def __call__(self, func):
        @wraps(func)
        def impl(*a, **kw):
            if self.title != func.__name__:  # 如果不相等,说明title是传进来的,将title输出
                logger.info(self.title)
            params = func_parameters(func, *a, **kw)
            args = list(map(lambda x: represent(x), a))
            with StepContext(self.title.format(*args, **params), params):
                logger.info(func.__qualname__)  # 打印执行的类及方法
                # LOG.info(format_function_doc(func))  # 打印类的注释文档
                return func(*a, **kw)

        return impl


def format_function_doc(func):
    """处理方法注释"""
    if not isinstance(func, FunctionType):  # 如果在装饰器中,此判断没用
        raise TypeError('this param type is not function')
    if func.__doc__:
        # 只取第一行
        return func.__doc__.strip().split('\n')[0]
    else:
        return 'This is function is not doc'


def report_add_png(path, name):
    """添加指定图片到报告"""
    try:

        with open(path, mode='rb') as f:
            file = f.read()
            allure.attach(file, name=name, attachment_type=allure.attachment_type.PNG)
    except FileNotFoundError as e:
        raise Exception("对比图片可能不存在")


def report_add_text(text, name):
    """添加文本到报告"""
    allure.attach(text, name=name, attachment_type=allure.attachment_type.TEXT)
