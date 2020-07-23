import json
import datetime
import decimal

class ComplexEncode(json.JSONEncoder):
    def default(self, obj):                 # pylint: disable=E0202
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)

def callJson(data=None):
    if data:
        data = json.dumps(data, ensure_ascii=False, 
                                sort_keys=True, 
                                indent=4,
                                cls=ComplexEncode)
    return data