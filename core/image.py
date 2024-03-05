import base64
import hashlib
import os
import re
import shutil
import urllib.request
from pathlib import Path
import numpy as np
import cv2
from image_similarity_measures.quality_metrics import ssim
from loguru import logger

from conf.Research import BaseConfig
from core.allure_report import report_add_text


def get_canvas_base64(page, number):
    """
    获取指定的canvas图片。比如容积视图是3个图片
    :arg number: 第几个canvas
    """
    js_str = f'() => document.querySelectorAll("canvas")[{number}].toDataURL()'
    img_base64 = page.evaluate(js_str)
    hash_str = md5_(img_base64)
    # logger.debug(f'哈希值：{hash_str}')
    return hash_str, img_base64


def md5_(s: str):
    """
    获取md5值
    """
    return hashlib.md5(s.encode()).hexdigest()


def get_image_by_url(temp_image, url):
    """
    当获取到的是url地址时,讲图片地址临时生成图片保存到本地,然后计算base64
    """
    if not Path(temp_image).parent.exists():
        os.makedirs(Path(temp_image).parent)
    urllib.request.urlretrieve(url, filename=temp_image)
    urllib.request.urlcleanup()


def img_base64_to_bytes(img_base64: str):
    """图片的base64转字节"""
    img_base64 = img_base64.removeprefix("data:image/png;base64,")
    img_base64 = img_base64.removeprefix("data:image/jpg;base64,")
    # 打印当前图片的md5，方便获取图片名称
    # logger.debug(md5_(img_base64))
    return base64.b64decode(img_base64)


def diff_image(local_image, temp_image):
    ssim_value = 0
    cut_image(temp_image)
    if os.path.exists(local_image):  # 原始图存在,进行比对,如果不存在,返回失败
        image1 = cv2.imread(local_image)
        image2 = cv2.imread(temp_image)
        try:
            ssim_value = ssim(image1, image2)
        except AssertionError as e:
            # 更新图片模式，如果图片大小不一样，则越过报错，由后面逻辑使用当前截图作为本地图片
            if not BaseConfig.update_image:
                raise Exception(f"形状不一致:{e}")
        logger.debug(f'ssim: {ssim_value}')
        if ssim_value > 0.999:
            return True
        logger.warning(ssim_value)
        report_add_text(str(ssim_value), name='误差值非1')

        # 更新图片模式，如果图片对比失败，删除老图
        if BaseConfig.update_image and Path(local_image).exists():
            logger.debug(f'删除文件{local_image}')
            Path(local_image).unlink()
            shutil.copy(temp_image, local_image)
            return True
        return False
    elif BaseConfig.update_image or BaseConfig.auto_fill:
        # 更新当前截图作为本地图片
        shutil.copy(temp_image, local_image)
        return True
    else:
        return False


def base64_to_image(p, s):
    if not Path(p).parent.exists():
        os.makedirs(Path(p).parent)
    with open(p, 'wb') as f:
        f.write(img_base64_to_bytes(s))


def auto_fill_image_hash_to_scrip(case_path, image_hash):
    """把图片的md5写入正在执行的case脚本中"""
    lines = []
    # 控制符，每次调用只填写一张图片hash，按循序填写
    tag = True
    with open(case_path, "r+", encoding='UTF-8') as f:
        for line in f.readlines():
            tab = re.search("对比(.*?)\(", line) or re.search("reduced_value(.*?)=(\s*)", line)
            if tab is not None and tag:
                pos = tab.end()
                if line[pos - 1:pos + 3].replace("'", '"') == '("")' or line[pos - 1:pos + 3].replace("'", '"') == '("",' or line[pos:pos + 3].replace("'", '"').strip() == '""':
                    line = line[:pos + 1] + image_hash + line[pos + 1:]
                    tag = False
            lines.append(line)
    with open(case_path, "w+", encoding='UTF-8') as fs:
        fs.truncate()
        for line in lines:
            fs.write(f"{line}")


def set_hash_to_image_name(hash_img, img_dir):
    """
    用图片的md5作为图片的名称
    """
    temp_image = f'{img_dir}\\{hash_img}_temp.png'
    local_image = f'{img_dir}\\{hash_img}.png'
    return temp_image, local_image


def cut_image(image_path: str):
    """
    根据脑图大小边缘矩形框裁剪图片
    :param image_path: 图片
    :return: 裁剪后的图片
    """
    image = cv2.imread(image_path)  # 读取图片
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 转灰度图

    # 用Sobel算子计算x，y方向上的梯度，之后在x方向上减去y方向上的梯度，通过这个减法，我们留下具有高水平梯度和低垂直梯度的图像区域。
    gradX = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=1, dy=0)
    gradY = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=0, dy=1)
    gradient = cv2.subtract(gradX, gradY)  # 计算两个数组的差
    gradient = cv2.convertScaleAbs(gradient)  # 转回uint8

    # 进行均值滤波 参数说明：img表示输入的图片， (3, 3) 表示进行均值滤波的方框大小
    blurred = cv2.blur(gradient, (9, 9))

    # 轮廓检测
    (cnts, _) = cv2.findContours(blurred.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 所有轮廓的最大值和最小值
    x_list = []
    y_list = []
    # 循环遍历所有轮廓
    for i in range(len(cnts)):
        # 计算最大轮廓的旋转边界框
        rect = cv2.minAreaRect(cnts[i])
        # box是矩形轮廓四个点的坐标，并向上取整
        box = np.int0(np.ceil(cv2.boxPoints(rect)))
        Xs = [i[0] for i in box]
        Ys = [i[1] for i in box]
        x_list.append(min(Xs))
        x_list.append(max(Xs))
        y_list.append(min(Ys))
        y_list.append(max(Ys))
        # 解除下方禁用查看矩形轮廓
        # cv2.drawContours(image, [box], -1, (0, 255, 0), 3)
        # cv2.imwrite(image_path+"contoursImage.png", image)

    # 取所有矩形轮廓的最大值和最小值作为裁剪的边界
    x1 = min(x_list)
    x2 = max(x_list)
    y1 = min(y_list)
    y2 = max(y_list)

    # 为了规避脑子过大导致坐标为负数的情况
    if x1 < 0:
        x1 = 0
    if y1 < 0:
        y1 = 0
    crop_image = image[y1:y2, x1:x2]
    cv2.imwrite(image_path, crop_image)
    return crop_image


def contrast(local_image, temp_image):
    """
    对比两张图片的区别
    :param local_image: 本地图片
    :param temp_image: 临时图片
    :return: 差异图片
    """
    # 读取两张图片
    img1 = cv2.imread(local_image)
    img2 = cv2.imread(temp_image)

    # 将两张图片转换为灰度图像
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # 计算两张图片的差异
    diff = cv2.absdiff(gray1, gray2)

    # 对差异图像进行二值化处理
    _, thresh = cv2.threshold(diff, 5, 255, cv2.THRESH_BINARY)

    # 找到差异图像中的轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 筛选轮廓，只保留面积大于100的轮廓
    for contour in contours:
        if cv2.contourArea(contour) > 100:
            # 在原始图像中标记出差异点的位置
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
    # 获取temp_image的文件名和文件路径
    filename = os.path.basename(temp_image)
    directory = os.path.dirname(temp_image)
    # 将文件名和文件路径组合成新的文件名
    new_path = os.path.join(directory, f"contrast_{filename}")
    cv2.imwrite(new_path, img2)
    return new_path
