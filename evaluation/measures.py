class MeasureCleanPerStep:
    def __init__(self):
        self.score = 0

    def update(self, cleaned):
        if cleaned:
            self.score += 1

class MeasureCleanAndMovePositive:
    def __init__(self):
        self.score = 0
        self.moves = 0
        self.cleaned = 0

    def update(self, cleaned, moved):
        if cleaned:
            self.score += 1
            self.cleaned += 1
        if moved:
            self.moves += 1

    def final_score(self):
        # Score positivo: sujeiras limpas menos movimentos (quanto maior, melhor)
        return max(0, self.cleaned - self.moves)
