import random
from math import ceil

# Students and papers
students = [f"S{i+1}" for i in range(26)]  # S1, S2, ..., S26
papers = [f"P{i+1}" for i in range(26)]    # P1, P2, ..., P26
trusted_evaluators = {"S12": 0.3, "S17": 0.8, "S18": 1.0}  # Trust levels
k = 3  # Base evaluations per paper

# Initialize evaluation counts and pairs
evaluation_count = {student: 0 for student in students}
paper_count = {paper: 0 for paper in papers}  # Track how many times each paper is evaluated
pairs = {student: [] for student in students}

# Calculate maximum evaluations for each student
max_evaluations = {
    student: ceil(2 * k * level) for student, level in trusted_evaluators.items()
}
for student in students:
    if student not in trusted_evaluators:
        max_evaluations[student] = k  # Default max evaluations for non-trusted evaluators

# Prepare list of evaluations (each paper appears k times)
remaining_evaluations = papers * k
random.shuffle(remaining_evaluations)  # Shuffle for fairness

def redistribute_evaluations(paper, evaluator):
    """
    Remove one assignment from another evaluator to make room for the current evaluation.
    """
    for other_student in students:
        if other_student != evaluator and paper in pairs[other_student]:
            pairs[other_student].remove(paper)
            evaluation_count[other_student] -= 1
            return

# Assign evaluations
for evaluation in remaining_evaluations:
    # Find valid evaluators
    possible_evaluators = [
        student for student in students
        if evaluation_count[student] < max_evaluations[student]  # Respect max limits
        and evaluation not in pairs[student]  # Avoid duplicate evaluations for the same paper
    ]

    # If no possible evaluator, redistribute evaluations
    if not possible_evaluators:
        # Pick a random trusted evaluator and redistribute
        evaluator = random.choice(list(trusted_evaluators.keys()))
        redistribute_evaluations(evaluation, evaluator)
        possible_evaluators = [evaluator]

    # Assign the evaluation to a random valid evaluator
    evaluator = random.choice(possible_evaluators)
    pairs[evaluator].append(evaluation)
    evaluation_count[evaluator] += 1
    paper_count[evaluation] += 1

# Ensure all papers are evaluated exactly k times
for paper, count in paper_count.items():
    if count != k:
        raise ValueError(f"Paper {paper} is evaluated {count} times instead of {k}.")

# Print the results
print("Evaluations assigned to each student:")
for student, assigned_papers in pairs.items():
    print(f"{student}: {assigned_papers} (Total: {len(assigned_papers)})")

# Print paper evaluation counts
print("\nNumber of times each paper is evaluated:")
for paper, count in paper_count.items():
    print(f"{paper}: {count}")
