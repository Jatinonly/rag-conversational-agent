
def reciprocal_rank_fusion(
    ranked_lists: list[list[int]],
    k: int = 60,
) -> dict[int, float]:

    scores = {}

    for ranked_list in ranked_lists:
        for rank, chunk_id in enumerate(ranked_list, start=1):
            score = 1 / (k + rank)

            if chunk_id not in scores:
                scores[chunk_id] = 0

            scores[chunk_id] += score

    return scores
