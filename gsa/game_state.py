import flower
import field
import person

class GameState:
    def __init__(self, deployment_file):
        self.flowers = flower.readFlowersFromDeploymentYAML(deployment_file)
        self.field = field.Field(deployment_file)
        self.people = person.People()
        self.stateful_games = []

    def runStatelessGame(self, game):
        game.run(self.flowers)

    def runStatefulGame(self, game):
        self.stateful_games.append(game)

    def clearStatefulGames(self):
        for game in self.stateful_games:
            game.stop(self)
        self.stateful_games = []

    def updateStatefulGames(self):
        self.stateful_games = [g for g in self.stateful_games if not g.isDone()]
        for game in self.stateful_games:
            game.runLoop(self)
