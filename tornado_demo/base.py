import json
import datetime
import decimal

# 格式化时间
class ComplexEncode(json.JSONEncoder):
    def default(self, obj):                 # pylint: disable=E0202
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        # return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.date):
            # return obj.strftime('%Y-%m-%d')
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)