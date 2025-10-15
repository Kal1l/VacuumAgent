class MeasureCleanPerStep:
    def __init__(self):
        self.score = 0

    def update(self, cleaned):
        if cleaned:
            self.score += 1

class MeasureCleanAndMovePenalty:
    def __init__(self):
        self.score = 0

    def update(self, cleaned, moved):
        if cleaned:
            self.score += 1
        if moved:
            self.score -= 1

