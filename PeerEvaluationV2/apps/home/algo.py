import random
from math import floor


def distribute_papers(
        authors,  # List of length p, authors[i] = who wrote paper i
        e,  # Number of evaluators/peers
        trusted_evaluators,  # Subset of peer indices that can receive extra papers
        shuffle=True
):
    """
    Distribute all papers so that no one gets their own paper.
    'trusted_evaluators' is a set of evaluator indices who can handle more papers if needed.

    Returns:
        assignment: list of length p, where assignment[i] = evaluator for paper i,
                    or None if distribution not possible.
    """

    p = len(authors)

    # ----------------- Step 1: Compute capacities for each evaluator -----------------
    capacity = [0] * e
    trusted_set = set(trusted_evaluators)

    if p <= e:
        # Case A: p <= e
        # We'll try to assign each paper to a distinct evaluator.
        # If p < e, then only trusted get the papers (or if not enough trusted, might extend to others).
        # Example approach:
        #   - Sort evaluators so that trusted appear first
        #   - Assign 1 paper to each until we exhaust p
        eval_sorted = list(range(e))
        eval_sorted.sort(key=lambda x: x not in trusted_set)
        # This puts trusted evaluators first, so they get assigned first.

        used = 0
        for ev in eval_sorted:
            if used < p:
                capacity[ev] = 1
                used += 1
            else:
                break
        # If used < p after this, means we don't have enough evaluators (unlikely).

    else:
        # Case B: p > e
        base = p // e
        remainder = p % e
        # Everyone gets `base`
        for ev in range(e):
            capacity[ev] = base

        # Distribute the remainder among trusted first, then others if remainder remains
        for ev in range(e):
            if remainder <= 0:
                break
            # if this evaluator is trusted, give them +1
            if ev in trusted_set:
                capacity[ev] += 1
                remainder -= 1

        # If remainder is still > 0 after giving each trusted +1,
        # distribute among non-trusted as well
        for ev in range(e):
            if remainder <= 0:
                break
            if ev not in trusted_set:
                capacity[ev] += 1
                remainder -= 1

    # ----------------- Step 2: Assign each paper to a valid evaluator -----------------
    assignment = [None] * p
    paper_ids = list(range(p))
    if shuffle:
        random.shuffle(paper_ids)

    for pap in paper_ids:
        possible_evs = []
        for ev in range(e):
            if capacity[ev] > 0 and ev != authors[pap]:
                possible_evs.append(ev)

        if not possible_evs:
            # No valid evaluator found -> distribution fails
            return None

        # Pick one evaluator from the valid pool (could pick randomly or e.g. first)
        chosen_ev = random.choice(possible_evs)
        assignment[pap] = chosen_ev
        capacity[chosen_ev] -= 1

    # ----------------- Step 3: Check the "last paper" scenario & swap if needed -----------------
    last_paper = paper_ids[-1]  # The last paper we assigned in the shuffled order
    if assignment[last_paper] == authors[last_paper]:
        # We need to swap with some other paper
        # Let's find any paper 'j' to swap with, ensuring neither ends up with their own author
        for j in range(p):
            if j == last_paper:
                continue

            current_ev_for_j = assignment[j]
            if (current_ev_for_j != authors[last_paper]) and \
                    (authors[j] != assignment[last_paper]):
                # swap them
                assignment[last_paper], assignment[j] = assignment[j], assignment[last_paper]
                break
        # If we can't find a swap partner, distribution might fail or remain with a conflict
        if assignment[last_paper] == authors[last_paper]:
            return None  # no swap found

    return assignment


def run_evaluations_k_times(authors, e, trusted_evaluators, k=None):
    """
    Run the distribution process 'k' times (default k = p//2),
    returning a list of all assignments (one per round).

    :param authors: list, authors[i] = the peer who wrote paper i
    :param e: number of evaluators
    :param trusted_evaluators: set or list of evaluator indices
    :param k: how many times to run (if None, default = p//2)
    :return:
        all_assignments: list of length k,
                         each element is a list 'assignment' of length p
                         or None if distribution failed in that round
    """
    p = len(authors)
    if k is None:
        k = 5  # for example

    all_assignments = []
    for round_idx in range(k):
        # We can shuffle differently each round for variety
        assignment = distribute_papers(authors, e, trusted_evaluators, shuffle=True)
        all_assignments.append(assignment)

    return all_assignments


# ------------------- DEMO -------------------
if __name__ == "__main__":
    # Example:
    # Let's say we have 6 evaluators (0..5),
    # and 8 papers (indices 0..7).
    # authors[i] = who wrote paper i.
    # Suppose papers 0..3 were written by evaluators 0..3,
    # and papers 4..7 were also by evaluators 0..3 (duplicates).
    authors = [0,1,2,4,5,5]
    e = 4
    trusted_evaluators = [1,2]  # let's say evaluators #4 and #5 are "trusted"

    # We'll run k = p//2 = 4 rounds
    results = run_evaluations_k_times(authors, e, trusted_evaluators, k=None)

    for round_idx, assignment in enumerate(results, start=1):
        print(f"--- Round {round_idx} ---")
        if assignment is None:
            print("  Distribution failed.")
        else:
            for pap, ev in enumerate(assignment):
                print(f"  Paper {pap} (author={authors[pap]}) -> Evaluator {ev}")
            print()
