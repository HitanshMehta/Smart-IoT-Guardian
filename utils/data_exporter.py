import json
import csv
from datetime import datetime

class DataExporter:
    @staticmethod
    def export_to_json(data, filename=None):
        if not filename:
            filename = f"iot_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return filename
    
    @staticmethod
    def export_to_csv(data, filename=None):
        if not filename:
            filename = f"iot_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if data:
            keys = data[0].keys()
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
        return filename