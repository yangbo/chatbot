# 保存抓取数据到 sqlite 数据库的相关代码
# 创建时间：2019-07-19

from orator import DatabaseManager, Schema, Model
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

config = {
    'sqlite': {
        'driver': 'sqlite',
        'database': dir_path + '/../../../../xie-zhi-chatbot-data/data/faq-v1-20190916.db',
        'log_queries': False
    }
}

db = DatabaseManager(config)
Model.set_connection_resolver(db)


class FaqFindlaw(Model):
    __fillable__ = ['question_title', 'question', 'question_time',
                    'answer_count', 'best_answer', 'other_answers', 'category',
                    'location', 'help_people_count', 'page_url']


def create_schema():
    """创建表结构
    sqlite 可以使用的字段类型请参考这里 http://www.sqlitetutorial.net/sqlite-data-types/
    """
    schema = Schema(db)
    if schema.has_table('faq_findlaws'):
        return
    with schema.create('faq_findlaws') as table:
        # 自增主键
        table.increments('id')
        # 问题标题
        table.text('question_title')
        # 问题正文
        table.text('question')
        # 提问时间
        table.datetime('question_time')
        # 回答数量
        table.small_integer('answer_count')
        # 最佳答案
        table.text('best_answer')
        # 其他答案，用 | 竖线分隔
        table.text('other_answers')
        # 问题类别，如：
        table.string('category')
        # 地点
        table.string('location')
        # 已经帮助多少人
        table.integer('help_people_count')
        # 页面地址
        table.string('page_url')
        # 创建时间和更新时间
        table.timestamps()


if __name__ == '__main__':
    n = 0
    for chunk in FaqFindlaw.chunk(100):
        for faq in chunk:
            print("问：%s\n答：%s" % (faq.question, faq.best_answer))
            n += 1
            if n == 500:
                exit(0)
