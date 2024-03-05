from po.lcos.base_locs import BaseLocs


class LeftMenu:
    """
    页面左侧创建项目菜单
    """
    创建项目 = 'span:text("创建项目")'
    选择项目 = lambda name: f'span:has-text("{name}")'  # #projectListId >> text=Rest20201029
    # Subjects = '#projectListId >> div:has-text=用户'
    # 选择用户 = lambda name: f'button:has-text(\"{name}\")'  # #projectListId >> text=Rest20201029


class Main(BaseLocs):
    """
    页面主功能区
    """
    选择用户 = lambda name: f'button:has-text(\"{name}\")'  # #projectListId >> text=Rest20201029
    选择处理结果 = lambda name: f'.job-card-wrap:has-text("处理完成")  div:has-text("{name}")'
    关闭按钮 = '[aria-label="Close"]'  # 四图快照的关闭按钮
