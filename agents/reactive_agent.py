import random


class ReactiveAgent:
    """
    Agente reativo simples que toma decisões apenas com base na percepção atual,
    sem manter modelo do ambiente ou histórico de ações.
    """
    
    def select_action(self, percept):
        """
        Seleciona uma ação com base na percepção atual.
        Limpa se estiver sujo, caso contrário move aleatoriamente.
        
        Args:
            percept: Percepção local do ambiente
            
        Retorna:
            Ação a ser executada (CLEAN, UP, DOWN, LEFT, RIGHT)
        """
        
        if percept['current_dirty']:
            return 'CLEAN'
        else:
            actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
            # Tenta qualquer direção, mas penalidade só conta se movimento for possível
            return random.choice(actions)