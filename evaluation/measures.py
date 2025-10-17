class MeasureCleanPerStep:
    """
    Métrica que conta o número de ações de limpeza executadas.
    Usada para avaliar a eficácia básica do agente.
    """
    
    def __init__(self):
        """Inicializa o contador de pontuação."""

        self.score = 0

    def update(self, cleaned):
        """
        Atualiza pontuação baseada em ação de limpeza.
        
        Args:
            cleaned: Boolean indicando se houve limpeza
        """

        if cleaned:
            self.score += 1


class MeasureCleanAndMovePositive:
    """
    Métrica que equilibra limpeza e movimentação.
    Incentiva limpeza eficiente com menos movimentos.
    """
    
    def __init__(self):
        """Inicializa contadores para limpeza, movimento e pontuação."""
        self.score = 0
        self.moves = 0
        self.cleaned = 0

    def update(self, cleaned, moved):
        """
        Atualiza contadores de limpeza e movimento.
        
        Args:
            cleaned: Boolean indicando se houve limpeza
            moved: Boolean indicando se houve movimento
        """

        if cleaned:
            self.score += 1
            self.cleaned += 1
        if moved:
            self.moves += 1

    def final_score(self):
        """
        Calcula pontuação final: sujeiras limpas - movimentos.
        Quanto maior o valor, mais eficiente o agente.
        
        Returns:
            Pontuação final (mínimo 0)
        """
        
        return max(0, self.cleaned - self.moves)