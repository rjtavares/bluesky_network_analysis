import networkx as nx
import json
import os

def create_network_graph(main_following, network_data, include_secondary_follows=False):
    """Create a NetworkX graph from the follow data"""
    G = nx.DiGraph()  # Create a directed graph
    
    # Add main user and their follows
    source_user = "user"  # This represents the main user
    G.add_node(source_user, node_type="source")
    
    # Add edges from the source user to all their follows
    for follow in main_following:
        handle = follow['handle']
        G.add_node(handle, 
                   node_type="following",
                   display_name=follow.get('display_name', handle),
                   description=follow.get('description', ''))
        G.add_edge(source_user, handle)
    
    # Add edges between following accounts
    for account, following_list in network_data.items():
        for follow in following_list:
            follower_handle = account
            followee_handle = follow['handle']
            
            if include_secondary_follows:
                # If followee is not already in the graph, add it
                if not G.has_node(followee_handle):
                    G.add_node(followee_handle, 
                               node_type="following",
                               display_name=follow.get('display_name', followee_handle),
                               description=follow.get('description', ''))
                # Add edges from the follower to the followee
                G.add_edge(follower_handle, followee_handle)
            else:
                # Only add edges if both nodes are already in the graph
                if G.has_node(follower_handle) and G.has_node(followee_handle):
                    G.add_edge(follower_handle, followee_handle)
    
    return G

def export_to_graphml(G, output_folder='output_data', output_file='bluesky_network.graphml'):
    """Export the network to GraphML format"""
    # Create output directory if it doesn't exist
    output_file = os.path.join(output_folder, output_file)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Create a copy of the graph to modify attributes
    H = G.copy()
    
    # Replace None values with empty strings in node attributes
    for node in H.nodes():
        for key in H.nodes[node]:
            if H.nodes[node][key] is None:
                H.nodes[node][key] = ""
    
    # Replace None values with empty strings in edge attributes
    for u, v in H.edges():
        for key in H.edges[u, v]:
            if H.edges[u, v][key] is None:
                H.edges[u, v][key] = ""
    
    # Export the modified graph
    nx.write_graphml(H, output_file)
    print(f"\nNetwork data exported to '{output_file}'")

def load_network_data(main_json_path, network_dir):
    """Load the network data from the JSON files"""
    # Load main user's following list
    with open(main_json_path, 'r', encoding='utf-8') as f:
        main_following = json.load(f)
    
    # Load following network data
    network_data = {}
    for filename in os.listdir(network_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(network_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                network_data[filename.replace('.json', '')] = json.load(f)
    
    return main_following, network_data


if __name__ == "__main__":
    """Main function to run the network analysis"""
    # Define paths
    main_json_path = 'bluesky_data/following.json'
    network_dir = 'bluesky_data/following_network'
    
    # Load the data
    main_following, network_data = load_network_data(main_json_path, network_dir)
    
    # Create and export the basic network graph
    G = create_network_graph(main_following, network_data)
    export_to_graphml(G)

    # Create and export the extended network graph
    G = create_network_graph(main_following, network_data, include_secondary_follows=True)
    export_to_graphml(G, output_file='bluesky_network_extended.graphml')

