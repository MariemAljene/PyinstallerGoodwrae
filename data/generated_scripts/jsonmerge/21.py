import json
from collections import OrderedDict
from jsonmerge import Merger

schema = {
    "properties": {
        "property1": {
            "mergeStrategy": "objectMerge",
            "mergeOptions": {
                "override": True
            }
        },
        "property2": {
            "mergeStrategy": "objectMerge",
            "mergeOptions": {
                "strategy": "$patch"
            }
        },
        "property3": {
            "mergeStrategy": "arrayMergeById",
            "mergeOptions": {
                "idRef": "id"
            }
        }
    }
}

# Initialize JSON Merge object
merger = Merger(schema)

try:
    # Mock data and merging operations
    for i in range(50):
        # JSON objects
        base = OrderedDict([
            ("property1", {"id": i, "value": chr(i + 65)}),
            ("property2", {"id": i + 1, "value": chr(i + 66)}),
            ("property3", [{"id": i + 2, "value": chr(i + 67)}, {"id": i + 3, "value": chr(i + 68)}])
        ])

        head = OrderedDict([
            ("property1", {"id": i, "value": chr(i + 70)}),
            ("property2", {"id": i + 1, "value": chr(i + 71)}),
            ("property3", [{"id": i + 2, "value": chr(i + 72)}, {"id": i + 3, "value": chr(i + 73)}])
        ])

        # Merge JSON objects
        result = merger.merge(base, head)

        # Print merged JSON 5 times
        for _ in range(5):
            print(json.dumps(result, indent=4))

except ValueError as ve:
    print(f"Merge conflict occurred: {ve}")