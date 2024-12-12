import networkx as nx

from build_graph import create_network_graph, load_network_data

def recommend_accounts(G, source_user="user", num_recommendations=10):
    """Recommend accounts based on Jaccard similarity"""

    # Convert directed graph to undirected
    print("Converting graph to undirected...")
    undirected_G = G.to_undirected()

    # Filter nodes for performance
    # print nr. of nodes
    print("Filtering nodes for performance...", )
    print(f"Number of nodes before filtering: {len(undirected_G.nodes)}")
    filtered_nodes = [node for node in G.nodes if G.degree[node] < 2]
    undirected_G.remove_nodes_from(filtered_nodes)
    print(f"Number of nodes after filtering: {len(undirected_G.nodes)}")

    # Get all nodes that are not connected to the source user
    print("Getting all nodes that are not connected to the source user...")
    all_nodes = set(undirected_G.nodes)
    source_user_neighbors = set(undirected_G.neighbors(source_user))
    other_nodes = all_nodes - source_user_neighbors - {source_user}

    # List of pairs with user and other_nodes
    print("Creating list of pairs with user and other nodes...")
    pairs = [(source_user, node) for node in other_nodes]

    # Calculate Jaccard similarity between source user and all other users
    print("Calculating Jaccard similarity...")
    recommended_users = similarity_list(nx.jaccard_coefficient(undirected_G, ebunch=pairs), source_user, num_recommendations)

    print("Calculating Adamic-Adar similarity...")
    recommended_users = similarity_list(nx.adamic_adar_index(undirected_G, ebunch=pairs), source_user, num_recommendations)

    return recommended_users

def similarity_list(similarity_iterable, source_user="user", num_recommendations=10):
    similarity_scores = {}
    for u, v, p in similarity_iterable:
        if u == source_user:
            similarity_scores[v] = p

    # Sort users by similarity score and return top recommendations
    print("Sorting similarity scores...")
    sorted_users = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
    recommendations = sorted_users[:num_recommendations]
   
    # Print recommended accounts
    print(f"Recommended accounts for {source_user}:")
    for user, score in recommendations:
        print(user, score)

    return recommendations

if __name__ == "__main__":
    # Define paths
    main_json_path = 'bluesky_data/following.json'
    network_dir = 'bluesky_data/following_network'
    
    # Load the data
    main_following, network_data = load_network_data(main_json_path, network_dir)
    
    # Create the network graph
    G = create_network_graph(main_following, network_data, include_secondary_follows=True)
    
    # Recommend accounts
    recommend_accounts(G, source_user="user")