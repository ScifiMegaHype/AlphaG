class Goal():
    def __init__(self, scorer: str, number_of_goals: int, team_ranking: int, opponent_ranking: int, team_goal_count: int, opponent_goal_count: int, last_ranking: int):
        self.scorer = scorer
        self.number_of_goals = number_of_goals
        self.team_ranking = team_ranking
        self.opponent_ranking = opponent_ranking
        self.team_goal_count = team_goal_count
        self.opponent_goal_count = opponent_goal_count
        self.last_ranking = last_ranking

    def alphaG(self): # Takes into account caliber of opponents scored against
        return self.number_of_goals * (1 + (self.team_ranking/self.last_ranking) - (self.opponent_ranking/self.last_ranking))
        
    def alphaGv2(self): # Additionally takes into account final game state
        multiplier = .5 # Normalises a 1-0 winning goal for evenly matched teams as a alphaG of 1
        return multiplier * self.alphaG() * (1 + (self.number_of_goals)/(self.team_goal_count+self.opponent_goal_count))
