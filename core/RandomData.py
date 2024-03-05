from faker import Faker

faker = Faker(['en-US'])


class Random:
    @staticmethod
    def faker():
        return faker

    @staticmethod
    def random_number():
        """
        10位随机数
        :return:
        """
        return faker.numerify(text='%#########')

    @staticmethod
    def phone_number():
        """
        生成随机手机号
        """
        return Faker('zh_CN').phone_number()

    @staticmethod
    def name():
        return faker.name()

if __name__ == '__main__':
    print(Random.phone_number())
