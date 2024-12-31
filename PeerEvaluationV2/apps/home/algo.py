import networkx as nx
import math


def capacity_from_incentive(incentive, base_k):
    """
    Given a peer's incentive (in [0,1]) and the base K (e.g. 3),
    return the integer capacity (max #papers they can review).

    Ranges (example):
      0.10-0.30 -> k * 1.2
      0.31-0.50 -> k * 1.3
      0.51-0.70 -> k * 1.4
      0.71-0.95 -> k * 1.45
      0.96-1.0  -> k * 1.5
    Otherwise, if < 0.1, treat them as a normal peer with capacity = k.
    (You can adjust these cutoffs/behavior as desired.)
    """

    if incentive < 0.1:
        return base_k
    elif 0.10 <= incentive <= 0.30:
        return math.ceil(base_k * 1.2)
    elif 0.31 <= incentive <= 0.50:
        return math.ceil(base_k * 1.3)
    elif 0.51 <= incentive <= 0.70:
        return math.ceil(base_k * 1.4)
    elif 0.71 <= incentive <= 0.95:
        return math.ceil(base_k * 1.45)
    else:  # 0.96 <= incentive <= 1.0
        return math.ceil(base_k * 1.5)


def assign_papers(
        peers, papers,
        k=3,
        incentives=None,  # list or dict of incentives for each peer, or None
        paper_capacity=None
):
    """
    Assign each paper to exactly k distinct peers if possible (3 by default).
    Each peer can't review its own paper. Peers may have different capacities
    depending on a 'trusted incentive'.

    :param peers:    list of peer IDs, e.g. ["A1","A2",..., "A26"]
    :param papers:   list of paper IDs, e.g. ["P1","P2",..., "P26"]
                     (same length as peers)
    :param k:        default #papers each peer can review (3 by default).
    :param incentives:
        - a dict {peerID -> float_in_[0,1]} or a list of floats
          (must be same length as peers). If None, all peers have capacity=k.
    :param paper_capacity:
        - how many distinct reviewers each paper can have.
          default to k=3, but you can raise it if, for instance,
          you want to allow more than 3 reviewers per paper.

    :return:
        If a valid assignment is found:
          list of (peerID, paperID) pairs.
        Else None.
    """
    if len(peers) != len(papers):
        raise ValueError("Number of peers and papers must match.")

    n = len(peers)
    if paper_capacity is None:
        paper_capacity = k  # typically 3

    # Build a directed graph for the flow network
    G = nx.DiGraph()
    source = "S"
    sink = "T"
    G.add_node(source)
    G.add_node(sink)

    # We'll create nodes for each peer (left side) and each paper (right side).
    peer_nodes = [f"peer_{i}" for i in range(n)]
    paper_nodes = [f"paper_{i}" for i in range(n)]

    # A helper to get capacity for each peer based on incentive
    def get_peer_capacity(idx):
        if incentives is None:
            return k
        # If incentives is a dict, get by key. If it's a list, use index.
        inc = incentives[peers[idx]] if isinstance(incentives, dict) else incentives[idx]
        return capacity_from_incentive(inc, k)

    # 1) Source -> Peer edges
    #    capacity = how many papers this peer can review (k or more if trusted).
    for i, pn in enumerate(peer_nodes):
        cap = get_peer_capacity(i)
        G.add_edge(source, pn, capacity=cap)

    # 2) Paper -> Sink edges
    #    capacity = how many distinct reviews we want for this paper (usually k).
    for j, ppr in enumerate(paper_nodes):
        G.add_edge(ppr, sink, capacity=paper_capacity)

    # 3) Peer -> Paper edges
    #    capacity=1 if the peer is not the owner of that paper.
    #    We rely on the naming convention to check if "A1" matches "P1", etc.
    for i, peerID in enumerate(peers):
        for j, paperID in enumerate(papers):
            # We assume "A1" owns "P1" (matching the numeric portion).
            # So let's parse out the numeric suffix and compare:
            # e.g. "A26" -> 26; "P26" -> 26
            # If they match, skip the edge (can't self-review).

            # Simple approach: compare everything after the letter
            # (assuming the format "A##", "P##").
            peer_num = peerID[1:]  # "1", "2", "26", ...
            paper_num = paperID[1:]  # "1", "2", "26", ...

            if peer_num != paper_num:
                # Add edge with capacity=1
                G.add_edge(peer_nodes[i], paper_nodes[j], capacity=1)

    # 4) Compute max flow
    flow_value, flow_dict = nx.maximum_flow(G, source, sink)

    # We want each paper to get 'paper_capacity' reviews, so the total
    # desired flow is paper_capacity * n. If flow_value < that, we failed.
    if flow_value < paper_capacity * n:
        return None

    # 5) Extract the assignment from the flow dictionary
    #    For each peer->paper edge that has flow=1, that means
    #    "peer i is assigned to paper j".
    assignments = []

    for i, pn in enumerate(peer_nodes):
        out_edges = flow_dict[pn]  # dict of {paper_node: flow_amt}
        for ppr_node, amt in out_edges.items():
            if amt > 0 and ppr_node.startswith("paper_"):
                # Identify which paper index that node is
                paper_idx = int(ppr_node.split("_")[1])
                # We have an assignment: peer i -> paper paper_idx
                assignments.append((peers[i], papers[paper_idx]))

    return assignments


# ---------------------- DEMO ----------------------
if __name__ == "__main__":
    # Example:
    # Let's say we have 6 peers & 6 papers (matching addresses):
    #   peers:  ["A1","A2","A3","A4","A5","A6"]
    #   papers: ["P1","P2","P3","P4","P5","P6"]
    #
    # We want each paper to get k=3 reviews.
    # Suppose we have some trust incentives for each peer:
    #  - A1 => 0.05  (less than 0.1 => capacity = k=3)
    #  - A2 => 0.40  (between 0.31-0.50 => k*1.3 => 3.9 => 4)
    #  - A3 => 0.70  (between 0.51-0.70 => k*1.4 => 4.2 => 5)
    #  - A4 => 0.95  (between 0.71-0.95 => k*1.45=> 4.35=>5)
    #  - A5 => 0.99  (>=0.96 => k*1.5 => 4.5 =>5)
    #  - A6 => 0.00  (<=0.1 => capacity=3)
    #
    # We'll see if we can get a valid distribution so that each of the 6 papers
    # is assigned 3 distinct reviewers, with no one reviewing their own paper.

    peers_list = [
        "A1", "A2", "A3", "A4", "A5", "A6",
        "A7", "A8", "A9", "A10", "A11", "A12",
        "A13", "A14", "A15", "A16", "A17", "A18",
        "A19", "A20", "A21", "A22", "A23", "A24",
        "A25", "A26"
    ]

    papers_list = [
        "P1", "P2", "P3", "P4", "P5", "P6",
        "P7", "P8", "P9", "P10", "P11", "P12",
        "P13", "P14", "P15", "P16", "P17", "P18",
        "P19", "P20", "P21", "P22", "P23", "P24",
        "P25", "P26"
    ]

    # Let's define incentives as a dict:
    trust_incentives = {
        "A1": 0.05,
        "A2": 0.40,
        "A3": 0.70,
        "A4": 0.95,
        "A5": 0.99,
        "A6": 0.00,
        "A7": 0.10,
        "A8": 0.15,
        "A9": 0.20,
        "A10": 0.25,
        "A11": 0.30,
        "A12": 0.35,
        "A13": 0.45,
        "A14": 0.50,
        "A15": 0.55,
        "A16": 0.60,
        "A17": 0.65,
        "A18": 0.75,
        "A19": 0.80,
        "A20": 0.85,
        "A21": 0.90,
        "A22": 0.93,
        "A23": 0.96,
        "A24": 0.98,
        "A25": 0.99,
        "A26": 1.00
    }

    k = 3  # base number of papers each peer should evaluate

    assignment = assign_papers(peers_list, papers_list, k, trust_incentives)

    if assignment is None:
        print("No valid assignment found.")
    else:
        print("Found an assignment of size:", len(assignment))
        # Each of 6 papers should appear exactly 3 times => total = 18 edges
        # Let's group by paper to see which peers got assigned
        from collections import defaultdict

        by_paper = defaultdict(list)
        for peer, paper in assignment:
            by_paper[paper].append(peer)

        for paper, assigned_peers in by_paper.items():
            print(f"{paper} reviewed by {assigned_peers}")
