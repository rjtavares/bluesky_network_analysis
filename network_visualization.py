import networkx as nx
import matplotlib.pyplot as plt
import json
import os
import csv
import numpy as np
from fa2 import ForceAtlas2
from scipy import sparse
from build_graph import create_network_graph, load_network_data


def detect_communities(G):
    """Detect communities in the network using Louvain method"""
    print("\nDetecting communities...")
    communities = nx.community.louvain_communities(G)
    print(f"Found {len(communities)} communities")
    return communities

def export_nodes(G, communities, output_file='output_data/nodes_info.csv'):
    """Export node information including communities and centrality metrics"""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Calculate various centrality metrics
    degree_cent = nx.degree_centrality(G)
    betweenness_cent = nx.betweenness_centrality(G)
    eigenvector_cent = nx.eigenvector_centrality(G, max_iter=1000)
    
    # Find community membership for each node
    community_map = {}
    for idx, community in enumerate(communities):
        for node in community:
            community_map[node] = idx
    
    # Export nodes with their metrics
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow([
            'Handle',
            'DisplayName',
            'Description',
            'NodeType',
            'Community',
            'DegreeCentrality',
            'BetweennessCentrality',
            'EigenvectorCentrality',
            'Followers',
            'Following',
            'Posts',
            'JoinDate'
        ])
        
        # Write node data
        for node in G.nodes():
            node_data = G.nodes[node]
            writer.writerow([
                node,  # Handle
                node_data.get('display_name', ''),
                node_data.get('description', ''),
                node_data.get('node_type', ''),
                community_map.get(node, -1),  # Community ID
                round(degree_cent[node], 4),
                round(betweenness_cent[node], 4),
                round(eigenvector_cent[node], 4),
                G.in_degree(node),  # Followers
                G.out_degree(node),  # Following
                node_data.get('posts_count', 0),
                node_data.get('created_at', '')
            ])
    
    print(f"\nNode information exported to '{output_file}'")
    print("Included metrics:")
    print("- Community membership")
    print("- Degree centrality")
    print("- Betweenness centrality")
    print("- Eigenvector centrality")
    print("- Network statistics (followers/following)")

def visualize_network(G, communities, output_file='output_data/bluesky_network.png'):
    """Visualize the network using NetworkX and Matplotlib"""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    plt.figure(figsize=(20, 20))
    
    # Initialize ForceAtlas2 with custom settings
    forceatlas2 = ForceAtlas2(
        # Behavior alternatives
        outboundAttractionDistribution=True,  # Dissuade hubs
        linLogMode=False,  # Not implemented yet
        adjustSizes=False,  # Not implemented yet
        edgeWeightInfluence=0.0,  # Ignore edge weights for more even spacing

        # Performance
        jitterTolerance=2.0,  # Increased for more movement
        barnesHutOptimize=True,
        barnesHutTheta=2.0,  # Increased for faster convergence
        multiThreaded=False,  # Not implemented yet

        # Tuning
        scalingRatio=20.0,  # Significantly increased for more spacing
        strongGravityMode=True,  # Keep components together
        gravity=0.5,  # Reduced to allow more expansion

        # Log
        verbose=True
    )
    
    # Calculate layout using ForceAtlas2
    print("\nCalculating network layout...")
    # Convert to scipy sparse matrix first
    A = nx.adjacency_matrix(G)
    pos = forceatlas2.forceatlas2(A, pos=None, iterations=2000)
    
    # Convert positions back to dictionary format
    pos = {node: pos[i] for i, node in enumerate(G.nodes())}
    
    # Create a color map for communities
    num_communities = len(communities)
    color_map = plt.colormaps['Set3'](np.linspace(0, 1, num_communities))
    
    # Assign colors to nodes based on their community
    node_colors = []
    for node in G.nodes():
        if G.nodes[node]['node_type'] == 'source':
            node_colors.append('red')  # Keep source node red
        else:
            # Find which community this node belongs to
            for idx, community in enumerate(communities):
                if node in community:
                    node_colors.append(color_map[idx])
                    break
    
    # Calculate node sizes based on degree centrality
    degree_centrality = nx.degree_centrality(G)
    node_sizes = [3000 if G.nodes[node]['node_type'] == 'source' else 
                  200 + 3000 * degree_centrality[node] for node in G.nodes()]
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos,
                          node_color=node_colors,
                          node_size=node_sizes,
                          alpha=0.6)
    
    # Draw edges with arrows
    nx.draw_networkx_edges(G, pos,
                          edge_color='gray',
                          arrows=True,
                          arrowsize=10,
                          alpha=0.2,  # Reduced edge alpha for better visibility
                          width=0.5)
    
    # Draw labels with font size based on degree centrality
    labels = {node: node for node in G.nodes()}
    
    # Calculate font sizes: minimum 4, maximum 12, scaled by degree centrality
    font_sizes = {}
    min_font, max_font = 4, 12
    min_cent = min(degree_centrality.values())
    max_cent = max(degree_centrality.values())
    
    for node in G.nodes():
        if G.nodes[node]['node_type'] == 'source':
            font_sizes[node] = max_font  # Source node gets maximum font size
        else:
            # Scale font size between min_font and max_font based on degree centrality
            scale = (degree_centrality[node] - min_cent) / (max_cent - min_cent)
            font_sizes[node] = min_font + scale * (max_font - min_font)
    
    # Draw labels for each node with its calculated font size
    for node, font_size in font_sizes.items():
        nx.draw_networkx_labels(G, pos,
                              {node: node},
                              font_size=font_size,
                              font_weight='bold')
    
    plt.title("Bluesky Follow Network\nColored by Communities", fontsize=16, pad=20)
    plt.axis('off')
    
    # Save the plot
    print(f"Saving visualization...")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nNetwork visualization has been saved as '{output_file}'")
    print(f"\nNetwork Statistics:")
    print(f"Number of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")
    print(f"Number of communities detected: {len(communities)}")
    
    # Calculate and print some network metrics
    print("\nTop 5 accounts by degree centrality:")
    degree_cent = nx.degree_centrality(G)
    top_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:5]
    for node, centrality in top_degree:
        print(f"{node}: {centrality:.3f}")

    # Calculate and print betweenness centrality
    print("\nTop 5 accounts by betweenness centrality:")
    betweenness_cent = nx.betweenness_centrality(G)
    top_betweenness = sorted(betweenness_cent.items(), key=lambda x: x[1], reverse=True)[:5]
    for node, centrality in top_betweenness:
        print(f"{node}: {centrality:.3f}")


def main():
    """Main function to run the network analysis"""
    # Define paths
    main_json_path = 'bluesky_data/following.json'
    network_dir = 'bluesky_data/following_network'
    
    # Load the data
    main_following, network_data = load_network_data(main_json_path, network_dir)
    
    # Create the network graph
    G = create_network_graph(main_following, network_data)
    
    # Detect communities
    communities = detect_communities(G)

    # Export node information    
    export_nodes(G, communities)

    # Visualize the network
    visualize_network(G, communities)

if __name__ == "__main__":
    main()
