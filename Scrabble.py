import random
from tkinter import *
import copy
import pandas as pd
import numpy as np

'''
- This is the final version, though there are bound to still be some bugs
A few notes about playing against the computer:
- Basis of algorithm:
    For each tile on the board:
        - find all words you can make incorporating said tile & other tiles in possession
        - select the 10 highest scoring words, based on pure letter values, ignoring any potential bonuses or extra words created
        - place each word on the potential board horizontally and vertically
        - check if potential board is a valid move
        - if so, check if the score of the move is greater than the current highest-scoring move 
        - if so, change the stored value of highest score to current value, and save the current board state
- This is not efficient, but seems to do the trick within a reasonable time (up to 60 seconds)
- Gets slower as more tiles added (up to a minute towards the end of the game)
- Finds it harder to find moves as more tiles added, and may fail to find moves towards end of game
- Often finds really weird/wacky words in scrabble dictionary
- Computer can't currently play first move
'''

class Game:
    #creating class variables which can be reused for every game
    subscripts = [' ','₁','₂','₃','₄','₅','₆','₇','₈','₉','ₓ']
    letter_values = {" ": 0, "a": 1 , "b": 3 , "c": 3 , "d": 2 , "e": 1 , "f": 4 , "g": 2 , "h": 4 , "i": 1 , "j": 8 , "k": 5 , "l": 1 , "m": 3 , "n": 1 , "o": 1 , "p": 3 , "q": 10, "r": 1 , "s": 1 , "t": 1 , "u": 1 , "v": 4 , "w": 4 , "x": 8 , "y": 4 , "z": 10}
    inital_tiles = ['j','k','q','x','z',*(['b']*2),*(['c']*2),*(['f']*2),*(['h']*2),*(['m']*2),*(['p']*2),*(['v']*2),*(['w']*2),*(['y']*2),*(['g']*3),*(['d']*4),*(['l']*4),*(['s']*4),*(['u']*4),*(['n']*6),*(['r']*7),*(['t']*7),*(['o']*8),*(['a']*9),*(['i']*9),*(['e']*12)]
    dic = open('large_dic.txt').read().split()
    dic_df = pd.DataFrame({'word':dic})
    global values 
    values = letter_values
    #need to declare global copy of letter_values, as for some reason below line doesn't work otherwise
    dic_df['score'] = [sum([values[l] for l in word]) for word in dic_df['word']]
    large_dic = set(dic)
    #Locations of multi-word tiles
    triple_word = {(0,0),(0,7),(0,14),(7,14),(14,14)}
    triple_letter = {(5,1),(9,1),(9,5),(5,5),(13,5),(9,9),(13,9)}
    double_word = {(1,1),(2,2),(3,3),(4,4),(13,13),(12,12),(11,11),(10,10), (13,1),(12,2),(11,3),(10,4),(7,7)}
    double_letter = {(0,3),(2,6),(3,7),(2,8),(3,14),(11,14),(7,11),(6,12),(8,12),(6,6),(8,8),(8,6)}
    #constants - these values may need to be altered to fit your OS & screen size3301301
    DEFAULT_COLOR = 'medium sea green'#'AntiqueWhite3'
    TILE_COLOR = 'blanched almond'
    TW_COLOR = 'IndianRed2'
    TL_COLOR = 'deep sky blue'
    DW_COLOR = 'light pink'
    DL_COLOR = 'PaleTurquoise1'
    CENTRE_COLOR = 'gold'
    BOARD_SIZE = 15
    SIDE_PANEL_SIZE = 5
    OFFSET_X = 0
    OFFSET_Y = 6
    TILE_SIZE = 30
    TITLE_FONT_SIZE = 30
    SUBTITLE_FONT_SIZE = 17
    INFO_FONT_SIZE = 17
    TILE_FONT_SIZE = 20
    #TKinter Window
    window = Tk()
    window.geometry("900x700") 
    window.resizable(0, 0)


    def __init__(self, player2):
        self.__tiles_remaining = copy.deepcopy(Game.inital_tiles)
        random.shuffle(self.__tiles_remaining)
        self.__words_produced = []
        self.__tiles_occupied = set()
        self.__confirmed_board = [[' ' for x in range(Game.BOARD_SIZE)] for y in range(Game.BOARD_SIZE)]
        self.__potential_board = copy.deepcopy(self.__confirmed_board)
        self.__current_turn = 0
        self.__players = [Player(1)]
        if player2 == 'Computer':
            self.__players.append(Computer(2))
        else:
            self.__players.append(Player(2))
        self.__top_up_tiles()
        self.__buttons = []
        self.__player_tile_buttons = []
        self.__board_tile_selected = False
        self.__tile_swap = False
        self.__game_over = False
        self.__to_be_swapped = []
        self.__selected_board_tile_pos = tuple()
        self.__selected_board_tile_char = ' '
        self.__move_feedback = '                                        '
        self.__player_tile_selected = False
        self.__selected_player_tile_pos = -1
        self.__selected_player_tile_char = ' '
        self.__new_tiles = set()
        self.__round = 0
        self.__create_interface()
        self.__winner_message = ''
        

    def __create_interface(self):
        self.__create_widgets()
        self.__update_live_info()
        self.__create_board()
        self.__create_tiles()
    
    def __update_turn_interface(self):
        self.__update_tiles()
        self.__update_board()
    
    def __update_full_interface(self):
        self.__update_live_info()
        self.__update_tiles()
        self.__update_board()

    def __create_widgets(self):
        title = Label(Game.window, text = "SCRABBLE", font=("Comic Sans MS", Game.TITLE_FONT_SIZE, 'bold'))
        title.grid(row = 0, columnspan = Game.BOARD_SIZE)
        #needs to be changed if AI implemented
        self.__players_label = Label(Game.window, font=("Arial", Game.SUBTITLE_FONT_SIZE, 'italic'))
        self.__players_label.grid(row = 1, columnspan = Game.BOARD_SIZE, padx = 20)
        restart_human = Button(Game.window, text = 'Restart vs Human', command = self.__restart_vs_human, font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'), width = 17)
        restart_human.grid(row = 2, column = Game.OFFSET_X, columnspan = Game.BOARD_SIZE//2, pady = 10)
        restart_human = Button(Game.window, text = 'Restart vs Computer', command = self.__restart_vs_computer, font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'), width = 17)
        restart_human.grid(row = 2, column = Game.OFFSET_X + Game.BOARD_SIZE//2 + 1, columnspan = Game.BOARD_SIZE//2)
        reset_tiles = Button(Game.window, text = 'Restart Your Move', command = self.__restart_move, font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'), width = 17)
        reset_tiles.grid(row = 0, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)
        draft_submit_move = Button(Game.window, text = 'Draft Submit Move', command = self.__handle_draft_submit_move, font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'), width = 17)
        draft_submit_move.grid(row = 1, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)
        submit_move = Button(Game.window, text = 'Final Submit Move', command = self.__handle_submit_move, font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'), width = 17)
        submit_move.grid(row = 2, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)
        swap_tiles = Button(Game.window, text = 'Swap Tiles', command = self.__handle_swap_tiles, font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'), width = 17)
        swap_tiles.grid(row = 3, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)
        feedback_headline = Label(Game.window, text = 'Feedback on latest submission:', font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'))
        feedback_headline.grid(row = Game.OFFSET_Y + 4, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE,  padx = 20, sticky = W)
        self.__feedback_label = Label(Game.window, font=("Arial", Game.INFO_FONT_SIZE))
        self.__feedback_label.grid(row = Game.OFFSET_Y+5, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)
        current_status_headline = Label(Game.window, font = ("Arial", Game.SUBTITLE_FONT_SIZE, "bold"), text = 'Current Status:')
        current_status_headline.grid(row = Game.OFFSET_Y + 7, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)
        self.__current_status_label = Label(Game.window, font=("Arial", Game.INFO_FONT_SIZE))
        self.__current_status_label.grid(row = Game.OFFSET_Y + 8, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)
        self.__current_turn_label = Label(Game.window, font=("Arial", Game.INFO_FONT_SIZE))
        self.__current_turn_label.grid(row = 3, column = Game.OFFSET_X, columnspan = Game.BOARD_SIZE//2 + 2, sticky = W)
        self.__tiles_left_label = Label(Game.window, font=("Arial", Game.INFO_FONT_SIZE))
        self.__tiles_left_label.grid(row = 3, column = Game.OFFSET_X + Game.BOARD_SIZE//2 + 1, columnspan = Game.BOARD_SIZE//2, sticky = E, pady = 5)
        scores_headline = Label(Game.window, text = "Current Scores:", font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'))
        scores_headline.grid(row = Game.OFFSET_Y, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)
        self.__scores_labels = []
        for i in range(2):
            score_label = Label(Game.window, font = ("Arial", Game.INFO_FONT_SIZE))
            score_label.grid(row = Game.OFFSET_Y + 1 + i, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)
            self.__scores_labels.append(score_label)
        self.__tile_headline = Label(Game.window, font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'))
        self.__tile_headline.grid(row = Game.OFFSET_Y + Game.BOARD_SIZE + 1, column = Game.OFFSET_X, columnspan = Game.BOARD_SIZE,  sticky = W)
        key = Label(Game.window, text = "Color Key:", font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'))
        key.grid(row = Game.OFFSET_Y+10, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)
        dw = Label(Game.window, text = "Double Word", font=("Arial", Game.INFO_FONT_SIZE, 'italic'), fg = Game.DW_COLOR)
        dw.grid(row = Game.OFFSET_Y+11, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)
        dl = Label(Game.window, text = "Double Letter", font=("Arial", Game.INFO_FONT_SIZE, 'italic'), fg = Game.DL_COLOR)
        dl.grid(row = Game.OFFSET_Y+12, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)
        tw = Label(Game.window, text = "Triple Word", font=("Arial", Game.INFO_FONT_SIZE, 'italic'), fg = Game.TW_COLOR)
        tw.grid(row = Game.OFFSET_Y+13, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)
        tl = Label(Game.window, text = "Triple Letter", font=("Arial", Game.INFO_FONT_SIZE, 'italic'), fg = Game.TL_COLOR)
        tl.grid(row = Game.OFFSET_Y+14, column = Game.BOARD_SIZE, columnspan = Game.SIDE_PANEL_SIZE, padx = 20, sticky = W)


    def __update_live_info(self):
        self.__players_label.config(text = '        ' + self.__players[0].get_type() + ' v ' + self.__players[1].get_type() + '        ')
        self.__feedback_label.config(text = self.__move_feedback + '            ')
        self.__current_turn_label.config(text = 'Current Turn: ' + self.__players[self.__current_turn].get_name() + '   ')
        self.__tiles_left_label.config(text = "     Tiles Remaining: " + str(len(self.__tiles_remaining)))
        for i in range(2):
            self.__scores_labels[i].config(text = self.__players[i].get_name() + ': ' + str(self.__players[i].get_current_points()) + '     ')
        self.__tile_headline.config(text = self.__players[self.__current_turn].get_name() + ' tiles:')
        if self.__game_over:
            self.__current_status_label.config(text = 'GAME OVER: ' + self.__winner_message + '                 ')
        elif self.__players[self.__current_turn].get_type() == 'Human' and not self.__tile_swap:
            self.__current_status_label.config(text = 'Awaiting human submission                               ')
        elif self.__players[self.__current_turn].get_type() == 'Human' and  self.__tile_swap:
            self.__current_status_label.config(text = 'Please select tiles to be swapped                        ')
        else:
            self.__current_status_label.config(text = 'Patience please...computer is generating moves.')
        
    
    def __create_board(self):
        self.__buttons = []
        for y in range(Game.BOARD_SIZE):
            for x in range(Game.BOARD_SIZE):
                button_frame = Frame(Game.window, width = Game.TILE_SIZE, height = Game.TILE_SIZE)
                button_frame.propagate(False)
                button_frame.grid(row = Game.OFFSET_Y + y, column = Game.OFFSET_X + x, sticky = "nsew") 
                button_tile = Button(button_frame, text = '  ', font=("Arial", Game.TILE_FONT_SIZE), relief = 'groove')
                button_tile.bind('<Button 1>', self.__handle_button_click)
                button_tile.pack(expand=True, fill=BOTH)
                self.__buttons.append(button_tile)
        self.__update_board()

    def __create_tiles(self):
        self.__player_tile_buttons = []
        tiles = self.__players[self.__current_turn].get_tiles()
        for i in range(7):
            tile_frame = Frame(Game.window, width = Game.TILE_SIZE, height = Game.TILE_SIZE)
            tile_frame.propagate(False)
            tile_frame.grid(row = Game.BOARD_SIZE + Game.OFFSET_Y + 2, column = Game.OFFSET_X + i, sticky = "nsew", pady = 4)
            char = tiles[i]
            color = Game.TILE_COLOR
            if char == ' ': color = Game.DEFAULT_COLOR
            text_color = 'red'
            if self.__player_tile_selected and self.__selected_player_tile_pos == i: text_color = 'green'
            player_tile = Button(tile_frame, text = char.upper() + Game.subscripts[Game.letter_values[char]], font=("Arial", Game.TILE_FONT_SIZE), relief = 'raised', bg = color, fg = text_color)
            player_tile.bind('<Button 1>', self.__handle_tile_click)
            player_tile.pack(expand=True, fill=BOTH)
            self.__player_tile_buttons.append(player_tile)
    
    def __update_tiles(self):
        tiles = self.__players[self.__current_turn].get_tiles()
        for i in range(7):
            char = tiles[i]
            color = Game.TILE_COLOR
            if char == ' ': color = Game.DEFAULT_COLOR
            text_color = 'red'
            if self.__player_tile_selected and self.__selected_player_tile_pos == i: text_color = 'green'
            if self.__tile_swap and i in self.__to_be_swapped: text_color = 'blue'
            self.__player_tile_buttons[i].configure(text = char.upper() + Game.subscripts[Game.letter_values[char]], bg = color, fg = text_color)
            

    def __update_board(self):
        for b in range(Game.BOARD_SIZE**2):
            y = b//15
            x = b % 15
            self.__buttons[b].config(text = self.__potential_board[y][x].upper() + Game.subscripts[Game.letter_values[self.__potential_board[y][x]]])
            if self.__potential_board[y][x] != ' ':
                self.__buttons[b].config(bg = Game.TILE_COLOR)
                if self.__board_tile_selected and self.__selected_board_tile_pos == (y,x):
                    self.__buttons[b].config(fg = 'green')
                elif self.__confirmed_board[y][x] == ' ':
                    self.__buttons[b].config(fg = 'red')
                else:
                    self.__buttons[b].config(fg = 'black')
                    self.__buttons[b].bind('<Button 1>', self.__handle_inactive_button)
            else:
                color = Game.DEFAULT_COLOR
                if (y,x) in Game.double_word or (x,y) in Game.double_word: color = Game.DW_COLOR 
                elif (y,x) in Game.triple_word or (x,y) in Game.triple_word: color = Game.TW_COLOR 
                elif (y,x) in Game.triple_letter or (x,y) in Game.triple_letter: color = Game.TL_COLOR 
                elif (y,x) in Game.double_letter or (x,y) in Game.double_letter: color = Game.DL_COLOR 
                self.__buttons[b].config(bg = color)

    def __handle_button_click(self, event):
        #retrieving the locations of a button click (quite complicated as buttons are stored in frames)
        if self.__players[self.__current_turn].get_type() == 'Human' and not self.__game_over and not self.__tile_swap:
            location = self.__buttons.index(event.widget)
            y = location//15
            x = location % 15
            if self.__potential_board[y][x] == ' ' and self.__player_tile_selected:
                self.__potential_board[y][x] = self.__selected_player_tile_char
                self.__players[self.__current_turn].remove_tile(self.__selected_player_tile_pos)
                self.__player_tile_selected = False
                self.__new_tiles.add((y,x))
            elif self.__potential_board[y][x] == ' ' and self.__board_tile_selected:
                self.__potential_board[y][x] = self.__selected_board_tile_char
                self.__potential_board[self.__selected_board_tile_pos[0]][self.__selected_board_tile_pos[1]] = ' '
                self.__new_tiles.remove(self.__selected_board_tile_pos)
                self.__board_tile_selected = False
                self.__new_tiles.add((y,x))
            elif self.__potential_board[y][x] != ' ':
                self.__board_tile_selected = True
                self.__player_tile_selected = False
                self.__selected_board_tile_pos = (y,x)
                self.__selected_board_tile_char = self.__potential_board[y][x]
            self.__update_turn_interface()
    
    def __handle_inactive_button(self, event):
        pass
    
    def __handle_tile_click(self,event):
        if self.__players[self.__current_turn].get_type() == 'Human' and not self.__game_over:
            location = self.__player_tile_buttons.index(event.widget)
            character = self.__players[self.__current_turn].get_tiles()[location]
            if self.__tile_swap and location not in self.__to_be_swapped:
                self.__to_be_swapped.append(location)
            elif self.__tile_swap and location in self.__to_be_swapped:
                self.__to_be_swapped.remove(location)
            elif self.__board_tile_selected and character == ' ':
                self.__board_tile_selected = False
                self.__players[self.__current_turn].return_tile(location, self.__selected_board_tile_char)
                self.__potential_board[self.__selected_board_tile_pos[0]][self.__selected_board_tile_pos[1]] = ' '
                self.__new_tiles.remove(self.__selected_board_tile_pos)
            elif character != ' ':
                self.__board_tile_selected = False
                self.__player_tile_selected = True
                self.__selected_player_tile_pos = location
                self.__selected_player_tile_char = character
            self.__update_turn_interface()

    def __top_up_tiles(self):
        needed = self.__players[self.__current_turn].get_tiles_needed()
        if needed > len(self.__tiles_remaining): 
            needed = len(self.__tiles_remaining)
        to_be_added = [self.__tiles_remaining.pop() for i in range(needed)]
        self.__players[self.__current_turn].refill_tiles(to_be_added)

    def __restart_vs_human(self):
        self.__init__('Player')
    
    def __restart_vs_computer(self):
        self.__init__('Computer')
    
    def __restart_move(self):
        if self.__players[self.__current_turn].get_type() == 'Human' and not self.__game_over:
            self.__reset_tiles()
            self.__tile_swap = False
            self.__to_be_swapped = []
            self.__update_full_interface()

    
    def __reset_tiles(self):
        chars = []
        for t in self.__new_tiles:
            chars.append(self.__potential_board[t[0]][t[1]])
            self.__potential_board[t[0]][t[1]] = ' '
        self.__new_tiles = set()
        self.__players[self.__current_turn].refill_tiles(chars)
        self.__update_turn_interface()
        self.__board_tile_selected = False
        self.__player_tile_selected = False
    
    def __handle_submit_move(self):
        if self.__players[self.__current_turn].get_type() == 'Human' and not self.__game_over:
            self.__submit_move()
    
    def __handle_draft_submit_move(self):
        if self.__players[self.__current_turn].get_type() == 'Human' and not self.__tile_swap and not self.__game_over:
            self.__check_submission()
            self.__update_full_interface()
    
    def __handle_swap_tiles(self):
        if self.__players[self.__current_turn].get_type() == 'Human' and not self.__game_over:
            if len(self.__new_tiles) > 0:
                self.__reset_tiles()
            self.__tile_swap = True
        self.__update_full_interface()
    
    def __do_swap_tiles(self):
        if len(self.__to_be_swapped) > 0:
            for location in self.__to_be_swapped:
                tile = self.__players[self.__current_turn].get_tile(location)
                self.__tiles_remaining.append(tile)
                self.__players[self.__current_turn].remove_tile(location)
            self.__tile_swap = False
            self.__move_feedback = self.__players[self.__current_turn].get_name() + ' decided to swap ' + str(len(self.__to_be_swapped)) + ' tiles          '
            self.__to_be_swapped = []
            random.shuffle(self.__tiles_remaining)
            return True
        else:
            self.__move_feedback = 'Please select at least 1 tile to be swapped'
            return False

    def __submit_move(self):
        if self.__tile_swap:
            result = self.__do_swap_tiles()
            if result == False:
                print('Invalid submission')
                self.__restart_move()
            else:
                self.__current_turn = (self.__current_turn + 1) % 2
                self.__top_up_tiles()
                self.__round += 1
        else:
            result = self.__check_submission()
            if result == False:
                print('Invalid submission')
                self.__restart_move()
            else:
                words_created = result[0]
                word_scores = result[1]
                self.__players[self.__current_turn].add_words_played(words_created)
                self.__players[self.__current_turn].increment_score(sum(word_scores))
                self.__words_produced = self.__words_produced + words_created
                self.__confirmed_board = copy.deepcopy(self.__potential_board)
                self.__current_turn = (self.__current_turn + 1) % 2
                self.__tiles_occupied = self.__tiles_occupied.union(self.__new_tiles)
                self.__top_up_tiles()
                self.__round += 1
            self.__new_tiles = set()
            self.__check_game_over()
        self.__update_full_interface()
        if result != False and self.__players[self.__current_turn].get_type() == 'Computer':
            Game.window.after(2000,self.__generate_computer_moves)

    def __check_game_over(self):
        if set(self.__players[self.__current_turn].get_tiles()) == {' '} and len(self.__tiles_remaining) == 0:
            self.__game_over = True
            if self.__players[0].get_current_points() == self.__players[1].get_current_points():
                self.__winner_message = 'Tie'
            elif self.__players[0].get_current_points() > self.__players[1].get_current_points():
                self.__winner_message = self.__players[0].get_name() + ' WINS'
            elif self.__players[0].get_current_points() < self.__players[1].get_current_points():
                self.__winner_message = self.__players[1].get_name() + ' WINS'
        
        
    def __check_submission(self):
        x_s = set()
        y_s = set()
        for tile in self.__new_tiles:
            x_s.add(tile[1])
            y_s.add(tile[0])
        if len(x_s) > 1 and len(y_s) > 1:
            self.__move_feedback = 'Place tiles on a single row/column'
            return False
        #Scanning row by row
        unused_tiles = copy.deepcopy(self.__new_tiles)
        new_words = []
        word_scores = []
        complete_tile_usage = False
        for y in range(Game.BOARD_SIZE):
            new_word = False
            old_tile = False
            current_word = ''
            current_word_score = 0
            score_multiplier = 1
            tiles_used = set()
            for x in range(Game.BOARD_SIZE):
                try: current_tile = self.__potential_board[y][x]
                except:
                    print()
                    for i in self.__potential_board:
                        print(i)
                    input()
                    print(Game.BOARD_SIZE)
                    print(x,y)
                previous_tile = self.__confirmed_board[y][x]
                if current_tile != ' ':
                    if len(current_word) == 0:
                        start = [y, x]
                    current_word += current_tile 
                    current_word_score += Game.letter_values[current_tile]  
                    #print(previous_tile,current_tile)  
                    if previous_tile == ' ':
                        tiles_used.add((y,x))
                        new_word = True
                        if (y,x) in Game.double_word or (x,y) in Game.double_word:
                            #print('DOUBLE WORD')
                            score_multiplier *= 2
                        elif (y,x) in Game.triple_word or (x,y) in Game.triple_word:
                            #print('TRIPLE WORD')
                            score_multiplier *= 3
                        elif (y,x) in Game.double_letter or (x,y) in Game.double_letter:
                            #print('DOUBLE LETTER', current_tile)
                            current_word_score += Game.letter_values[current_tile]  
                        elif (y,x) in Game.triple_letter or (x,y) in Game.triple_letter:
                            #print('TRIPLE LETTER', current_tile)
                            current_word_score += Game.letter_values[current_tile]*2  

                    elif previous_tile == current_tile:
                        old_tile = True
                if current_tile == ' ' or x == Game.BOARD_SIZE - 1:
                    if new_word and len(current_word) > 1:
                        if current_word not in Game.large_dic:
                            self.__move_feedback = current_word.upper() + ' is not in the dictionary'
                            return False
                        if tiles_used == self.__new_tiles:
                            complete_tile_usage = True
                        current_word_score *= score_multiplier
                        new_words.append(current_word)
                        word_scores.append(current_word_score)
                        if old_tile:
                            unused_tiles = unused_tiles - tiles_used
                    current_word = ''
                    current_word_score = 0
                    score_multiplier = 1
                    new_word = False
                    old_tile = False
                    tiles_used = set()
        #Scanning column by column
        for x in range(Game.BOARD_SIZE):
            new_word = False
            old_tile = False
            current_word = ''
            tiles_used = set()
            for y in range(Game.BOARD_SIZE):
                current_tile = self.__potential_board[y][x]
                previous_tile = self.__confirmed_board[y][x]
                if current_tile != ' ':
                    if len(current_word) == 0:
                        start = [y, x]
                    current_word += current_tile 
                    current_word_score += Game.letter_values[current_tile]  
                    if previous_tile == ' ':
                        tiles_used.add((y,x))
                        new_word = True
                        if (y,x) in Game.double_word or (x,y) in Game.double_word:
                            #print('DOUBLE WORD')
                            score_multiplier *= 2
                        elif (y,x) in Game.triple_word or (x,y) in Game.triple_word:
                            #print('TRIPLE WORD')
                            score_multiplier *= 3
                        elif (y,x) in Game.double_letter or (x,y) in Game.double_letter:
                            #print('DOUBLE LETTER', current_tile)
                            current_word_score += Game.letter_values[current_tile]  
                        elif (y,x) in Game.triple_letter or (x,y) in Game.triple_letter:
                            #print('TRIPLE LETTER', current_tile)
                            current_word_score += Game.letter_values[current_tile]*2  
                    elif previous_tile == current_tile:
                        old_tile = True
                if current_tile == ' ' or y == Game.BOARD_SIZE - 1:
                    if new_word and len(current_word) > 1:
                        if current_word not in Game.large_dic:
                            self.__move_feedback = current_word.upper() + ' is not in the dictionary'
                            return False
                        if tiles_used == self.__new_tiles:
                            complete_tile_usage = True
                        current_word_score *= score_multiplier
                        new_words.append(current_word)
                        word_scores.append(current_word_score)
                        if old_tile:
                            unused_tiles = unused_tiles - tiles_used
                    current_word = ''
                    current_word_score = 0
                    score_multiplier = 1
                    new_word = False
                    old_tile = False
                    tiles_used = set()

        right_angle = False
        if len(unused_tiles) > 0:
            if len(x_s)  == 1:
                for t in self.__new_tiles:
                    y = t[0]
                    x = t[1]
                    try:
                        if self.__potential_board[y][x+1] != ' ':
                            right_angle = True
                            break
                    except: print("AAARRRGGGGHH")
                    try:
                        if self.__potential_board[y][x-1] != ' ':
                            right_angle = True
                            break
                    except: print("AAARRRGGGGHH")
            elif  len(y_s) == 1:
                for t in self.__new_tiles:
                    y = t[0]
                    x = t[1]
                    try:
                        if self.__potential_board[y+1][x] != ' ':
                            right_angle = True
                            break
                    except: print("AAARRRGGGGHH")
                    try:
                        if self.__potential_board[y-1][x] != ' ':
                            right_angle = True
                            break
                    except: print("AAARRRGGGGHH")

        if self.__round > 0 and len(unused_tiles) != 0 and not right_angle:
            self.__move_feedback = 'Form new words with existing tiles'
            return False
        if self.__round == 0 and (7,7) not in self.__new_tiles:
            self.__move_feedback = 'Place first word on centre square'
            return False
        if not complete_tile_usage:
            self.__move_feedback = 'Form a single word with all tiles used'
            return False
        if len(new_words) == 0:
            self.__move_feedback = 'Create at least one new word'
            return False
        if self.__players[self.__current_turn].get_type() == 'Human':
            self.__move_feedback = 'VALID SUBMISSION - ' + str(sum(word_scores)) + ' POINTS!'
        else:
            self.__move_feedback = 'COMPUTER SUBMISSION - ' + str(sum(word_scores)) + ' POINTS'
        if len(self.__new_tiles) == 7:
            word_scores.append(50)
            new_words.append('BINGO BONUS!!')
            self.__move_feedback += ' (+50 bingo)'
        print([new_words, word_scores])
        return [new_words, word_scores]

    def __generate_computer_moves(self):
        best_move_score = 0
        best_move_direction = ''
        best_move_board = []
        best_move_tiles = set()
        tiles = self.__players[self.__current_turn].get_tiles()
        for iterator in range(2):
            for tile in self.__tiles_occupied:
                current_tile = self.__confirmed_board[tile[0]][tile[1]]
                tiles.append(current_tile)
                if iterator == 0: words = self.__players[self.__current_turn].get_highest_scoring_moves(tiles, current_tile)
                else: words = self.__players[self.__current_turn].get_lowest_scoring_moves(tiles, current_tile)
                for w in words:
                    #placing vertically
                    pos = w.index(current_tile)
                    start = (tile[0]-pos, tile[1])
                    max_length = 15 - tile[0]
                    if max_length >= len(w):
                        valid = True
                        for i in range(len(w)):
                            y = start[0] + i
                            x = start[1]
                            if self.__potential_board[y][x] == ' ':
                                self.__new_tiles.add((y,x))
                                self.__potential_board[y][x] = w[i]
                            elif self.__potential_board[y][x] == w[i]:
                                continue
                            else:
                                valid = False
                                break
                        if valid:
                            result = self.__check_submission()
                            if result != False:
                                score = sum(result[1])
                                if score > best_move_score:
                                    best_move_score = score
                                    best_move_board = copy.deepcopy(self.__potential_board)
                                    best_move_tiles = copy.deepcopy(self.__new_tiles)

                    #placing horizontally
                    start = (tile[0], tile[1]-pos)
                    max_length = 15 - tile[1]
                    if max_length >= len(w):
                        valid = True
                        for i in range(len(w)):
                            y = start[0]
                            x = start[1] + i
                            if self.__potential_board[y][x] == ' ':
                                self.__new_tiles.add((y,x))
                                self.__potential_board[y][x] = w[i]
                            elif self.__potential_board[y][x] == w[i]:
                                continue
                            else:
                                valid = False
                                break
                        if valid:
                            result = self.__check_submission()
                            if result != False:
                                score = sum(result[1])
                                if score > best_move_score:
                                    best_move_score = score
                                    best_move_board = copy.deepcopy(self.__potential_board)
                                    best_move_tiles = copy.deepcopy(self.__new_tiles)

                    self.__new_tiles = set()
                    self.__potential_board = copy.deepcopy(self.__confirmed_board)
            
                tiles.pop()
                j = 1
            
            if best_move_score != 0:
                break
                
            #if no words are found, algorithm is repeated but searching for 10 lowest scoring moves for each tile instead
        for t in best_move_tiles:
            char = best_move_board[t[0]][t[1]]
            self.__players[self.__current_turn].remove_char(char)

        if best_move_score > 0:
            self.__new_tiles = copy.deepcopy(best_move_tiles)
            self.__potential_board = copy.deepcopy(best_move_board)
        else:
            self.__tile_swap = True
            self.__to_be_swapped = [i for i in range(7)]
        self.__update_turn_interface()
        Game.window.after(2000, self.__submit_move)

class Player:
    def __init__(self, position):
        self._points = 0
        self._tiles = [' ' for i in range(7)]
        self._words_played =[]
        self._type = 'Human'
        self._name = 'Player ' + str(position)    

    def refill_tiles(self, new_tiles):
        l = len(new_tiles)
        for i in range(l):
            self._tiles[self._tiles.index(' ')] = new_tiles.pop(0)
    
    def remove_tile(self, pos):
        self._tiles[pos] = ' '
    
    def remove_char(self, char):
        self._tiles[self._tiles.index(char)] = ' '
    
    def return_tile(self, pos, char):
        self._tiles[pos] = char
    
    def get_tiles_needed(self):
        return self._tiles.count(' ')
    
    def get_tile(self, location):
        return self._tiles[location]
    
    def get_tiles(self):
        return self._tiles
    
    def get_words_played(self):
        return self._words_played
    
    def get_current_points(self):
        return self._points
    
    def get_name(self):
        return self._name
    
    def get_type(self):
        return self._type
    
    def add_words_played(self, words):
        self._words_played = self._words_played + words
    
    def increment_score(self, points):
        self._points += points

class Computer(Player):
    def __init__(self, position):
        super().__init__(position)
        self._type = 'Computer'

    def get_highest_scoring_moves(self, tiles, must_have):
        #semi brute-force of trying to find 10 highest-scoring words from avaiable tiles
        relevant_tiles = Game.dic_df[[all(True if (word.count(letter) <= tiles.count(letter)) and (must_have in word) else False for letter in word) for word in Game.dic_df['word']]]
        relevant_tiles = relevant_tiles.sort_values('score',ascending = False).head(10)
        #print(relevant_tiles.head())
        return list(relevant_tiles['word'])
    
    def get_lowest_scoring_moves(self, tiles, must_have):
        relevant_tiles = Game.dic_df[[all(True if (word.count(letter) <= tiles.count(letter)) and (must_have in word) else False for letter in word) for word in Game.dic_df['word']]]
        relevant_tiles = relevant_tiles.sort_values('score',ascending = True).head(10)
        return list(relevant_tiles['word'])

Game('Computer')
Game.window.mainloop()