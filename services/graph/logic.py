import spacy

def extract_svo_relations(doc):
    relations = []
    for sent in doc.sents:
        for token in sent:
            if "subj" in token.dep_:
                subject = token.text
                verb = token.head.text
                obj = None
                for child in token.head.children:
                    if "dobj" in child.dep_:
                        obj = child.text
                        break
                    # Nếu không có dobj, tìm pobj (tân ngữ của giới từ)
                    if obj is None and "prep" in child.dep_:
                        for subchild in child.children:
                            if "pobj" in subchild.dep_:
                                obj = subchild.text
                                break
                if obj:
                    relations.append((subject, verb, obj))
    return relations

def build_graph(entities, relations):
    nodes = list(set(entities + [rel[0] for rel in relations] + [rel[2] for rel in relations]))
    node_map = {name: i for i, name in enumerate(nodes)}

    edges = []
    for subj, verb, obj in relations:
        if subj in node_map and obj in node_map:
            edges.append((subj, obj, verb))

    return {"nodes": [{"id": i, "name": name} for i, name in enumerate(nodes)], "edges": edges}
