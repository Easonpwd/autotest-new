"""
# 自定义异常类 #
"""


class GotoTimeOut(Exception):
    """
    打开页面超时
    """

    def __init__(self, message):
        self.message = message
