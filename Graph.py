class Node(object):
    def __init__(self, id, label = None, properties = None, values = None,
                 anchors = None, top = False):
        self.id = id
        self.label = label
        self.properties = properties
        self.values = values
        self.incoming_edges = set()
        self.outgoing_edges = set()
        self.anchors = anchors
        self.is_top = top

    @staticmethod
    def decode(json):
        id = json["id"]
        label = json.get("label", None)
        properties = json.get("properties", None)
        values = json.get("values", None)
        anchors = json.get("anchors", None)
        return Node(id, label, properties, values, anchors)

class Edge(object):

    def __init__(self, src, tgt, lab, normal = None,
                 attributes = None, values = None):
        self.src = src
        self.tgt = tgt
        self.lab = lab
        self.normal = normal
        self.attributes = attributes
        self.values = values
