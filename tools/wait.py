# 轮询频率
import time

from loguru import logger

POLL_FREQUENCY = 1


class Wait:
    """
    动态等待
    """

    def __init__(self, timeout=15, poll_frequency=POLL_FREQUENCY, message=None):
        self._timeout = timeout
        self._poll = poll_frequency
        self.message = message
        if self._poll == 0:
            self._poll = POLL_FREQUENCY

    def 尝试打开四图快照(self, page, poll_frequency=3000):
        """
        尝试指定时间内打开四图快照，如果提示请稍后，则不断重试，直到超时
        """

        end_time = time.time() + self._timeout

        while True:
            try:
                page.click('span[role="button"]:has-text("4图快照")')
                logger.debug('点击4图快照')
                page.locator('id=rcDialogTitle0').wait_for(timeout=poll_frequency)  # 这里是毫秒
                logger.debug('等待dialog')
                return page
            except Exception:
                logger.warning("暂时没打开")

            time.sleep(self._poll)
            if time.time() > end_time:
                logger.info("点击4图快照，查看超时")
                raise TimeoutError('超时了')
