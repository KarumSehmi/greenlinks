from django.core.management.base import BaseCommand
from django.utils import timezone
from playergame.models import DailyGame
from playergame.utils import precompute_links, load_and_preprocess_player_data
import random
from playergame.models import GameSession

class Command(BaseCommand):
    help = 'Precompute game rounds for the next set of days'
    USED_PAIRS_FILE = 'used_pairs.txt'  # File to store used player pairs

    def handle(self, *args, **kwargs):
        player_data = load_and_preprocess_player_data()

        GameSession.objects.all().delete()
        

        # Define the three separate lists of players
        current_popular_players = [
            "Lionel Messi", "Cristiano Ronaldo", "Neymar", "Kylian Mbappé", "Mohamed Salah", "Virgil van Dijk", "Kevin De Bruyne", 
            "Harry Kane", "Karim Benzema", "Robert Lewandowski", "Antoine Griezmann", "Sadio Mané", "Raheem Sterling", 
            "Gianluigi Donnarumma", "Thibaut Courtois", "Jan Oblak", "Ederson", "Alisson Becker", "Marc-André ter Stegen", 
            "Jadon Sancho", "Kai Havertz", "Joshua Kimmich", "Leon Goretzka", "Matthijs de Ligt", "Frenkie de Jong", 
            "Achraf Hakimi", "Romelu Lukaku", "Erling Haaland", "Phil Foden", "Jack Grealish", "Marcus Rashford", 
            "Christian Pulisic", "Bruno Fernandes", "Timo Werner", "Hakim Ziyech", "Riyad Mahrez", "João Cancelo", 
            "Ilkay Gündogan", "Aymeric Laporte", "Raphael Varane", "Victor Osimhen", "Fikayo Tomori", "Mason Mount", 
            "Rodri", "Dani Olmo", "Pedri", "Gavi", "Ansu Fati", "Vinícius Júnior", "Federico Valverde", "Dusan Vlahović", 
            "Lautaro Martínez", "Mason Greenwood", "Martin Ødegaard", "Alexander Isak", "Jurrien Timber", "James Maddison", 
            "Declan Rice", "Phil Jones", "Richarlison", "Gabriel Martinelli", "Bukayo Saka", "Federico Chiesa", 
            "Manuel Locatelli", "Marcos Llorente", "Jules Koundé", "Rúben Dias", "João Félix", "Alphonso Davies", 
            "Weston McKennie", "Giovani Lo Celso", "Rodrigo Bentancur", "Kalvin Phillips", "Lucas Paquetá", 
            "Dominic Calvert-Lewin", "Gerard Moreno", "Ferran Torres", "Nuno Mendes", "Jamal Musiala", "Eduardo Camavinga", 
            "Jude Bellingham", "Giovanni Reyna", "Sergiño Dest", "Reece James", "Kai Havertz", "Tammy Abraham", 
            "Federico Dimarco", "Matthieu Guendouzi", "Nicolo Zaniolo", "Florian Neuhaus", "Dani Carvajal", "Jorginho", 
            "Karim Adeyemi", "Dušan Tadić", "Florian Wirtz", "Leroy Sané", "Moussa Diaby", "Ruben Loftus-Cheek", 
            "Cristian Romero", "Achraf Hakimi", "Yannick Carrasco", "Davinson Sánchez", "Wilfried Zaha", "Hirving Lozano", 
            "Steven Bergwijn", "Mikel Oyarzabal", "Sandro Tonali", "Manuel Akanji", "Alessandro Bastoni", "John McGinn", 
            "James Ward-Prowse", "Allan Saint-Maximin", "Declan Rice", "Emiliano Martínez", "Diogo Jota", "Mason Mount", 
            "Edouard Mendy", "Aaron Ramsdale", "Ben White", "Tyrick Mitchell", "Conor Gallagher"
            ]

        
        current_normal_players = [
            "Gareth Bale", "Paul Pogba", "Toni Kroos", "Dani Carvajal", "Gerard Moreno", "Sergio Agüero", "Eden Hazard", 
            "Thiago Silva", "Benjamin Mendy", "Kalidou Koulibaly", "Donny van de Beek", "Memphis Depay", "Thomas Lemar", 
            "Kieran Trippier", "Yannick Carrasco", "Keylor Navas", "Wojciech Szczęsny", "Samir Handanović", "Emiliano Martínez", 
            "Jordan Pickford", "Kasper Schmeichel", "Rui Patrício", "Pepe Reina", "Joe Hart", "Nelson Semedo", "Nelson Oliveira", 
            "Saúl Ñíguez", "Álvaro Morata", "César Azpilicueta", "Marcos Alonso", "Jordi Alba", "Mario Götze", "Julian Draxler", 
            "Sami Khedira", "Christoph Metzelder", "Hakan Çalhanoğlu", "Emre Can", "Serge Gnabry", "Niklas Süle", "Leroy Sané", 
            "Thorgan Hazard", "Marco Reus", "Mats Hummels", "Leonardo Bonucci", "Giorgio Chiellini", "Federico Chiesa", 
            "Juan Cuadrado", "Paulo Dybala", "Lorenzo Insigne", "Dries Mertens", "Arkadiusz Milik", "Hirving Lozano", 
            "Nicolò Barella", "Alexis Sánchez", "Henrikh Mkhitaryan", "Edin Džeko", "Chris Smalling", "Diego Costa", 
            "Thomas Partey", "Dani Parejo", "Frenkie de Jong", "Memphis Depay", "Daley Blind", "Joel Matip", "Adrien Rabiot", 
            "Lucas Hernández", "Moussa Sissoko", "Serge Aurier", "Thomas Lemar", "Aymeric Laporte", "Dele Alli", "Youri Tielemans", 
            "Steven Bergwijn", "Lucas Digne", "Florian Thauvin", "Axel Witsel", "Dan-Axel Zagadou", "Bernd Leno", "Alvaro Odriozola", 
            "Dani Olmo", "Ousmane Dembélé", "Ferran Torres", "Marcos Acuña", "Roberto Firmino", "Diogo Jota", "Pablo Sarabia", 
            "Raúl Jiménez", "Willian", "Pedro Neto", "Ferran Torres", "Bernardo Silva", "Wilfried Zaha", "Nathan Aké", 
            "Kieran Tierney", "Callum Wilson", "Allan Saint-Maximin", "Raphinha", "Lucas Torreira", "Renato Sanches", "Isco", 
            "Brahim Diaz", "Mario Hermoso", "Eric García", "Angelino", "Pierre-Emile Højbjerg", "Tammy Abraham", "Theo Hernandez", 
            "Alessio Romagnoli", "Sandro Tonali", "Dani Ceballos", "Daniel James", "Luke Shaw", "John Stones", "Emil Forsberg", 
            "Emiliano Buendía", "Aaron Ramsdale", "Nicolas Pepe", "Bertrand Traoré", "Emi Martinez", "Wesley Fofana", "Ben White", 
            "Max Aarons", "Patrick Bamford", "Michail Antonio", "Tyrone Mings", "Oliver Skipp", "Diego Llorente", "Ezri Konsa", 
            "Tyrick Mitchell", "Marc Cucurella", "Ferran Jutglà", "Ruben Neves", "Francisco Trincão", "André Silva", 
            "Dominic Szoboszlai", "Bryan Gil", "Giovanni Simeone", "Takefusa Kubo", "Kaoru Mitoma", "Adama Traoré", "Danny Ings"
        ]


        older_popular_players = [
            "Ronaldinho", "Thierry Henry", "Zinedine Zidane", "Andrea Pirlo", "David Beckham", "Xavi", "Andres Iniesta", "Kaka", 
            "Frank Lampard", "Steven Gerrard", "Wayne Rooney", "Zlatan Ibrahimović", "Francesco Totti", "Alessandro Del Piero", 
            "Paolo Maldini", "Iker Casillas", "Gianluigi Buffon", "Sergio Ramos", "Gerard Piqué", "Carles Puyol", "Luis Suárez", 
            "Luka Modrić", "Didier Drogba", "Samuel Eto'o", "Arjen Robben", "Franck Ribéry", "Manuel Neuer", "Mesut Özil", 
            "Dani Alves", "Marcelo", "Nemanja Vidić", "Patrice Evra", "Philipp Lahm", "David Villa", "Fernando Torres", 
            "Carlos Tevez", "Robin van Persie", "Clarence Seedorf", "Cafu", "Javier Zanetti", "Claude Makélélé", "Patrick Vieira", 
            "Gennaro Gattuso", "David Silva", "Juan Mata", "Ángel Di María", "Wesley Sneijder", "Maicon", "Michael Ballack", 
            "Bastian Schweinsteiger", "Miroslav Klose", "Luca Toni", "Xabi Alonso", "Fernando Hierro", "Marco Materazzi", 
            "Lilian Thuram", "Fabien Barthez", "Diego Forlán", "Deco", "Hernán Crespo", "Rivaldo", "Ruud van Nistelrooy", 
            "Alan Shearer", "Rio Ferdinand", "John Terry", "Sol Campbell", "Javier Mascherano", "Roberto Carlos", "Diego Godín", 
            "Pepe", "Yaya Touré", "Edinson Cavani", "Gianfranco Zola", "George Weah", "Roberto Baggio", "Paolo Rossi", "Roy Keane", 
            "Gary Neville", "Jaap Stam", "Nemanja Matić", "Diego Milito", "Hernanes", "Antonio Di Natale", "Gabriel Batistuta", 
            "Jürgen Klinsmann", "Edgar Davids", "Rui Costa", "Alessandro Nesta", "Christian Vieri", "Filippo Inzaghi", 
            "David Trezeguet", "Fernando Redondo", "Gabriel Heinze", "Fernando Morientes", "Roberto Ayala", "Simone Inzaghi", 
            "Samuel Umtiti", "Mario Gomez", "Pierre-Emerick Aubameyang", "Thomas Müller", "Javi Martínez", "Jerome Boateng", 
            "Javier Hernández", "Arturo Vidal", "Ivan Rakitić", "Ivan Perišić", "Mario Mandžukić", "Radamel Falcao", 
            "Gonzalo Higuaín", "Dusan Tadić", "Edwin van der Sar", "Dida", "Victor Valdés", "Jens Lehmann", "Petr Čech", 
            "Clarence Seedorf", "Michael Owen", "Alessandro Nesta", "Alessandro Costacurta", "Jaap Stam", "Pavel Nedvěd", 
            "George Hagi", "Gheorghe Popescu", "Jay-Jay Okocha", "Roberto Carlos", "Franck de Boer", "Fernando Hierro", 
            "Patrick Kluivert", "Fernando Redondo", "Claudio Taffarel", "Tino Asprilla", "Hristo Stoichkov", "Carlos Valderrama", 
            "Lothar Matthäus", "Roberto Donadoni", "Rudi Völler", "Bebeto", "Davor Šuker", "Zico", "Johan Cruyff", 
            "Ryan Giggs", "Michael Carrick", "Ashley Cole", "Didier Drogba", "Nicolas Anelka", "Peter Crouch", "Gareth Barry"
        ]


        # Link types for each round
        used_pairs_set = self.load_used_pairs()

        # Link types for each round
        link_types = ["both", "both", "club"]

        # Precompute for the next 10 days
        for i in range(90):
            game_date = timezone.now().date() + timezone.timedelta(days=i)
            
            # Generate three valid pairs of players for each day
            daily_pairs = []
            link_lengths = [2, 3, 3]  # Required lengths for each round

            # Round 1: Use only current_popular_players
            while True:
                pair = tuple(sorted(random.sample(current_popular_players, 2)))
                pair_str = f"{pair[0]},{pair[1]}"

                if pair_str in used_pairs_set:
                    print("already used", player1, player2)
                    continue

                precomputed_link = precompute_links([pair], player_data, ["both"])

                if precomputed_link and len(precomputed_link[0]) == link_lengths[0]:
                    daily_pairs.append(pair)
                    used_pairs_set.add(pair_str)  # Add to used pairs set
                    self.save_pair(pair_str)  # Save to file
                    break

            # Round 2: Use one current_popular and one current_normal
            while True:
                player1 = random.choice(current_popular_players)
                player2 = random.choice(current_normal_players)
                pair = tuple(sorted([player1, player2]))
                pair_str = f"{pair[0]},{pair[1]}"

                if pair_str in used_pairs_set:

                    print("already used", player1, player2)
                    continue

                precomputed_link = precompute_links([pair], player_data, ["both"])

                if precomputed_link and len(precomputed_link[0]) == link_lengths[1]:
                    daily_pairs.append(pair)
                    used_pairs_set.add(pair_str)
                    self.save_pair(pair_str)
                    break

            # Round 3: Use one current_popular and one older_popular
            while True:
                player1 = random.choice(current_popular_players)
                player2 = random.choice(older_popular_players)
                pair = tuple(sorted([player1, player2]))
                pair_str = f"{pair[0]},{pair[1]}"

                if pair_str in used_pairs_set:
                    print("already used", player1, player2)
                    continue

                precomputed_link = precompute_links([pair], player_data, ["club"])

                if precomputed_link and len(precomputed_link[0]) == link_lengths[2]:
                    daily_pairs.append(pair)
                    used_pairs_set.add(pair_str)
                    self.save_pair(pair_str)
                    break

            # Precompute the links for the valid pairs
            precomputed_links = precompute_links(daily_pairs, player_data, link_types)

            # Store in the database
            daily_game, created = DailyGame.objects.update_or_create(
                date=game_date,
                defaults={
                    'player_pairs': daily_pairs,
                    'precomputed_links': precomputed_links,
                    'link_types': link_types
                }
            )

            # Print statements to check the stored data
            print(f"{'Created' if created else 'Updated'} DailyGame for {game_date}")
            print(f"Player Pairs: {daily_game.player_pairs}")
            print(f"Link Types: {daily_game.link_types}")
            print(f"Precomputed Links: {daily_game.precomputed_links}\n")

        self.stdout.write(self.style.SUCCESS('Successfully precomputed game rounds for the next 30 days'))

    def load_used_pairs(self):
        """Load previously used pairs from the file."""
        used_pairs_set = set()
        try:
            with open(self.USED_PAIRS_FILE, 'r', encoding='utf-8') as file:
                for line in file:
                    used_pairs_set.add(line.strip())
        except FileNotFoundError:
            # If the file doesn't exist, return an empty set
            pass
        return used_pairs_set


    def save_pair(self, pair):

        with open(self.USED_PAIRS_FILE, 'a', encoding='utf-8') as file:
            file.write(f"{pair}\n")
