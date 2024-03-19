import json


"""EXAMPLE OF MDJ FILE
{"_type":"Project","_id":"AAAAAAFF+h6SjaM2Hec=","name":"Untitled","ownedElements":[{"_type":"ERDDataModel","_id":"AAAAAAGOWQ6Yfno6Sgc=","_parent":{"$ref":"AAAAAAFF+h6SjaM2Hec="},"name":"Data Model1","ownedElements":[{"_type":"ERDDiagram","_id":"AAAAAAGOWQ6Yfno7AA8=","_parent":{"$ref":"AAAAAAGOWQ6Yfno6Sgc="},"name":"ERDDiagram1","ownedViews":[{"_type":"ERDEntityView","_id":"AAAAAAGOWQ83GXppu4Q=","_parent":{"$ref":"AAAAAAGOWQ6Yfno7AA8="},"model":{"$ref":"AAAAAAGOWQ83GXpnf0I="},"subViews":[{"_type":"LabelView","_id":"AAAAAAGOWQ83GXpqqPI=","_parent":{"$ref":"AAAAAAGOWQ83GXppu4Q="},"font":"Arial;13;1","left":40,"top":117,"width":174.21875,"height":13,"text":"Entity1"},{"_type":"ERDColumnCompartmentView","_id":"AAAAAAGOWQ83GXprpx4=","_parent":{"$ref":"AAAAAAGOWQ83GXppu4Q="},"model":{"$ref":"AAAAAAGOWQ83GXpnf0I="},"subViews":[{"_type":"ERDColumnView","_id":"AAAAAAGOWQ9mk3qXiYc=","_parent":{"$ref":"AAAAAAGOWQ83GXprpx4="},"model":{"$ref":"AAAAAAGOWQ9mkHqUmQA="},"font":"Arial;13;0","left":45,"top":140,"width":164.21875,"height":13},{"_type":"ERDColumnView","_id":"AAAAAAGOWQ+TlXqezOg=","_parent":{"$ref":"AAAAAAGOWQ83GXprpx4="},"model":{"$ref":"AAAAAAGOWQ+TknqbL0o="},"font":"Arial;13;0","left":45,"top":155,"width":164.21875,"height":13}],"font":"Arial;13;0","left":40,"top":135,"width":174.21875,"height":38}],"font":"Arial;13;0","left":40,"top":112,"width":174.21875,"height":96,"nameLabel":{"$ref":"AAAAAAGOWQ83GXpqqPI="},"columnCompartment":{"$ref":"AAAAAAGOWQ83GXprpx4="}},{"_type":"ERDEntityView","_id":"AAAAAAGOWQ9GKXp1M0A=","_parent":{"$ref":"AAAAAAGOWQ6Yfno7AA8="},"model":{"$ref":"AAAAAAGOWQ9GKHpzGi4="},"subViews":[{"_type":"LabelView","_id":"AAAAAAGOWQ9GKXp2vK0=","_parent":{"$ref":"AAAAAAGOWQ9GKXp1M0A="},"font":"Arial;13;1","left":360,"top":117,"width":167.96630859375,"height":13,"text":"Entity2"},{"_type":"ERDColumnCompartmentView","_id":"AAAAAAGOWQ9GKXp3f3o=","_parent":{"$ref":"AAAAAAGOWQ9GKXp1M0A="},"model":{"$ref":"AAAAAAGOWQ9GKHpzGi4="},"subViews":[{"_type":"ERDColumnView","_id":"AAAAAAGOWQ+ornqkrgs=","_parent":{"$ref":"AAAAAAGOWQ9GKXp3f3o="},"model":{"$ref":"AAAAAAGOWQ+oqnqhydU="},"font":"Arial;13;0","left":365,"top":140,"width":157.96630859375,"height":13},{"_type":"ERDColumnView","_id":"AAAAAAGOWQ/Agnqryv0=","_parent":{"$ref":"AAAAAAGOWQ9GKXp3f3o="},"model":{"$ref":"AAAAAAGOWQ/Af3qoabo="},"font":"Arial;13;0","left":365,"top":155,"width":157.96630859375,"height":13},{"_type":"ERDColumnView","_id":"AAAAAAGOWQ/Zp3qxf6g=","_parent":{"$ref":"AAAAAAGOWQ9GKXp3f3o="},"model":{"$ref":"AAAAAAGOWQ/Zo3qu2gI="},"font":"Arial;13;0","left":365,"top":170,"width":157.96630859375,"height":13}],"font":"Arial;13;0","left":360,"top":135,"width":167.96630859375,"height":53}],"font":"Arial;13;0","left":360,"top":112,"width":167.96630859375,"height":76,"nameLabel":{"$ref":"AAAAAAGOWQ9GKXp2vK0="},"columnCompartment":{"$ref":"AAAAAAGOWQ9GKXp3f3o="}},{"_type":"ERDRelationshipView","_id":"AAAAAAGOWQ9GM3qD3fM=","_parent":{"$ref":"AAAAAAGOWQ6Yfno7AA8="},"model":{"$ref":"AAAAAAGOWQ9GM3p/A1A="},"subViews":[{"_type":"EdgeLabelView","_id":"AAAAAAGOWQ9GM3qE3Jw=","_parent":{"$ref":"AAAAAAGOWQ9GM3qD3fM="},"font":"Arial;13;0","left":259,"top":127,"width":57.0908203125,"height":13,"alpha":1.5707963267948966,"distance":15,"hostEdge":{"$ref":"AAAAAAGOWQ9GM3qD3fM="},"edgePosition":1,"text":"Entity1_id"},{"_type":"EdgeLabelView","_id":"AAAAAAGOWQ9GM3qF9sU=","_parent":{"$ref":"AAAAAAGOWQ9GM3qD3fM="},"font":"Arial;13;0","left":239,"top":127,"height":13,"alpha":0.5235987755982988,"distance":30,"hostEdge":{"$ref":"AAAAAAGOWQ9GM3qD3fM="},"edgePosition":2},{"_type":"EdgeLabelView","_id":"AAAAAAGOWQ9GM3qGzFI=","_parent":{"$ref":"AAAAAAGOWQ9GM3qD3fM="},"font":"Arial;13;0","left":334,"top":127,"height":13,"alpha":-0.5235987755982988,"distance":30,"hostEdge":{"$ref":"AAAAAAGOWQ9GM3qD3fM="}}],"font":"Arial;13;0","head":{"$ref":"AAAAAAGOWQ9GKXp1M0A="},"tail":{"$ref":"AAAAAAGOWQ83GXppu4Q="},"lineStyle":2,"points":"214:148;360:148","nameLabel":{"$ref":"AAAAAAGOWQ9GM3qE3Jw="},"tailNameLabel":{"$ref":"AAAAAAGOWQ9GM3qF9sU="},"headNameLabel":{"$ref":"AAAAAAGOWQ9GM3qGzFI="}}]},{"_type":"ERDEntity","_id":"AAAAAAGOWQ83GXpnf0I=","_parent":{"$ref":"AAAAAAGOWQ6Yfno6Sgc="},"name":"Entity1","ownedElements":[{"_type":"ERDRelationship","_id":"AAAAAAGOWQ9GM3p/A1A=","_parent":{"$ref":"AAAAAAGOWQ83GXpnf0I="},"name":"Entity1_id","end1":{"_type":"ERDRelationshipEnd","_id":"AAAAAAGOWQ9GM3qApUM=","_parent":{"$ref":"AAAAAAGOWQ9GM3p/A1A="},"reference":{"$ref":"AAAAAAGOWQ83GXpnf0I="}},"end2":{"_type":"ERDRelationshipEnd","_id":"AAAAAAGOWQ9GM3qBtvE=","_parent":{"$ref":"AAAAAAGOWQ9GM3p/A1A="},"reference":{"$ref":"AAAAAAGOWQ9GKHpzGi4="},"cardinality":"0..*"}}],"columns":[{"_type":"ERDColumn","_id":"AAAAAAGOWQ9mkHqUmQA=","_parent":{"$ref":"AAAAAAGOWQ83GXpnf0I="},"name":"Entity1_id","type":"INTEGER","length":0,"primaryKey":true},{"_type":"ERDColumn","_id":"AAAAAAGOWQ+TknqbL0o=","_parent":{"$ref":"AAAAAAGOWQ83GXpnf0I="},"name":"Column1","type":"TEXT"}]},{"_type":"ERDEntity","_id":"AAAAAAGOWQ9GKHpzGi4=","_parent":{"$ref":"AAAAAAGOWQ6Yfno6Sgc="},"name":"Entity2","columns":[{"_type":"ERDColumn","_id":"AAAAAAGOWQ+oqnqhydU=","_parent":{"$ref":"AAAAAAGOWQ9GKHpzGi4="},"name":"Entity2_id","type":"INTEGER","length":0,"primaryKey":true},{"_type":"ERDColumn","_id":"AAAAAAGOWQ/Af3qoabo=","_parent":{"$ref":"AAAAAAGOWQ9GKHpzGi4="},"name":"Column1","type":"TEXT"},{"_type":"ERDColumn","_id":"AAAAAAGOWQ/Zo3qu2gI=","_parent":{"$ref":"AAAAAAGOWQ9GKHpzGi4="},"name":"Entity1_id","type":"INTEGER","length":0,"foreignKey":true}]}]}]}
"""

class ER:
    def __init__(self, mdj_file):
        with open(mdj_file) as f:
            mdj_data = json.load(f)

        def minify_mdj(data):
            min_data = data.copy()
            keys_to_remove = []
            for key in min_data.keys():
                if key == 'style' or key == "font" or key == "left" or key == "top" or key == "width"  or key == "height" or "Label" in key or key == "alpha" or "view" in key or key == "ownedViews":
                    keys_to_remove.append(key)
                elif isinstance(min_data[key], dict):
                    min_data[key] = minify_mdj(min_data[key])
                elif isinstance(min_data[key], list):
                    for i in range(len(min_data[key])):
                        min_data[key][i] = minify_mdj(min_data[key][i])
            for key in keys_to_remove.copy():  # Create a copy of the keys before removing them
                min_data.pop(key)
            return min_data

        #self.mdj_data = minify_mdj(mdj_data)
        self.mdj_data = mdj_data

    def get_mdj_data(self):
        return self.mdj_data
    
    # Based off of the EXAMPLE OF MDJ FILE STRUCTURE above
    def get_entities(self):
        entities = []
        for entity in self.mdj_data["ownedElements"][0]["ownedElements"]:
            if entity["_type"] == "ERDEntity":
                entities.append(entity)
        return entities

    def get_relationships(self):
        relationships = []
        for entity in self.get_entities():
            print(entity.keys())
            if "ownedElements" in entity.keys():
                for relationship in entity["ownedElements"]:
                    if relationship["_type"] == "ERDRelationship":
                        relationships.append(relationship)
        return relationships
    
    def get_entity_columns(self, entity):
        columns = []
        for column in entity["columns"]:
            columns.append(column)
        return columns
    
    def get_relationship_ends(self, relationship):
        ends = []
        for end in relationship["ownedElements"]:
            if end["_type"] == "ERDRelationshipEnd":
                ends.append(end)
        return ends
    
    def get_relationship_end_reference(self, end):
        return end["reference"]
    
    def get_relationship_end_cardinality(self, end):
        return end["cardinality"]
    
    def pretty_print(self, data):
        print(json.dumps(data, indent=4, sort_keys=True))
    

# EXAMPLE USAGE
er = ER("DBProject.mdj")
#print(er.pretty_print(er.get_entities()))
print(er.pretty_print(er.get_relationships()))

    

