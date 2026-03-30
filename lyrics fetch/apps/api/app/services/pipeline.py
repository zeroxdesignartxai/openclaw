def run_cluster_pipeline(category: str, user_data, parsed):
    # Hidden internal pipeline — placeholder for tokenize ➜ feature ➜ cluster
    tokens = str(user_data).split()
    cluster_id = hash(" ".join(tokens[:3] + [category])) % 1000
    return {"cluster_id": cluster_id, "token_count": len(tokens)}
