import xml.etree.ElementTree as ET

OPTIONAL_STYLE = 'dot' # other option is 'dash', or even a tuple of ('dot','dash')

class Edge:
    def __init__(self, fromNode, toNode, interaction, is_optional=False):
        self.fromNode = fromNode
        self.toNode = toNode
        self.interaction = interaction
        self.is_optional = is_optional

    def __str__(self) -> str:
        return '<Edge from {} to {} with interaction={}, optional={}>'.format(self.fromNode, self.toNode, self.interaction, self.is_optional)

    def __eq__(self, o) -> bool:
        if isinstance(o, Edge):
            return self.fromNode == o.fromNode and \
                self.toNode == o.toNode and \
                self.interaction == o.interaction and \
                self.is_optional == o.is_optional
        return False

    def __hash__(self) -> int:
        return hash((self.fromNode,self.toNode,self.interaction,self.is_optional)) 


def parse_node_id(full_node_id):
    full_node_id = full_node_id.replace(' ','_')
    return full_node_id[full_node_id.find(':')+1:]

def get_with_sif():
    edge_set = set()
    sif_filename = input('Enter .sif filename: ')

    # iterate through .sif file
    with open(sif_filename, 'r') as f:
        for line in f.readlines():
            # parse the .sif line as an edge.
            # format is 'nodeID1 [tab] [PROMOTES | REPRESSES | REGULATES] [tab] nodeID2'
            tokens = line.split('\t')
            from_node = parse_node_id(tokens[0])
            interaction_str = tokens[1].rstrip()
            to_node = parse_node_id(tokens[2]).rstrip() # remove newline char
            brein_format_interaction = 'positive' if (tokens[1] == 'PROMOTES') else 'negative'
            edge = Edge(from_node, to_node, brein_format_interaction)
            edge_set.add(edge)
    return edge_set

def get_with_btp():
    edge_set = set()
    btp_filename = input('Enter .btp filename: ')
    root = ET.parse(btp_filename).getroot()

    node_id_to_name = {}
    ref_to_edge = {}

    # build map of (id -> gene_name)
    for gene in root.iter('gene'):
        attr = gene.attrib
        node_id_to_name[attr['id']] = attr['name']

    # find links and make corresponding edges
    for link in root.iter('link'):
        attr = link.attrib
        from_node_name = node_id_to_name[attr['src']]
        to_node_name = node_id_to_name[attr['targ']]
        interaction = 'positive' if attr['sign'] == '+' else 'negative'
        edge = Edge(from_node_name, to_node_name, interaction)
        ref_to_edge[attr['id']] = edge
        edge_set.add(edge)

    # update edges to reflect optional/mandatory status
    for node in root.findall(".//drop[perLinkDrawStyle]"):
        style = node[0][0].attrib['style']
        edge = ref_to_edge[node.attrib['ref']]
        if style == OPTIONAL_STYLE: edge.is_optional = True
    
    return edge_set

def main():
    #edge_set = get_with_sif()
    edge_set = get_with_btp()
    
    print('EDGE SET:')
    for e in edge_set: print(e)

    with open('output2.txt', 'w') as f:
        text = ''
        for edge in edge_set:
            text += '{}\t{}\t{};\n'.format(edge.fromNode, edge.toNode, edge.interaction)
        f.write(text.rstrip())

main()