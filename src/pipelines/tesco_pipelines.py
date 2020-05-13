import json
from datetime import datetime


# Tesco Pipeline
class TescoPipeline:

    def open_spider(self, spider):
        self.file = open(f'tesco-{datetime.now()}.json', 'w')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()
