import allure

from conf.Research import User
from core.allure_report import step

login_user = User


@allure.title('质量控制')
def test_rest_qc_acc(goto_rest_qc_acc_page, img_path):
    page = goto_rest_qc_acc_page
    page.set_image_dir(img_path)

    with step('Step 1: 对比图片'):
        reduced_value = '8487d4b7571daa923da6b6f8e72777ec'
        page.对比图片(reduced_value)
