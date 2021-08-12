# Scrabble
Graphic Implementation of Scrabble (with TKinter), including an artificial player.

# Requirements
- Python 3.8+
- TKinter
- Pandas
- NumPy

# Gameplay
This is a 2-player graphic implementation of Scrabble.  There are 2 game modes: human vs human or human vs computer.

To place a word, simply click on a tile and click on the square you'd like to move it to.  

You can use the draft submit button to check whether a move is valid and how many points it would score.  Full move validation and scoring is implemented.  

It is also possible to swap tiles as a move.

Once you "final submit" a valid move, it is the turn of the other player or computer.

The computer player uses a heuristic approach to finding high-scoring moves.  As the game progresses, the time for the computer to make a move increases, up to approximately 1 minute.

The winner is the player with more points when the tiles run out.
