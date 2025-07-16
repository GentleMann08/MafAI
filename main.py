from ollama import chat, generate
from random import randint, shuffle

class AI:
    model = "qwen3:14b" 
    temperature = 0.9

    @staticmethod
    def checkStreaming(response, stream, is_chat) -> str:
        if stream:
            full_response = ""
            for chunk in response:
                print(chunk['message']['content'] if is_chat else chunk['response'], end = '', flush=True)
                full_response += chunk['message']['content'] if is_chat else chunk['response']
            
            print()
            return full_response
        else:
            return response['message']['content'] if is_chat else response['response']

    @staticmethod
    def shortGen(prompt, seed = randint(0, 100), think = False, stream = True) -> str:
        response = generate(
            model = AI.model,
            prompt = prompt,
            options = {"temperature": AI.temperature, "seed": seed},
            think = think,
            stream = stream
        )

        return AI.checkStreaming(response = response, stream = stream, is_chat = False)
    
    @staticmethod
    def shortChat(context, seed = randint(0, 100), think = True, stream = True):
        response = chat(
            model = AI.model,
            messages = context,
            options = {"temperature": AI.temperature, "seed": seed},
            think = think,
            stream = stream
        )

        return AI.checkStreaming(response = response, stream = stream, is_chat = True)
    
class Game:
    def __init__(self, players_count = 6, roles = ['Mafia', 'Doctor', 'Citizen', 'Citizen', 'Citizen', 'Citizen']):
        self.players_count = players_count

        shuffle(roles)
        self.roles = roles

        self.features = {
            'names': [],
            'characters': [],
            'biography': [],
            'roles': []
        }

        self.players = []

        self.game_context = []

    def playersGeneration(self):
        for index in range(self.players_count):
            player = Player()
            self.players.append(player)
            player.generatePlayerByAI(players = self.features, role = self.roles[index])

    def addToGameContext(self, role, content):
        content_dictionary = {
            'role': f'{role.name} {role.surname}' if type(role) == Player else str(role),
            'content': content
        }

        for player in self.players:
            player.context.append(content_dictionary)

    def meeting(self, topic='Пришла пора представиться!', personal_topic="Расскажите о себе другим игрокам."):
        self.addToGameContext(role='game', content=topic)
        for player in self.players:
            if player.is_alive:

                player.context.append({
                    'role': 'game',
                    'content': f'{player.name} {player.surname}, ваша очередь: {personal_topic}'
                })

                statement = AI.shortChat(player.context)
                self.addToGameContext(role=player, content=statement)

                print(player.context)

class Player:
    def generatePlayerByAI(self, players, role = "Citizen"):
        self.role = role
        self.is_alive = True

        player_name = AI.shortGen(prompt = f"Сгенерируй имя и фамилию на польский манер (на русском языке) для игры в мафию в формате 'name-surname' (всего два слова через пробел). Уже имеются: {players["names"]}.")
        self.name, self.surname = player_name.split()[0], player_name.split()[1]
        players["names"].append(f'{self.name} {self.surname}')

        character_prompt = f"Персонажа зовут {self.name} {self.surname}. Сгенерируйте характер персонажа одним предложением в рамках соционики. Не углубляйся в биографию. Уже есть следующие характеры: {players["characters"]}. Характер: "
        self.character = AI.shortGen(prompt = character_prompt)
        players["characters"].append(self.character)

        biography_prompt = f"Персонажа зовут {self.name} {self.surname}. Характер персонажа: {self.character}. Сгенерируй профессию и прошлое персонажа двумя предложениями. Уже есть следующие биографии: {players["biography"]}. Биография: "
        self.biography = AI.shortGen(prompt = biography_prompt)
        players["biography"].append(self.biography)

        self.context = [
            {
                'role': 'system',
                'content': 'Вы - игрок в настольную игру "Мафия". Ваша задача не выдавать свою роль и бороться с игроками из других команд. Сейчас Вам будут выданы Ваши данные. Придерживайтесь их.'
            },
            {
                'role': 'game',
                'content': f'Ваше имя: "{self.name} {self.surname}", Ваш характер: "{self.character}", Ваша биография: "{self.biography}", Ваша роль: "{self.role}".'
            }
        ]

    def generatePlayerByInput(self, name, surname, character, biography):
        self.name = name
        self.surname = surname
        self.character = character
        self.biography = biography


def main():
    Mafia = Game(players_count = 3)

    Mafia.playersGeneration()

    players = ""
    for player in Mafia.players:
        players += f'{player.name} {player.surname}, '

    Mafia.addToGameContext(role = 'game', content = f"Играют следующие игроки: {players[:-2]}.")
    input(Mafia.game_context)

    # Mafia.meeting()

if __name__ == "__main__":
    main()