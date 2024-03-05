import time

import allure
from allure_commons.types import AttachmentType
from loguru import logger

from conf.Research import BaseConfig
from core.allure_report import report_add_png, report_add_text
from core.image import img_base64_to_bytes, get_image_by_url, diff_image, base64_to_image, get_canvas_base64, \
    set_hash_to_image_name, md5_, auto_fill_image_hash_to_scrip, contrast
from po.lcos.base_locs import BaseLocs
from po.page.base_page import BasePage


class ResearchPage(BasePage):
    """
    通用操作封装
    """

    @staticmethod
    def assert_false(img_base64, image_hash, reduced_value):
        logger.error(image_hash)
        allure.attach(img_base64_to_bytes(img_base64), name='FailureScreenshot', attachment_type=AttachmentType.PNG)
        allure.attach(img_base64, name='image_base64', attachment_type=AttachmentType.TEXT)
        assert False, f"reduced_value: {reduced_value} != {image_hash}"

    @allure.step('等待 loading结束')
    def loading(self):
        self.is_element_hidden(BaseLocs.Loading)
        return self

    @allure.step
    def 对比图片(self, reduced_value, number=0):
        temp_image = f'{self.get_image_dir()}\\{reduced_value}_temp.png'  # 每次执行获取的脑图
        local_image = f'{self.get_image_dir()}\\{reduced_value}.png'  # 本地对比图

        time_sleep = 0.5

        for i in range(2):
            time.sleep(time_sleep)
            logger.debug(f'休息 {time_sleep} 秒')
            time_sleep = time_sleep + 2
            hash_str, img_base64 = get_canvas_base64(self.page, number)
            # 如果是debug模式且图片名称传空，新生成图片的名称直接用它的md5,并且把md5按顺序填写到代码中
            if len(reduced_value.strip()) == 0 and BaseConfig.auto_fill:
                temp_image, local_image = set_hash_to_image_name(hash_str, self.get_image_dir())
                auto_fill_image_hash_to_scrip(self.get_running_case_path(), hash_str)
            base64_to_image(temp_image, img_base64)
            if diff_image(local_image, temp_image):
                break
        else:
            report_add_png(temp_image, name='失败图')
            report_add_png(local_image, name='原始图')
            contrast_path = contrast(local_image, temp_image)
            report_add_png(contrast_path, name='对比图')
            assert False, '图片对比失败'
        return self

    @allure.step
    def 根据属性对比脑图(self, reduced_value, attr_value):
        temp_image = f'{self.get_image_dir()}\\{reduced_value}_temp.png'
        local_image = f'{self.get_image_dir()}\\{reduced_value}.png'

        attr_value = self.get_attribute(attr_value, 'src')
        hash_str = md5_(attr_value)
        # 如果是debug模式且图片名称传空，新生成图片的名称直接用md5,并且把md5按顺序填写到代码中
        if len(reduced_value.strip()) == 0 and BaseConfig.auto_fill:
            temp_image, local_image = set_hash_to_image_name(hash_str, self.get_image_dir())
            auto_fill_image_hash_to_scrip(self.get_running_case_path(), hash_str)
        if attr_value.startswith('https'):  # 图片是从服务端获取的
            get_image_by_url(temp_image, attr_value)
        elif attr_value.startswith('data:image/png;base64'):
            base64_to_image(temp_image, attr_value)

        else:
            report_add_text(attr_value, name='attribute_value')
            raise Exception("根据属性获取标签内容出错")

        if diff_image(local_image, temp_image) is False:
            report_add_png(temp_image, name='失败图')
            report_add_png(local_image, name='原始图')
            contrast_path = contrast(local_image, temp_image)
            report_add_png(contrast_path, name='对比图')
            assert False, '图片对比失败'
        return self

    @allure.step
    def 对比四图快照(self, reduced_value):
        """获取4图快照图片md5值,进行对比"""
        logger.info("获取四图快照：")
        self.根据属性对比脑图(reduced_value, 'img[alt="img"]')

    @allure.step
    def 对比8图快照(self, reduced_value0, reduced_value1):
        """分别获取个体、组水平4图快照图片md5值,进行对比"""
        logger.info("获取8图快照：")
        self.根据属性对比脑图(reduced_value0, "//div[contains(@class, 'left_container')]//img")
        self.根据属性对比脑图(reduced_value1, "//div[contains(@class, 'right_container')]//img")

    @allure.step
    def 对比切片图(self, reduced_value):
        """容积视图下，冠状位，矢状位，轴状位的弹窗图"""
        self.根据属性对比脑图(reduced_value, '//*[@id="slice-img"]/img')

    @allure.step
    def 全屏截图对比(self, reduced_value):
        """
        不需要条件的图片对比
        :param reduced_value: 图片名
        """
        temp_image = f'{self.get_image_dir()}\\{reduced_value}_temp.png'
        local_image = f'{self.get_image_dir()}\\{reduced_value}.png'
        self.page.screenshot(path=temp_image, full_page=True)
        if diff_image(local_image, temp_image) is False:
            report_add_png(temp_image, name='失败图')
            report_add_png(local_image, name='原始图')
            contrast_path = contrast(local_image, temp_image)
            report_add_png(contrast_path, name='对比图')
            assert False, '图片对比失败'
        return self

    @allure.step
    def check_is_loading(self, locator: str):
        """
        先判断是否已经勾选了，如果没有，勾选后，需要等待更新
        """
        if self.locator(locator).is_checked() is False:
            self.click(locator).loading()
        return self